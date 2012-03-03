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

from django.db import models

class BlobField(models.Field):
    # XXX This is unfinished, but since we don't write BLOBs
    #     at the moment, it does not matter.

    description = 'Sqlite BLOB Field'

    def db_type(self, connection):
        return 'BLOB'

class TileModel(models.Model):

    zoom = models.IntegerField(primary_key=True)
    tilex = models.IntegerField()
    tiley = models.IntegerField()
    pixbuf = BlobField()

    class Meta:
        abstract = True
