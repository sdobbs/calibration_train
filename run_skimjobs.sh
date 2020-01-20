#!/bin/bash

export LOCKFILE=lock.online
cd /home/gxproj3/calibration_train

source /home/gxproj3/.profile

# run job
if [ ! -f $LOCKFILE ]; then
    touch $LOCKFILE
    #python skim_new_data.py 50010- 
    python skim_new_data.py 70100- >& /work/halld/home/gxproj3/calibration_train/log/calib.`date +%F_%T`.log
    #python skim_new_data-primex.py 70100- >& /work/halld/home/gxproj3/calibration_train/log/calib.`date +%F_%T`.log
    rm -f $LOCKFILE

    # send update email
    #if [ -f "message.txt" ]; then
    #   cp -v message.txt /group/halld/Users/sdobbs/simple_email_list/lists/online_calibrations/
    #cd /group/halld/Users/sdobbs/simple_email_list/lists/online_calibrations
    #/group/halld/Users/sdobbs/simple_email_list/scripts/simple_email_list.pl
    #fi

else
    echo "process is locked by another job, exiting..."
fi
