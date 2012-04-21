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

import django
import psycopg2.extras

def set_schema(sender, connection, **kwargs):
    cursor = connection.cursor()
    cursor.execute("SET search_path TO skating,public;")
    psycopg2.extras.register_hstore(cursor, globally=True, unicode=True)

if django.VERSION >= (1,1):
    from django.db.backends.signals import connection_created
    connection_created.connect(set_schema)

