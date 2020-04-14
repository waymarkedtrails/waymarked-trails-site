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

""" Database for the classic route view (hiking, cycling, etc.)
"""
from collections import namedtuple, OrderedDict

import osgende
from osgende.generic import FilteredTable
from osgende.lines import RelationWayTable, SegmentsTable
from osgende.relations import RelationHierarchy
from osgende.common.tags import TagStore

from sqlalchemy import MetaData, select, text

from db.tables.countries import CountryGrid
from db.tables.routes import Routes
from db.tables.route_nodes import GuidePosts, NetworkNodes
from db.tables.updates import UpdatedGeometriesTable
from db.tables.styles import StyleTable
from db.configs import RouteDBConfig
from db import conf

CONFIG = conf.get('ROUTEDB', RouteDBConfig)


class DB(osgende.MapDB):
    routeinfo_class = Routes

    def __init__(self, options):
        setattr(options, 'schema', CONFIG.schema)
        osgende.MapDB.__init__(self, options)

        country = CountryGrid(MetaData(), CONFIG.country_table)
        if not self.get_option('no_engine') and not country.data.exists(self.engine):
            raise RuntimeError("No country table found.")

    def create_table_dict(self):
        self.metadata.info['srid'] = CONFIG.srid
        self.metadata.info['num_threads'] = self.get_option('numthreads')

        tables = OrderedDict()
        # first the update table: stores all modified routes, points
        uptable = UpdatedGeometriesTable(self.metadata, CONFIG.change_table)
        tables['updates'] = uptable

        # First we filter all route relations into an extra table.
        rfilt = FilteredTable(self.metadata, CONFIG.route_filter_table,
                              self.osmdata.relation,
                              text("(%s)" % CONFIG.relation_subset))
        tables['relfilter'] = rfilt

        # Then we create the connection between ways and relations.
        # This also adds geometries.
        relway = RelationWayTable(self.metadata, CONFIG.way_relation_table,
                                  self.osmdata.way, rfilt, osmdata=self.osmdata)
        tables['relway'] = relway

        # From that create the segmented table.
        segments = SegmentsTable(self.metadata, CONFIG.segment_table, relway,
                                 (relway.c.rels,))
        tables['segments'] = segments

        # hierarchy table for super relations
        rtree = RelationHierarchy(self.metadata, CONFIG.hierarchy_table, rfilt)
        tables['hierarchy'] = rtree

        # routes table: information about each route
        routes = self.routeinfo_class(self.metadata, CONFIG.route_table,
                                      rfilt, relway, rtree,
                                      CountryGrid(MetaData(), CONFIG.country_table))
        tables['routes'] = routes

        # finally the style table for rendering
        style = StyleTable(self.metadata, routes, segments, rtree,
                           conf.get('DEFSTYLE'), uptable)
        tables['style'] = style

        # optional table for guide posts
        if conf.isdef('GUIDEPOSTS'):
            cfg = conf.get('GUIDEPOSTS')
            filt = FilteredTable(self.metadata, cfg.table_name + '_view',
                                 self.osmdata.node, text(cfg.node_subset),
                                 view_only=True)
            tables['gp_filter'] = filt
            tables['guideposts'] = GuidePosts(self.metadata, filt)
        # optional table for network nodes
        if conf.isdef('NETWORKNODES'):
            cfg = conf.get('NETWORKNODES')
            filt = FilteredTable(self.metadata, cfg.table_name + '_view',
                                 self.osmdata.node,
                                 self.osmdata.node.c.tags.has_key(cfg.node_tag),
                                 view_only=True)
            tables['nnodes_filter'] = filt
            tables['networknodes'] = NetworkNodes(self.metadata, filt)

        return tables

    def create_tables(self):
        tables = self.create_table_dict()

        _RouteTables = namedtuple('_RouteTables', tables.keys())

        return _RouteTables(**tables)

    def dataview(self):
        schema = self.get_option('schema', '')
        if schema:
            schema += '.'
        with self.engine.begin() as conn:
            conn.execute("""CREATE OR REPLACE VIEW %sdata_view AS
                            SELECT geom FROM %s%s"""
                         % (schema, schema, str(self.tables.style.data.name)))

    def mkshield(self):
        route = self.tables.routes
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


