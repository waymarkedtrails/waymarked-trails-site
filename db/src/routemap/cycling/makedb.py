#!/usr/bin/python
# This file is part of Lonvia's cycling Map
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
Create, import and modify cycling relation tables.

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
import guideposts as hposts
import psycopg2.extensions

class cyclingStyleMaker:

    def __init__(self, dba):
        db = postgisconn.connect(dba)
        self.segments = hrel.Segments(db)
        self.hierarchy =  hrel.Hierarchies(db)
        self.routes =  hrel.Routes(db)
        self.style = hstyle.cyclingStyleDefault(db)
        self.update = hrel.UpdatedGeometries(db)
        self.networknode = hposts.NetworkNodes(db)
        self.db = db

    def create_tables(self):
        self.segments.create()
        self.hierarchy.create()
        self.routes.create()
        self.style.create()
        self.update.create()
        self.networknode.create()


    def import_data(self):
        print datetime.now(),"Importing segments..."
        self.segments.construct()
        print datetime.now(),"Importing hierarchies..."
        self.hierarchy.construct()
        print datetime.now(),"Importing routes..."
        self.routes.construct()
        print datetime.now(),"Importing style..."
        self.style.truncate()
        self.style.synchronize(0, None)
        print datetime.now(),"Importing network nodes..."
        self.networknode.construct()

    def update_data(self):
        self.update.truncate()
        # Commit here, so that the map is not updated
        # when something goes wrong afterwards.
        self.db.commit()
        print datetime.now(),"Updating segments..."
        self.segments.update(self.update)
        print datetime.now(),"Updating hierarchies..."
        self.hierarchy.construct()
        print datetime.now(),"Updating routes..."
        self.routes.update()
        print datetime.now(),"Updating style..."
        self.style.synchronize(
                self.segments.first_new_id, self.update)
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
        hm = cyclingStyleMaker('dbname=%s user=%s password=%s' % (options.database, options.username, options.password))
        hm.execute_action(args[0])
        hm.finalize()
