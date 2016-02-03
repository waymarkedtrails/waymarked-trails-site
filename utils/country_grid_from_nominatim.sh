#/bin/bash
#
# Downloads the country grid from Nominatim and apply it to the database
# given in the command line

DBNAME=$1

cd /tmp
git clone -n https://github.com/twain47/Nominatim --depth 1
cd Nominatim
git checkout HEAD data/country_osm_grid.sql

psql -d $DBNAME -c "DROP table IF EXISTS country_osm_grid"
psql -d $DBNAME -f data/country_osm_grid.sql
psql -d $DBNAME -c "ALTER TABLE country_osm_grid ADD COLUMN geom geometry(Geometry,3857)"
psql -d $DBNAME -c "UPDATE country_osm_grid SET geom=ST_Transform(geometry, 3857)"
psql -d $DBNAME -c "ALTER TABLE country_osm_grid DROP COLUMN geometry"

cd /tmp
rm -r Nominatim
