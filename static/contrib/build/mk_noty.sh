#!/bin/bash
#
# Pack necessary parts of noty
#
# Usage: mk_noty.sh <source directory>
#
# Sources available here: 
# http://needim.github.io/noty/
#
# The final library will be suffixed with the git version.
#
# Requires yui-compressor to be installed, normally available
# as a Debian/Ubunutu package.

CONTRIBDIR=$( cd $(dirname $0); cd .. ; pwd -P )
SOURCEDIR="$1"

GITVERSION=`cd $SOURCEDIR; git rev-parse --short HEAD`
SOURCES="js/noty/jquery.noty.js js/noty/layouts/top.js js/noty/themes/default.js"
OUTFILE=${CONTRIBDIR}/`basename $SOURCEDIR`-$GITVERSION.js

for s in $SOURCES; do
  CMDLINE="$CMDLINE $SOURCEDIR/$s"
done

cat $CMDLINE | yui-compressor --type js  >> $OUTFILE