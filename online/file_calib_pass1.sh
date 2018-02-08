#!/bin/bash
# Do a second pass of calibrations on an EVIO file

RUN=$1

source setup_gluex.sh

echo ==START PASS1==
date

export JANA_CALIB_URL=mysql://ccdb_user@hallddb.jlab.org/ccdb
export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
export VARIATION=calib

export JANA_CALIB_CONTEXT="variation=$VARIATION" 
#export JANA_CALIB_CONTEXT="variation=default" 

RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

echo running pass1 ... >> message.txt

# copy input file to local disk - SWIF only sets up a symbolic link to it
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio

# config
#CALIB_PLUGINS=HLDetectorTiming,BCAL_TDC_Timing,CDC_amp
CALIB_PLUGINS=HLDetectorTiming,CDC_amp,TOF_TDC_shift
CALIB_OPTIONS=" -PEVENTS_TO_KEEP=2000000 -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
#CALIB_OPTIONS=" -PEVENTS_TO_KEEP=1500000 -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
#CALIB_OPTIONS=" -PEVENTS_TO_KEEP=500000 -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
#CALIB_OPTIONS=" -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=100 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
PASS2_OUTPUT_FILENAME=hd_calib_pass1_Run${RUN}.root
# run
echo ==second pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS2_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
retval=$?

echo ==done==
date

exit $retval
