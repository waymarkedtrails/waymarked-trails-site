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

@cherrypy.tools.db()
@cherrypy.tools.add_language()
class RoutesApi(object):

    def __init__(self, confname, config):
        self.config = config
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
    def by_area(self, bbox, **params):
        b = Bbox(bbox)

        if 'lang' in params:
            lang = (params)
        else:
            lang = cherrypy.request.lang_list

        mapdb = cherrypy.request.app.config['DB']['map']
        conn = cherrypy.request.db

        r = mapdb.tables.routes.data
        res = sa.select([r.c.id, r.c.name])\
               .where(r.c.id == 29003)

        out = []
        for r in conn.execute(res):
            out.append({ 'id' : r['id'],
                         'name' : r['name']
                       })

        return out
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
    def index(self, oid):
        return "TODO: General info about relation %s" % oid

    @cherrypy.expose
    def geom(self, oid):
        return "TODO: geometry of relation %s" % oid

    @cherrypy.expose
    def wikilink(self, oid):
        return "TODO: wikilink of relation %s" % oid

    @cherrypy.expose
    def gpx(self, oid):
        return "TODO: GPX of relation %s" % oid

