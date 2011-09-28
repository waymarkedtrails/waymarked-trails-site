import django
import psycopg2.extras

def set_schema(sender, **kwargs):
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute("SET search_path TO cycling,public;")
    psycopg2.extras.register_hstore(cursor, globally=True, unicode=True)

if django.VERSION >= (1,1):
    from django.db.backends.signals import connection_created
    connection_created.connect(set_schema)

