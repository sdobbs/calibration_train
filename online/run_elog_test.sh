#!/bin/bash

#export LOCKFILE=lock.online
cd /home/sdobbs/work/calibration_train/online

export HOME=/home/sdobbs
export USER=sdobbs
source setup_gluex.sh

export GROUP=users-1
export HOST=gluon105.jlab.org
export HOSTNAME=gluon105.jlab.org
export HOSTTYPE=x86_64-linux
export MACHINE=Linux-x86_64
export MACHTYPE=x86_64
export OSTYPE=Linux


#env | sort > log/env.`date +%F_%T`.log

LOGNAME=elog.`date +%F_%T`.log
echo ==submit logbook entry== > log/$LOGNAME
#/site/ace/certified/apps/bin/logentry --title "Run 50905 online calibrations" --html --body /home/sdobbs/work/calibrations/RunPeriod-2018-08/Run050905/logbook.txt --entrymaker hdops --tag Autolog --logbook TLOG --noqueue  --cert /gluonwork1/Users/sdobbs/calibration_train/online/elogcert >& log/elog.`date +%F_%T`.log

echo ==try 1== >> log/$LOGNAME
/site/ace/certified/apps/bin/logentry --title "Run 50905 online calibrations" --html --body /home/sdobbs/work/calibrations/RunPeriod-2018-08/Run050905/logbook.txt --entrymaker hdops --tag Autolog --logbook TLOG --noqueue  2>&1 >> log/$LOGNAME
echo ==try 2== >> log/$LOGNAME
/site/ace/certified/apps/bin/logentry --title "Run 50905 online calibrations" --html --body /home/sdobbs/work/calibrations/RunPeriod-2018-08/Run050905/logbook.txt --entrymaker hdops --tag Autolog --logbook TLOG --cert /gluonwork1/Users/sdobbs/calibration_train/online/elogcert --noqueue  2>&1 >> log/$LOGNAME

exit

# run job
if [ ! -f $LOCKFILE ]; then
    touch $LOCKFILE
    python run_prompt_calibrations.py 50638- >& log/calib.`date +%F_%T`.log
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
