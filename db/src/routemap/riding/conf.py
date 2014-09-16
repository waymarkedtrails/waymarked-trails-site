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

DB_SCHEMA = 'riding'
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
"""Name of table riding network nodes."""
DB_GUIDEPOST_TABLE = PGTableName('guideposts', DB_SCHEMA)
""" Name of the table containing guidepost information. """


####   Configuration related to OSM tagging.

TAGS_ROUTE_SUBSET = """tags ? 'route' 
                       AND tags->'type' IN ('route', 'superroute') 
                       AND 'horse' = any( regexp_split_to_array(tags->'route', ';'))
                       AND NOT (tags ? 'state' AND tags->'state' = 'proposed')
                       """
""" Subset of relations that contain riding routes. """
TAGS_NETWORK_MAP = {
                     'nhn': 10, 'rhn': 20, 'lhn': 30,
                     'nwn': 10, 'rwn': 20, 'lwn': 30, 'nwn:kct' : 10,
                     'ncn': 10, 'rcn': 20, 'lcn': 30,
                   }
""" Mapping of network tags to levels """
TAGS_NETWORKNODE_SUBTAG = "rhn_ref"
TAGS_GUIDEPOST_SUBSET = "tags @> 'tourism=>information, information=>guidepost'::hstore and tags ? 'horse'"

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
SYMBOLS_OSMCSYMBOLPATH = os.path.join(SYMBOLS_SYMPATH, 'foreground')
SYMBOLS_OSMCBGSYMBOLPATH = os.path.join(SYMBOLS_SYMPATH, 'background')
SYMBOLS_OSMC_COLORS = { 'black' : (0, 0, 0),
                        'blue' : (0.03, 0.20, 1),
                        'brown' : (0.59, 0.32, 0.11),
                        'gray' : (0.5, 0.5, 0.5),
                        'green' : (0.34, 0.68, 0),
                        'orange' : (1, 0.64, 0.02),
                        'purple' : (0.70, 0.06, 0.74),
                        'red' : (0.88, 0.15, 0.05),
                        'white' : (1, 1, 1),
                        'yellow' : (0.91, 0.88, 0.16)
                      }


####   Configuration related to web-server configuration

WEB_BASEDIR = '../../static'
"""Base directory where static web content should be saved."""
WEB_SYMBOLDIR = os.path.join(WEB_BASEDIR, 'ridingsyms')
"""Directory where symbol images should be saved."""

