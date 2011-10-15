# This file is part of Lonvia's cycling Map
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

DB_SCHEMA = 'skating'
""" Name of schema to use. Must include the final dot. """
DB_ROUTE_TABLE = PGTableName('routes', DB_SCHEMA)
""" Name of table containing route information. """
DB_SEGMENT_TABLE = PGTableName('segments', DB_SCHEMA)
""" Name of table containing way segment information. """
DB_HIERARCHY_TABLE = PGTableName("hierarchy", DB_SCHEMA)
"""Name of table containing relation relations. """
DB_DEFAULT_STYLE_TABLE = PGTableName("defstyle", DB_SCHEMA)
"""Name of table containing style information for the default style."""
DB_CHANGE_TABLE = PGTableName("changed_objects", DB_SCHEMA)
"""Name of table holding changed geometries."""
DB_NETWORKNODE_TABLE = PGTableName("networknodes", DB_SCHEMA)
"""Name of table cycle network nodes."""

####   Configuration related to OSM tagging.

TAGS_ROUTE_SUBSET = """tags ? 'route' 
                       AND tags->'type' IN ('route', 'superroute') 
                       AND tags->'route' = 'inline_skates'"""
""" Subset of relations that contain cycling routes. """
TAGS_NETWORK_MAP = { 'national': 10, 'regional': 20, 'local': 30 }
""" Mapping of network tags to levels """

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
SYMBOLS_SWISS_BGCOLOR = '#e750de'
"""Background color for Swiss mobility labels"""
SYMBOLS_SWISS_NETWORK = ('regional', 'national')
"""Valid values for network tag foe Swiss mobility lables"""


####   Configuration related to web-server configuration

WEB_BASEDIR = '../../static'
"""Base directory where static web content should be saved."""
WEB_SYMBOLDIR = os.path.join(WEB_BASEDIR, 'skatingsyms')
"""Directory where symbol images should be saved."""

