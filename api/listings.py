# This file is part of waymarkedtrails.org
# Copyright (C) 2016 Sarah Hoffmann
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
from io import StringIO
import cherrypy
import sqlalchemy as sa

import config.defaults
import api.common

class GenericList(object):

    def num_param(self, limit, default, maxval):
        if limit is not None and limit.isdigit():
            limit = int(limit)

            return min(limit, maxval)

        return default

    def create_list_output(self, qkey, qvalue, res):
        out = OrderedDict()
        out[qkey] = qvalue
        out['symbol_url'] = '%(MEDIA_URL)s/symbols/%(BASENAME)s/' % (
                              cherrypy.request.app.config['Global'])
        out['results'] = [api.common.RouteDict(r) for r in res]
        return out

    def create_segments_out(self, segments):
        outstr = StringIO()
        outstr.write("""{ "type": "FeatureCollection",
                        "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
                        "features": [""")

        sep = ''
        for r in segments:
            outstr.write(sep)
            outstr.write('{ "type": "Feature", "geometry":')
            outstr.write(r[2])
            outstr.write(', "id" : "')
            outstr.write(str(r[0]))
            outstr.write(str(r[1]))
            outstr.write('"}')
            sep = ','

        outstr.write("]}")

        return outstr.getvalue().encode('utf-8')


class RouteLists(GenericList):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def by_area(self, bbox, limit=None, **params):
        b = api.common.Bbox(bbox)
        limit = self.num_param(limit, 20, 100)

        mapdb = cherrypy.request.app.config['DB']['map']
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

        return self.create_list_output('bbox', b.coords,
                                       cherrypy.request.db.execute(res))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def search(self, query=None, limit=None, page=None):
        cfg = cherrypy.request.app.config
        limit = self.num_param(limit, 10, 100)
        page = self.num_param(page, 1, 10)

        maxresults = page * limit

        r = cfg['DB']['map'].tables.routes.data
        base = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol, r.c.level])

        objs = []

        # First try: exact match of ref
        refmatch = base.where(r.c.name == '[%s]' % query).limit(maxresults+1)

        objs = cherrypy.request.db.execute(refmatch)[:]

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

            maxsim = None
            for r in cherrypy.request.db.execute(res):
                if maxsim is None:
                    maxsim = r['sim']
                elif maxsim > r['sim'] * 3:
                    break
                objs.append(r)

        return self.create_list_output('query', query, objs[:limit])


    @cherrypy.expose
    def segments(self, ids=None, bbox=None, **params):
        b = api.common.Bbox(bbox)

        idlist = [ int(x) for x in ids.split(',') if x.isdigit() ]

        r = cherrypy.request.app.config['DB']['map'].tables.routes.data

        sel = sa.select([sa.text("'r'"), r.c.id,
                         r.c.geom.ST_Intersection(b.as_sql()).ST_AsGeoJSON()])\
               .where(r.c.id.in_(idlist))

        cherrypy.response.headers['Content-Type'] = 'text/json'

        return self.create_segments_out(cherrypy.request.db.execute(sel))


