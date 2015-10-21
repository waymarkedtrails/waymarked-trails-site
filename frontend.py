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
import cherrypy
from jinja2 import Template

import config.defaults

class Trails(object):

    def __init__(self, config):
        self.config = config
        self.main_page = Template('Hello {{ name }}!')

    @cherrypy.expose
    def index(self):
        return self.main_page.render(name='foo')


class site_config: pass

for var in dir(sys.modules['config.defaults']):
    if var.isupper():
        setattr(site_config, var, getattr(sys.modules['config.defaults'], var))

def setup_site(confname, script_name=''):
    cherrypy.tree.mount(Trails(site_config), script_name + '/',
                        os_join(site_config.SITECONF_DIR, confname + '.conf'))

    # now disable trailing slash
    cherrypy.config.update({'tools.trailing_slash.on': False })

def application(environ, start_response):
    """ Handler for WSGI appications."""
    setup_site(environ['WMT_CONFIG'], script_name=environ['SCRIPT_NAME'])
    globals()['application'] = cherrypy.tree
    return cherrypy.tree(environ, start_response)

if __name__ == '__main__':
    setup_site(os_environ['WMT_CONFIG'])
    cherrypy.engine.start()
    cherrypy.engine.block()
