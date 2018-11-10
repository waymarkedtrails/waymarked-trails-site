# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2015 Michael Spreng
#               2018 Sarah Hoffmann
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

from osgende.common.table import TableSource
from osgende.common.sqlalchemy import DropIndexIfExists, CreateTableAs
from osgende.common.threads import ThreadableDBObject
from osgende.common.tags import TagStore
from osgende.common.build_geometry import build_route_geometry
from osgende.lines import PlainWayTable

import sqlalchemy as sa
from sqlalchemy.sql import functions as saf
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape, from_shape
from shapely.ops import linemerge

from db.common.symbols import ShieldFactory
from db.configs import PisteTableConfig, RouteTableConfig
from db import conf

CONF = conf.get('PISTE', PisteTableConfig)

shield_fab = ShieldFactory(*CONF.symbols)

def _add_piste_columns(table, name):
    table.append_column(sa.Column('name', sa.String))
    table.append_column(sa.Column('intnames', JSONB))
    table.append_column(sa.Column('symbol', sa.String))
    table.append_column(sa.Column('difficulty', sa.SmallInteger))
    table.append_column(sa.Column('piste', sa.SmallInteger))
    table.append_column(sa.Index('idx_%s_iname' % name, sa.text('upper(name)')))

def _basic_tag_transform(osmid, tags):
    outtags = { 'intnames' : {} }

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
    difficulty = tags.get('piste:difficulty')
    difficulty = CONF.difficulty_map.get(difficulty, 0)
    outtags['difficulty'] = difficulty
    outtags['piste'] = CONF.piste_type.get(tags.get('piste:type'), 0)

    return outtags, difficulty


class PisteRoutes(ThreadableDBObject, TableSource):
    """ Table that creates information about the routes. This includes
        general information as well as the geometry.
    """

    def __init__(self, meta, name, relations, ways, hierarchy, countries):
        table = sa.Table(name, meta)
        table.append_column(sa.Column('id', sa.BigInteger,
                                      primary_key=True, autoincrement=False))
        table.append_column(sa.Column('top', sa.Boolean))
        _add_piste_columns(table, name)
        table.append_column(sa.Column('geom', Geometry('GEOMETRY', srid=ways.srid)))

        super().__init__(table, relations.change)

        self.rels = relations
        self.ways = ways
        self.rtree = hierarchy
        self.countries = countries

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
        self.insert_objects(conn, subset)


    def construct(self, engine):
        h = self.rtree.data
        idx = sa.Index(self.data.name + '_iname_idx', sa.func.upper(self.c.name))

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

    def _construct_row(self, obj, conn):
        tags = TagStore(obj['tags'])

        outtags, difficulty = _basic_tag_transform(obj['id'], tags)

        # we don't support hierarchy at the moment
        outtags['top']  = True

        # geometry
        geom = build_route_geometry(conn, obj['members'], self.ways, self.data)

        if geom is None:
            return None

        if geom.geom_type not in ('MultiLineString', 'LineString'):
            raise RuntimeError("Bad geometry %s for %d" % (geom.geom_type, obj['id']))

        # if the route is unsorted but linear, sort it
        if geom.geom_type == 'MultiLineString':
            fixed_geom = linemerge(geom)
            if fixed_geom.geom_type == 'LineString':
                geom = fixed_geom

        outtags['geom'] = from_shape(geom, srid=self.c.geom.type.srid)
        outtags['symbol'] = shield_fab.create_write(tags, '', difficulty)
        outtags['id'] = obj['id']

        return outtags


class PisteWayInfo(PlainWayTable):

    def add_columns(self, dest, src):
        _add_piste_columns(dest, 'piste_way_info')

    def transform_tags(self, obj):
        tags = TagStore(obj['tags'])

        outtags, difficulty = _basic_tag_transform(obj['id'], tags)
        outtags['symbol'] = shield_fab.create_write(tags, '', difficulty)

        return outtags
