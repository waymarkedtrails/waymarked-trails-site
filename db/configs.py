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
""" Default configurations.
"""

from db.common.route_types import Network

class RouteDBConfig(object):
    schema = None
    srid = 3857

    country_table = 'country_osm_grid'
    change_table = 'changed_objects'
    route_filter_table = "filtered_relations"
    way_relation_table = "way_relations"
    segment_table = 'segments'
    hierarchy_table = 'hierarchy'
    route_table = 'routes'
    style_table = 'defstyle'

    relation_subset = None

class SlopeDBConfig(RouteDBConfig):
    joinedway_table = 'joined_slopeways'
    way_subset = None

class RouteTableConfig(object):
    table_name = 'routes'

    network_map = {}
    tag_filter = None
    symbols = None

class PisteTableConfig(object):
    route_table_name = 'routes'
    way_table_name = 'slopeways'
    style_table_name = 'defstyle'

    symbols = None

    difficulty_map = {'novice'       : 1,
                      'easy'         : 2,
                      'intermediate' : 3,
                      'advanced'     : 4,
                      'expert'       : 5,
                      'extreme'      : 6,
                      'freeride'     : 10,
                      # unknown value: 0
                     }

    piste_type = {'downhill'      : 1,
                  'nordic'        : 2,
                  'skitour'       : 3,
                  'sled'          : 4,
                  'hike'          : 5,
                  'sleigh'        : 6,
                  # unknown value : 0
                 }

class GuidePostConfig:
    table_name = 'guideposts'
    node_subset = 'tags @> \'{ "tourism" : "information", "information": "guidepost"}\'::jsonb'
    subtype = None
    require_subtype = False


class NetworkNodeConfig:
    table_name = 'networknodes'
    node_tag = 'ref'


