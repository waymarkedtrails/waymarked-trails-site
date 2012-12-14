#!/usr/bin/env python
import os
import sys
from django import VERSION
import psycopg2.extras

sitename = 'hiking'

def set_schema(sender, connection, **kwargs):
    cursor = connection.cursor()
    cursor.execute("SET search_path TO %s,public;" % sitename)
    psycopg2.extras.register_hstore(cursor, globally=True, unicode=True)


if __name__ == "__main__":
    from django.core.management import execute_from_command_line

    sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../..')))
    sys.path.append(os.path.normpath(os.path.join(os.path.realpath(__file__), '../../../../config')))

    if len(sys.argv) > 1 and sys.argv[-1] in ('hiking', 'cycling', 'skating', 'mtbmap'):
        sitename = sys.argv[-1]
        args = sys.argv[:-1]
    else:
        args = sys.argv

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "routemap.sites.settings." + sitename )
    if VERSION >= (1,1):
        from django.db.backends.signals import connection_created
        connection_created.connect(set_schema)

    execute_from_command_line(args)

