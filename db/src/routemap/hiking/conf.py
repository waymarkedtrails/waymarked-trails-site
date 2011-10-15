# This file is part of Lonvia's Hiking Map
# Copyright (C) 2011 Sarah Hoffmann
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
""" Collection of configuration variables.
"""

import os.path
from osgende.common.postgisconn import PGTableName

####    Configuration options related to the database.

DB_SCHEMA = 'hiking'
""" Name of schema to use. Must include the final dot. """
DB_GUIDEPOST_TABLE = PGTableName('guideposts', DB_SCHEMA)
""" Name of the table containing guidepost information. """
DB_NETWORKNODE_TABLE = PGTableName('networknodes', DB_SCHEMA)
""" Name of the table containing network nodes (as used in the Netherlands)"""
DB_ROUTE_TABLE = PGTableName('routes', DB_SCHEMA)
""" Name of table containing route information. """
DB_SEGMENT_TABLE = PGTableName('segments', DB_SCHEMA)
""" Name of table containing way segment information. """
DB_COUNTRY_TABLE = PGTableName('countries', DB_SCHEMA)
""" Name of table containing country polygons. """
DB_HIERARCHY_TABLE = PGTableName("hierarchy", DB_SCHEMA)
"""Name of table containing relation relations. """
DB_DEFAULT_STYLE_TABLE = PGTableName("defstyle", DB_SCHEMA)
"""Name of table containing style information for the default style."""
DB_CHANGE_TABLE = PGTableName("changed_objects", DB_SCHEMA)
"""Name of table holding changed geometries."""


####    Configuration related to OSM tagging.

TAGS_ROUTE_SUBSET = """tags ? 'route' and tags->'type' IN ('route', 'superroute') 
                    AND tags->'route' IN ('hiking', 'foot', 'walking')"""
""" Subset of relations that contain hiking routes. """
TAGS_NETWORK_MAP = { 'iwn': 0,'nwn': 10, 'rwn': 20, 'lwn': 30 }
TAGS_GUIDEPOST_SUBSET = "tags @> 'tourism=>information, information=>guidepost'::hstore"
TAGS_NETWORKNODE_SUBSET = "tags ? 'rwn_ref'"


####   Configuration options related to symbol generation

SYMBOLS_SYMPATH = '../symbols'
SYMBOLS_BGCOLORS = [ '#b20303', '#152eec', '#ffa304', '#8c00db' ]
"""Background colors to use for the different levels."""
SYMBOLS_IMAGE_SIZE = (2,15)
"""Size for labels without loaded images"""
SYMBOLS_TEXT_COLOR = 'black'
"""Text color for reference labels"""
SYMBOLS_TEXT_BGCOLOR = '#FFFFFF'
"""Background on reference labels"""
SYMBOLS_SWISS_BGCOLOR = '#7cad00'
"""Background color for Swiss mobility labels"""
SYMBOLS_SWISS_NETWORK = ('rwn', 'nwn')
"""Valid values for network tag foe Swiss mobility lables"""
SYMBOLS_KCTCOLORS = ('red', 'blue', 'green', 'yellow')
SYMBOLS_KCTTYPES = ('major', 'local', 'interesting_object', 'learning',
                'peak', 'ruin', 'spring')
SYMBOLS_KCTSYMPATH = os.path.join(SYMBOLS_SYMPATH, 'kct')
SYMBOLS_OSMCSYMBOLPATH = os.path.join(SYMBOLS_SYMPATH, 'foreground')
SYMBOLS_OSMCBGSYMBOLPATH = os.path.join(SYMBOLS_SYMPATH, 'background')
SYMBOLS_SM_TEXT_COLORS = ('black', 'blue', 'gray', 'white', 'yellow', 'green', 
                       'orange', 'red')
    

#### Configuration related to web-server configuration

WEB_BASEDIR = '../../static'
"""Base directory where static web content should be saved."""
WEB_SYMBOLDIR = os.path.join(WEB_BASEDIR, 'hikingsyms')
"""Directory where symbol images should be saved."""

