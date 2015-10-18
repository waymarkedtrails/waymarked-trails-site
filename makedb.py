#!/usr/bin/python3
# This file is part of the Waymarked Trails Map Project
# Copyright (C) 2011-2015 Sarah Hoffmann
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
"""

from argparse import ArgumentParser, RawTextHelpFormatter
from textwrap import dedent
import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

def prepare(options):
    dba = URL('postgresql', username=options.username,
                  password=options.password, database=options.database)
    engine = create_engine(dba, echo=options.echo_sql)
    """ Creates the necessary indices on a new DB."""
    engine.execute("CREATE INDEX idx_relation_member ON relation_members USING btree (member_id, member_type)")
    #engine.execute("idx_nodes_tags ON nodes USING GIN(tags)")
    #engine.execute("idx_ways_tags ON ways USING GIN(tags)")
    #engine.execute("idx_relations_tags ON relations USING GIN(tags)")

    engine.execute("ANALYSE")
    engine.execute("CREATE EXTENSION pg_trgm")


if __name__ == "__main__":
    # fun with command line options
    parser = ArgumentParser(usage='%(prog)s [options] <routemap> <action>',
                            formatter_class=RawTextHelpFormatter,
                            description=__doc__)
    parser.add_argument('-d', action='store', dest='database', default='planet',
                       help='name of database')
    parser.add_argument('-u', action='store', dest='username', default=None,
                       help='database user')
    parser.add_argument('-U', action='store', dest='ro_user', default=None,
                       help='read-only database user')
    parser.add_argument('-p', action='store', dest='password', default=None,
                       help='password for database')
    parser.add_argument('-j', action='store', dest='numthreads', default=None,
                       type=int, help='number of parallel threads to use')
    parser.add_argument('-n', action='store', dest='nodestore', default=None,
                       help='location of nodestore')
    parser.add_argument('-v', '--verbose', action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO,
                        help="Enable debug output")
    parser.add_argument('-V', '--verbose-sql', action='store_true', dest="echo_sql",
                        help="Enable output of SQL statements")
    parser.add_argument('routemap',
                        help='name of map (available: TODO)')
    parser.add_argument('action',
                        help=dedent("""\
                        one of the following:
                          prepare   - create the necessary indexes on a new osgende DB
                                      (routemap must be 'db')
                          create    - discard any existing tables and create new empty ones
                          import    - truncate all tables and create new content from the osm data tables
                          update    - update all tables (from the *_changeset tables)
                          mkshields - force remaking of all shield bitmaps
                          restyle   - recompute the style tables"""))

    options = parser.parse_args()

    # setup logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=options.loglevel,
                        datefmt='%y-%m-%d %H:%M:%S')

    if options.routemap == 'db':
        if options.action == 'prepare':
            prepare(options)
            exit(0)
        else:
            print("Unknown action '%s' for DB." % options.action)
            exit(1)

    os.environ['ROUTEMAPDB_CONF_MODULE'] = 'maps.%s' % options.routemap

    try:
        from db import conf
    except ImportError:
        print("Cannot find route map named '%s'." % options.routemap)
        raise

    try:
        mapdb_pkg = 'db.%s' % conf.get('MAPTYPE')
        __import__(mapdb_pkg)
        mapdb_class = getattr(sys.modules[mapdb_pkg], 'DB')
    except ImportError:
        print("Unknown map type '%s'." % conf.MAPTYPE)
        raise

    mapdb = mapdb_class(options)

    if options.action == 'import':
        getattr(mapdb, 'construct')()
    else:
        getattr(mapdb, options.action)()
    mapdb.finalize(options.action == 'update')
