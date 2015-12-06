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
from geoalchemy2.elements import WKTElement

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
        #return "ST_SetSRID(ST_MakeBox2D(ST_Point(%f,%f),ST_Point(%f,%f)),3857)" % self.coords
        return sa.func.ST_SetSrid(sa.func.ST_MakeBox2D(
                    WKTElement('POINT(%f %f)' % self.coords[0:2]),
                    WKTElement('POINT(%f %f)' % self.coords[2:4])), 3857)



class RouteLists(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
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

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search(self, query=None, limit=None, page=None):
        cfg = cherrypy.request.app.config
        limit = int(limit) if limit is not None and limit.isdigit() else 10
        if limit > 100:
            limit = 100
        page = int(page) if page is not None and page.isdigit() else 1
        if page > 10:
            page = 10

        maxresults = page * limit

        r = cfg['DB']['map'].tables.routes.data
        base = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol, r.c.level])

        out = OrderedDict()
        out['query'] = query
        out['symbol_url'] = '%(MEDIA_URL)s/symbols/%(BASENAME)s/' % cfg['Global']

        objs = []

        # First try: exact match of ref
        refmatch = base.where(r.c.name == '[%s]' % query).limit(maxresults+1)

        for r in cherrypy.request.db.execute(refmatch):
            objs.append(api.common.RouteDict(r))

        # Second try: fuzzy matching of text
        if len(objs) <= maxresults:
            sim = sa.func.similarity(r.c.name, query)
            res = sa.select([r.c.id, r.c.name, r.c.intnames,
                              r.c.symbol, r.c.level, sim.label('sim')])\
                    .where(r.c.name.notlike('(%'))\
                    .order_by('sim DESC')\
                    .limit(maxresults - len(objs) + 1)
            if objs:
                res = res.where(sim > 0.5)
            else:
                res = res.where(sim > 0.1)

            print(res)

            maxsim = None
            for r in cherrypy.request.db.execute(res):
                print(r['sim'])
                if maxsim is None:
                    maxsim = r['sim']
                    print("Initial", maxsim)
                elif maxsim > r['sim'] * 3:
                    break
                objs.append(api.common.RouteDict(r))

        out['results'] = objs[:limit]

        return out


    @cherrypy.expose
    def segments(self, ids=None, bbox=None, **params):
        b = Bbox(bbox)

        idlist = [ int(x) for x in ids.split(',') if x.isdigit() ]

        r = cherrypy.request.app.config['DB']['map'].tables.routes.data

        sel = sa.select([r.c.id,
                         r.c.geom.ST_Intersection(b.as_sql()).ST_AsGeoJSON()])\
               .where(r.c.id.in_(idlist))

        cherrypy.response.headers['Content-Type'] = 'text/json'

        outstr = """{ "type": "FeatureCollection",
                    "crs": { "type": "name",
                             "properties": { "name": "EPSG:3857"}
                           },
                    "features": ["""

        sep = ''
        print(sel)
        for r in cherrypy.request.db.execute(sel):
            outstr += sep + '{ "type": "Feature", "geometry":'
            outstr += r[1]
            outstr += ', "id" :' + str(r[0]) + '}'
            sep = ','

        outstr += "]}"

        return outstr.encode('utf-8')
