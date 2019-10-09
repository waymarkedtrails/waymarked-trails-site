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

from types import MethodType

from db.configs import *
from db.styles.route_network_style import RouteNetworkStyle
from os.path import join as os_join
from config.defaults import MEDIA_ROOT

cai_level = { 'T' : '1', 'E' : '2', 'EE' : '3' }

def filter_route_tags(outtags, tags):
    """ Additional tag filtering specifically for hiking routes.
    """
    network = tags.get('network', '')
    if network == 'uk_ldp':
        if tags.get('operator', '') == 'National Trails':
            outtags.level = Network.NAT()
        else:
            outtags.level = Network.REG()

    # Czech system
    for (k,v) in tags.items():
        if k.startswith('kct_'):
            outtags.network = 'CT'
            if network == '' and v == 'major':
                outtags.level = Network.NAT(-1) if k[4:] == 'red' else Network.REG(-1)

    # Region-specific tagging:

    # in the UK slightly downgrade nwns (to distinguish them from National Trails)
    if outtags.country == 'gb' and network == 'nwn':
        outtags.level = Network.NAT(-1)

    # find Swiss hiking network
    if outtags.country == 'ch' and network == 'lwn':
        ot = tags.get('osmc:symbol', '')
        if ot.startswith('yellow:'):
            outtags.network = 'AL1'
        if ot.startswith('red:'):
            outtags.network = 'AL2'
        if ot.startswith('blue:'):
            outtags.network = 'AL4'

    # Italian hiking network (see #266), also uses Swiss system
    if outtags.country == 'it' and network == 'lwn' \
        and tags.get('osmc:symbol', '').startswith('red') and 'cai_scale' in tags:
        outtags.network = 'AL' + cai_level.get(tags['cai_scale'], '4')

    # Fränkischer Albverein (around Nürnberg)
    #  too extensive regional network, so downgrade for later display
    if tags.get('operator', '') == u'Fränkischer Albverein':
        outtags.level -= 2

def hiking_add_to_collector(self, c, relinfo):
    if relinfo['top']:
        c['toprels'].append(relinfo['id'])
        if relinfo['network'] is None:
            c['class'] |= 1 << relinfo['level']
            self.add_shield_to_collector(c, relinfo)
        else:
            c['style'] = relinfo['network']
            if relinfo['network'].startswith('AL'):
                if relinfo['country'] != 'ch':
                    self.add_shield_to_collector(c, relinfo)
            elif relinfo['network'] == 'NDS':
                pass # no shields, no coloring
            else:
                c['class'] |= 1 << relinfo['level']
                self.add_shield_to_collector(c, relinfo)
    else:
        c['cldrels'].append(relinfo['id'])

MAPTYPE = 'routes'

ROUTEDB = RouteDBConfig()
ROUTEDB.schema = 'hiking'
ROUTEDB.relation_subset = """
    tags ? 'route' and tags->>'type' IN ('route', 'superroute')
    AND array['hiking', 'foot', 'walking'] && regexp_split_to_array(tags->>'route', ';')
    AND NOT (tags ? 'state' AND tags->>'state' = 'proposed')"""

ROUTES = RouteTableConfig()
ROUTES.network_map = {
        'iwn': Network.INT(),
        'nwn': Network.NAT(),
        'rwn': Network.REG(),
        'lwn': Network.LOC()
        }
ROUTES.tag_filter = filter_route_tags
ROUTES.symbols = ( 'ShieldImage',
                   'SwissMobile',
                   'JelRef',
                   'KCTRef',
                   'ItalianHikingRefs',
                   'OSMCSymbol',
                   'TextColorBelow',
                   'TextSymbol')

DEFSTYLE = RouteNetworkStyle()
DEFSTYLE.add_to_collector = MethodType(hiking_add_to_collector, DEFSTYLE)

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
    # permission from Stadtmarketing Eupen
    'eupen' : { 'operator' : 'Stadt Eupen - Stadtmarketing',
                'name' : 'Eupen rundum'},
}
