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

import routemap.common.mapdb

import routemap.cycling.relations as hrel
import routemap.cycling.style_default as hstyle
import routemap.cycling.guideposts as hposts

class RouteMapDB(routemap.common.mapdb.MapDB):

    def create_table_objects(self):
        self.update_table = hrel.UpdatedGeometries(db)
        self.segment_table = hrel.Segments(db)
        self.data_table = [
            self.segment_table,
            hrel.Hierarchies(db),
            hrel.Routes(db),
            hposts.NetworkNodes(db)
        ]
        self.style_tables = [
            hstyle.cyclingStyleDefault(db)
        ]


