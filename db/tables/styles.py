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

from sqlalchemy import Table, Column, BigInteger, ForeignKey, select, func
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_Simplify

class SegmentStyle(object):

    def __init__(self, meta, name, osmdata, routes, segments, hierarchy):
        self.t_route = routes
        self.t_segment = segments
        self.t_hier = hierarchy
        self.t_relchange = osmdata.relation.change
        srid = segments.data.c.geom.type.srid
        self.data = Table(name, meta,
                          Column('id', BigInteger,
                                 ForeignKey(segments.data.c.id, ondelete='CASCADE')),
                          Column('geom', Geometry('GEOMETRY', srid=srid)),
                          Column('geom100', Geometry('GEOMETRY', srid=srid)),
                         )
        for c in self.columns():
            self.data.append_column(c)

    def truncate(self, conn):
        conn.execute(self.data.delete())

    def construct(self, engine):
        self.truncate(engine)
        self.synchronize(engine, 0)

    def update(self, engine):
        self.synchronize(engine, self.t_segment.first_new_id)

    def synchronize(self, engine, firstid):
        # cache routing information, so we don't have to get it every time
        route_cache = {}

        with engine.begin() as conn:
            h = self.t_hier.data
            s = self.t_segment.data
            sel = select([s.c.id, func.array_agg(h.c.parent).label('rels')])\
                     .where(s.c.rels.any(h.c.child)).group_by(s.c.id)

            if firstid > 0:
                sel = sel.where(s.c.id >= firstid)

            for seg in conn.execute(sel):
                self._update_segment_style(conn, seg, route_cache)

            # and copy geometries
            sel = self.data.update().where(self.data.c.id == s.c.id)\
                          .values(geom=ST_Simplify(s.c.geom, 1),
                                  geom100=ST_Simplify(s.c.geom, 100))
            if firstid > 0:
                sel = sel.where(self.data.c.id >= firstid)
            conn.execute(sel)

            # now synchronize all segments where a hierarchical relation has changed
            if firstid > 0:
                segs = select([s.c.id, s.c.rels], distinct=True)\
                        .where(s.c.rels.any(h.c.child))\
                        .where(h.c.depth > 1)\
                        .where(s.c.id < firstid)\
                        .where(h.c.parent.in_(select([self.t_relchange.c.id])))\
                        .alias()
                h2 = self.t_hier.data.alias()
                sel = select([segs.c.id, func.array_agg(h2.c.parent).label('rels')])\
                         .where(segs.c.rels.any(h2.c.child)).group_by(segs.c.id)

                for seg in conn.execute(sel):
                    self._update_segment_style(conn, seg, route_cache, update=True)

    def _update_segment_style(self, conn, seg, route_cache, update=False): 
        seginfo = self.segment_info()
        for rel in seg['rels']:
            if rel in route_cache:
                relinfo = route_cache[rel]
            else:
                sel = self.t_route.data.select().where(self.t_route.data.c.id == rel)
                relinfo = conn.execute(sel).first()
                route_cache[rel] = relinfo

            if relinfo is None:
                print("Warning: no information for relation", rel)
            else:
                seginfo.append(relinfo)

        if update:
            conn.execute(self.data.update().where(self.data.c.id == seg['id'])
                          .values(**seginfo.to_dict(seg['id'])))
        else:
            conn.execute(self.data.insert(seginfo.to_dict(seg['id'])))


