# -*- coding: utf-8 -*-

#from collections import namedtuple
#from django.utils.translation import ugettext as _
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
#from django.views.generic.simple import direct_to_template
#from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page

import django.contrib.gis.geos as geos

from osgeo import gdal
from scipy.ndimage import map_coordinates
from shapely.geometry import shape
from shapely.geometry import asLineString
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely import wkt

import geojson
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pyproj
import random
import json

# Cache is set in seconds to 24 hrs, but should also be cleared on database update as there is no invalidation mechanism yet.
@cache_page(60 * 60 * 24, cache="default")
def elevation_profile_json(request, route_id=None, manager=None):
    #import elevationprofile
    try:
        rel = manager.get(id=route_id)
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})
    nrpoints = rel.geom.num_coords
    #print nrpoints
    #print rel.geom.num_coords
    
    linestrings = rel.geom
    
    
    geojson = ""
    
    newLinstrings = wkt.loads(linestrings.wkt)
    if(newLinstrings.geom_type == "MultiLineString"):
        print "Antall linestrings: " , len(newLinstrings)
        if newLinstrings.is_simple:
            print "Linje med opphold"
        elif newLinstrings.is_ring:
            print "Linje med ringer"
        else:
            print "Linje med forgreininger"
            print newLinstrings[0].length
            print newLinstrings[1].length
            print newLinstrings[2].length
            print newLinstrings[3].length
            print str(newLinstrings[2].intersects(newLinstrings[0]))
            print str(newLinstrings[2].intersects(newLinstrings[1]))
            print str(newLinstrings[2].intersects(newLinstrings[2]))
            print str(newLinstrings[2].intersects(newLinstrings[3]))

        
        #elevationRaster =  createMultiLineGraph(linestrings)
        geojson = ""
        return HttpResponseNotFound(json.dumps(geojson), content_type="text/json")
    else:
        # Array holding information used in graph
        distArray = []
        elevArray = []
        pointX = []
        pointY = []
        
        # Test code to test custom linestring
        """
        lon = 11.21889
        lat = 59.57127
        lon2 = 11.22460
        lat2 = 59.55879
        fromProj = pyproj.Proj(init='epsg:4326')
        toProj = pyproj.Proj(init='epsg:3785')
        x1, y1 = pyproj.transform(fromProj, toProj, lon, lat)
        x2, y2 = pyproj.transform(fromProj, toProj, lon2, lat2)
        linestrings = LineString([(x1, y1), (x2, y2)])
        """
        
        # Calculate elevations
        distArray, elevArray, pointX, pointY = calcElev(linestrings)  
        
        # Smooth graph
        elevArray = smoothList(elevArray, 7)  
        
        # Make sure we start at lowest point on relation
        # Reverse array if last elevation is lower than first elevation
        if(elevArray[0]>elevArray[len(elevArray)-1]):
            elevArray = elevArray[::-1]
        
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
                   'features': features}
        #print geojson
    
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


def elevation_profile_png(request, route_id=None, manager=None):
    #import elevationprofile
    try:
        rel = manager.get(id=route_id)
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})
    nrpoints = rel.geom.num_coords
    print nrpoints
    print rel.geom.num_coords
    
    linestrings = rel.geom
    if(linestrings.geom_type == "MultiLineString"):
        elevationRaster =  createMultiLineGraph(linestrings)
    else:
        elevationRaster =  createLineGraph(linestrings)
    
    image_data = open(elevationRaster, "rb").read()
    return HttpResponse(image_data, mimetype="image/png")
    #return HttpResponse(elevationRaster, content_type="text/html")
    
    
