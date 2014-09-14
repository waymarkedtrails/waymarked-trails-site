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
"""The default style of the map.
"""

from osgende.common.postgisconn import PGTable
import conf

class RidingStyleDefault(PGTable):
    """Table saving style information for the default style for each
       way segment.

       The class table describes the classification. Each byte stands for
       one class: iwn, nwn rwn, lwn. 0x40 is used for standard classification
       and values above below for ways that need a slightly different
       handling in style. 

       The id column is linked to the segment table via a reference
       relation that also takes care of deleting rows that are no longer
       needed. 'synchronize' then takes care of newly added segments.
    """

    def __init__(self,db):
        PGTable.__init__(self, db,
                         name=conf.DB_DEFAULT_STYLE_TABLE)

    def create(self):
        self.layout((
               ("id",         "bigint PRIMARY KEY REFERENCES %s ON DELETE CASCADE" 
                                % conf.DB_SEGMENT_TABLE.fullname) ,
               ("class",      "int"),
               ("network",    "varchar(2)"),
               ("style",      "int"),
               ("inrshields", "text[]"),
               ("allshields", "text[]")
               ))
        self.add_geometry_column("geom", conf.DB_SRID, 'GEOMETRY', with_index=True)
        self.add_geometry_column("geom100", conf.DB_SRID, 'GEOMETRY', with_index=True)
                        
    def construct(self):
        self.synchronize(0)


    def update(self):
        raise Exception('Unimplemented')

    def synchronize(self, firstid, uptable):
        """Creates style information for all segments with an id greater or
           equal 'firstid'.
        """
        # cache routing information, so we don't have to get it every time
        self.routes = {}

        # field hash
        self.fields = {}

        cur = self.db.select("""SELECT seg.id, array_agg(h.parent) as rels
                               FROM %s h, %s seg
                              WHERE h.child = ANY(seg.rels)
                                AND seg.id >= %%s
                              GROUP BY seg.id""" 
                          % (  conf.DB_HIERARCHY_TABLE.fullname,
                               conf.DB_SEGMENT_TABLE.fullname),
                          (firstid,))
                       
        for seg in cur:
            self._update_segment_style(seg)
            
        if uptable is not None:
            self.db.query("""INSERT INTO %s (action, geom)
                          SELECT 'C', geom100 FROM %s WHERE id >= %%s
                       """ % (uptable.table, self.table), (firstid,))

        # and copy geometries
        self.db.query("""UPDATE %s d SET geom=ST_Simplify(s.geom, 1), 
                                      geom100=ST_Simplify(s.geom, 100)
                      FROM %s s WHERE s.id = d.id AND s.id >= %%s
                   """ % (self.table, conf.DB_SEGMENT_TABLE.fullname),
                   (firstid, ))  


        # now synchronize all segments where a hierarchical relation has changed
        if firstid > 0:
            cur = self.db.select("""SELECT segs.id, array_agg(h.parent) as rels
                             FROM %s h,
                             (SELECT DISTINCT seg.id, seg.rels, seg.geom
                               FROM %s h, %s seg
                              WHERE h.child = ANY(seg.rels)
                                AND h.depth > 1
                                AND seg.id < %%s
                                AND h.parent IN 
                                 (SELECT id FROM relation_changeset)
                             ) as segs
                             WHERE h.child = ANY(segs.rels)
                             GROUP BY id"""
                            % (  conf.DB_HIERARCHY_TABLE.fullname,
                                 conf.DB_HIERARCHY_TABLE.fullname,
                                 conf.DB_SEGMENT_TABLE.fullname),
                          (firstid,))

            for seg in cur:
                self._update_segment_style(seg, update=True)
                if uptable is not None:
                    self.db.query("""INSERT INTO %s (action,geom)
                                  SELECT 'M', geom100 FROM %s
                                  WHERE id = %%s""" 
                                  % (uptable.table, self.table), 
                                  (seg['id'],))


    def _update_segment_style(self, seg, update=False): 
        seginfo = _SegmentInfo()
        for rel in seg['rels']:
            if rel in self.routes:
                relinfo = self.routes[rel]
            else:
                c2 = self.db.select("SELECT * FROM %s WHERE id = %%s"
                                   % (conf.DB_ROUTE_TABLE.fullname),
                                  (rel,))
                relinfo = c2.fetchone()
                self.routes[rel] = relinfo

            if relinfo is None:
                print "Warning: no information for relation",rel
            else:
                seginfo.append_style(relinfo)

        if update:
            self.update_values(seginfo.make_db_fields(), 
                               'id = %s', (seg['id'],))
        else:
            self.insert_values(seginfo.make_db_fields(seg['id']))


class _SegmentInfo:
    classvalues = [ 0x40000000, 0x400000, 0x4000, 0x40]

    def __init__(self):
        self.network = None
        self.style = 0
        self.classification = 0
        self.inrshields = []
        self.allshields = []

    def append_style(self, relinfo):
        if not relinfo['top']:
            return

        level = min(relinfo['level'] / 10, 3)
        classification = self.classvalues[level]
        self.classification |= classification

        if relinfo['symbol'] is not None:
            if classification >= 0x4000 and len(self.inrshields) < 5:
                self.inrshields.append(relinfo['symbol'])
            if len(self.allshields) < 5:
                self.allshields.append(relinfo['symbol'])

    def make_db_fields(self, id=None):
        fields = {}
        if id is not None:
            fields['id'] = id
        if self.network is not None:
            fields['network'] = self.network
        fields['style'] = self.style
        fields['class'] = self.classification
        fields['inrshields'] = self.inrshields
        fields['allshields'] = self.allshields

        return fields
