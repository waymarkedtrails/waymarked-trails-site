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
""" Collection of configuration variables.
"""

import os.path
from osgende.common.postgisconn import PGTableName

from siteconfig import DATABASES, PROJECTDIR, MEDIA_ROOT

####    Configuration options related to the database.

DB_SCHEMA = 'cycling'
DB_SRID = DATABASES['default']['SRID']
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
DB_GUIDEPOST_TABLE = PGTableName('guideposts', DB_SCHEMA)
""" Name of the table containing guidepost information. """

####   Configuration related to OSM tagging.

TAGS_ROUTE_SUBSET = """tags ? 'route' 
                       AND tags->'type' IN ('route', 'superroute') 
                       AND tags->'route' = 'bicycle'
                       AND NOT (tags ? 'state' AND tags->'state' = 'proposed')
                    """
""" Subset of relations that contain cycling routes. """
TAGS_NETWORK_MAP = { 'icn': 0,'ncn': 10, 'rcn': 20, 'lcn': 30 }
""" Mapping of network tags to levels """
TAGS_NETWORKNODE_SUBTAG = "rcn_ref"
TAGS_GUIDEPOST_SUBSET = "tags @> 'tourism=>information, information=>guidepost'::hstore"

####   Configuration options related to symbol generation

SYMBOLS_SYMPATH = '../symbols'
SYMBOLS_BGCOLORS = [ '#b20303', '#152eec', '#ffa304', '#8c00db' ]
SYMBOLS_LEVELCOLORS = ((0.7, 0.01, 0.01), 
                       (0.08, 0.18, 0.92), 
                       (0.99, 0.64, 0.02),
                       (0.55, 0.0, 0.86))
"""Background colors to use for the different levels."""
SYMBOLS_IMAGE_BORDERWIDTH = 2.5
SYMBOLS_IMAGE_SIZE = (15,15)
"""Size for labels without loaded images"""
SYMBOLS_TEXT_FONT = "DejaVu-Sans Condensed Bold 7.5"
SYMBOLS_TEXT_COLOR = (0,0,0)
"""Text color for reference labels"""
SYMBOLS_TEXT_BGCOLOR = (1,1,1)
SYMBOLS_TEXT_BORDERWIDTH = 5
"""Background on reference labels"""
SYMBOLS_SWISS_FONT='DejaVu-Sans Oblique Bold 10'
SYMBOLS_SWISS_BGCOLOR = (0.48, 0.66, 0.0)
"""Background color for Swiss mobility labels"""
SYMBOLS_SWISS_NETWORK = ('rwn', 'nwn')
SYMBOLS_SWISS_OPERATORS = ('swiss mobility',
                           'wanderland schweiz', 
                           'schweiz mobil',
                           'skatingland schweiz',
                           'veloland schweiz',
                           'schweizmobil',
                          )
SYMBOLS_COLORBOX_TAGS = {"operator" : "Norwich City Council"}
####   Configuration related to web-server configuration

WEB_BASEDIR = '../../static'
"""Base directory where static web content should be saved."""
WEB_SYMBOLDIR = os.path.join(WEB_BASEDIR, 'cyclingsyms')
"""Directory where symbol images should be saved."""