def createLineGraph(linestrings):

    # Size of final image
    pngWidth = 3 
    pngHeight = 2 
    
    # Array holding information used in graph
    distArray = []
    elevArray = []
    pointX = []
    pointY = []
    
    # Calculate elevations
    distArray, elevArray, pointX, pointY = calcElev(linestrings)    
    
    # Instantiate figure
    fig = plt.figure(num=None, figsize=(pngWidth, pngHeight), dpi=50)
    ax = fig.add_subplot(111)
    plt.grid(True)
    
    # Textlabels
    plt.xlabel(ur'Avstand p\u00E5 turen ', fontsize=10) #xlabel("\u00B0/Avstand på turen")
    plt.ylabel(ur'Antall h\u00F8ydemeter' , fontsize=10)

    # Create the plot
    ax.plot(distArray, elevArray)
    
    # Create custom ticks along plot
    locs, labels = plt.xticks()
    newLabels = []
    steps = 5
    distance = max(distArray)
    newLabels.append('') # First label in empty
    if distance>20000:
        for i in range(len(locs)):
            label = steps #int(labels[i])/1000
            newLabels.append(str(label) + 'km')
            steps = steps + 5
         
        plt.xticks(locs, newLabels )
        #plt.xticks(locs, ['', '5km','10km','15km','20km','25km', '30km'] )
    else:
        # Make different ticks depending on length of route
        if distance<2001:
            graphStep = 0.5
        elif distance > 2000 and distance<4000:
            graphStep = 1
        else:
            graphStep = 4
        steps = 0
        locSteps = 0
        newLocs = []
        newLocs.append(0)
        while locSteps<distance:
            steps = steps + graphStep
            locSteps = locSteps + graphStep*1000
            newLabels.append(str(steps) + 'km')
            newLocs.append(locSteps)
        plt.xticks(newLocs, newLabels )
        
        
    # Make sure there is some room around the graph
    # And make sure y=0 is always minimum y value    
    heightDiff = max(elevArray) - min(elevArray)
    heightBuffer = 0.6 * heightDiff
    minGraphBuffer = min(elevArray)-(0.1 * heightDiff)
    heightBuffer = (0.5 * heightDiff)
    if heightBuffer>250: # Make sure buffer is not too big 
        heightBuffer = 250 
    maxGraphBuffer = max(elevArray) + heightBuffer
    if minGraphBuffer<0: # Make sure graph starts at zero
        minGraphBuffer = 0
    ax.set_ylim(minGraphBuffer,maxGraphBuffer) 
        
    # Save image
    randomNum = int(random.random()*100000000)
    filename = settings.ELEVATION_PROFILE_TMP_DIR + "/elev_"+ str(randomNum) +".png"
    plt.savefig(filename, bbox_inches='tight', facecolor='#ecece9', edgecolor='none')
   
    return filename
    
