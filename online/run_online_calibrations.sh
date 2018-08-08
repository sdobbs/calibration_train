#!/bin/bash

export LOCKFILE=lock.online
cd /home/sdobbs/work/calibration_train/online

source setup_gluex.sh

# run job
if [ ! -f $LOCKFILE ]; then
    touch $LOCKFILE
    python run_prompt_calibrations.py 50010- >& log/calib.`date +%F_%T`.log
    rm -f $LOCKFILE

    # send update email
    #if [ -f "message.txt" ]; then
    #   cp -v message.txt /group/halld/Users/sdobbs/simple_email_list/lists/online_calibrations/
    #	cd /group/halld/Users/sdobbs/simple_email_list/lists/online_calibrations
    #	/group/halld/Users/sdobbs/simple_email_list/scripts/simple_email_list.pl
    #fi

else
    echo "process is locked by another job, exiting..."
fi
