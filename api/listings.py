# This file is part of waymarkedtrails.org
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

import cherrypy
import sqlalchemy as sa

import config.defaults
import api.common

class Bbox(object):

    def __init__(self, value):
        parts = value.split(',')
        if len(parts) != 4:
            raise cherrypy.HTTPError(400, "No valid map area specified. Check the bbox parameter in the URL.")
        try:
            self.coords = tuple([float(x) for x in parts])
        except ValueError:
            raise cherrypy.HTTPError(400, "Invalid coordinates given for the map area. Check the bbox parameter in the URL.")

    def as_sql(self):
        return "SRID=3857;LINESTRING(%f %f, %f %f)" % self.coords



@cherrypy.tools.json_out()
class RouteLists(object):

    @cherrypy.expose
    def by_area(self, bbox, limit=20, **params):
        cfg = cherrypy.request.app.config
        b = Bbox(bbox)

        if limit > 100:
            limit = 100

        out = OrderedDict()
        out['bbox'] = b.coords
        out['symbol_url'] = '%(MEDIA_URL)s/symbols/%(BASENAME)s/' % cfg['Global']

        mapdb = cfg['DB']['map']
        r = mapdb.tables.routes.data
        s = mapdb.tables.segments.data
        h = mapdb.tables.hierarchy.data

        rels = sa.select([sa.func.unnest(s.c.rels).label('rel')], distinct=True)\
                .where(s.c.geom.intersects(b.as_sql())).alias()
        res = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol, r.c.level])\
               .where(r.c.top)\
               .where(r.c.id.in_(sa.select([h.c.parent], distinct=True)
                                   .where(h.c.child == rels.c.rel)))\
               .order_by(r.c.level, r.c.name)\
               .limit(limit)

        out['relations'] = [api.common.RouteDict(r)
                                   for r in cherrypy.request.db.execute(res)]

        return out


    @cherrypy.expose
    @cherrypy.popargs('zoom', 'x', 'y')
    def tile(self, zoom, x, y):
        return "TODO: get data for tile %s/%s/%s" % (zoom, x, y)

    def search(self, query=None):
        return "TODO: search"

    def segments(self, ids=None, bbox=None):
        return "TODO: jsonbox"

