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

class PisteNetworkStyle(object):
    table_name = 'piste_style'

    def __init__(self, difficulties, types):
        self.difficulty_map = difficulties
        self.piste_type = types

    def add_columns(self, table):
        table.append_column(sa.Column('symbol', ARRAY(sa.String)))

        for c in self.difficulty_map:
            table.append_column(sa.Column(c, sa.Boolean))
        for c in self.piste_type:
            table.append_column(sa.Column(c, sa.Boolean))

    def new_collector(self):
        coll = {'symbol' : []}
        for c in self.difficulty_map:
            coll[c] = False
        for c in self.piste_type:
            coll[c] = False

        return coll

    def add_to_collector(self, c, relinfo):
        if not relinfo['top']:
            return

        for k, v in self.difficulty_map.items():
            if relinfo['difficulty'] == v:
                c[k] = True
        for k, v in self.piste_type.items():
            if relinfo['piste'] == v:
                c[k] = True

        if relinfo['symbol'] is not None and len(c['symbol']) < 5:
                c['symbol'].append(relinfo['symbol'])

    def to_columns(self, c):
        return c
