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
from osgende.common.sqlalchemy import DropIndexIfExists, CreateTableAs
from osgende.common.threads import ThreadableDBObject
from osgende.common.tags import TagStore
from osgende.common.build_geometry import build_route_geometry
from shapely.ops import linemerge

from db.common.symbols import ShieldFactory
from db.common.route_types import Network
from db.configs import RouteTableConfig
from db import conf

import sqlalchemy as sa
from sqlalchemy.sql import functions as saf
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape

log = logging.getLogger(__name__)

ROUTE_CONF = conf.get('ROUTES', RouteTableConfig)

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

def _compute_route_level(network):
    # Multi-modal routes might have multiple network tags
    for n in network.split(';'):
        if n in ROUTE_CONF.network_map:
            return ROUTE_CONF.network_map[n]

    return Network.LOC()


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
                        sa.Column('itinary', JSONB),
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

        self.numthreads = meta.info.get('num_threads', 1)


    def _insert_objects(self, conn, subsel=None):
        h = self.rtree.data
        max_depth = conn.scalar(sa.select([saf.max(h.c.depth)]))

        subtab = sa.select([h.c.child, saf.max(h.c.depth).label("lvl")])\
                   .group_by(h.c.child).alias()

        # Process relations by hierarchy, starting with the highest depth.
        # This guarantees that the geometry of member relations is already
        # available for processing the relation geometry.
        if max_depth is not None:
            for level in range(max_depth, 1, -1):
                subset = self.rels.data.select()\
                          .where(subtab.c.lvl == level)\
                          .where(self.rels.c.id == subtab.c.child)
                if subsel is not None:
                    subset = subset.where(subsel)
                self.insert_objects(conn, subset)

        # Lastly, process all routes that are nobody's child.
        subset = self.rels.data.select()\
                 .where(self.rels.c.id.notin_(
                     sa.select([h.c.child], distinct=True).as_scalar()))
        if subsel is not None:
            subset = subset.where(subsel)
        self.insert_objects(conn, subset)


    def construct(self, engine):
        h = self.rtree.data
        idx = sa.Index(self.data.name + '_iname_idx', sa.func.upper(self.data.c.name))

        with engine.begin() as conn:
            conn.execute(DropIndexIfExists(idx))
            self.truncate(conn)

            max_depth = conn.scalar(sa.select([saf.max(h.c.depth)]))

        subtab = sa.select([h.c.child, saf.max(h.c.depth).label("lvl")])\
                   .group_by(h.c.child).alias()

        # Process relations by hierarchy, starting with the highest depth.
        # This guarantees that the geometry of member relations is already
        # available for processing the relation geometry.
        if max_depth is not None:
            for level in range(max_depth, 1, -1):
                subset = self.rels.data.select()\
                          .where(subtab.c.lvl == level)\
                          .where(self.rels.c.id == subtab.c.child)
                self.insert_objects(engine, subset)

        # Lastly, process all routes that are nobody's child.
        subset = self.rels.data.select()\
                 .where(self.rels.c.id.notin_(
                     sa.select([h.c.child], distinct=True).as_scalar()))
        self.insert_objects(engine, subset)

        with engine.begin() as conn:
            idx.create(conn)

    def update(self, engine):
        with engine.begin() as conn:
            # delete removed relations
            conn.execute(self.delete(self.rels.select_delete()))
            # collect all changed relations in a temporary table
            # 1. relations added or modified
            sels = [sa.select([self.rels.cc.id])]
            # 2. relations with modified geometries
            w = self.ways
            sels.append(sa.select([saf.func.unnest(w.c.rels).label('id')], distinct=True)
                          .where(w.c.id.in_(w.select_add_modify())))

            conn.execute('DROP TABLE IF EXISTS __tmp_osgende_routes_updaterels')
            conn.execute(CreateTableAs('__tmp_osgende_routes_updaterels',
                         sa.union(*sels), temporary=False))
            tmp_rels = sa.Table('__tmp_osgende_routes_updaterels',
                                sa.MetaData(), autoload_with=conn)

            # 3. parent relation of all of them
            conn.execute(tmp_rels.insert().from_select(tmp_rels.c,
                sa.select([self.rtree.c.parent], distinct=True)
                  .where(self.rtree.c.child.in_(sa.select([tmp_rels.c.id])))))

            # and insert/update all
            self._insert_objects(conn, self.rels.c.id.in_(tmp_rels.select()))

            tmp_rels.drop(conn)

    def insert_objects(self, engine, subset):
        res = engine.execution_options(stream_results=True).execute(subset)

        workers = self.create_worker_queue(engine, self._process_construct_next)
        for obj in res:
            workers.add_task(obj)

        workers.finish()


    def _process_construct_next(self, obj):
        cols = self._construct_row(obj, self.thread.conn)

        if cols is not None:
            self.thread.conn.execute(self.upsert_data().values(cols))
        else:
            self.thread.conn.execute(self.data.delete().where(self.c.id == obj['id']))


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
                outtags.level = _compute_route_level(v)

        if tags.get('network:type') == 'node_network':
            outtags.level = Network.LOC.min()

        # child relations
        relids = [ r['id'] for r in obj['members'] if r['type'] == 'R']

        members = obj['members']
        if len(relids) > 0:
            # Is this relation part of a cycle? Then drop the relation members
            # to not get us in trouble with geometry building.
            h1 = self.rtree.data.alias()
            h2 = self.rtree.data.alias()
            sql = sa.select([h1.c.parent])\
                    .where(h1.c.parent == obj['id'])\
                    .where(h1.c.child == h2.c.parent)\
                    .where(h2.c.child == obj['id'])
            if (self.thread.conn.execute(sql).rowcount > 0):
                members = [ m for m in obj['members'] if m['type'] == 'W' ]
                relids = []

        # geometry
        geom = build_route_geometry(conn, members, self.ways, self.data)

        if geom is None:
            return None

        if geom.geom_type not in ('MultiLineString', 'LineString'):
            raise RuntimeError("Bad geometry %s for %d" % (geom.geom_type, obj['id']))

        # if the route is unsorted but linear, sort it
        if geom.geom_type == 'MultiLineString':
            fixed_geom = linemerge(geom)
            if fixed_geom.geom_type == 'LineString':
                geom = fixed_geom

        outtags.geom = from_shape(geom, srid=self.data.c.geom.type.srid)

        # find the country
        if len(relids) > 0:
            sel = sa.select([self.c.country], distinct=True)\
                    .where(self.c.id.in_(relids))
        else:
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

        if outtags.network is None:
            if tags.get('network:type') == 'node_network':
                outtags.network = 'NDS'

        if outtags.top is None:
            if 'network' in tags and tags.get('network:type') != 'node_network':
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
