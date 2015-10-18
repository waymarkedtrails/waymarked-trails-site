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

""" Database for the classic route view (hiking, cycliing, etc.)
"""
import osgende
from osgende.update import UpdatedGeometriesTable
from osgende.relations import RouteSegments, RelationHierarchy
from osgende.tags import TagStore

from sqlalchemy import MetaData, select, text

from db.tables.countries import CountryGrid
from db.tables.routes import RouteInfo, RouteSegmentStyle
from db.tables.route_nodes import GuidePosts, NetworkNodes
from db.configs import RouteDBConfig
from db import conf

CONFIG = conf.get('ROUTEDB', RouteDBConfig)

class DB(osgende.MapDB):
    routeinfo_class = RouteInfo
    segmentstyle_class = RouteSegmentStyle

    def __init__(self, options):
        setattr(options, 'schema', CONFIG.schema)
        osgende.MapDB.__init__(self, options)

    def create_tables(self):
        self.metadata.info['srid'] = CONFIG.srid

        tables = []
        # first the update table:
        # stores all modified routes (no changes in guideposts or
        # network nodes are tracked)
        uptable = UpdatedGeometriesTable(self.metadata, CONFIG.change_table)
        tables.append(uptable)

        # segment table: route segments only
        segtable = RouteSegments(self.metadata, CONFIG.segment_table,
                                 self.osmdata, subset=CONFIG.relation_subset,
                                 geom_change=uptable)
        segtable.set_num_threads(self.get_option('numthreads'))
        tables.append(segtable)

        # hierarchy table for super relations
        r = self.osmdata.relation.data
        hiertable = RelationHierarchy(self.metadata, CONFIG.hierarchy_table,
                                      self.osmdata,
                                      subset=select([r.c.id])
                                              .where(text(CONFIG.relation_subset)))
        tables.append(hiertable)

        # routes table: information about each route
        routetable = self.routeinfo_class(segtable, hiertable,
                                     CountryGrid(MetaData(), CONFIG.country_table))
        routetable.set_num_threads(self.get_option('numthreads'))
        tables.append(routetable)

        # finally the style table for rendering
        tables.append(self.segmentstyle_class(self.metadata, routetable,
                                              segtable, hiertable))

        # optional table for guide posts
        if conf.isdef('GUIDEPOSTS'):
            tables.append(GuidePosts(self.metadata, self.osmdata, uptable))
        # optional table for network nodes
        if conf.isdef('NETWORKNODES'):
            tables.append(NetworkNodes(self.metadata, self.osmdata, uptable))

        return tables


    def mkshield(self):
        for t in self.tables:
            if isinstance(t, self.routeinfo_class):
                route = t
                break
        else:
             raise RuntimeError("Route info table not found.")

        rel = self.osmdata.relation.data
        sel = select([rel.c.tags, route.data.c.country, route.data.c.level])\
                .where(rel.c.id == route.data.c.id)

        donesyms = set()

        with self.engine.begin() as conn:
            for r in conn.execution_options(stream_results=True).execute(sel):
                sym = route.symbols.create(TagStore(r["tags"]), r["country"],
                                           r["level"])

                if sym is not None:
                    symid = sym.get_id()

                    if symid not in donesyms:
                        donesyms.add(symid)
                        route.symbols.write(sym, True)


