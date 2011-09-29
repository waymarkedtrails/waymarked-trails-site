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
