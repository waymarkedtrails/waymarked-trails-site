# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2012 Sarah Hoffmann
#               2012-2013 Michael Spreng
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

from django.contrib.gis.db import models
import routemap.util.customfields as cfields
from django.db import connection, transaction
from django.conf import settings

from osgende.tags import TagStore

class RouteTableModel(models.Model):
    """Generalized model for table with route information.
    """

    # only the fields required by the generalized functions
    # are added here
    id = cfields.BigIntegerField(primary_key=True)
    name = models.TextField(null=True)
    intnames = cfields.HStoreField()
    geom = models.GeometryField(srid=settings.DATABASES['default']['SRID'])

    def tags(self):
        if not hasattr(self,'_tags'):
            cursor = connection.cursor()
            cursor.execute("SELECT tags FROM relations WHERE id = %s", (self.id,))
            ret = cursor.fetchone()
            self._tags = TagStore(ret[0] if ret is not None else {})
        return self._tags

    def localize_name(self, locstrings):
        for locstring in locstrings:
            if locstring in self.intnames:
                if not self.name == self.intnames[locstring]:
                    self.origname = self.name
                    self.name = self.intnames[locstring]
                return

        if self.name[0] == '(' and self.name[-1] == ')':
            t = self.tags()
            if 'note' in t:
                self.origname = t['note']

    def subroutes(self, locales=[]):
        """Returns child routes of the relation as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT r.id, r.name, r.intnames FROM routes r, relation_members m
                          WHERE m.relation_id = %s
                          AND m.member_id = r.id AND m.member_type='R'
                          ORDER BY m.sequence_id""", locales)


    def superroutes(self, locales=[]):
        """Returns parent routes of the relation as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT id, name, intnames FROM routes
                          WHERE id IN 
                          (SELECT parent FROM hierarchy
                           WHERE child = %s AND depth = 2)""", locales)


    def _route_list(self, query, locales=[], osm_type = None):
        """Returns parent / child routes of the relation as a dict with 
            the fields 'id', 'name' and, in case the name has been
            localized 'origname' with the original name tag.
        """
        cursor = connection.cursor()
        cursor.execute(query, (self.id,))
        ret = []
        for rel in cursor:
            info = { 'id' : rel[0], 'name' : rel[1] }
            if osm_type:
                info['id'] = osm_type + str(info['id'])
            for locale in locales:
                if locale in rel[2]:
                    if rel[2][locale] != rel[1]:
                        info['name'] = rel[2][locale]
                        info['origname'] = rel[1]
                    break
            ret.append(info)
        return ret

    def get_id(self):
        return str(self.id)

    class Meta:
        abstract = True



class CyclingRoutes(RouteTableModel):
    """Table with information about cycling routes.
    """

    symbol = models.TextField(null=True)
    level = models.IntegerField()
    top = models.BooleanField()

    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'cycling'


class HikingRoutes(RouteTableModel):
    """Table with information about hiking routes.
    """

    symbol = models.TextField(null=True)
    country = models.CharField(max_length=3, null=True)
    network = models.CharField(max_length=2, null=True)
    level = models.IntegerField()
    top = models.BooleanField()

    objects = models.GeoManager()
        
    class Meta:
        db_table = u'routes'
        db_tablespace = u'hiking'

class MtbRoutes(RouteTableModel):
    """Table with information about mountain biking routes.
    """

    symbol = models.TextField(null=True)
    level = models.IntegerField()
    top = models.BooleanField()
    
    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'mtbmap'
        
        
class SkatingRoutes(RouteTableModel):
    """Table with information about inline skating routes.
    """

    symbol = models.TextField(null=True)
    level = models.IntegerField()
    top = models.BooleanField()
    
    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'skating'
        
class RidingRoutes(RouteTableModel):
    """Table with information about riding routes.
    """

    symbol = models.TextField(null=True)
    level = models.IntegerField()
    top = models.BooleanField()

    objects = models.GeoManager()

    class Meta:
        db_table = u'routes'
        db_tablespace = u'riding'


class Slopes(RouteTableModel):
    """Table with information about slopemap routes.
    """

    symbol = models.TextField(null=True)
    downhill = models.BooleanField()
    nordic = models.BooleanField()
    sled = models.BooleanField()
    hike = models.BooleanField()
    sleigh = models.BooleanField()
    
    novice = models.BooleanField()
    easy = models.BooleanField()
    intermediate = models.BooleanField()
    advanced = models.BooleanField()
    expert = models.BooleanField()
    extreme = models.BooleanField()
    freeride = models.BooleanField()

    objects = models.GeoManager()

    osm_type = 'w'

    def subroutes(self, locales=[]):
        """
           ways do not have children. return empty list.
        """
        return []


    def superroutes(self, locales=[]):
        """Returns parent clusters of ways as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT virtual_id, name, intnames FROM slopeways, joined_slopeways
                          WHERE child = id AND id = %s""", locales, 'v')

    def tags(self):
        if not hasattr(self,'_tags'):
            cursor = connection.cursor()
            cursor.execute("SELECT tags FROM ways WHERE id = %s", (self.id,))
            ret = cursor.fetchone()
            self._tags = TagStore(ret[0] if ret is not None else {})
        return self._tags

    def get_id(self):
        return 'w' + str(self.id)

    class Meta:
        db_table = u'slopeways'
        db_tablespace = u'slopemap'

