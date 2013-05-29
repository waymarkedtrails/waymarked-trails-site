# -*- coding: utf-8 -*-
# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2012-2013 Espen Oldeman Lund
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.translation import ugettext as _

import django.contrib.gis.geos as geos

from osgeo import gdal
from scipy.ndimage import map_coordinates
from shapely.geometry import shape
from shapely.geometry import asLineString
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely import wkt
from math import ceil

import random
import numpy as np
import json
import math

from django.utils.importlib import import_module

table_module, table_class = settings.ROUTEMAP_ROUTE_TABLE.rsplit('.',1)
table_module = import_module(table_module)

db_srid = int(settings.DATABASES['default']['SRID'])

def elevRound(x, base=5):
    return int(base * round(float(x)/base))

def elevation_profile_json(request, route_id=None):
    cacheTime = 60*60*24

    # Check if geojson for this relation exist in cache
    # If not, create it
    geojson = None
    if not settings.DEBUG:
        geojson = cache.get(route_id)
    if geojson is None:
        qs = getattr(table_module, table_class).objects.filter(id=route_id)
        # for the moment only simple line strings can be processed because
        # multiline strings are not correctly ordered.
        qs = qs.extra(where=["ST_GeometryType(geom) = 'ST_LineString'"]).only("geom")
        if not qs:
            return HttpResponseNotFound(json.dumps(geojson), content_type="text/json")
        rel = qs[0]
        nrpoints = rel.geom.num_coords
        linestrings = rel.geom
        newLinstrings = wkt.loads(linestrings.wkt)

        # Array holding information used in graph
        distArray = []
        elevArray = []
        pointX = []
        pointY = []

        # Calculate elevations
        distArray, elevArray, pointX, pointY = calcElev(linestrings)

        # set void areas to None
        elevArray = np.array([x if x > -5000 else None for x in elevArray], dtype=np.float)

        # Smooth graph
        elevArray = smoothList(elevArray, 7)

        # Make sure we start at lowest point on relation
        # Reverse array if last elevation is lower than first elevation
        if pointX[0] > pointX[-1]:
            elevArray = elevArray[::-1]
            pointX = pointX[::-1]
            pointY = pointY[::-1]
            maxdist = distArray[-1]
            distArray = [maxdist - d for d in distArray[::-1]]
            
        # Calculate accumulated ascent
        # Slightly complicated by the fact that we have to jump over voids.
        accuracy = settings.ELEVATION_ACCURACY
        formerHeight = None
        firstvalid = None
        lastvalid = None
        accumulatedAscent = 0
        for x in range (1, len(elevArray)-1):
            currentHeight = elevArray[x]
            if not np.isnan(currentHeight):
                lastvalid = currentHeight
                if formerHeight is None:
                    formerHeight = currentHeight
                    firstvalid = currentHeight
                else:
                    if (elevArray[x-1] < currentHeight > elevArray[x+1]) or \
                         (elevArray[x-1] > currentHeight < elevArray[x+1]):
                        diff = currentHeight-formerHeight
                        if math.fabs(diff)>accuracy:
                            if diff>accuracy:
                                accumulatedAscent += diff
                            formerHeight = currentHeight

        if lastvalid is None:
            # looks like the route is completely within a void
            return HttpResponseNotFound(json.dumps(geojson), content_type="text/json")

        # collect the final point
        diff = lastvalid-formerHeight
        if diff>accuracy:
            accumulatedAscent += diff
        accumulatedAscent = elevRound(accumulatedAscent, settings.ELEVATION_ROUNDING)
            
        # Calculate accumulated descent
        accumulatedDescent = accumulatedAscent - (lastvalid - firstvalid)
        accumulatedDescent = elevRound(accumulatedDescent, settings.ELEVATION_ROUNDING)
        

        features = []
        for i in range(len(elevArray)):
            geom = {'type': 'Point', 'coordinates': [pointX[i],pointY[i]]}
            feature = {'type': 'Feature',
                       'geometry': geom,
                       'properties': {'distance': str(distArray[i]), 'elev': str(elevArray[i])}
                       }
            features.append(feature);
            
        prop = {}
        if accumulatedAscent < accuracy:
            prop['accumulatedAscent'] = _("less than %s m") % accuracy
        else:
            prop['accumulatedAscent'] = _("%s m") % accumulatedAscent
        if accumulatedDescent < accuracy:
            prop['accumulatedDescent'] = _("less than %s m") % accuracy
        else:
            prop['accumulatedDescent'] = _("%s m") % accumulatedDescent

        geojson = {'type': 'FeatureCollection',
                   'crs': {'type': 'EPSG', 'properties': {'code':str(db_srid)}},
                   'properties': prop,
                   'features': features}

        # Cache geojson
        cache.set(route_id, geojson, cacheTime)

    return HttpResponse(json.dumps(geojson), content_type="text/json")

