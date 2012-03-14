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

from django.contrib.gis.db import models
import routemap.util.customfields as cfields
from django.db import connection, transaction
import routemap.util.tagformat as tagformat

class RouteTableModel(models.Model):
    """Generalized model for table with route information.
    """

    # only the fields required by the generalized functions
    # are added here
    id = cfields.BigIntegerField(primary_key=True)
    name = models.TextField(null=True)
    intnames = cfields.HStoreField()
    geom = models.GeometryField(srid=900913)

    def tags(self):
        if not hasattr(self,'_tags'):
            cursor = connection.cursor()
            cursor.execute("SELECT tags FROM relations WHERE id = %s", (self.id,))
            ret = cursor.fetchone()
            self._tags = ret[0] if ret is not None else None
        return self._tags
    

    def get_formatted_tags(self, locales):
        """Return a transformed taglist that localizes tags
           according to the given language preferences and
           standardize some other tags.

           Current list of standardized tags:
            website, wikipedia
        """
        ret = self.make_localized_tags(locales)
        tags = self.tags()

        # special case wikipedia, standard is :en
        if 'wikipedia' not in ret and 'wikipedia:en' in tags:
            ret['wikipedia'] = tags['wikipedia:en']

        # make a correct website link
        if 'url' in ret:
            ret['website'] = ret['url']

        if 'website' in ret:
            if ret['website'].find(':') < 0:
                ret['website'] = 'http://%s' % ( ret['website'])

        return ret

    def make_localized_tags(self, locales):
        """Returns the list of tags localized according to the
           language preferences given in locales.

           locales must be a hash where the keys are language
           codes and the values are weights.
        """
        ret = {}
        tagweights = {}
        for k,v in self.tags().iteritems():
            idx = k.find(':')
            if idx > 0 and k[idx+1:] in locales:
                outkey = k[:idx]
                w = locales[k[idx+1:]]
                if outkey not in ret or w > tagweights[outkey]:
                    ret[outkey] = v
                    tagweights[outkey] = w
            else:
                if k not in ret:
                    ret[k] = v
                    tagweights[k] = -1000.0
        return ret

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

    def distance_km(self):
        tags = self.tags()
        dist = tags.get('distance', tags.get('length'))
        return tagformat.convert_to_km(dist)


    def subroutes(self, locales=[]):
        """Returns parent routes of the relation as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT id, name, intnames FROM routes
                          WHERE id IN 
                          (SELECT child FROM hierarchy
                           WHERE parent = %s AND depth = 2)""", locales)


    def superroutes(self, locales=[]):
        """Returns parent routes of the relation as
           a list of triples (id, name, intnames)
        """
        return self._route_list("""SELECT id, name, intnames FROM routes
                          WHERE id IN 
                          (SELECT parent FROM hierarchy
                           WHERE child = %s AND depth = 2)""", locales)


    def _route_list(self, query, locales=[]):
        """Returns parent routes of the relation as a dict with 
            the fields 'id', 'name' and, in case the name has been
            localized 'origname' with the original name tag.
        """
        cursor = connection.cursor()
        cursor.execute(query, (self.id,))
        ret = []
        for rel in cursor:
            info = { 'id' : rel[0] }
            for locale in locales:
                if locale in rel[2]:
                    info['name'] = rel[2][locale]
                    info['origname'] = rel[1]
                break
            else:
                info['name'] = rel[1]
            ret.append(info)
        return ret


    class Meta:
        abstract = True
