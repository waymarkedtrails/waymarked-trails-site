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
from geoalchemy2 import Geometry

from osgende.common.table import TableSource
from osgende.common.threads import ThreadableDBObject

class StyleTable(ThreadableDBObject, TableSource):
    """ Generic way table with styling information.
    """
    def __init__(self, meta, routes, segments, hierarchy, style_config):
        self.config = style_config
        srid = segments.srid

        table = sa.Table(self.config.table_name, meta,
                         sa.Column('id', sa.BigInteger
                                   ,primary_key=True, autoincrement=False),
                         sa.Column('geom', Geometry('LINESTRING', srid=srid)),
                         sa.Column('geom100', Geometry('LINESTRING', srid=srid))
                         )

        self.config.add_columns(table)

        super().__init__(table, segments.change)

        self.rels = routes
        self.ways = segments
        self.rtree = hierarchy

    def construct(self, engine):
        self.synchronize(engine)

    def update(self, engine):
        self.synchronize(engine, self.c.id.in_(sa.select([self.ways.cc.id])))

    def synchronize(self, engine, subset=None):
        self.route_cache = {}

        h = self.rtree
        m = self.ways
        parents = sa.select([h.c.parent])\
                      .where(h.c.child == sa.func.any(m.c.rels))\
                      .distinct().as_scalar()

        sql = sa.select([m.c.id, (m.c.rels + sa.func.array(parents)).label('rels')])

        if subset is not None:
            sql.where(subset)

        route_sql = sa.select([c for c in self.rels.c if c.name != 'geom'])

        with engine.begin() as conn:
            res = engine.execution_options(stream_results=True).execute(sql)
            workers = self.create_worker_queue(engine, self._process_construct_next)
            for obj in res:
                # build cache in the main thread, so that workers only read
                cache_todo = [ x for x in obj['rels'] if x not in self.route_cache ]
                if cache_todo:
                    subres = conn.execute(route_sql.where(self.rels.c.id.in_(cache_todo)))
                    for route in subres:
                        self.route_cache[route['id']] = route
                workers.add_task(obj)

        workers.finish()

        del self.route_cache

        # now update the geometries
        sql = self.data.update().values(geom=m.c.geom.ST_Simplify(1),
                                        geom100=m.c.geom.ST_Simplify(100))\
                                .where(self.data.c.geom == None)\
                                .where(self.data.c.id == m.c.id)
        engine.execute(sql)


    def _process_construct_next(self, obj):
        cols = self._construct_row(obj, self.thread.conn)

        if cols is not None:
            self.thread.conn.execute(self.upsert_data().values(cols))

    def _construct_row(self, obj, conn):
        seginfo = self.config.new_collector()
        for rel in obj['rels']:
            if rel not in self.route_cache:
                print("Warning: no information for relation", rel)
            else:
                self.config.add_to_collector(seginfo, self.route_cache[rel])

        outdata = self.config.to_columns(seginfo)
        outdata['id']  = obj['id']
        outdata['geom'] = None
        outdata['geom100'] = None

        return outdata




