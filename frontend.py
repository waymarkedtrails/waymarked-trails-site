#!/usr/bin/python3
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
from json import dumps
import cherrypy
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

import config.defaults
import api.tools

cherrypy.tools.db = api.tools.SATool()

from api.routes import RoutesApi
from frontend.compatibility import CompatibilityLinks
from frontend.help import Helppages

_ = lambda x: x

http_error = {
    None : _('Something unexpected happend.'),
    '404' : _("It looks like the page you are looking for doesn't exist. If you think that you have found a broken link, don't hesitate to contact us.")
    }

@cherrypy.tools.I18nTool()
class Trails(object):

    def __init__(self, mapdb, maptype, langs, debug=False):
        self.api = RoutesApi(mapdb, maptype)
        self.help = Helppages()
        compobj = CompatibilityLinks()
        for l in langs:
            setattr(self, l[0], compobj)
        if not debug:
            cherrypy.config.update({'error_page.default': Trails.error_page})

    @cherrypy.expose
    def index(self, **params):
        gconf = cherrypy.request.app.config.get('Global')
        lconf = cherrypy.request.app.config.get('Site')
        _ = cherrypy.request.i18n.gettext
        js_params = { 'MEDIA_URL': gconf['MEDIA_URL'],
                      'API_URL' : gconf['API_URL'],
                      'TILE_URL' : lconf['tile_url'],
                      'HILLSHADING_URL' : gconf['HILLSHADING_URL'],
                      'GROUPS' : dict([(k, _(v)) for k,v in lconf['groups'].items()]),
                      'GROUP_SHIFT' : lconf['group_shift'],
                      'GROUPS_DEFAULT' : lconf['groups_default'],
                      'BASEMAPS' : gconf['BASEMAPS']}
        if hasattr(self.api, 'tiles'):
            js_params['VTILE_URL'] = gconf['API_URL'] + '/tiles/';
        else:
            js_params['VTILE_URL'] = False
        return cherrypy.request.templates.get_template('index.html').render(
                                     g=gconf, l=lconf, jsparam = dumps(js_params))

    @staticmethod
    def error_page(status, message, traceback, version):
        gconf = cherrypy.request.app.config.get('Global')
        lconf = cherrypy.request.app.config.get('Site')
        _ = cherrypy.request.i18n.gettext
        bug = _("Bugs may be reported via the [github project page](https://github.com/lonvia/waymarked-trails-site/issues). Please make sure to describe what you did to produce this error and include the original message below.")
        return cherrypy.request.templates.get_template('error.html').render(
                g=gconf, l=lconf, bugreport=bug,
                message=_(http_error.get(status[0:3], http_error[None])),
                srcmsg= status + ': ' + message)

class _MapDBOption:
    no_engine = True

def setup_site(confname, script_name='', debug=False):
    globalconf = {}
    for var in dir(sys.modules['config.defaults']):
        if var.isupper():
            globalconf[var] = getattr(sys.modules['config.defaults'], var)

    site_cfg = {}
    try:
        __import__('config.sites.' + confname)
        site_cfg = getattr(sys.modules['config.sites.' + confname], 'SITE', {})
    except ImportError:
        print("Missing config for site '%s'. Skipping." % site)
        raise

    os_environ['ROUTEMAPDB_CONF_MODULE'] = 'maps.%s' % confname
    from db import conf as db_config
    mapdb_pkg = 'db.%s' % db_config.get('MAPTYPE')
    mapdb_class = __import__(mapdb_pkg, globals(), locals(), ['DB'], 0).DB

    mapdb = mapdb_class(_MapDBOption())

    app = cherrypy.tree.mount(Trails(mapdb, db_config.get('MAPTYPE'),
                                     globalconf['LANGUAGES'], debug=debug),
                              script_name + '/',
                              {
                                  '/favicon.ico':
                                  {
                                      'tools.staticfile.on': True,
                                      'tools.staticfile.filename':
                                        '%s/img/map/map_%s.ico' %
                                        (globalconf['MEDIA_ROOT'], confname)
                                  }
                              })

    app.config['DB'] = { 'map' : mapdb }
    app.config['Global'] = globalconf
    app.config['Global']['BASENAME'] = confname
    app.config['Global']['MAPTYPE'] = db_config.get('MAPTYPE')
    app.config['Site'] = site_cfg

    # now disable trailing slash
    cherrypy.config.update({'tools.trailing_slash.on': False })


def application(environ, start_response):
    """ Handler for WSGI appications. Assume that it does not run threaded."""
    dba = URL('postgresql', username=config.defaults.DB_USER,
                            database=config.defaults.DB_NAME,
                           password=config.defaults.DB_PASSWORD)
    cherrypy.thread_data.conn = create_engine(dba, echo=False).connect()
    setup_site(environ['WMT_CONFIG'], script_name=environ['SCRIPT_NAME'], debug=False)
    cherrypy.config.update({'log.wsgi' : True, 'log.screen' : False})
    globals()['application'] = cherrypy.tree
    return cherrypy.tree(environ, start_response)

if __name__ == '__main__':
    api.tools.SAEnginePlugin(cherrypy.engine).subscribe()
    setup_site(os_environ['WMT_CONFIG'], debug=True)
    if 'WMT_LISTEN' in os_environ:
        cherrypy.config.update({'server.socket_host' : os_environ['WMT_LISTEN']})
    if 'WMT_PORT' in os_environ:
        cherrypy.config.update({'server.socket_port' : int(os_environ['WMT_PORT'])})
    cherrypy.engine.start()
    cherrypy.engine.block()
