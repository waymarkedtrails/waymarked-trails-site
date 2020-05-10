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
import sqlalchemy as sa
from sqlalchemy.engine.url import URL

from config import defaults as config

def prepare(options):
    dba = URL('postgresql', username=options.username,
                  password=options.password, database=options.database)
    engine = sa.create_engine(dba, echo=options.echo_sql)
    """ Creates the necessary indices on a new DB."""
    #engine.execute("CREATE INDEX idx_relation_member ON relation_members USING btree (member_id, member_type)")
    #engine.execute("idx_nodes_tags ON nodes USING GIN(tags)")
    #engine.execute("idx_ways_tags ON ways USING GIN(tags)")
    #engine.execute("idx_relations_tags ON relations USING GIN(tags)")
    engine.execute("CREATE INDEX idx_node_changeset on node_changeset(id)")

    engine.execute("ANALYSE")
    engine.execute("CREATE EXTENSION pg_trgm")

def handle_base_db(mapdb_class, options):
    if options.action == 'prepare':
        prepare(options)
        return 0

    if options.action in ('import', 'update'):
        args = ['osgende-import', '-d', options.database, '-r', options.replication]
        if options.username:
            args.extend(('-u', options.username))
        if options.password:
            args.extend(('-p', options.password))
        if options.nodestore:
            args.extend(('-n', options.nodestore))
        if options.action == 'import':
            args.extend(('-i', '-c'))
            args.append(options.input_file)
        else:
            mapdb = mapdb_class(options)
            with mapdb.engine.begin() as conn:
                basemap_seq = mapdb.status.get_sequence(conn, 'base')
                oldest = mapdb.status.get_min_sequence(conn)
            if basemap_seq > oldest:
                print("Derived maps not yet updated. Skipping base map update.")
                exit(0)
            args.extend(('-S', str(options.diff_size*1024)))

        print('osgende-import', args)
        os.execvp('osgende-import', args)
    else:
        print("Unknown action '%s' for DB." % options.action)

    return 1

def handle_route_db(mapname, mapdb_class, options):
    mapdb = mapdb_class(options)

    with mapdb.engine.begin() as conn:
        basemap_seq = mapdb.status.get_sequence(conn, 'base')
        map_date = mapdb.status.get_sequence(conn, mapname)

    if options.action == 'update':
        if map_date is None:
            print("Map not available.")
            exit(1)

        if basemap_seq <= map_date:
            print("Data already up-to-date. Skipping.")
            exit(0)

    if options.action == 'import':
        # make sure to delete traces of previous imports
        with mapdb.engine.begin() as conn:
            mapdb.status.remove_status(conn, mapname)

        mapdb.construct()
    else:
        getattr(mapdb, options.action)()

    if options.action in ('import', 'update'):
        with mapdb.engine.begin() as conn:
            mapdb.status.set_status_from(conn, mapname, 'base')

    mapdb.finalize(options.action == 'update')

if __name__ == "__main__":
    # fun with command line options
    parser = ArgumentParser(usage='%(prog)s [options] <routemap> <action>',
                            formatter_class=RawTextHelpFormatter,
                            description=__doc__)
    parser.add_argument('-d', action='store', dest='database',
                        default=config.DB_NAME,
                        help='name of database')
    parser.add_argument('-u', action='store', dest='username',
                        default=config.DB_USER,
                        help='database user')
    parser.add_argument('-U', action='store', dest='ro_user',
                        default=config.DB_RO_USER,
                        help='read-only database user')
    parser.add_argument('-p', action='store', dest='password',
                        default=config.DB_PASSWORD,
                        help='password for database')
    parser.add_argument('-j', action='store', dest='numthreads', default=1,
                        type=int, help='number of parallel threads to use')
    parser.add_argument('-n', action='store', dest='nodestore',
                        default=config.DB_NODESTORE,
                        help='location of nodestore')
    parser.add_argument('-r', action='store', dest='replication',
                        default=config.REPLICATION_URL,
                        help='URL of OSM data replication service to use')
    parser.add_argument('-S', action='store', dest='diff_size',
                        type=int, default=config.REPLICATION_SIZE)
    parser.add_argument('-v', '--verbose', action="store_const", dest="loglevel",
                        const=logging.DEBUG, default=logging.INFO,
                        help="Enable debug output")
    parser.add_argument('-V', '--verbose-sql', action='store_true', dest="echo_sql",
                        help="Enable output of SQL statements")
    parser.add_argument('-f', action='store', dest='input_file', default=None,
                        help='name of input file ("db import" only)')
    parser.add_argument('routemap',
                        help='name of map (available: TODO) or db for the OSM data DB')
    parser.add_argument('action',
                        help=dedent("""\
                        one of the following:
                          prepare  - create the necessary indexes on a new osgende DB
                                     (routemap must be 'db')
                          create   - discard any existing tables and create new empty ones
                          import   - truncate all tables and create new content from the osm data tables
                                     (with db: create a new database and import osm data tables)
                          dataview - create or update data_view table containing all visible
                                     geometries (needed for tile creation)
                          update   - update all tables (from the *_changeset tables)
                                     (with db: update from given replication service)
                          mkshield - force remaking of all shield bitmaps"""))

    options = parser.parse_args()

    # setup logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=options.loglevel,
                        datefmt='%y-%m-%d %H:%M:%S')

    mapname = 'hiking' if options.routemap == 'db' else options.routemap
    os.environ['ROUTEMAPDB_CONF_MODULE'] = 'maps.%s' % mapname

    try:
        from db import conf
    except ImportError:
        print("Cannot find route map named '%s'." % options.routemap)
        raise

    try:
        mapdb_pkg = 'db.%s_maptype' % conf.get('MAPTYPE')
        __import__(mapdb_pkg)
        mapdb_class = getattr(sys.modules[mapdb_pkg], 'DB')
    except ImportError:
        print("Unknown map type '%s'." % conf.get('MAPTYPE'))
        raise

    # Update of the base DB.
    if options.routemap == 'db':
        exit(handle_base_db(mapdb_class, options))

    handle_route_db(mapname, mapdb_class, options)
