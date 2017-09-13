# This file is part of waymarkedtrails.org
# Copyright (C) 2012-2013 Espen Oldeman Lund
# Copyright (C) 2015 Sarah Hoffmann
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

from collections import OrderedDict
from math import ceil, fabs

from osgeo import gdal
import numpy
from scipy.ndimage import map_coordinates

import config.defaults

def compute_elevation(segments, bounds, outdict):
    """ Takes a MultiPoint geometry and computes the elevation.
        Returns an array of x, y, ele.
    """
    # load the relevant elevation data
    dem = Dem(config.defaults.DEM_FILE)
    band_array, xmax, ymin, xmin, ymax = dem.raster_array(bounds)
    del dem

    ny, nx = band_array.shape

    elepoints = []
    ascent = 0
    descent = 0
    for xcoord, ycoord, pos in segments:
        # Turn these into arrays of x & y coords
        xi = numpy.array(xcoord, dtype=numpy.float)
        yi = numpy.array(ycoord, dtype=numpy.float)

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
        elev = smooth_list(map_coordinates(band_array, [yi, xi], order=1))

        a, d = compute_ascent(elev)
        ascent += a
        descent += d

        prop = 0 if elepoints else 1
        for x, y, ele, p in zip(xcoord, ycoord, elev, pos):
            info = OrderedDict()
            info['x'] = x
            info['y'] = y
            info['ele'] = float(ele)
            info['prop'] = prop
            info['pos'] = p
            elepoints.append(info)
            prop = 1

    outdict['elevation'] = elepoints
    outdict['ascent']  = ascent
    outdict['descent'] = descent

def round_elevation(x, base=config.defaults.DEM_ROUNDING):
    return int(base * round(float(x)/base))

def compute_ascent(elev):
    """ Calculate accumulated ascent and descent.
        Slightly complicated by the fact that we have to jump over voids.
    """
    accuracy = config.defaults.DEM_ACCURACY
    formerHeight = None
    firstvalid = None
    lastvalid = None
    accumulatedAscent = 0
    for x in range (1, len(elev)-1):
        currentHeight = elev[x]
        if not numpy.isnan(currentHeight):
            lastvalid = currentHeight
            if formerHeight is None:
                formerHeight = currentHeight
                firstvalid = currentHeight
            else:
                if (elev[x-1] < currentHeight > elev[x+1]) or \
                        (elev[x-1] > currentHeight < elev[x+1]):
                    diff = currentHeight-formerHeight
                    if fabs(diff) > accuracy:
                        if diff > accuracy:
                            accumulatedAscent += diff
                        formerHeight = currentHeight

    if lastvalid is None:
        # looks like the route is completely within a void
        return 0, 0

    # collect the final point
    diff = lastvalid - formerHeight
    if diff > accuracy:
        accumulatedAscent += diff

    # ascent, descent
    return round_elevation(accumulatedAscent), round_elevation(accumulatedAscent - (lastvalid - firstvalid))


class Dem(object):

    def __init__(self, src):
        self.source = gdal.Open(src)
        self.transform = self.source.GetGeoTransform()

    def raster_array(self, bbox):
        # Calculate pixel coordinates (rounding always toward the outside)
        ulx, uly = (int(x) for x in self.geo_to_pixel(bbox[0], bbox[3]))
        lrx, lry = (int(ceil(x)) for x in self.geo_to_pixel(bbox[2], bbox[1]))

        # Get rasterarray
        band_array = self.source.GetRasterBand(1).ReadAsArray(ulx, uly,
                                                              lrx - ulx + 1,
                                                              lry - uly + 1)

        # compute true boundaries (after rounding) of raster array
        xmax, ymax = self.pixel_to_geo(ulx, uly)
        xmin, ymin = self.pixel_to_geo(lrx, lry)

        return band_array, xmin, ymin, xmax, ymax

    def geo_to_pixel(self, x, y):
        g0, g1, g2, g3, g4, g5 = self.transform

        if g2 == 0:
            xPixel = (x - g0) / float(g1)
            yPixel = (y - g3 - xPixel*g4) / float(g5)
        else:
            xPixel = (y*g2 - x*g5 + g0*g5 - g2*g3) / float(g2*g4 - g1*g5)
            yPixel = (x - g0 - xPixel*g1) / float(g2)

        return xPixel, yPixel


    def pixel_to_geo(self, x, y):
        g0, g1, g2, g3, g4, g5 = self.transform

        if g2 == 0:
            xout = x*float(g1) + g0
            yout = float(g5)*y + float(g4)*(x - g0)/g1 + g3
        else:
            xout = g2*y + x*g1 + float(g0)
            yout = (x*(float(g2*g4)-float(g1*g5)+xout*g5-g0*g5+g2*g3))/float(g2)

        return xout, yout

#
# Code from http://stackoverflow.com/questions/5515720/python-smooth-time-series-data
#
def smooth_list(x,window_len=7,window='hanning'):
    s = numpy.r_[2*x[0] - x[window_len-1::-1], x, 2*x[-1] - x[-1:-window_len:-1]]
    if window == 'flat': #moving average
        w = numpy.ones(window_len,'d')
    else:
        w = getattr(numpy, window)(window_len)

    y = numpy.convolve(w/w.sum(), s, mode='same')

    return y[window_len:-window_len+1]