#
# Code from http://stackoverflow.com/questions/5515720/python-smooth-time-series-data
#
def smoothList(x,window_len=7,window='hanning'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."
    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
    s=np.r_[2*x[0]-x[window_len-1::-1],x,2*x[-1]-x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:  
        w=eval('np.'+window+'(window_len)')
    y=np.convolve(w/w.sum(),s,mode='same')

    return y[window_len:-window_len+1]
    

def convertGeoLocationToPixelLocation(X, Y, geotransform):
    g0, g1, g2, g3, g4, g5 = geotransform
    xGeo, yGeo =  X, Y
    if g2 == 0:
        xPixel = (xGeo - g0) / float(g1)
        yPixel = (yGeo - g3 - xPixel*g4) / float(g5)
    else:
        xPixel = (yGeo*g2 - xGeo*g5 + g0*g5 - g2*g3) / float(g2*g4 - g1*g5)
        yPixel = (xGeo - g0 - xPixel*g1) / float(g2)
    return xPixel, yPixel


def convertPixelLocationToGeoLocation(x, y, geotransform):
    g0, g1, g2, g3, g4, g5 = geotransform

    if g2 == 0:
        xout = x*float(g1) + g0
        yout = float(g5)*y + float(g4)*(x - g0)/g1 + g3
    else:
        xout = g2*y + x*g1 + float(g0)
        yout = (x*(float(g2*g4)-float(g1*g5)+xout*g5-g0*g5+g2*g3))/float(g2)
    return xout, yout



def createRasterArray(ulx, uly, lrx, lry):
    
    source = gdal.Open(settings.ELEVATION_PROFILE_DEM)
    gt = source.GetGeoTransform()
    
    # Calculate pixel coordinates (rounding always toward the outside)
    upperLeftPixelX, upperLeftPixelY = convertGeoLocationToPixelLocation(ulx, uly, gt)
    lowerRightPixelX, lowerRightPixelY = convertGeoLocationToPixelLocation(lrx, lry, gt)
    upperLeftPixelX = int(upperLeftPixelX)
    upperLeftPixelY = int(upperLeftPixelY)
    lowerRightPixelX = int(ceil(lowerRightPixelX))
    lowerRightPixelY = int(ceil(lowerRightPixelY))
    # Get rasterarray
    band_array = source.GetRasterBand(1).ReadAsArray(upperLeftPixelX, upperLeftPixelY , lowerRightPixelX-upperLeftPixelX+1 , lowerRightPixelY-upperLeftPixelY+1)

    source = None # close raster
    # compute true boundaries (after rounding) of raster array
    xmax, ymax = convertPixelLocationToGeoLocation(upperLeftPixelX, upperLeftPixelY, gt)
    xmin, ymin = convertPixelLocationToGeoLocation(lowerRightPixelX, lowerRightPixelY, gt)
    return band_array, xmin, ymin, xmax, ymax

def calcElev(linestring):
    # Calculate area in image to get
    # Get bounding box of area
    bbox = linestring.extent # GeoDjango extent

    # Holds coordinates where we check for elevation
    pointArrayX = []
    pointArrayY = []
    # Holds distance according to above coordinates
    distArray = []
    
    # Uglyness: guess the right UTM-Zone
    centerpt = geos.Point((bbox[0] + bbox[2])/2.0, (bbox[1] + bbox[3])/2.0, srid=db_srid)
    centerpt.transform(4326)
    if centerpt.y > 0:
        localProjection = 32600
    else:
        localProjection = 32700
    localProjection = localProjection + int((centerpt.x + 180)/6)
    linestring.transform(localProjection)

    #
    # Set distance for interpolation on line according to length of route
    # - projectedLinestrings.length defines length of route in meter 
    # - stepDist defines how often we want to extract a height value
    #   i.e. stepDist=50 defines that we should extract an elevation value for 
    #   every 50 meter along the route
    stepDist = 0
    if linestring.length < 2000: 
        stepDist = 20
    elif linestring.length >1999 and linestring.length < 4000:
        stepDist = 100
    elif linestring.length >3999 and linestring.length < 10000:
        stepDist = 100
    else:
        stepDist = 200
            
    #
    # Make interpolation point along line with stepDist form above.
    # Add these point to arrays.
    # Need to convert line to Shapely since we are using interpolate function
    #
    wktLine = linestring.wkt
    shapelyLinestring = wkt.loads(wktLine)
    step = 0        
    while step<linestring.length+stepDist:
        shapelyPoint =  shapelyLinestring.interpolate(step)
        wktPoint = wkt.dumps(shapelyPoint)
        geoDjangoPoint = geos.fromstr(wktPoint, srid=localProjection)
        geoDjangoPoint.transform(db_srid)
        pointArrayX.append(geoDjangoPoint.x)
        pointArrayY.append(geoDjangoPoint.y)
        distArray.append(step)
        step = step + stepDist
            
   
    # Expand the bounding box with 200 meter on each side
    band_array, xmax, ymin, xmin, ymax = createRasterArray(bbox[0], bbox[3], bbox[2], bbox[1])
    
    ny, nx = band_array.shape

    # Turn these into arrays of x & y coords
    xi = np.array(pointArrayX, dtype=np.float)
    yi = np.array(pointArrayY, dtype=np.float)

    # Now, we'll set points outside the boundaries to lie along an edge
    xi[xi > xmax] = xmax
    xi[xi < xmin] = xmin
    yi[yi > ymax] = ymax
    yi[yi < ymin] = ymin

    # We need to convert these to (float) indicies
    #   (xi should range from 0 to (nx - 1), etc)
    xi = (nx - 1) * (xi - xmin) / (xmax - xmin)
    yi = -(ny - 1) * (yi - ymax) / (ymax - ymin)

    # Interpolate elevation values
    # map_coordinates does cubic interpolation by default, 
    # use "order=1" to preform bilinear interpolation
    elev = map_coordinates(band_array, [yi, xi], order=1)

    return (distArray, elev, pointArrayX, pointArrayY)
    


