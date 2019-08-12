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
        cherrypy.response.headers['Content-Type'] = 'text/json'
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
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def by_area(self, bbox, limit=None, **params):
        b = api.common.Bbox(bbox)
        limit = self.num_param(limit, 20, 100)

        mapdb = cherrypy.request.app.config['DB']['map']
        r = mapdb.tables.routes.data
        s = mapdb.tables.segments.data
        h = mapdb.tables.hierarchy.data

        rels = sa.select([sa.func.unnest(s.c.rels).label('rel')], distinct=True)\
                .where(s.c.geom.ST_Intersects(b.as_sql())).alias()
        res = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol, r.c.level,
                         r.c.ref])\
               .where(r.c.top)\
               .where(sa.or_(r.c.id.in_(sa.select([h.c.parent], distinct=True)
                                   .where(h.c.child == rels.c.rel)),
                             r.c.id.in_(rels)
                     ))\
               .order_by(sa.desc(r.c.level), r.c.name)\
               .limit(limit)

        return self.create_list_output('bbox', b.coords,
                                       cherrypy.request.db.execute(res))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def by_ids(self, ids, limit=None, **params):
        i = [int(n) for n in ids.split(',') if n.isdigit()][:100] # allow max 100 integer ids

        mapdb = cherrypy.request.app.config['DB']['map']
        r = mapdb.tables.routes.data

        res = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol,
                         r.c.level, r.c.ref])\
               .where(r.c.id.in_(i))\
               .order_by(r.c.level, r.c.name)

        return self.create_list_output('ids', i,
                                       cherrypy.request.db.execute(res))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def search(self, query=None, limit=None, page=None):
        cfg = cherrypy.request.app.config
        limit = self.num_param(limit, 10, 100)
        page = self.num_param(page, 1, 10)

        maxresults = page * limit

        r = cfg['DB']['map'].tables.routes.data
        base = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol,
                          r.c.ref, r.c.level])

        objs = []

        # First try: exact match of ref
        refmatch = base.where(sa.func.lower(r.c.ref) == query.lower()).limit(maxresults+1)
        for o in cherrypy.request.db.execute(refmatch):
            objs.append(o)

        # If that did not work and the search term is a number, maybe a relation
        # number?
        if not objs and len(query) > 3 and query.isdigit():
            idmatch = base.where(r.c.id == int(query))
            for o in cherrypy.request.db.execute(idmatch):
                objs.append(o)
            if objs:
                return self.create_list_output('query', query, objs)

        # Second try: fuzzy matching of text
        if len(objs) <= maxresults:
            sim = sa.func.similarity(r.c.name, query)
            res = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.ref,
                              r.c.symbol, r.c.level, sim.label('sim')])\
                    .order_by(sa.desc(sim))\
                    .limit(maxresults - len(objs) + 1)
            if objs:
                res = res.where(sim > 0.5)
            else:
                res = res.where(sim > 0.1)

            maxsim = None
            for o in cherrypy.request.db.execute(res):
                if maxsim is None:
                    maxsim = o['sim']
                elif maxsim > o['sim'] * 3:
                    break
                objs.append(o)

        return self.create_list_output('query', query, objs[:limit])


    @cherrypy.expose
    @cherrypy.tools.gzip(mime_types=['text/json'])
    def segments(self, relations=None, bbox=None, **params):
        b = api.common.Bbox(bbox)

        objs = []

        if relations is not None:
            idlist = [ int(x) for x in relations.split(',') if x.isdigit() ]

            r = cherrypy.request.app.config['DB']['map'].tables.routes.data

            sel = sa.select([sa.literal("r"), r.c.id,
                             r.c.geom.ST_Intersection(b.as_sql()).ST_AsGeoJSON()])\
                   .where(r.c.id.in_(idlist))

            objs = cherrypy.request.db.execute(sel)

        return self.create_segments_out(objs)

