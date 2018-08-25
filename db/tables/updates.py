# This file is part of Osgende
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
"""
Tables to trace updates
"""

from sqlalchemy import Table, Column, String
from geoalchemy2 import Geometry

class UpdatedGeometriesTable(object):
    """Table that stores just a list of geometries that have been changed
       in the course of an update.

       This table contains created and modified geometries as well as
       deleted ones.
    """

    def __init__(self, meta, name):
        srid = meta.info.get('srid', 4326)
        self.data = Table(name, meta,
                          Column('geom', Geometry('GEOMETRY', srid=srid)))

    def clear(self, conn):
        conn.execute(self.data.delete())

    def create(self, engine):
        self.data.create(bind=engine, checkfirst=True)

    def construct(self, engine):
        self.clear(engine)

    def update(self, engine):
        self.clear(engine)

    def add(self, conn, geom):
        conn.execute(self.data.insert().values(geom=geom))

    def add_from_select(self, conn, stm):
        conn.execute(self.data.insert().from_select(self.data.c, stm))
