from django.contrib.gis.db import models
import cycling.util.customfields as cfields
from django.db import connection, transaction
import django.contrib.gis.geos as geos
import util

class CyclingRoutes(models.Model):
    """Table with information about cycling routes.
    """
    
    id = cfields.BigIntegerField(primary_key=True) 
    name = models.TextField(null=True)
    intnames = cfields.HStoreField()
    symbol = models.TextField(null=True)
    network = models.CharField(max_length=2, null=True)
    level = models.IntegerField()
    top = models.BooleanField()
    geom = models.GeometryField(srid=900913)

    objects = models.GeoManager()

    def get_local_tags(self, locstring):
        locstring = ':'+locstring
        loclen = -len(locstring)
        ret = {}
        tags = self.tags()
        for k,v in tags.iteritems():
            if k.endswith(locstring):
                ret[k[:loclen]] = v
            else:
                if k not in ret:
                    ret[k] = v
        # special case wikipedia, standard is :en
        if 'wikipedia' not in ret and 'wikipedia:en' in tags:
            ret['wikipedia'] = tags['wikipedia:en']

        return ret

    def localize_name(self, locstring):
        if locstring in self.intnames and not self.name == self.intnames[locstring]:
            self.origname = self.name
            self.name = self.intnames[locstring]


    def tags(self):
        if not hasattr(self,'_tags'):
            cursor = connection.cursor()
            cursor.execute("SELECT tags FROM relations WHERE id = %s", (self.id,))
            ret = cursor.fetchone()
            self._tags = ret[0] if ret is not None else {}
        return self._tags

    def distance_km(self):
        tags = self.tags()
        dist = tags.get('distance', tags.get('length'))
        return None if dist is None else util.convert_to_km(dist)


    def subroutes(self, locale=None):
        """Returns parent routes of the relation as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT id, name, intnames FROM routes
                          WHERE id IN 
                          (SELECT child FROM hierarchy
                           WHERE parent = %s AND depth = 2)""", locale)


    def superroutes(self, locale=None):
        """Returns parent routes of the relation as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT id, name, intnames FROM routes
                          WHERE id IN 
                          (SELECT parent FROM hierarchy
                           WHERE child = %s AND depth = 2)""", locale)


    def _route_list(self, query, locale=None):
        """Returns parent routes of the relation as
           a list of triples (id, name, intnames)
        """
        cursor = connection.cursor()
        cursor.execute(query, (self.id,))
        ret = []
        for rel in cursor:
            info = { 'id' : rel[0] }
            if locale in rel[2]:
                info['name'] = rel[2][locale]
                info['origname'] = rel[1]
            else:
                info['name'] = rel[1]
            ret.append(info)
        return ret


    class Meta:
        db_table = u'routes'
        db_tablespace = u'cycling'

class CyclingSegments(models.Model):
    """Styling information for default style.
    """
    
    id = cfields.BigIntegerField(primary_key=True)
    spnt = cfields.BigIntegerField()
    epnt = cfields.BigIntegerField()
    ways = cfields.BigIntArrayField()
    rels = cfields.BigIntArrayField()
    geom = models.LineStringField(srid=900913)

    objects = models.GeoManager()

    class Meta:
        db_table = u'segments'

class CyclingDefStyle(models.Model):
    """Styling information for default style.
    """
    
    id = cfields.BigIntegerField(primary_key=True)

    objects = models.GeoManager()

