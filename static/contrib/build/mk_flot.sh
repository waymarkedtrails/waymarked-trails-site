#!/bin/bash
#
# Pack necessary parts of the flot library.
#
# Usage: mk_flot.sh <flot directory>
#
# Requires flot: http://www.flotcharts.org/
# and axislabels plugin: https://github.com/markrcote/flot-axislabels.git
#
# Unpack both in the same base directory.
# The final library will have the same name as the directory.
#
# You will need the closure compiler for this. Get the latest source
# at http://closure-compiler.googlecode.com/files/compiler-latest.zip
# unzip and copy compiler.jar as closure-compiler.jar into this build
# directory

CONTRIBDIR=$( cd $(dirname $0); cd .. ; pwd -P )
SOURCEDIR="$1"

SOURCES="jquery.flot.js jquery.flot.crosshair.js"
PLUGINS="flot-axislabels/jquery.flot.axislabels.js"
ADDSOURCES="excanvas.min.js"
OUTFILE=${CONTRIBDIR}/`basename $SOURCEDIR`.js

echo '/*' > $OUTFILE
cat $SOURCEDIR/LICENSE.txt >> $OUTFILE
echo '*/' >> $OUTFILE

for s in $SOURCES; do
  CMDLINE="$CMDLINE --js $SOURCEDIR/$s"
done

for p in $PLUGINS; do
  CMDLINE="$CMDLINE --js `dirname $SOURCEDIR`/$p"
  sed '/\*\//q' `dirname $SOURCEDIR`/$p >> $OUTFILE
done

java -jar closure-compiler.jar $CMDLINE >> $OUTFILE

for s in $ADDSOURCES; do
    cp $SOURCEDIR/$s $CONTRIBDIR
done