class ShieldConfiguration(object):
    symbol_outdir = None
    symbol_dir = 'maps/symbols'

    image_size = (15, 15)
    wide_image_size = (22, 15)
    image_border_width = 2.5

    text_border_width = 2.5
    text_bgcolor = (1, 1, 1) # white
    text_color = (0, 0, 0) # black
    text_font = "DejaVu-Sans Condensed Bold 7.5"

    level_colors = { Network.INT : (0.7, 0.01, 0.01),
                     Network.NAT : (0.08, 0.18, 0.92),
                     Network.REG : (0.99, 0.64, 0.02),
                     Network.LOC : (0.55, 0.0, 0.86)
                   }

    swiss_mobile_font ='DejaVu-Sans Oblique Bold 10'
    swiss_mobile_bgcolor = (0.48, 0.66, 0.0)
    swiss_mobile_color = (1, 1, 1)
    swiss_mobile_networks = ('rwn', 'nwn', 'lwn')
    swiss_mobile_operators = ('swiss mobility',
                              'wanderland schweiz', 
                              'schweiz mobil',
                              'skatingland schweiz',
                              'veloland schweiz',
                              'schweizmobil',
                              'stiftung schweizmobil'
                             )

    jel_path = "jel"
    jel_types = ("3","4","atl","atlv","bfk","bor","b","but","c","eml","f3","f4",
                 "fatl","fatlv","fbor","fb","fc","feml","ffut","fii","fivv",
                 "fkor","flo","fl","fm","fmtb","fnw","fpec","f","f+","fq","ftfl",
                 "ftmp","ft","fut","fx","ii","ivv","k3","k4","karsztb","katl",
                 "katlv","kbor","kb","kc","keml","kfut","kii","kivv","kkor",
                 "klo","kl","km","kmtb","knw","kor","kpec","k","k+","kq","ktfl",
                 "ktmp","kt","kx","l3","l4","latl","latlv","lbor","lb","lc",
                 "leml","lfut","lii","livv","lkor","llo","ll","lm","lmtb","lnw",
                 "lo","lpec","l","l+","lq","ls","ltfl","ltmp","lt","lx","mberc",
                 "m","mtb","nw","p3","p4","palma","palp","patl","patlv","pbor",
                 "pb","pc","pec","peml","pfut","pii","pivv","pkor","plo","pl",
                 "pmet","pm","pmtb","+","pnw","ppec","p","p+","pq","ptfl","ptmp",
                 "pt","px","q","rc","s3","s4","salp","satl","satlv","sbarack",
                 "sbor","sb","sc","seml","sfut","sgy","sii","sivv","skor","slo",
                 "sl","sm","smtb","smz","snw","spec","s","s+","sq","ste","stfl",
                 "stj","stm","stmp","st","sx","sz","tfl","tmp","tny","t","x",
                 "z3","z4","zatl","zatlv","zbic","zbor","zb","zc","zeml","zfut",
                 "zii","zivv","zkor","zlo","zl","zm","zmtb","znw","zpec","z",
                 "z+","zq","ztfl","ztmp","zt","zut","zx","zszolo")

    cai_border_width = 5
    kct_path = 'kct'
    kct_colors = {'red' : (1, 0, 0),
                  'blue' : (0.04, 0.34, 0.64),
                  'green' : (0, 0.51, 0.31),
                  'yellow' : (1.0, 0.81, 0)}
    kct_types = ('major', 'local', 'interesting_object', 'learning',
                 'peak', 'ruin', 'spring', 'horse')

    osmc_path = 'osmc'
    osmc_colors = { 'black' : (0, 0, 0),
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

    shield_path = 'shields'
    shield_names = {}

    slope_colors = ((0, 0, 0),
                    (0.0, 0.439, 0.16),
                    (0.082, 0.18, 0.925),
                    (0.698, 0.012, 0.012),
                    (0, 0, 0),
                    (0, 0, 0),
                    (0, 0, 0),
                    (1.0, 0.639, 0.016))

    # used in backgrounds
    color_names = {
               'black'   : (0., 0., 0.),
               'gray'    : (.5, .5, .5),
               'grey'    : (.5, .5, .5),
               'maroon'  : (.5, 0., 0.),
               'olive'   : (.5, .5, 0.),
               'green'   : (0., .5, 0.),
               'teal'    : (0., .5, .5),
               'navy'    : (0., 0., .5),
               'purple'  : (.5, 0., .5),
               'white'   : (1., 1., 1.),
               'silver'  : (.75, .75, .75),
               'red'     : (1., 0., 0.),
               'yellow'  : (1., 1., 0.),
               'lime'    : (0., 1., 0.),
               'aqua'    : (0., 1., 1.),
               'blue'    : (0., 0., 1.),
               'fuchsia' : (1., 0., 1.) }

    # used for underlining text
    colorbox_names = {
               'aqua'    : [(0., 1., 1.), (.5, .5, .5)],
               'black'   : [(0., 0., 0.), (1., 1., 1.)],
               'blue'    : [(0., 0., 1.), (1., 1., 1.)],
               'brown'   : [(0.76, 0.63, 0.08), (.3, .3, .3)],
               'green'   : [(0., 1., 0.), (.5, .5, .5)],
               'gray'    : [(.5, .5, .5), (1., 1., 1.)],
               'grey'    : [(.6, .6, .6), (.6, .6, .6)],
               'maroon'  : [(.5, 0., 0.), (1., 1., 1.)],
               'orange'  : [(1., .65, 0.), (1., 1., 1.)],
               'pink'    : [(1., 0., 1.), (1., 1., 1.)],
               'purple'  : [(.5, 0., .5), (1., 1., 1.)],
               'red'     : [(1., 0., 0.), (1., 1., 1.)],
               'violet'  : [(.55, .22, .79), (1., 1., 1.)],
               'white'   : [(1., 1., 1.), (0., 0., 0.)],
               'yellow'  : [(1., 1., 0.), (.51, .48, .23)],
               }

