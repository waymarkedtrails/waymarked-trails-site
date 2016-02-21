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
""" Customized tables for route DB: relation information and style.
"""

from sqlalchemy import Table, Column, String, SmallInteger, Integer, Boolean, \
                       select, func, Index, text, BigInteger
from sqlalchemy.dialects.postgresql import HSTORE, ARRAY, array
from geoalchemy2 import Geometry

from osgende.relations import Routes

from db.configs import RouteTableConfig, RouteStyleTableConfig
from db import conf
from db.common.symbols import ShieldFactory
from db.tables.styles import SegmentStyle

ROUTE_CONF = conf.get('ROUTES', RouteTableConfig)

class RouteInfo(Routes):

    def __init__(self, segments, hierarchy, countries):
        super().__init__(ROUTE_CONF.table_name, segments, hiertable=hierarchy)
        self.country_table = countries
        self.symbols = ShieldFactory(*ROUTE_CONF.symbols)

    def columns(self):
        return (Column('name', String),
                Column('intnames', HSTORE),
                Column('symbol', String),
                Column('country', String(length=3)),
                Column('network', String(length=2)),
                Column('level', SmallInteger),
                Column('top', Boolean),
                Column('geom', Geometry('GEOMETRY',
                                        srid=self.segment_table.data.c.geom.type.srid)),
                Index('idx_%s_iname' % ROUTE_CONF.table_name, text('upper(name)'))
               )

    def transform_tags(self, osmid, tags):
        #print "Processing", osmid
        outtags = { 'intnames' : {},
                    'level' : 35,
                    'network' : '',
                    'top' : None,
                    'geom' : None}

        # determine name and level
        for (k,v) in tags.items():
            if k == 'name':
                outtags[k] = v
            elif k.startswith('name:'):
                outtags['intnames'][k[5:]] = v
            elif k == 'ref':
                if 'name' not in outtags:
                    outtags['name'] = '[%s]' % v
            elif k == 'network':
                outtags['level'] = ROUTE_CONF.network_map.get(v, 35)

        if 'name'not in outtags:
            outtags['name'] = '(%s)' % osmid

        # find all relation parts
        h = self.hierarchy_table.data
        parts = select([h.c.child]).where(h.c.parent == osmid)

        # get the geometry
        s = self.segment_table.data
        sel = select([func.st_linemerge(func.st_collect(s.c.geom))])\
                .where(s.c.rels.op('&& ARRAY')(parts))
        outtags['geom'] = self.thread.conn.scalar(sel)

        # find the country
        c = self.country_table
        sel = select([c.column_cc()], distinct=True)\
                .where(c.column_geom().ST_Intersects(outtags['geom']))
        cur = self.thread.conn.execute(sel)

        if cur.rowcount == 1:
            cntry = cur.scalar()
        elif cur.rowcount > 1:
            # XXX should be counting here
            cntry = cur.scalar()
        else:
            cntry = None

        outtags['country'] = cntry
        outtags['symbol'] = self.symbols.create_write(tags, cntry, outtags['level'])

        # custom filter callback
        if ROUTE_CONF.tag_filter is not None:
            ROUTE_CONF.tag_filter(outtags, tags)

        if outtags['top'] is None:
            if 'network' in tags:
                h = self.hierarchy_table.data
                r = self.src.data
                sel = select([text("'a'")]).where(h.c.child == osmid)\
                                         .where(r.c.id == h.c.parent)\
                                         .where(h.c.depth == 2)\
                                         .where(r.c.tags['network'] == tags['network'])\
                                         .limit(1)

                top = self.thread.conn.scalar(sel)

                outtags['top'] = (top is None)
            else:
                outtags['top'] = True

        return outtags


STYLE_CONF = conf.get('DEFSTYLE', RouteStyleTableConfig)

class RouteSegmentStyle(SegmentStyle):

    def __init__(self, meta, osmdata, routes, segments, hierarchy):
        super().__init__(meta, STYLE_CONF.table_name, osmdata,
                         routes, segments, hierarchy)


    def columns(self):
        return (Column('class', Integer),
                Column('network', String(length=2)),
                Column('style', Integer),
                Column('inrshields', ARRAY(String)),
                Column('allshields', ARRAY(String)),
               )

    def segment_info(self):
        seginfo = RouteSegmentInfo()
        seginfo.compute_info = STYLE_CONF.segment_info
        return seginfo

class RouteSegmentInfo:

    def __init__(self):
        self.network = None
        self.style = 0
        self.classification = 0
        self.inrshields = set()
        self.allshields = set()

    def append(self, relinfo):
        if relinfo['top']:
            self.compute_info(self, relinfo)

    def add_shield(self, shield, isinr):
        if isinr and len(self.inrshields) < 5:
            self.inrshields.add(shield)
        if len(self.allshields) < 5:
            self.allshields.add(shield)

    def to_dict(self, id=None):
        return { 'id' : id,
                 'network' : self.network,
                 'style' : self.style,
                 'class' : self.classification,
                 'inrshields' : list(self.inrshields),
                 'allshields' : list(self.allshields)
               }
