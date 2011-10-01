# vim: set fileencoding=utf-8
# This file is part of Lonvia's Hiking Map
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
""" Tables storing information derived from the hiking relations.
    
    The hiking net is saved in Segments. A segment is strictly linear and goes from 
    one intersection to the next, with no Segments crossing or touching it. A Segment
    can be composed of multiple OSM ways (or parts thereof in the case where there is
    an intersection in the middle of the way) but all ways must be members of exactly
    the same relation set and not change role within one relation.

    Intersections are OSM nodes that are start and end points of Segments. At the moment
    this is a purely virtual concept, there is no table storing Intersections.

    Routes describe the properties of the actual hiking relations. There is one route
    per relation.

    Route hierarchy describes the relation between the routes.

    For creation and update, order of operation is as follows:

    1. update of geometry and admin info for Segments
    2. update hierarchy
    3. update of Route table (note that some properties of a route may
       depend on its location, so the segments of each route must be known
       first)

    The actualy rendering information is computed seperately. This allows to use
    different rendering styles on the same table. For the moment there is only
    style_default.py.
"""

import os.path

from osgende import OsmosisSubTable,RelationHierarchy, RelationSegments
from osgende.common.postgisconn import PGTable
import conf
import symbols

class Hierarchies(RelationHierarchy):
    """Table saving the relation between the relations.

       This is a simple relation hierarchy table. For more information see
       :class:`osmtables.RelationHierarchy`.
    """

    def __init__(self, db):
        RelationHierarchy.__init__(self, db,
                    name=conf.DB_HIERARCHY_TABLE,
                    subset="""SELECT id FROM relations
                              WHERE %s""" % (conf.TAGS_ROUTE_SUBSET))


class UpdatedGeometries(PGTable):
    """Table that stores just a list of geometries that have been changed
       in the course of an update.

       This table contains created and modified geometries as well as
       deleted ones.
    """

    def __init__(self, db):
        PGTable.__init__(self, db, conf.DB_CHANGE_TABLE)

    def create(self):
        PGTable.create(self, "(action  char(1))")
        self.add_geometry_column("geom", "900913", 'GEOMETRY', with_index=True)

    def add(self, geom, action='M'):
        self.query("INSERT INTO %s (action, geom) VALUES (%%s, %%s)"
                     % (self.table), (action, geom))

class Segments(RelationSegments):
    """ Segments are the basic way system of the network.

        Segments require an up-to-date country table. Note, however, that the
        country of the Segment is only calculated when it is updated. If a segment
        changes a country due to movement of a boundary, this will go undetected.
    """
    def __init__(self, db, country):
        RelationSegments.__init__(self, db, conf.DB_SEGMENT_TABLE,
                         conf.TAGS_ROUTE_SUBSET,
                         country_table=country,
                         country_column='code')


