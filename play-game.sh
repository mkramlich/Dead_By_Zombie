export GROGDJANGO=`dirname $0`
#echo GROGDJANGO: $GROGDJANGO
cd $GROGDJANGO

export PYTHONPATH=$GROGDJANGO/src:$PYTHONPATH
#echo PYTHONPATH: $PYTHONPATH

# historical list of deprecation warning filters:
# -W ignore:^raising*:DeprecationWarning:webhack:8912
# -W ignore:^raising*:DeprecationWarning:webhack:5352
# -W ignore:^raising*:DeprecationWarning:deadbyzombie.webhack:8688

#/usr/bin/env python2.5 $GROGDJANGO/src/deadbyzombie/DeadByZombie.pyc
/usr/bin/env python2.5 $GROGDJANGO/src/deadbyzombie/DeadByZombie.py
