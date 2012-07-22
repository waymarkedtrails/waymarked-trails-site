# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
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

import osgende

import conf

import routemap.hiking.relations as hrel
import routemap.hiking.style_default as hstyle
import routemap.admin.countries as hadmin
import routemap.hiking.guideposts as hposts

class RouteMapDB(osgende.mapdb.MapDB):

    def create_table_objects(self):
        # stores all modified routes (no changes in guideposts or 
        # network nodes are tracked)
        self.update_table = osgende.UpdatedGeometriesTable(self.db, conf.DB_CHANGE_TABLE)

        # Country polygons
        countries = hadmin.CountryTable(self.db)

        # Route segment for the routable network
        self.segment_table = osgende.RelationSegments(self.db, 
                         conf.DB_SEGMENT_TABLE,
                         conf.TAGS_ROUTE_SUBSET,
                         country_table=countries,
                         country_column='code',
                         uptable=self.update_table)
        self.segment_table.set_num_threads(self.options.numthreads)

        # table saving the relation between the routes
        hiertable = osgende.RelationHierarchy(self.db,
                            name=conf.DB_HIERARCHY_TABLE,
                            subset="""SELECT id FROM relations
                                      WHERE %s""" % (conf.TAGS_ROUTE_SUBSET))

        routetable = hrel.Routes(self.db, self.segment_table, hiertable)
        routetable.set_num_threads(self.options.numthreads)

        self.data_tables = [
            self.segment_table,
            hiertable,
            routetable,
            hposts.GuidePosts(self.db),
            hposts.NetworkNodes(self.db),
        ]
        self.style_tables = [
            hstyle.HikingStyleDefault(self.db)
        ]

    def make_shields(self):
        self.generate_shields(hrel.symboltypes)
