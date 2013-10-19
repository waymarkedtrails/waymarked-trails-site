# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
#               2012-2013 Michael Spreng
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
from siteconfig import *


# Django settings for slopemap project.
_ = lambda s : s

# Project settings
ROUTEMAP_PAGEINFO = {
    # Translators: This is the category of routes for the active map view, will be preceded by site name, such as "Waymarked Trails: ".
    "maptopic" : _("Winter sport slopes"),
    "mapdescription" : _("Waymarked Trails shows winter sport slopes, with maps and information from OpenStreetMap."),
    "cssfile" : "slope_theme.css",
    "bgimage" : "banner_slopemap.jpg",
    "iconimg" : "map_slope.ico"
}

ROUTEMAP_ROUTE_TABLE = 'routemap.sites.models.SlopeRelations'
ROUTEMAP_WAY_TABLE = 'routemap.sites.models.Slopes'
ROUTEMAP_JOINED_WAY_TABLE = 'routemap.sites.models.JoinedSlopes'
ROUTEMAP_SCHEMA = 'slopemap'
ROUTEMAP_COMPILED_SYMBOL_PATH = 'slopemapsyms'

ROUTEMAP_TILE_URL = ROUTEMAP_TILE_BASEURL + '/slopemap'

ROUTEMAP_ROUTEINFO_URLS = 'routemap.apps.slopeinfo.urls'

ROUTEMAP_HELPPAGES = {
   'source' : PROJECTDIR + 'django/locale/%s/helppages.yaml',
   "structure" : (("about", "slopemap", "osm"),
                  ("rendering", "sloperoutes", "slopeclassification", "slopemaplabels",
                      ("elevationprofiles", "general"),
                  ),
                  ("technical", "general", "translation"),
                  ("legal", "copyright", "usage", "disclaimer"),
                  ("acknowledgements", "text"),
                  ("contact", "text")
                 )
}
