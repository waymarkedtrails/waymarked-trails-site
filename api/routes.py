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
from datetime import datetime
import sqlalchemy as sa

import config.defaults
import api.details
import api.listings


@cherrypy.tools.db()
class RoutesApi(object):

    def __init__(self, maptype):
        # sub-directories
        if maptype == 'routes':
            self.list = api.listings.RouteLists()
            self.details = RouteDetails()
        elif maptype == 'slopes':
            self.list = api.listings.SlopeLists()
            self.details = SlopeDetails()

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("/help")

    @cherrypy.expose
    def last_update(self):
        return datetime.now().isoformat(' ')


class RouteDetails(object):

    def __init__(self):
        self.relation = api.details.RelationInfo('level')

class SlopeDetails(object):

    def __init__(self):
        self.relation = api.details.RelationInfo('piste')
        self.way = api.details.WayInfo('piste')
        self.wayset = api.details.WaySetInfo('piste')
