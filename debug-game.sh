export GROGDJANGO=`dirname $0`
#echo GROGDJANGO: $GROGDJANGO
cd $GROGDJANGO
export PYTHONPATH=$GROGDJANGO/src:$PYTHONPATH

/usr/bin/env python2.5 $GROGDJANGO/src/deadbyzombie/pdb_dbz.py