def createMultiLineGraph(linestrings):
    
    """
    #argWidth = request.args.getlist("width")
    pngWidth = 3#int(argWidth[0])/100
    #argHeight = request.args.getlist("height")
    pngHeight = 2#int(argHeight[0])/100
    
    #linestrings = findLinestrings()
    
    distArray = []
    elevSumArray = []
    pointX = []
    pointY = []
    maxHeight = 0
    minHeight = 100000
    
    sizeX = pngWidth
    sizeY = pngHeight
    
    fig = plt.figure(num=None, figsize=(sizeX, sizeY), dpi=80)
    plt.subplots_adjust(wspace=0.05)

    dist = 0
    totalPlots = len(linestrings)
    numPlots = 0
    plots = []
    
    for linestring in linestrings:
        distArray, elevArray, _pointX, _pointY = calcElev(linestring)
        print "Nytt array"
        for elev in elevArray:
            print elev
            
        numPlots = numPlots + 1
        #for i in range(len(_elevArray)):
        #    dist = dist + stepDist
        #    distArray.append(dist)
        #    elevArray.append(_elevArray[i])
        #    pointX.append(_pointX[i])
        #    pointY.append(_pointY[i])   
    
        _minHeight = min(elevArray)
        if _minHeight < minHeight:
            minHeight = _minHeight
        _maxHeight = max(elevArray)
        if _maxHeight > maxHeight:
            maxHeight = _maxHeight    
        #elevSumArray.append(elevArray)
        plotNumber = str(1) + str(totalPlots) + str(numPlots)
        if numPlots > 1: # Ikke første grafen
            ax = plt.subplot(int(plotNumber), sharey=plots[0])
        else:
            ax = plt.subplot(int(plotNumber))
        ax.plot(distArray, elevArray)
        plots.append(ax)
        plt.title("Deltur " + str(numPlots))
        plt.grid(True)
      
     
        locs, labels = plt.xticks()
        newLabels = []
        steps = 5
        distance = max(distArray)
        print "Distance: " +  str(distance)
        newLabels.append('') # First label in empty
        if distance>20000:
            for i in range(len(locs)):
                label = steps #int(labels[i])/1000
                newLabels.append(str(label) + 'km')
                steps = steps + 5
             
            plt.xticks(locs, newLabels )
            #plt.xticks(locs, ['', '5km','10km','15km','20km','25km', '30km'] )
        else:
            if distance>0 and distance<1000:
                graphStep = 0.2
            elif distance>1000 and distance<2000:
                graphStep = 0.5
            elif distance>2000 and distance<4000:
                graphStep = 0.5
            elif distance>4000 and distance<1000000000:
                    graphStep = 2           
            steps = 0
            locSteps = 0
            newLocs = []
            newLocs.append(0)
            while locSteps<distance:
                steps = steps + graphStep
                locSteps = locSteps + graphStep*1000
                newLabels.append(str(steps) + 'km')
                newLocs.append(locSteps)
                #print str(locSteps) + " " +  str(steps)
            plt.xticks(newLocs, newLabels )
           
        
        
    print "maxHeight " + str(maxHeight)    
    print "minHeight " + str(minHeight)    
    heightDiff = maxHeight - minHeight
    heightBuffer = 0.6 * heightDiff
    minGraphBuffer = minHeight-(0.1 * heightDiff)
    heightBuffer = (0.5 * heightDiff)
    if heightBuffer>250: # Make sure buffer is not too big 
        heightBuffer = 250 
    maxGraphBuffer = maxHeight + heightBuffer
    if minGraphBuffer<0: # Make sure graph starts at zero
        minGraphBuffer = 0
    ax.set_ylim(minGraphBuffer,maxGraphBuffer) 
    
    for i in range(len(plots)):
        yticklabels = plots[i].get_yticklabels()
        plt.setp(yticklabels, visible=False)    
    
    yticklabels = plots[0].get_yticklabels()
    plt.setp(yticklabels, visible=True)    
    
    
    plt.savefig('elev.png', bbox_inches='tight')
    """
    
    filename = settings.ELEVATION_PROFILE_ERROR_IMG
    
    return filename
    
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

    # Holds coordinates where we check for elevation
    pointArrayX = []
    pointArrayY = []
    # Holds distance according to above coordinates
    distArray = []
    
    
    #
    # Convert line to spherical mercator
    #
    print "Starter transformering..."
    # Convert to numpy array
    ag = np.asarray(linestring)
    # Extract one array for lon and one for lat
    lon, lat = zip(*ag)
    # Define projections
    fromProj = pyproj.Proj(init='epsg:3785')
    toProj = pyproj.Proj(init='epsg:32633')
    # Reproject the line
    x2, y2 = pyproj.transform(fromProj, toProj, lon, lat)
    # Create new numpy array
    a = np.array(zip(x2,y2))
    # Recreate linestring
    projectedLinestrings = asLineString(a)
    print "Slutt transformering..."
    #
    # Set distance for interpolation on line according to length of route
    # - projectedLinestrings.length defines length of route in meter 
    # - stepDist defines how often we want to extract a height value
    #   i.e. stepDist=50 defines that we should extract an elevation value for 
    #   every 50 meter along the route
    stepDist = 0
    if projectedLinestrings.length < 2000: 
        stepDist = 20
    elif projectedLinestrings.length >1999 and projectedLinestrings.length < 4000:
        stepDist = 100
    elif projectedLinestrings.length >3999 and projectedLinestrings.length < 10000:
        stepDist = 100
    else:
        stepDist = 200
        
    
    
    #
    # Make interpolation point along line with stepDist form above.
    # Add these point to arrays.
    #
    step = 0    
    # Trur ikke multilinestringer kommer inn her lenger
    # så koden kan sannsynligvis fjernes
    
    print "Starter interpolering..."
    if(projectedLinestrings.geom_type == "MultiLineString"):
        for linestring in projectedLinestrings:
            while step<linestring.length+stepDist:
                point =  linestring.interpolate(step)
                # Project back to spherical mercator coordinates
                x, y = pyproj.transform(toProj, fromProj, point.x, point.y)
                pointArrayX.append(x)
                pointArrayY.append(y)
                distArray.append(step)
                step = step + stepDist
    elif(projectedLinestrings.geom_type == "LineString"):
        #linestring = projectedLinestrings
        while step<projectedLinestrings.length+stepDist:
            point =  projectedLinestrings.interpolate(step)
            # Project back to spherical mercator coordinates
            x, y = pyproj.transform(toProj, fromProj, point.x, point.y)
            pointArrayX.append(x)
            pointArrayY.append(y)
            distArray.append(step)
            step = step + stepDist
    print "Slutt interpolering..."
    print len(distArray)
    
    """    
    for coords in projectedLinestrings.coords:
        point  = Point(coords)
        x, y = pyproj.transform(toProj, fromProj, point.x, point.y)    
        pointArrayX.append(x)
        pointArrayY.append(y)
        distArray.append(projectedLinestrings.project(point))
    """
            
    # Calculate area in image to get
    # Get bounding box of area
    bbox = linestring.extent # GeoDjango extent
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
    


