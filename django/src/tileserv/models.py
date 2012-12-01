# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
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

from django.http import Http404
from django.db import models
from math import pi,exp,atan
import mapnik
from sqlite3 import Binary

RAD_TO_DEG = 180/pi

class GoogleProjection:
    def __init__(self,levels=18):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2

    def fromTileToLL(self, zoom, x, y):
         e = self.zc[zoom]
         f = (x*256.0 - e[0])/self.Bc[zoom]
         g = (y*256.0 - e[1])/-self.Cc[zoom]
         h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)


class BlobField(models.Field):
    description = 'Sqlite BLOB Field'

    def db_type(self, connection):
        return 'BLOB'

    def get_db_prep_value(self, value, connection, prepared=False):
        return Binary(value)

class TileModel(models.Model):

    zoom = models.IntegerField(primary_key=True)
    tilex = models.IntegerField()
    tiley = models.IntegerField()
    pixbuf = BlobField()

    class Meta:
        abstract = True


class TileManager(models.Manager):

    def __init__(self, style, empty=None, maxzoom=18):
        models.Manager.__init__(self)
        self.emptytile = empty

        self.map = mapnik.Map(256, 256)
        mapnik.load_map(self.map, style)
        self.mproj = mapnik.Projection(self.map.srs)
        self.gproj = GoogleProjection(maxzoom)


    def get_image(self, zoom, tilex, tiley):
        objset = self.filter(zoom=zoom,tilex=tilex,tiley=tiley)

        if not objset:
            if self.emptytile is None:
                raise Http404
            else:
                return self.emptytile

        image = objset[0].pixbuf
        if image is None:
            print 'Rendering tile', zoom, tilex, tiley
            p0 = self.gproj.fromTileToLL(zoom, tilex, tiley+1)
            p1 = self.gproj.fromTileToLL(zoom, tilex+1, tiley)

            c0 = self.mproj.forward(mapnik.Coord(p0[0],p0[1]))
            c1 = self.mproj.forward(mapnik.Coord(p1[0],p1[1]))

            bbox = mapnik.Box2d(c0.x, c0.y, c1.x, c1.y)
            self.map.zoom_to_box(bbox)

            im = mapnik.Image(256, 256)
            mapnik.render(self.map, im)

            image = im.tostring('png256')
            # update the hard way, django can't handle multikeys
            objset.update(pixbuf=image)

        return image
