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
import cherrypy
from sqlalchemy import func
from geoalchemy2.elements import WKTElement

class RouteDict(OrderedDict):

    def __init__(self, db_entry):
        super().__init__(self)
        self['type'] = db_entry.get['type'] if db_entry.has_key('type') else 'relation'
        self['id'] = db_entry['id']

        for l in cherrypy.request.locales:
            if l in db_entry['intnames']:
                self['name'] = db_entry['intnames'][l]
                if self['name'] != db_entry['name']:
                    self['local_name'] = db_entry['name']
                break
            else:
                self['name'] = db_entry['name']
        self['group'] = db_entry['level']
        if 'symbol' in db_entry:
            self['symbol_id'] = str(db_entry['symbol'])

    def add_if(self, key, value):
        if value:
            self[key] = value


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
        return func.ST_SetSrid(func.ST_MakeBox2D(
                    WKTElement('POINT(%f %f)' % self.coords[0:2]),
                    WKTElement('POINT(%f %f)' % self.coords[2:4])), 3857)