class JoinedWaysTableModel(models.Model):
    """Generalized model for table with joined way information.
    """

    # only the fields required by the generalized functions
    # are added here
    virtual_id = cfields.BigIntegerField()
    child = cfields.BigIntegerField(primary_key=True)

    def tags(self):
        if not hasattr(self,'_tags'):
            cursor = connection.cursor()
            cursor.execute("SELECT tags FROM ways WHERE id = %s", (self.child,))
            ret = cursor.fetchone()
            self._tags = TagStore(ret[0] if ret is not None else {})
        return self._tags

    def localize_name(self, locstrings):
        related_row = self._ways.objects.get(id=self.child)
        intnames = related_row.intnames
        name = related_row.name
        for locstring in locstrings:
            if locstring in intnames:
                if not name == intnames[locstring]:
                    self.origname = name
                    name = intnames[locstring]
                return

        if name[0] == '(' and name[-1] == ')':
            t = related_row.tags()
            if 'note' in t:
                self.origname = t['note']

    def subroutes(self, locales=[]):
        """Returns child routes of the joined way as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT id, name, intnames FROM slopeways, joined_slopeways
                          WHERE child = id AND virtual_id = %s""", locales, 'w')

    def superroutes(self, locales=[]):
        """
           there are no superroutes. Return empty list.
        """
        return []

    def _route_list(self, query, locales=[], osm_type = None):
        """Returns parent / child routes of the relation as a dict with
            the fields 'id', 'name' and, in case the name has been
            localized 'origname' with the original name tag.
        """
        cursor = connection.cursor()
        cursor.execute(query, (self.virtual_id,))
        ret = []
        for rel in cursor:
            info = { 'id' : rel[0], 'name' : rel[1] }
            if osm_type:
                info['id'] = osm_type + str(info['id'])
            for locale in locales:
                if locale in rel[2]:
                    if rel[2][locale] != rel[1]:
                        info['name'] = rel[2][locale]
                        info['origname'] = rel[1]
                    break
            ret.append(info)
        return ret

    def get_id(self):
        return 'v' + str(self.virtual_id)

    def symbol(self):
        related_row = self._ways.objects.get(id=self.child)
        return related_row.symbol

    def name(self):
        related_row = self._ways.objects.get(id=self.child)
        return related_row.name


    class Meta:
        abstract = True

class JoinedSlopes(JoinedWaysTableModel):

    _ways = Slopes

    osm_type = 'v'

    class Meta:
        db_table = u'joined_slopeways'
        db_tablespace = u'slopemap'

class SlopeRelations(RouteTableModel):
    """Table with information about slopemap routes.
    """

    symbol = models.TextField(null=True)
    downhill = models.BooleanField()
    nordic = models.BooleanField()
    sled = models.BooleanField()
    hike = models.BooleanField()
    sleigh = models.BooleanField()
    
    novice = models.BooleanField()
    easy = models.BooleanField()
    intermediate = models.BooleanField()
    advanced = models.BooleanField()
    expert = models.BooleanField()
    extreme = models.BooleanField()
    freeride = models.BooleanField()

    objects = models.GeoManager()

    osm_type = 'r'

    def tags(self):
        if not hasattr(self,'_tags'):
            cursor = connection.cursor()
            cursor.execute("SELECT tags FROM relations WHERE id = %s", (self.id,))
            ret = cursor.fetchone()
            self._tags = TagStore(ret[0] if ret is not None else {})
        return self._tags

    def get_id(self):
        return 'r' + str(self.id)

    class Meta:
        db_table = u'routes'
        db_tablespace = u'slopemap'

        
class SegmentTableModel(models.Model):
    """Segment table.
    """

    id = cfields.BigIntegerField(primary_key=True)
    nodes = cfields.BigIntArrayField()
    ways = cfields.BigIntArrayField()
    rels = cfields.BigIntArrayField()
    geom = models.GeometryField(srid=settings.DATABASES['default']['SRID'])

    class Meta:
        abstract = True


class HikingSegments(SegmentTableModel):
    country = models.CharField(max_length=2, null=True)
    objects = models.GeoManager()
        
    class Meta:
        db_table = u'segments'
        db_tablespace = u'hiking'

class CyclingSegments(SegmentTableModel):
    objects = models.GeoManager()
        
    class Meta:
        db_table = u'segments'
        db_tablespace = u'cycling'

class SkatingSegments(SegmentTableModel):
    objects = models.GeoManager()
        
    class Meta:
        db_table = u'segments'
        db_tablespace = u'skating'

class MtbSegments(SegmentTableModel):
    objects = models.GeoManager()
        
    class Meta:
        db_table = u'segments'
        db_tablespace = u'mtbmap'
