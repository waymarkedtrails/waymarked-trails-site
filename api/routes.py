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

import sys
from os.path import join as os_join
from os import environ as os_environ
import cherrypy
from datetime import datetime
import sqlalchemy as sa

import config.defaults

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

@cherrypy.tools.db()
@cherrypy.tools.add_language()
class RoutesApi(object):

    def __init__(self):
        # sub-directories
        self.list = ListRoutes()
        self.relation = RelationInfo()

    @cherrypy.expose
    def index(self):
        return "Hello API"

    @cherrypy.expose
    def last_update(self):
        return datetime.now().isoformat(' ')


@cherrypy.tools.json_out()
class ListRoutes(object):

    @cherrypy.expose
    def by_area(self, bbox, limit=20, **params):
        b = Bbox(bbox)

        if 'lang' in params:
            lang = (params)
        else:
            lang = cherrypy.request.lang_list

        if limit > 100:
            limit = 100

        mapdb = cherrypy.request.app.config['DB']['map']
        conn = cherrypy.request.db

        r = mapdb.tables.routes.data
        s = mapdb.tables.segments.data
        h = mapdb.tables.hierarchy.data
        rels = sa.select([sa.func.unnest(s.c.rels).label('rel')], distinct=True)\
                .where(s.c.geom.intersects(b.as_sql())).alias()
        res = sa.select([r.c.id, r.c.name, r.c.intnames])\
               .where(r.c.top)\
               .where(r.c.id.in_(sa.select([h.c.parent], distinct=True)
                                   .where(h.c.child == rels.c.rel)))\
               .order_by(r.c.level)\
               .limit(limit)

        out = []
        for r in conn.execute(res):
            desc = None
            for l in lang:
                if l in r['intnames']:
                    locname = r['intnames'][l]
                    if locname != r['name']:
                        desc = r['name']
                    break
            else:
                locname = r['name']
            out.append({ 'id' : r['id'],
                         'name' : locname
                       })

        return { 'bbox' : b.coords,
                 'symbol_url' : cherrypy.request.app.config['Global']['MEDIA_URL'],
                 'relations': out }
        #   qs = getattr(table_module, table_class).objects.filter(top=True).extra(where=(("""
        #    id = ANY(SELECT DISTINCT h.parent
        #             FROM hierarchy h,
        #                  (SELECT DISTINCT unnest(rels) as rel
        #                   FROM segments
        #                   WHERE geom && st_transform(ST_SetSRID(
        #                     'BOX3D(%f %f, %f %f)'::Box3d,4326),%%s)) as r
        #             WHERE h.child = r.rel)""" 
        #    % coords) % settings.DATABASES['default']['SRID'],)).order_by('level')


    @cherrypy.expose
    @cherrypy.popargs('zoom', 'x', 'y')
    def tile(self, zoom, x, y):
        return "TODO: get data for tile %s/%s/%s" % (zoom, x, y)

    def search(self, query=None):
        return "TODO: search"

    def segments(self, ids=None, bbox=None):
        return "TODO: jsonbox"

@cherrypy.popargs('oid')
class RelationInfo(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, oid):
        #raise cherrypy.HTTPError(404, "No relation with id %s in database." % oid)
        return { 'id' : oid, 'name' : 'Popcorn' }

    @cherrypy.expose
    def geom(self, oid):
        return "TODO: geometry of relation %s" % oid

    @cherrypy.expose
    def wikilink(self, oid):
        return "TODO: wikilink of relation %s" % oid

    @cherrypy.expose
    def gpx(self, oid):
        return "TODO: GPX of relation %s" % oid

