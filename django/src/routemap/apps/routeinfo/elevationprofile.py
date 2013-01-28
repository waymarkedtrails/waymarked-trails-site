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

import django.contrib.gis.geos as geos

from osgeo import gdal
from scipy.ndimage import map_coordinates
from shapely.geometry import shape
from shapely.geometry import asLineString
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely import wkt

import random
import numpy as np
import json
import math

from django.utils.importlib import import_module

table_module, table_class = settings.ROUTEMAP_ROUTE_TABLE.rsplit('.',1)
table_module = import_module(table_module)

def elevRound(x, base=5):
    return int(base * round(float(x)/base))

def elevation_profile_json(request, route_id=None):
    cacheTime = 60*60*24

    # Check if geojson for this relation exist in cache
    # If not, create it
    geojson = None #cache.get(route_id)
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

        # Smooth graph
        elevArray = smoothList(elevArray, 7)

        # Make sure we start at lowest point on relation
        # Reverse array if last elevation is lower than first elevation
        if(elevArray[0]>elevArray[len(elevArray)-1]):
            elevArray = elevArray[::-1]
            
        # Calculate accumulated ascent
        accuracy = 30
        formerHeight = 0
        accumulatedAscent = -elevArray[0] # Make sure we start at zero
        for currentHeight in elevArray:
            diff = currentHeight-formerHeight
            if math.fabs(diff)>accuracy:
                if diff>accuracy:
                    accumulatedAscent += diff
                formerHeight = currentHeight
        accumulatedAscent = elevRound(accumulatedAscent, 10)
            
        # Calculate accumulated descent
        accuracy = 30
        formerHeight = elevArray[0]
        accumulatedDescent = 0
        for currentHeight in elevArray:
            diff = formerHeight-currentHeight
            if math.fabs(diff)>accuracy:
                if diff>accuracy:
                    accumulatedDescent += diff
                formerHeight = currentHeight   
            #if height-elev<-5:  
            #    height = elev 
        accumulatedDescent = elevRound(accumulatedDescent, 10)

        features = []
        for i in range(len(elevArray)):
            geom = {'type': 'Point', 'coordinates': [pointX[i],pointY[i]]}
            feature = {'type': 'Feature',
                       'geometry': geom,
                       'crs': {'type': 'EPSG', 'properties': {'code':'900913'}},
                       'properties': {'distance': str(distArray[i]), 'elev': str(elevArray[i])}
                       }
            features.append(feature);

        geojson = {'type': 'FeatureCollection',
                   'properties': {'accumulatedAscent': str(accumulatedAscent),
                                  'accumulatedDescent': str(accumulatedDescent)},
                   'features': features}
        #print geojson

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
    

def convertGeoLocationToPixelLocation(X, Y, imageData):
    g0, g1, g2, g3, g4, g5 = imageData.GetGeoTransform()
    xGeo, yGeo =  X, Y
    if g2 == 0:
        xPixel = (xGeo - g0) / float(g1)
        yPixel = (yGeo - g3 - xPixel*g4) / float(g5)
    else:
        xPixel = (yGeo*g2 - xGeo*g5 + g0*g5 - g2*g3) / float(g2*g4 - g1*g5)
        yPixel = (xGeo - g0 - xPixel*g1) / float(g2)
    return int(round(xPixel)), int(round(yPixel))

def createRasterArray(ulx, uly, lrx, lry):
    
    source = gdal.Open(settings.ELEVATION_PROFILE_DEM)
    gt = source.GetGeoTransform()
    
    # Calculate pixel coordinates
    upperLeftPixelX, upperLeftPixelY = convertGeoLocationToPixelLocation(ulx, uly, source)
    lowerRightPixelX, lowerRightPixelY = convertGeoLocationToPixelLocation(lrx, lry, source)
    # Get rasterarray
    band_array = source.GetRasterBand(1).ReadAsArray(upperLeftPixelX, upperLeftPixelY , lowerRightPixelX-upperLeftPixelX , lowerRightPixelY-upperLeftPixelY)
    source = None # close raster
    return gt, band_array
    
def calcElev(linestring):
    # Calculate area in image to get
    # Get bounding box of area
    bbox = linestring.extent # GeoDjango extent

    # Holds coordinates where we check for elevation
    pointArrayX = []
    pointArrayY = []
    # Holds distance according to above coordinates
    distArray = []
    
    #
    # Convert line to UTM33
    # This should be changed according to coverage of your dataset
    #
    localProjection = 32633
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
        geoDjangoPoint.transform(900913)
        pointArrayX.append(geoDjangoPoint.x)
        pointArrayY.append(geoDjangoPoint.y)
        distArray.append(step)
        step = step + stepDist
            
   
    # Expand the bounding box with 200 meter on each side
    ulx = bbox[0]-200 
    uly = bbox[3]-200
    lrx = bbox[2]+200
    lry = bbox[1]+200
  
    gt, band_array = createRasterArray(ulx, uly, lrx, lry)
    
    nx = len(band_array[0])
    ny = len(band_array)

    # Compute mid-point grid spacings
    ax = np.array([ulx + ix*gt[1] + gt[1]/2.0 for ix in range(nx)])
    ay = np.array([uly + iy*gt[5] + gt[5]/2.0 for iy in range(ny)])

    # Create numpy array
    z = np.array(band_array)

    # Set min/max values of image
    ny, nx = z.shape
    xmin, xmax = ax[0], ax[nx-1] #ax[5136] 
    ymin, ymax = ay[ny-1], ay[0] #ay[5144], ay[0]
    
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
    elev = map_coordinates(z, [yi, xi], order=1)

    return (distArray, elev, pointArrayX, pointArrayY)
    


