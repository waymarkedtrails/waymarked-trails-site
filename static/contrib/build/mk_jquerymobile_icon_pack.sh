#!/bin/bash
#
# Pack necessary parts of jQuery-Mobile-Icon-Pack.
#
# Usage: mk_flot.sh <source directory>
#
# Sources available here: 
# https://github.com/commadelimited/jQuery-Mobile-Icon-Pack.git
#
# The final library will be suffixed with the git version.
#
# Requires yui-compressor to be installed, normally available
# as a Debian/Ubuntu package.

CONTRIBDIR=$( cd $(dirname $0); cd .. ; pwd -P )
SOURCEDIR="$1/original"
GITVERSION=`cd $SOURCEDIR; git rev-parse --short HEAD`
OUTFILE=$CONTRIBDIR/jqm-icon-pack-$GITVERSION.css

cp $SOURCEDIR/images/icons*.png $CONTRIBDIR/images

sed '/\*\//q' $SOURCEDIR/jqm-icon-pack-*-original.css > $OUTFILE
yui-compressor --type css $SOURCEDIR/jqm-icon-pack-*-original.css >> $OUTFILE
