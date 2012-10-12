# -*- coding: utf-8 -*-

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotFound
from django.conf import settings
from django.views.decorators.cache import cache_page

import django.contrib.gis.geos as geos

from osgeo import gdal
from scipy.ndimage import map_coordinates
from shapely.geometry import shape
from shapely.geometry import asLineString
from shapely.geometry import LineString
from shapely.geometry import Point
from shapely import wkt

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Cache is set in seconds to 24 hrs, but should also be cleared on database update as there is no invalidation mechanism yet.
#@cache_page(60 * 60 * 24, cache="default")
@cache_page(1, cache="default")
def elevation_profile_json(request, route_id=None, manager=None):
    try:
        rel = manager.get(id=route_id)
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})
    nrpoints = rel.geom.num_coords
    
    linestrings = rel.geom
    
    geojson = ""
    
    newLinstrings = wkt.loads(linestrings.wkt)
    if(newLinstrings.geom_type == "MultiLineString"):
        geojson = ""
        return HttpResponseNotFound(json.dumps(geojson), content_type="text/json")
    else:
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
    try:
        rel = manager.get(id=route_id)
    except:
        return direct_to_template(request, 'routes/info_error.html', {'id' : route_id})
    nrpoints = rel.geom.num_coords
    print nrpoints
    print rel.geom.num_coords
    
    linestrings = rel.geom
    if(linestrings.geom_type == "MultiLineString"):
        elevationRaster =  None
    else:
        elevationRaster =  createLineGraph(linestrings)
    
    image_data = open(elevationRaster, "rb").read()
    return HttpResponse(image_data, mimetype="image/png")
    
    
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
    plt.xlabel(ur'Avstand p\u00E5 turen ', fontsize=10) 
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
    


