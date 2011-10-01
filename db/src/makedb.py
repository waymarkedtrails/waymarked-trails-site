#!/usr/bin/python
# This file is part of Lonvia's Route Maps Project
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
Create, import and modify tables for a route map.

Usage: python makedb.py <routemap> <action>

<action> can be one of the following:
  create  - discard any existing tables and create new empty ones
  import  - truncate all tables and create new content from the Osmosis tables
  update  - update all tables (according to information in the *_changeset tables)
"""

from optparse import OptionParser
import sys

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

    if len(args) != 2:
        parser.print_help()
        exit(-1)
    
    try:
        modname = 'routemap.%s.db' % args[0]
        __import__(modname)
        dbmodule = sys.modules[modname]
    except ImportError:
        print "Cannot find route map named", args[0], "."
    mapdb = dbmodule.RouteMapDB('dbname=%s user=%s password=%s' % (options.database, options.username, options.password))
    mapdb.execute_action(args[1])
    mapdb.finalize(args[1] == 'update')
