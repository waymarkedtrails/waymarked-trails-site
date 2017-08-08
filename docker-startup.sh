#!/bin/bash

i=1
MAXCOUNT=60
echo "Waiting for PostgreSQL to be running"
while [ $i -le $MAXCOUNT ]
do
  pg_isready -q && echo "PostgreSQL running" && break
  sleep 2
  i=$((i+1))
done
test $i -gt $MAXCOUNT && echo "Timeout while waiting for PostgreSQL to be running"

case "$1" in
import)
  psql -c "SELECT 1 FROM pg_database WHERE datname = 'planet';" | grep -q 1 && dropdb planet

  python3 makedb.py -j 4 -f data.osm.pbf db import
  python3 makedb.py db prepare

  cd  /tmp
  curl -s http://www.nominatim.org/data/country_grid.sql.gz > country_grid.sql.gz && \
    gunzip country_grid.sql.gz

  psql -d planet -c "DROP TABLE IF EXISTS country_osm_grid" && \
    psql -d planet -f country_grid.sql && \
    psql -d planet -c "ALTER TABLE country_osm_grid ADD COLUMN geom geometry(Geometry,3857)" && \
    psql -d planet -c "UPDATE country_osm_grid SET geom=ST_Transform(geometry, 3857)" && \
    psql -d planet -c "ALTER TABLE country_osm_grid DROP COLUMN geometry" && \
    rm -f country_grid.sql

  cd /waymarkedtrails
  python3 makedb.py hiking create
  python3 makedb.py hiking import
  ;;
waymarkedtrails)
  # patch nginx conf
  cat config/nginx.default > /etc/nginx/sites-available/default
  WMT_CONFIG=hiking python3 frontend.py &
  nginx -g 'daemon off;'
  ;;
esac
