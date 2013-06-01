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
from siteconfig import *


# Django settings for MTB map project.
_ = lambda s : s

# Project settings
ROUTEMAP_PAGEINFO = {
    # Translators: This is the category of routes for the active map view, will be preceded by site name, such as "Waymarked Trails: ". "MTB" means "mountain bike".
    "maptopic" : _("MTB"),
    "mapdescription" : _("Waymarked Trails shows mountain biking (MTB) routes from the local to international level, with maps and information from OpenStreetMap."),
    "cssfile" : "mtb_theme.css",
    "bgimage" : "banner_mtb.jpg",
    "iconimg" : "map_mtb.ico"
}

ROUTEMAP_ROUTE_TABLE = 'routemap.sites.models.MtbRoutes'
ROUTEMAP_SEGMENT_TABLE = 'routemap.sites.models.MtbSegments'
ROUTEMAP_SCHEMA = 'mtbmap'
ROUTEMAP_COMPILED_SYMBOL_PATH = 'mtbsyms'

ROUTEMAP_TILE_URL = ROUTEMAP_TILE_BASEURL + '/mtb'

ROUTEMAP_HELPPAGES = {
   'source' : PROJECTDIR + 'django/locale/%s/helppages.yaml',
   "structure" : (("about", "mtb", "osm"),
                  ("rendering", "mtbroutes", "classification",
                   "labels", "hierarchy",
                     (("hierarchies", "text"),
                      ("elevationprofiles", "general"),
                  )),
                  ("technical", "general", "translation"),
                  ("legal", "copyright", "usage", "disclaimer"),
                  ("acknowledgements", "text"),
                  ("contact", "text")
                 )
}
