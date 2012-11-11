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

""" This model defines all tables related to boundaries.
"""

from osgende import RelationPolygons
import conf

class CountryTable(RelationPolygons):
    """The table containing country information.

       For the moment this only includes country code and geometry.
    """
    srid = conf.DB_SRID

    def __init__(self, db):
        # Very liberal here: only admin_level tag is required.
        RelationPolygons.__init__(self, db, conf.DB_COUNTRY_TABLE,
               subset="id = 51701", #"tags ? 'admin_level' AND tags->'admin_level' = '2'",
               child_tags = ['admin_level'], 
               transform='ST_SimplifyPreserveTopology(ST_Transform(%%s, %s), 10)' % conf.DB_SRID)

    def create(self):
        """Create a new empty table in the database.
        """
        self.layout((
                  ('code', 'varchar(2)'),
                  ))

    def transform_tags(self, osmid, tags):
        return { 'code': tags.get('ISO3166-1', tags.get('name', 'XX'))[:2] }

