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
""" Configuration for the Hiking map.
"""

from db.configs import *
from os.path import join as os_join
from config.defaults import MEDIA_ROOT

def filter_route_tags(outtags, tags):
    """ Additional tag filtering specifically for hiking routes.
    """
    network = tags.get('network', '')
    if network == 'uk_ldp':
        outtags['level'] = 10 if tags.get('operator', '') == 'National Trails' else 20

    # Czech system
    for (k,v) in tags.items():
        if k.startswith('kct_'):
            outtags['network'] = 'CT'
            if network == '' and tags[k] == 'major':
                outtags['level'] = 11 if k[4:] == 'red' else 21

    # Region-specific tagging:

    # in the UK slightly downgrade nwns (to distinguish them from National Trails)
    if outtags['country'] == 'gb' and network == 'nwn':
        outtags['level'] = 11

    # find Swiss hiking network
    if outtags['country'] == 'ch' and network == 'lwn':
        ot = tags.get('osmc:symbol', '')
        if ot.startswith('yellow:'):
            outtags['network'] = 'CH'
            outtags['level'] = 31
        if ot.startswith('red:'):
            outtags['network'] = 'CH'
            outtags['level'] = 32
        if ot.startswith('blue:'):
            outtags['network'] = 'CH'
            outtags['level'] = 33

    # Fränkischer Albverein (around Nürnberg)
    #  too extensive regional network, so we need to downgrade later
    if tags.get('operator', '') == u'Fränkischer Albverein':
        outtags['network'] = 'FA'

def compute_hiking_segment_info(self, relinfo):
    if relinfo['network'] == 'CH':
        self.network = 'CH'
        self.style = relinfo['level']
    else:
        if relinfo['network'] == 'FA' and relinfo['level'] == 20:
            # Fraenkischer Alpverein, downgrade rwns
            cl = 0x3000
        else:
            level = min(relinfo['level'] / 10, 3)
            classvalues = [ 0x40000000, 0x400000, 0x4000, 0x40]
            cl = classvalues[int(level)]
        self.classification |= cl

        if relinfo['symbol'] is not None:
            self.add_shield(relinfo['symbol'], cl >= 0x4000)


MAPTYPE = 'routes'

ROUTEDB = RouteDBConfig()
ROUTEDB.schema = 'hiking'
ROUTEDB.relation_subset = """
    tags ? 'route' and tags->'type' IN ('route', 'superroute')
    AND array['hiking', 'foot', 'walking'] && regexp_split_to_array(tags->'route', ';')
    AND NOT (tags ? 'state' AND tags->'state' = 'proposed')"""

ROUTES = RouteTableConfig()
ROUTES.network_map = { 'iwn': 0,'nwn': 10, 'rwn': 20, 'lwn': 30 }
ROUTES.tag_filter = filter_route_tags
ROUTES.symbols = ( 'ShieldImage',
                   'SwissMobile',
                   'JelRef',
                   'KCTRef',
                   'ItalianHikingRefs',
                   'OSMCSymbol',
                   'TextColorBelow',
                   'TextSymbol')

DEFSTYLE = RouteStyleTableConfig()
DEFSTYLE.segment_info = compute_hiking_segment_info

GUIDEPOSTS = GuidePostConfig()
GUIDEPOSTS.subtype = 'hiking'

NETWORKNODES = NetworkNodeConfig()
NETWORKNODES.node_tag = 'rwn_ref'

SYMBOLS = ShieldConfiguration()
SYMBOLS.symbol_outdir = os_join(MEDIA_ROOT, 'symbols/hiking')
SYMBOLS.shield_names = {
    # with friendly permission of Vogelsberg Touristik
    'vr_vb' :        {'operator':'Vogelsberger Höhenclub',
                      'name':'Vulkanring Vogelsberg'},
    # permission via Kulturverein Storndorf
    'judenpfad_vb' : { 'name' : 'Judenpfad Vogelsberg' },
    # permisson from Verkehrsverein Much
    'igel_much19' :  {'operator' : 'Verkehrsverein Much e.V.',
                      'name':'Familienwanderweg Much'},
}
