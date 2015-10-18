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
""" Tables for administrative structures
"""

from sqlalchemy import Table, Column, String, Float
from geoalchemy2 import Geometry

class CountryGrid(object):
    """Wraps a Nominatim country_osm_grid table.
    """

    def __init__(self, meta, name='country_osm_grid'):
        self.data = Table(name, meta,
                          Column('country_code', String),
                          Column('area', Float),
                          Column('geom', Geometry)
                         )

    def column_cc(self):
        return self.data.c.country_code

    def column_geom(self):
        return self.data.c.geom
