# This file is part of the Waymarked Trails Map Project
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
""" Configuration for the winter sports map.
"""

from db.configs import *
from db.styles.piste_network_style import PisteNetworkStyle
from os.path import join as os_join
from config.defaults import MEDIA_ROOT

MAPTYPE = 'slopes'

ROUTEDB = SlopeDBConfig()
ROUTEDB.schema = 'slopes'
ROUTEDB.relation_subset = """
    tags ? 'route' and tags->>'type' IN ('route', 'superroute')
    AND array['ski', 'piste'] && regexp_split_to_array(tags->>'route', ';')
    AND NOT (tags ? 'state' AND tags->>'state' = 'proposed')
    AND NOT (tags->>'piste:type' = 'skitour')"""
ROUTEDB.way_subset = """
    tags ? 'piste:type'
    AND NOT (tags ? 'state' AND tags->>'state' = 'proposed')
    AND NOT (tags->>'piste:type' = 'downhill'
             AND nodes[array_lower(nodes,1)] = nodes[array_upper(nodes,1)])
    AND NOT (tags->>'piste:type' = 'skitour')"""

PISTE = PisteTableConfig()
PISTE.symbols = ('Slopes', 'Nordic')

DEFSTYLE = PisteNetworkStyle(PISTE.difficulty_map, PISTE.piste_type)

SYMBOLS = ShieldConfiguration()
SYMBOLS.symbol_outdir = os_join(MEDIA_ROOT, 'symbols/slopes')
SYMBOLS.image_size = (20, 20)
SYMBOLS.text_color = (1, 1, 1) # white
SYMBOLS.text_bgcolor = (0, 0, 0) # black
