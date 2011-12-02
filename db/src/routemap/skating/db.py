# This file is part of Lonvia's Route Map Project
# Copyright (C) 2011 Sarah Hoffmann
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
import routemap.common.mapdb

import conf

import routemap.skating.relations as hrel
import routemap.skating.style_default as hstyle

class RouteMapDB(routemap.common.mapdb.MapDB):

    def create_table_objects(self):
        # stores all modified routes (no changes in guideposts or 
        # network nodes are tracked)
        self.update_table = osgende.UpdatedGeometriesTable(self.db, 
                conf.DB_CHANGE_TABLE)

        # Route segments for the routable network
        self.segment_table = osgende.RelationSegments(self.db, 
                conf.DB_SEGMENT_TABLE,
                conf.TAGS_ROUTE_SUBSET,
                uptable=self.update_table)
        self.segment_table.set_num_threads(self.numthreads)

        hiertable = osgende.RelationHierarchy(self.db,
                            name=conf.DB_HIERARCHY_TABLE,
                            subset="""SELECT id FROM relations
                                      WHERE %s""" % (conf.TAGS_ROUTE_SUBSET))

        hroutes = hrel.Routes(self.db, self.segment_table, hiertable)
        hroutes.set_num_threads(self.numthreads)

        self.data_tables = [
            self.segment_table,
            hiertable,
            hroutes,
        ]
        self.style_tables = [
            hstyle.SkatingStyleDefault(self.db)
        ]


