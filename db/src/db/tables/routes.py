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

from sqlalchemy import Table, Column, String, SmallInteger, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import HSTORE, ARRAY
from geoalchemy2 import Geometry

from osgende.relations import Routes

class RouteTableConfig(object):
    table_name = 'routes'

    network_map = {}
    tag_filter = lambda outtags, tags : None
    symbols = None

ROUTE_CONF = conf.get('ROUTES', RouteTableConfig)

class RouteInfo(Routes):

    def __init__(self, segments, hierarchy, countries):
        super().__init__(ROUTE_CONF.table_name, segments, hiertable=hierarchy)
        self.country_table = countries

    def columns(self):
        return (Column('name', String),
                Column('intnames', HSTORE),
                Column('symbol', String),
                Column('country', String(length=3)),
                Column('network', String(length=2)),
                Column('level', SmallInteger),
                Column('top', Boolean),
                Column('geom', Geometry('GEOMETRY',
                                        srid=self.segment_table.c.geom.type.srid)),
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
        for (k,v) in tags.iteritems():
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

        cur = self.thread.cursor

        # find all relation parts
        h = self.hierarchy_table
        cur = self.thread.conn.execute(select([h.c.child]).where(h.c.parent == osmid))
        parts = [ x for x in cur ]

        # get the geometry
        s = self.segment_table
        sel = select([func.st_linemerge(func.st_collect(s.c.geom))])\
                .where(s.c.rels.op('&&')(parts))
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
        if ROUTE_CONF.symbols is not None:
            outtags['symbol'] = ROUTE_CONF.symbols.create_write(outtags['level'],
                                                                 cntry, tags)

        # custom filter callback
        ROUTE_CONF.tag_filter(outtags, tags)

        if outtags['top'] is None:
            if 'network' in tags:
                h = self.hierarchy_table
                r = self.src.data
                sel = select([text('a')]).where(h.c.child == osmid)\
                                         .where(r.c.id == h.c.parent)\
                                         .where(h.c.depth == 2)\
                                         .where(r.c.tags['network'] == tags['network'])\
                                         .limit(1)

                top = self.thread.conn.scalar(sel)

                outtags['top'] = (top is None)
            else:
                outtags['top'] = True

        return outtags


class StyleTableConfig(object):
    table_name = 'defstyle'

    segment_info = None


STYLE_CONF = conf.get('DEFSTYLE', StyleTableConfig)

class RouteSegmentStyle(object):

    def __init__(self, meta, routes, segments, hierarchy):
        self.t_route = routes
        self.t_segment = segments
        self.t_hier = hierarchy
        self.data = Table(meta, STYLE_CONF.table_name,
                          Column('id', BigInteger,
                                 ForeignKey(segments.c.id, ondelete='CASCADE')),
                          Column('class', Integer),
                          Column('network', String(length=2)),
                          Column('style', Integer),
                          Column('inrshields', ARRAY[String]),
                          Column('allshields', ARRAY[String]),
                          Column('geom', Geometry('GEOMETRY', index=True,
                                         srid=segments.c.geom.type.srid)),
                          Column('geom', Geometry('GEOMETRY', index=True,
                                         srid=segments.c.geom.type.srid)),
                         )

    def truncate(self, conn):
        conn.execute(self.data.delete())

    def construct(self, engine):
        self.truncate(engine)
        self.synchronize(0)

    def update(self, engine):
        self.synchronize(self, t_segment.first_new_id)

    def synchronize(self, firstid):
        # cache routing information, so we don't have to get it every time
        route_cache = {}

        cur = self.db.select("""SELECT seg.id, array_agg(h.parent) as rels
                               FROM %s h, %s seg
                              WHERE h.child = ANY(seg.rels)
                                AND seg.id >= %%s
                              GROUP BY seg.id""" 
                          % (  conf.DB_HIERARCHY_TABLE.fullname,
                               conf.DB_SEGMENT_TABLE.fullname),
                          (firstid,))

class RouteSegmentInfo:

    def __init__(self):
        self.network = None
        self.style = 0
        self.classification = 0
        self.inrshields = set()
        self.allshields = set()

    def append(self, relinfo):
        if relinfo['top']:
            self.compute_info(relinfo)

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
