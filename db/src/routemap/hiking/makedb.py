#!/usr/bin/python
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

""" 
Create, import and modify hiking relation tables.

<action> can be one of the following:
  create  - discard any existing tables and create new empty ones
  import  - truncate all tables and create new content from the Osmosis tables
  update  - update all tables (according to information in the *_changeset tables)
"""

from optparse import OptionParser
from datetime import datetime

import osgende.common.postgisconn as postgisconn
import relations as hrel
import style_default as hstyle
import administrative as hadmin
import guideposts as hposts
import psycopg2.extensions

class HikingStyleMaker:

    def __init__(self, dba):
        db = postgisconn.connect(dba)
        self.countries = hadmin.CountryTable(db)
        self.segments = hrel.Segments(db, self.countries)
        self.hierarchy =  hrel.Hierarchies(db)
        self.routes =  hrel.Routes(db)
        self.style = hstyle.HikingStyleDefault(db)
        self.update = hrel.UpdatedGeometries(db)
        self.guidepost = hposts.GuidePosts(db)
        self.networknode = hposts.NetworkNodes(db)
        self.db = db

    def create_tables(self):
        self.countries.create()
        self.db.commit()
        self.segments.create()
        self.hierarchy.create()
        self.routes.create()
        self.style.create()
        self.update.create()
        self.guidepost.create()
        self.networknode.create()


    def import_data(self):
        print datetime.now(),"Importing countries..."
        self.countries.construct()
        print datetime.now(),"Importing segments..."
        self.segments.construct()
        print datetime.now(),"Importing hierarchies..."
        self.hierarchy.construct()
        print datetime.now(),"Importing routes..."
        self.routes.construct()
        print datetime.now(),"Importing style..."
        self.style.synchronize(0, None)
        print datetime.now(),"Importing guideposts..."
        self.guidepost.construct()
        print datetime.now(),"Importing network nodes..."
        self.networknode.construct()

    def update_data(self):
        self.update.truncate()
        # Commit here so that in case someyhing goes wrong
        # later, the map tiles are simply not touched
        self.db.commit()
        print datetime.now(),"Updating countries..."
        #self.countries.update()
        print datetime.now(),"Updating segments..."
        self.segments.update(self.update)
        print datetime.now(),"Updating hierarchies..."
        self.hierarchy.construct()
        print datetime.now(),"Updating routes..."
        self.routes.update()
        print datetime.now(),"Updating style..."
        self.style.synchronize(
                self.segments.first_new_id, self.update)
        print datetime.now(),"Updating guideposts..."
        self.guidepost.update()
        print datetime.now(),"Updating network nodes..."
        self.networknode.update()

    def finalize(self):
        cur = psycopg2.extensions.connection.cursor(self.db)
        cur.execute("ANALYSE")
        self.db.commit()

    # function mapping
    functions = { 'create' : create_tables,
              'import' : import_data,
              'update' : update_data,
            }

    def execute_action(self, action):
        self.functions[action](self)

if __name__ == "__main__":

    # fun with command line options
    parser = OptionParser(description=__doc__,
                          usage='%prog [options] <action>')
    parser.add_option('-d', action='store', dest='database', default='planet',
                       help='name of database')
    parser.add_option('-u', action='store', dest='username', default='osm',
                       help='database user')
    parser.add_option('-p', action='store', dest='password', default='',
                       help='password for database')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
    else:
        hm = HikingStyleMaker('dbname=%s user=%s password=%s' % (options.database, options.username, options.password))
        hm.execute_action(args[0])
        hm.finalize()
