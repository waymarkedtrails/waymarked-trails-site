# -*- coding: utf-8 -*-
# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
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

# common settings for all route maps
from routemap.common.settings import *
from routemap.common.settings import _BASEDIR

_ = lambda s : s

SECRET_KEY = ''
ROOT_URLCONF = 'routemap.hiking.urls'

# Project settings
ROUTEMAP_PAGEINFO = {
    # Translators: This is the category of routes for the active map view, will be preceded by site name, such as "Waymarked Trails: ".
    "maptopic" : _("Hiking"),
    "mapdescription" : _("OSM based map with international, national, regional and local walking routes highlighted."),
    "cssfile" : "hiking_theme.css",
    "bgimage" : "banner.jpg",
    "iconimg" : "map_hiking.ico"
}

ROUTEMAP_MAX_ROUTES_IN_LIST = 30
ROUTEMAP_SOURCE_SYMBOL_PATH = _BASEDIR + '../static/img/symbols'
ROUTEMAP_COMPILED_SYMBOL_PATH = 'hikingsyms'
ROUTEMAP_UPDATE_TIMESTAMP = _BASEDIR + '/../last_update'

ROUTEMAP_TILE_URL = ROUTEMAP_TILE_BASEURL + '/hiking'

ROUTEMAP_HELPPAGES = {
   'source' : _BASEDIR + 'locale/%s/helppages.yaml',
   "structure" : (("about", "hiking", "osm"),
                  ("rendering", "hikingroutes", "classification", "hikinglabels",
                   "hierarchy", "guideposts",
                     (("hierarchies", "text"),
                     ("osmc", "text"),
                     ("hikinglocal", "text", 
                        "czech", "germany", "hungary", "slovakia", "swiss", "uk"),
                  )),
                  ("technical", "general", "translation"),
                  ("legal", "copyright", "usage", "disclaimer"),
                  ("acknowledgements", "text"),
                  ("contact", "text")
                 )
}                  
