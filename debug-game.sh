export DBZ=`dirname $0`
#echo DBZ: $DBZ
cd $DBZ
export PYTHONPATH=$DBZ/src:$PYTHONPATH

/usr/bin/env python2.7 $DBZ/src/deadbyzombie/pdb_dbz.py
