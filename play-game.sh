export DBZ=`dirname $0`
#echo DBZ: $DBZ
cd $DBZ

export PYTHONPATH=$DBZ/src:$PYTHONPATH
#echo PYTHONPATH: $PYTHONPATH

/usr/bin/env python2.7 $DBZ/src/deadbyzombie/DeadByZombie.py
