# This file is part of Waymarked Trails
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

import logging

from osgende.common.table import TableSource
from osgende.common.sqlalchemy import DropIndexIfExists
from osgende.common.threads import ThreadableDBObject
from osgende.common.tags import TagStore
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

from db.common.symbols import ShieldFactory
from db.common.route_types import Network
from db.configs import RouteTableConfig
from db import conf

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape

log = logging.getLogger(__name__)

ROUTE_CONF = conf.get('ROUTES', RouteTableConfig)

def sqr_dist(p1, p2):
    """ Returns the squared simple distance of two points.
        As we only compare close distances, we neither care about curvature
        nor about square roots.
    """
    xd = p1[0] - p2[0]
    yd = p1[1] - p2[1]
    return xd * xd + yd * yd



class RouteRow(dict):
    fields = set(('id', 'intnames', 'name', 'level', 'ref', 'itinary', 'network', 'top', 'geom', 'symbol', 'country'))

    def __init__(self, id_):
        for attr in self.fields:
            self[attr] = None

        self['id'] = id_
        self['intnames'] = {}
        self['level'] = Network.LOC()

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        if name not in self.fields:
            raise ValueError("Bad field " + name)
        self[name] = value



class Routes(ThreadableDBObject, TableSource):
    """ Table that creates information about the routes. This includes
        general information as well as the geometry.
    """

    def __init__(self, meta, name, relations, ways, hierarchy, countries):
        table = sa.Table(name, meta,
                        sa.Column('id', sa.BigInteger,
                                  primary_key=True, autoincrement=False),
                        sa.Column('name', sa.String),
                        sa.Column('intnames', JSONB),
                        sa.Column('ref', sa.String),
                        sa.Column('itinary', ARRAY(sa.String)),
                        sa.Column('symbol', sa.String),
                        sa.Column('country', sa.String(length=3)),
                        sa.Column('network', sa.String(length=3)),
                        sa.Column('level', sa.SmallInteger),
                        sa.Column('top', sa.Boolean),
                        sa.Column('geom', Geometry('GEOMETRY', srid=ways.srid)))

        super().__init__(table, relations.change)

        self.rels = relations
        self.ways = ways
        self.rtree = hierarchy
        self.countries = countries

        self.symbols = ShieldFactory(*ROUTE_CONF.symbols)


    def construct(self, engine):
        idx = sa.Index(self.data.name + '_iname_idx', sa.func.upper(self.data.c.name))

        with engine.begin() as conn:
            conn.execute(DropIndexIfExists(idx))
            self.truncate(conn)

        # insert
        sql = self.rels.data.select()
        res = engine.execution_options(stream_results=True).execute(sql)
        workers = self.create_worker_queue(engine, self._process_construct_next)
        for obj in res:
            workers.add_task(obj)

        workers.finish()

        with engine.begin() as conn:
            idx.create(conn)


    def _process_construct_next(self, obj):
        cols = self._construct_row(obj, self.thread.conn)

        if cols is not None:
            self.thread.conn.execute(self.data.insert().values(cols))

    def _construct_row(self, obj, conn):
        tags = TagStore(obj['tags'])
        outtags = RouteRow(obj['id'])

        # determine name and level
        for k, v in tags.items():
            if k in ('name', 'ref'):
                outtags[k] = v
            elif k.startswith('name:'):
                outtags.intnames[k[5:]] = v
            elif k == 'network':
                outtags.level = ROUTE_CONF.network_map.get(v, Network.LOC())

        # geometry
        geom = self.build_geometry(obj['members'], conn)

        if geom is None:
            return None

        # if the route is unsorted but linear, sort it
        if geom.geom_type == 'MultiLineString':
            fixed_geom = linemerge(geom)
            if fixed_geom.geom_type == 'LineString':
                geom = fixed_geom

        outtags.geom = from_shape(geom, srid=self.data.c.geom.type.srid)

        # find the country
        c = self.countries
        sel = sa.select([c.column_cc()], distinct=True)\
                .where(c.column_geom().ST_Intersects(outtags.geom))
        cur = self.thread.conn.execute(sel)

        # should be counting when rowcount > 1
        if cur.rowcount >= 1:
            cntry = cur.scalar()
        else:
            cntry = None

        outtags.country = cntry
        outtags.symbol = self.symbols.create_write(tags, cntry, outtags.level)

        # custom filter callback
        if ROUTE_CONF.tag_filter is not None:
            ROUTE_CONF.tag_filter(outtags, tags)

        if outtags.top is None:
            if 'network' in tags:
                h = self.rtree.data
                r = self.rels.data
                sel = sa.select([sa.text("'a'")]).where(h.c.child == obj['id'])\
                                         .where(r.c.id == h.c.parent)\
                                         .where(h.c.depth == 2)\
                                         .where(r.c.tags['network'].astext == tags['network'])\
                                         .limit(1)

                top = self.thread.conn.scalar(sel)

                outtags.top = (top is None)
            else:
                outtags.top = True

        return outtags

    def build_geometry(self, members, conn):
        geoms = { 'W' : {}, 'R' : {} }
        for m in members:
            if m['type'] != 'N':
                geoms[m['type']][m['id']] = None
        # first get all involved geoemetries
        for kind, t in (('W', self.ways.data), ('R', self.data)):
            if geoms[kind]:
                sql = sa.select([t.c.id, t.c.geom]).where(t.c.id.in_(geoms[kind].keys()))
                for r in conn.execute(sql):
                    geoms[kind][r['id']] = to_shape(r['geom'])

        # now put them together
        is_turnable = False
        outgeom = []
        for m in members:
            t = m['type']
            # ignore nodes and missing ways and relations
            if t == 'N' or m['id'] not in geoms[t]:
                continue

            # convert this to a tuple of coordinates
            geom = geoms[t][m['id']]
            if geom is None:
                continue 
            if geom.geom_type == 'MultiLineString':
                geom = [list(g.coords) for g in list(geom.geoms)]
            else:
                geom = [list(geom.coords)]

            if outgeom:
                # try connect with previous geometry at end point
                if geom[0][0] == outgeom[-1][-1]:
                    outgeom[-1].extend(geom[0][1:])
                    outgeom.extend(geom[1:])
                    is_turnable = False
                    continue
                if geom[-1][-1] == outgeom[-1][-1]:
                    outgeom[-1].extend(geom[-1][-2::-1])
                    outgeom.extend(geom[-2::-1])
                    is_turnable = False
                    continue
                if is_turnable:
                    # try to connect with previous geometry at start point
                    if geom[0][0] == outgeom[-1][0]:
                        outgeom[-1].reverse()
                        outgeom[-1].extend(geom[0][1:])
                        outgeom.extend(geom[1:])
                        is_turnable = False
                        continue
                    if geom[-1] == outgeom[-1][0]:
                        outgeom[-1].reverse()
                        outgeom[-1].extend(geom[-1][-2::-1])
                        outgeom.extend(geom[-2::-1])
                        is_turnable = False
                        continue
                # nothing found, then turn the geometry such that the
                # end points are as close together as possible
                mdist = sqr_dist(outgeom[-1][-1], geom[0][0])
                d = sqr_dist(outgeom[-1][-1], geom[-1][-1])
                if d < mdist:
                    geom = [list(reversed(g)) for g in reversed(geom)]
                    mdist = d
                # For the second way in the relation, we also allow the first
                # to be turned, if the two ways aren't connected.
                if is_turnable and len(outgeom) == 1:
                    d1 = sqr_dist(outgeom[-1][0], geom[0][0])
                    d2 = sqr_dist(outgeom[-1][0], geom[-1][-1])
                    if d1 < mdist or d2 < mdist:
                        outgeom[-1].reverse()
                    if d2 < d1:
                        geom = [list(reversed(g)) for g in reversed(geom)]

            outgeom.extend(geom)
            is_turnable = True

        return LineString(outgeom[0]) if len(outgeom) == 1 else MultiLineString(outgeom)