class SlopeLists(GenericList):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def by_area(self, bbox, limit=None, **params):
        b = api.common.Bbox(bbox)
        limit = self.num_param(limit, 20, 100)

        mapdb = cherrypy.request.app.config['DB']['map']
        r = mapdb.tables.routes.data
        s = mapdb.tables.segments.data
        h = mapdb.tables.hierarchy.data

        # get relations
        rels = sa.select([sa.func.unnest(s.c.rels).label('rel')], distinct=True)\
                .where(s.c.geom.ST_Intersects(b.as_sql())).alias()
        res = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol,
                         r.c.piste.label('level')])\
               .where(r.c.top)\
               .where(r.c.id.in_(sa.select([h.c.parent], distinct=True)
                                   .where(h.c.child == rels.c.rel)))\
               .order_by(r.c.geom.ST_Distance(b.center_as_sql()))\
               .limit(limit)

        objs = [x for x in cherrypy.request.db.execute(res)]

        # get ways
        if len(objs) < limit:
            w = mapdb.tables.ways.data
            ws = mapdb.tables.joined_ways.data
            res = sa.select([sa.func.coalesce(ws.c.id, w.c.id).label('id'),
                             sa.case([(ws.c.id == None, 'way')], else_='wayset').label('type'),
                             w.c.name, w.c.intnames, w.c.symbol,
                             w.c.piste.label('level')], distinct=True)\
                  .select_from(w.outerjoin(ws, w.c.id == ws.c.child))\
                  .where(w.c.geom.ST_Intersects(b.as_sql()))\
                  .order_by(w.c.name)\
                  .limit(limit)

            for r in cherrypy.request.db.execute(res):
                objs.append(r)

        objs.sort(key=lambda x: x['level'])

        return self.create_list_output('bbox', b.coords, objs)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.gzip(mime_types=['application/json'])
    def search(self, query=None, limit=None, page=None):
        cfg = cherrypy.request.app.config
        limit = self.num_param(limit, 10, 100)
        page = self.num_param(page, 1, 10)

        maxresults = page * limit

        r = cfg['DB']['map'].tables.routes.data
        rbase = sa.select([r.c.id, r.c.name, r.c.intnames, r.c.symbol,
                          r.c.piste.label('level')])
        w = cfg['DB']['map'].tables.ways.data
        ws = cfg['DB']['map'].tables.joined_ways.data
        wbase = sa.select([sa.func.coalesce(ws.c.id, w.c.id).label('id'),
                             sa.case([(ws.c.id == None, 'way')], else_='wayset').label('type'),
                             w.c.name, w.c.intnames, w.c.symbol,
                             w.c.piste.label('level')], distinct=True)\
                  .select_from(w.outerjoin(ws, w.c.id == ws.c.child))

        todos = ((r, rbase), (w, wbase))

        objs = []

        # First try: exact match of ref
        for t, base in todos:
            if len(objs) <= maxresults:
                refmatch = base.where(t.c.name == '[%s]' % query).limit(maxresults - len(objs) + 1)
                for r in cherrypy.request.db.execute(refmatch):
                    objs.append(r)

        # If that did not work and the search term is a number, maybe a relation
        # number?
        if not objs and len(query) > 3 and query.isdigit():
            for t, base in todos:
                idmatch = base.where(t.c.id == int(query))
                for r in cherrypy.request.db.execute(idmatch):
                    objs.append(r)

            if objs:
                return self.create_list_output('query', query, objs)

        # Second try: fuzzy matching of text
        for t, base in todos:
            if len(objs) <= maxresults:
                sim = sa.func.similarity(t.c.name, query)
                res = base.column(sim.label('sim'))\
                        .where(t.c.name.notlike('(%'))\
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
    @cherrypy.tools.gzip(mime_types=['text/json'])
    def segments(self, relations=None, ways=None, waysets=None, bbox=None, **params):
        b = api.common.Bbox(bbox)
        tables = cherrypy.request.app.config['DB']['map'].tables
        objs = []

        if relations is not None:
            ids = [ int(x) for x in relations.split(',') if x.isdigit() ]
            r = tables.routes.data
            sel = sa.select([sa.literal("r"), r.c.id,
                             r.c.geom.ST_Intersection(b.as_sql()).ST_AsGeoJSON()])\
                   .where(r.c.id.in_(ids))
            for x in cherrypy.request.db.execute(sel):
                objs.append(x)

        if ways is not None:
            ids = [ int(x) for x in ways.split(',') if x.isdigit() ]
            w = tables.ways.data
            sel = sa.select([sa.literal("w"), w.c.id,
                             w.c.geom.ST_Intersection(b.as_sql()).ST_AsGeoJSON()])\
                    .where(w.c.id.in_(ids))
            for x in cherrypy.request.db.execute(sel):
                objs.append(x)

        if waysets is not None:
            ids = [ int(x) for x in waysets.split(',') if x.isdigit() ]
            ws = tables.joined_ways.data
            sel = sa.select([sa.literal("w"),
                             ws.c.id.label('id'),
                             sa.func.ST_AsGeoJSON(sa.func.ST_CollectionHomogenize(
                                 sa.func.ST_Collect(w.c.geom.ST_Intersection(b.as_sql()))))
                            ])\
                    .select_from(w.join(ws, w.c.id == ws.c.child))\
                    .where(ws.c.id.in_(ids)).group_by(ws.c.id)
            for x in cherrypy.request.db.execute(sel):
                objs.append(x)

        return self.create_segments_out(objs)


