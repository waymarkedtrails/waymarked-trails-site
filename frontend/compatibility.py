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

import cherrypy
import urllib.parse

import config.defaults

class CompatibilityLinks(object):

    def __init__(self):
        self.help = HelpCompatibility()

    def mkurl(self, base, params, fragm = {}):
        if 'zoom' in params and 'lat' in params and 'lon' in params:
            fragm['map'] = '%(zoom)s!%(lat)s!%(lon)s' % params

        if fragm:
            fragm = '?' + urllib.parse.urlencode(fragm, safe="/!")
        else:
            fragm = ''

        return config.defaults.BASE_URL + base + fragm

    @cherrypy.expose
    def index(self, **params):
        raise cherrypy.HTTPRedirect(self.mkurl("/#", params))

    @cherrypy.expose
    @cherrypy.popargs('rid')
    def relation(self, rid, **params):
        raise cherrypy.HTTPRedirect(self.mkurl("/#route", params,
                                               { 'type' : 'relation',
                                                 'id' : rid}))

    @cherrypy.expose
    @cherrypy.popargs('rid')
    def way(self, rid, **params):
        raise cherrypy.HTTPRedirect(self.mkurl("/#route", params,
                                               { 'type' : 'way',
                                                 'id' : rid}))

    @cherrypy.expose
    @cherrypy.popargs('rid')
    def joined_way(self, rid, **params):
        raise cherrypy.HTTPRedirect(self.mkurl("/#route", params,
                                               { 'type' : 'wayset',
                                                 'id' : rid}))

    @cherrypy.expose
    @cherrypy.popargs('rid', 'func')
    def routebrowser(self, rid, func, **params):
        raise cherrypy.HTTPRedirect("%s/api/details/relation/%s/%s"
                                    % (config.defaults.BASE_URL, rid, func))


class HelpCompatibility(object):
    def _cp_dispatch(self, vpath):
        path = []
        while vpath:
            path.append(vpath.pop())
        path.reverse()
        cherrypy.request.params['path'] = path
        return self

    @cherrypy.expose
    def index(self, **params):
        path = '/'.join(cherrypy.request.params.get('path', ('about',)))
        raise cherrypy.HTTPRedirect("%s/help/%s" % (config.defaults.BASE_URL, path))
