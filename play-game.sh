export DBZ=`dirname $0`
#echo DBZ: $DBZ
cd $DBZ

export PYTHONPATH=$DBZ/src:$PYTHONPATH
#echo PYTHONPATH: $PYTHONPATH

# historical list of deprecation warning filters:
# -W ignore:^raising*:DeprecationWarning:webhack:8912
# -W ignore:^raising*:DeprecationWarning:webhack:5352
# -W ignore:^raising*:DeprecationWarning:deadbyzombie.webhack:8688

/usr/bin/env python2.7 $DBZ/src/deadbyzombie/DeadByZombie.py