class Routes(OsmosisSubTable):
    """Preprocessed information about the hiking routes.

       It contains the following fields:

       * 'name' - the default name, generally taken from name-tag
          however, if the name is entirely in non-latin symbols,
          name:en is prefered if existing
       * 'intname' - collection of translated names
       * 'symbol' - unique name of the computed shield to use
       * 'country' - coutry the route is mainly in (in terms of
                     numbers of sections, TODO check this heuristic)
       * 'network' - special network it belongs to,
                     may affect rendering, default is ''
       * 'level' - importance in network with 0 being the most important
       * 'top' - if false then route constitutes only a subsection of
                 another route, check hierarchy table for potential parents
    """

    def __init__(self, db):
        OsmosisSubTable.__init__(self, db, "relation", 
                conf.DB_ROUTE_TABLE, conf.TAGS_ROUTE_SUBSET)

    def create(self):
        PGTable.create(self,
                    """(id       bigint PRIMARY KEY,
                        name     text,
                        intnames hstore,
                        symbol   text,
                        country  char(3),
                        network  varchar(2),
                        level    int,
                        top      boolean
                       )""")
        self.add_geometry_column("geom", "900913", 'GEOMETRY', with_index=True)
        self.query("CREATE INDEX route_iname ON %s USING btree(upper(name))" % self.table)

    def init_update(self):
        self.prepare("get_route_geometry(bigint)",
                     """SELECT ST_LineMerge(ST_Collect(geom))
                        FROM %s 
                        WHERE rels && ARRAY(SELECT child FROM %s
                                            WHERE $1 = parent)"""
                        % (conf.DB_SEGMENT_TABLE.fullname,
                           conf.DB_HIERARCHY_TABLE.fullname))
        self.prepare("get_route_top(bigint, varchar(2))",
                     """SELECT count(*) FROM %s h, relations r
                                 WHERE h.child = $1 AND r.id = h.parent
                                   AND h.depth = 2
                                   AND r.tags->'network' = $2
                              """ % (conf.DB_HIERARCHY_TABLE.fullname))
        self.prepare("get_route_country(bigint)",
                     """SELECT country, count(*) 
                        FROM %s s, %s h
                        WHERE $1 = h.parent AND
                              h.child = ANY(rels)
                        GROUP BY country ORDER BY count
                        LIMIT 1""" % (conf.DB_SEGMENT_TABLE.fullname,
                                      conf.DB_HIERARCHY_TABLE.fullname))


    def finish_update(self):
        self.deallocate("get_route_geometry")
        self.deallocate("get_route_top")
        self.deallocate("get_route_country")

    def transform_tags(self, osmid, tags):
        outtags = { 'intnames' : {}, 
                    'level' : 35, 
                    'network' : '', 
                    'top' : None}

        # default treatment of tags
        for (k,v) in tags.iteritems():
            if k == 'name':
                outtags[k] = v
            elif k.startswith('name:'):
                outtags['intnames'][k[5:]] = v
            elif k == 'ref':
                if 'name' not in outtags:
                    outtags['name'] = '[%s]' % v
            elif k == 'network':
                if v == 'uk_ldp':
                    outtags['level'] = 10 if tags.get('operator', '') == 'National Trails' else 20
                else:
                    outtags['level'] = conf.TAGS_NETWORK_MAP.get(v, 35)
            elif k.startswith('kct_'):
                outtags['network'] = 'CT'
                if 'network' not in tags and tags[k] == 'major':
                    outtags['level'] = 11 if k[4:] == 'red' else 21
                    

        # find out the country
        cntry = self.select_one("EXECUTE get_route_country(%s)", (osmid,))
        if cntry is not None:
            cntry = cntry.strip().lower()

        # Region-specific tagging:

        # in the UK slightly downgrade nwns (to distinguish them from National Trails)
        if cntry == 'gb' and tags.get('network', '') == 'nwn':
            outtags['level'] = 11

        # find Swiss hiking network
        if cntry == 'ch' and tags.get('network', '') == 'lwn':
            ot = tags.get('osmc:symbol', '')
            if ot.startswith('yellow:'):
                outtags['network'] = 'CH'
                outtags['level'] = 31
            if ot.startswith('red:'):
                outtags['network'] = 'CH'
                outtags['level'] = 32
            if ot.startswith('blue:'):
                outtags['network'] = 'CH'
                outtags['level'] = 33

        # Fränkischer Albverein (around Nürnberg)
        #  too extensive regional network, so we need to downgrade later
        if tags.get('operator') == u'Fränkischer Albverein':
            outtags['network'] = 'FA'
            
        outtags['symbol'] = self.get_symbol(outtags['level'], cntry, tags)
        outtags['country'] = cntry

        if 'name'not in outtags:
            outtags['name'] = '(%s)' % osmid

        if outtags['top'] is None:
            if 'network' in tags:
                top = self.select_one("EXECUTE get_route_top(%s, %s)",
                              (osmid, tags['network']))
                outtags['top'] = True if (top == 0) else False
            else:
                outtags['top'] = True

        # finally: compute the geometry
        outtags['geom'] = self.select_one("EXECUTE get_route_geometry(%s)", (osmid,))

        return outtags


    def get_symbol(self, level, cntry, tags):
        """Determine the symbol to use for the way and make sure
           that there is a bitmap in the filesystem.
        """

        sym = symbols.HikingSymbolDescriptor.make_symbol(tags, cntry, level)

        if sym is None:
            return None

        symid = sym.get_id()

        symfn = os.path.join(conf.WEB_SYMBOLDIR, "%s.png" % symid)

        if not os.path.isfile(symfn):
            sym.write_image(symfn)

        return symid

