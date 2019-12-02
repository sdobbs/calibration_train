#!/bin/bash

export LOCKFILE=lock.online
cd /home/sdobbs/work/calibration_train/online

export HOME=/home/sdobbs
source setup_gluex.sh

env >& log/env.`date +%F_%T`.log

# run job
if [ ! -f $LOCKFILE ]; then
    touch $LOCKFILE
    #python run_prompt_calibrations.py  60550-60851   >& log/calib.`date +%F_%T`.log
    python run_prompt_calibrations.py  60700-60851 |& tee log/calib.`date +%F_%T`.log
    rm -f $LOCKFILE

    # send update email
    if [ -f "message.txt" ]; then
       cp -v message.txt /group/halld/Users/sdobbs/simple_email_list/lists/online_calibrations/
    	cd /group/halld/Users/sdobbs/simple_email_list/lists/online_calibrations
    	/group/halld/Users/sdobbs/simple_email_list/scripts/simple_email_list.pl
    fi

else
    echo "process is locked by another job, exiting..."
fi
