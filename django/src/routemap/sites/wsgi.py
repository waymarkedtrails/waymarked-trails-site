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
"""
Apache mod_wsgi script.
The script needs to be executed in a process group that corresponds
to the map to be executed.

Your virtual server configuration should contain something along the lines of:

    WSGIDaemonProcess hiking
    WSGIProcessGroup hiking
    WSGIScriptAlias / /var/www/waymarked-trails/django/src/routemap/sites/wsgi.py
"""

import os
import sys
import mod_wsgi
import psycopg2.extras

sitename = mod_wsgi.process_group

def set_schema(sender, connection, **kwargs):
    """Put the schema into the search path."""
    cursor = connection.cursor()
    cursor.execute("SET search_path TO %s,public;" % sitename)
    psycopg2.extras.register_hstore(cursor, globally=True, unicode=True)


os.environ["DJANGO_SETTINGS_MODULE"] = 'routemap.sites.settings.' + sitename

basepath = os.path.normpath(os.path.join(os.path.realpath(__file__), '../../../../..'))
sys.path.append(os.path.join(basepath, 'django/src'))
sys.path.append(os.path.join(basepath, 'config'))

from django.db.backends.signals import connection_created
connection_created.connect(set_schema)


# This application object is used by the development server
# as well as any WSGI server configured to use this file.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
