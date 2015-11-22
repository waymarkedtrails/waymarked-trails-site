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

class RouteDict(OrderedDict):

    def __init__(self, db_entry):
        super().__init__(self)
        self['id'] = db_entry['id']

        for l in cherrypy.request.locales:
            if l in db_entry['intnames']:
                self['name'] = db_entry['intnames'][l]
                if self['name'] != db_entry['name']:
                    self['local_name'] = db_entry['name']
                break
            else:
                self['name'] = db_entry['name']
        self['importance'] = db_entry['level']
        if 'symbol' in db_entry:
            self['symbol'] = str(db_entry['symbol']) + '.png'

    def add_if(self, key, value):
        if value:
            self[key] = value
