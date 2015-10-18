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
""" Customized tables for piste routes and ways.
"""

from sqlalchemy import Column, String, SmallInteger, Integer, Boolean, \
                       ForeignKey, select, func, Index, text, BigInteger
from sqlalchemy.dialects.postgresql import HSTORE, ARRAY, array
from geoalchemy2 import Geometry

from osgende.relations import Routes
from osgende.ways import Ways

from db import conf
from db.common.symbols import ShieldFactory
from db.tables.styles import SegmentStyle
from db.configs import PisteTableConfig

CONF = conf.get('PISTE', PisteTableConfig)

def _create_piste_columns(name):
    cols = [Column('name', String),
            Column('intnames', HSTORE),
            Column('symbol', String),
           ]

    for c in CONF.difficulty_map:
        cols.append(Column(c, Boolean))
    for c in CONF.piste_type:
        cols.append(Column(c, Boolean))

    cols.append(Index('idx_%s_iname' % name, text('upper(name)')))
    return cols

def _basic_tag_transform(osmid, tags):
    outtags = { 'intnames' : {} }
    for c in CONF.difficulty_map:
        outtags[c] = False
    for c in CONF.piste_type:
        outtags[c] = False

    # determine name
    if 'piste:name' in tags:
        outtags['name'] = tags['piste:name']
    elif 'piste:ref' in tags:
        outtags['name'] = '[%s]' % tags['piste:ref']
    elif 'name' in tags:
        outtags['name'] = tags['name']
    elif 'ref' in tags:
        outtags['name'] = '[%s]' % tags['ref']
    else:
        # the default used to be to use the osmid.
        # We now expect the renderer to deal with that.
        outtags['name'] = None

    # also find name translations
    for (k,v) in tags.items():
        if k.startswith('name:'):
            outtags['intnames'][k[5:]] = v

    # determine kind of sports activity
    difficulty = 0
    if 'piste:difficulty' in tags:
        v = tags['piste:difficulty']
        if v in CONF.difficulty_map.keys():
            outtags[v] = True
            difficulty = CONF.difficulty_map[v]

    if 'piste:type' in tags:
        v = tags['piste:type']
        if v in CONF.piste_type:
            outtags[v] = True

    return outtags, difficulty


class PisteRouteInfo(Routes):

    def __init__(self, segments, hierarchy, countries):
        super().__init__(CONF.route_table_name, segments, hiertable=hierarchy)
        self.symbols = ShieldFactory(*CONF.symbols)

    def columns(self):
        cols = _create_piste_columns(CONF.route_table_name)
        cols.append(Column('top', Boolean))
        cols.append(Column('geom', Geometry('GEOMETRY',
                              srid=self.segment_table.data.c.geom.type.srid)))

        return cols


    def transform_tags(self, osmid, tags):
        outtags, difficulty = _basic_tag_transform(osmid, tags)

        # we don't support hierarchy at the moment
        outtags['top']  = True

        # find all relation parts
        h = self.hierarchy_table.data
        parts = select([h.c.child]).where(h.c.parent == osmid)

        # get the geometry
        s = self.segment_table.data
        sel = select([func.st_linemerge(func.st_collect(s.c.geom))])\
                .where(s.c.rels.op('&& ARRAY')(parts))
        outtags['geom'] = self.thread.conn.scalar(sel)

        outtags['symbol'] = self.symbols.create_write(tags, '', difficulty)

        return outtags


class PisteWayInfo(Ways):

    def __init__(self, meta, osmdata, subset=None, geom_change=None):
        super().__init__(meta, CONF.way_table_name, osmdata,
                         subset=subset, geom_change=geom_change)
        self.symbols = ShieldFactory(*CONF.symbols)

    def columns(self):
        return _create_piste_columns(CONF.way_table_name)

    def transform_tags(self, osmid, tags):
        outtags, difficulty = _basic_tag_transform(osmid, tags)

        outtags['symbol'] = self.symbols.create_write(tags, '', difficulty)

        return outtags


class PisteSegmentStyle(SegmentStyle):

    def __init__(self, meta, osmdata, routes, segments, hierarchy):
        super().__init__(meta, CONF.style_table_name, osmdata,
                         routes, segments, hierarchy)


    def columns(self):
        cols = [ Column('symbol', ARRAY(String)) ]

        for c in CONF.difficulty_map:
            cols.append(Column(c, Boolean))
        for c in CONF.piste_type:
            cols.append(Column(c, Boolean))

        return cols

    def segment_info(self):
        return PisteSegmentInfo()

class PisteSegmentInfo:

    def __init__(self):
        self.info = {}
        self.symbol = []

        for c in CONF.difficulty_map:
            self.info[c] = False
        for c in CONF.piste_type:
            self.info[c] = False

    def append(self, relinfo):
        if not relinfo['top']:
            return

        for k in self.info:
            if relinfo[k]:
                self.info[k] = True

        if relinfo['symbol'] is not None and len(self.symbol) < 5:
                self.symbol.append(relinfo['symbol'])

    def to_dict(self, id=None):
        fields = dict(self.info)
        fields['symbol'] = self.symbol
        fields['id'] = id

        return fields
