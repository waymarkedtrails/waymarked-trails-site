# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2018 Sarah Hoffmann
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

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ARRAY

from db.common.route_types import Network

class RouteNetworkStyle(object):
    table_name = 'network_style'

    def add_columns(self, table):
        table.append_column(sa.Column('class', sa.Integer))
        table.append_column(sa.Column('style', sa.String(3)))
        table.append_column(sa.Column('inrshields', ARRAY(sa.String)))
        table.append_column(sa.Column('lshields', ARRAY(sa.String)))
        table.append_column(sa.Column('toprels', ARRAY(sa.BigInteger)))
        table.append_column(sa.Column('cldrels', ARRAY(sa.BigInteger)))

    def new_collector(self):
        return {'style' : None,
                'class' : 0,
                'inrshields' : set(),
                'lshields' : set(),
                'toprels' : [],
                'cldrels' : [] }

    def add_to_collector(self, c, relinfo):
        if relinfo['top']:
            c['toprels'].append(relinfo['id'])

            if relinfo['network'] is None:
                c['class'] |= 1 << relinfo['level']
                self.add_shield_to_collector(c, relinfo)
            else:
                c['style'] = relinfo['network']
                if relinfo['network'] != 'NDS':
                    c['class'] |= 1 << relinfo['level']
                    self.add_shield_to_collector(c, relinfo)
        else:
            c['cldrels'].append(relinfo['id'])

    def to_columns(self, c):
        c['lshields'] = list(c['lshields'])[:5] if c['lshields'] else None
        c['inrshields'] = list(c['inrshields'])[:5] if c['inrshields'] else None

        return c

    def add_shield_to_collector(self, c, relinfo):
        if relinfo['symbol']  is None:
            return

        if relinfo['level'] <= Network.LOC.max():
            c['lshields'].add(relinfo['symbol'])
        else:
            c['inrshields'].add(relinfo['symbol'])
