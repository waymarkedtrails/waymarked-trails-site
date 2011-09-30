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

from django.db import models
from django.db.models.fields import IntegerField


class HStoreField(models.Field):

    description = "Postgresql Hstore"

    def db_type(self, connection):
        return 'hstore' # Postgresql only!


class BigIntArrayField(models.Field):

    description = "Postgresql Array of BigInts"

    def db_type(self, connection):
        return 'bigint[]' # Postgresql only!


class BigIntegerField(IntegerField):
    empty_strings_allowed=False
    def db_type(self, connection):
        return 'bigint' # Note this won't work with Oracle.
