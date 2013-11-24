# vim: set fileencoding=utf-8
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
from collections import defaultdict

import osgende
import conf
import routemap.common.symbols as symbols
import routemap.common.clearcache as clearcache
import shapely.ops as sops

symboltypes = (
            symbols.SlopeSymbol,
            symbols.NordicSymbol,
        )


class Ways(osgende.Ways):
    """Preprocessed information about the hiking routes.

       It contains the following fields:

       * 'name' - the default name, generally taken from piste:name-tag
       * 'intname' - collection of translated names
       * 'symbol' - unique name of the computed shield to use
       * 'difficulty' - piste:difficulty of the slope if available
       * 'type' - piste:type
    """
    srid = conf.DB_SRID

    def __init__(self, db, segtab, where, uptable = None):
        osgende.Ways.__init__(self, db, 
                segtab, where, uptable)
        self.geometry_column = 'geom'

    def create(self):
        layout = (  ('name',         'text'),
                    ('intnames',     'hstore'),
                    ('symbol',       'text')  )
        layout += tuple((k, 'boolean') for k in conf.TAGS_DIFFICULTY_MAP.keys())
        layout += tuple((k, 'boolean') for k in conf.TAGS_PISTETYPE_MAP.keys())

        self.layout(layout)

        self.db.query("CREATE INDEX way_iname ON %s USING btree(upper(name))" % self.table)

    def transform_tags(self, osmid, tags):
        #print "Processing", osmid
        outtags = { 'intnames'   : {}, }
        for k in conf.TAGS_DIFFICULTY_MAP.keys():
            outtags[k] = None
        for k in conf.TAGS_PISTETYPE_MAP.keys():
            outtags[k] = None

        difficulty = 0

        # default treatment of tags
        if tags.has_key('piste:name'):
            outtags['name'] = tags['piste:name']
        elif tags.has_key('piste:ref'):
            outtags['name'] = '[%s]' % tags['piste:ref']
        elif tags.has_key('name'):
            outtags['name'] = tags['name']
        elif tags.has_key('ref'):
            outtags['name'] = '[%s]' % tags['ref']
        else:
            outtags['name'] = '(%s)' % osmid


        for (k,v) in tags.iteritems():
            if k == 'piste:difficulty':
                if v in conf.TAGS_DIFFICULTY_MAP.keys():
                    outtags[v] = True
                    difficulty = conf.TAGS_DIFFICULTY_MAP[v]
            if k == 'piste:type':
                if v in conf.TAGS_PISTETYPE_MAP.keys():
                    outtags[v] = True
            if k.startswith('piste:name:'):
                outtags['intnames'][k[11:]] = v
                    
        outtags['symbol'] = symbols.get_symbol(difficulty, None, tags, symboltypes)

        return outtags
