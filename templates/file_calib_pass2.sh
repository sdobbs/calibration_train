#!/bin/bash
# Do a second pass of calibrations on an EVIO file

# initialize CCDB before running
#cp ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
cp -v ccdb_pass1.sqlite ccdb.sqlite
export JANA_CALIB_URL=sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    export CCDB_CONNECTION=$JANA_CALIB_URL
    #export CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ ! -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass2
else
    export VARIATION=calib
fi
#export JANA_CALIB_CONTEXT="variation=$VARIATION" 
export JANA_CALIB_CONTEXT="variation=default" 

RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio

# config
#CALIB_PLUGINS=HLDetectorTiming,BCAL_TDC_Timing,CDC_amp
CALIB_PLUGINS=HLDetectorTiming,CDC_amp
#CALIB_OPTIONS=" -PEVENTS_TO_KEEP=1500000 -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
CALIB_OPTIONS=" -PEVENTS_TO_KEEP=500000 -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
PASS2_OUTPUT_FILENAME=hd_calib_pass2_Run${RUN}_${FILE}.root
# run
echo ==second pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS2_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
retval=$?

# save results
mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/
swif outfile $PASS2_OUTPUT_FILENAME file:${OUTPUTDIR}/hists/Run${RUN}/${PASS2_OUTPUT_FILENAME}

exit $retval
