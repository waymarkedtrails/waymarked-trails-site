# This file is part of Lonvia's Route Maps Project
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

import routemap.hiking.relations as hrel
import routemap.hiking.style_default as hstyle
import routemap.hiking.administrative as hadmin
import routemap.hiking.guideposts as hposts

class RouteMapDB(routemap.common.mapdb.MapDB):

    def create_table_objects(self):
        self.update_table = hrel.UpdatedGeometries(self.db)
        countries = hadmin.CountryTable(self.db)
        self.segment_table = hrel.Segments(self.db, countries)
        self.data_tables = [
            countries,
            self.segment_table,
            hrel.Hierarchies(self.db),
            hrel.Routes(self.db),
            hposts.GuidePosts(self.db),
            hposts.NetworkNodes(self.db),
        ]
        self.style_tables = [
            hstyle.HikingStyleDefault(self.db)
        ]

