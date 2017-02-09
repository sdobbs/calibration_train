#!/bin/bash
# Do a second pass of calibrations on an EVIO file

# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
export JANA_CALIB_URL=sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if [ -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    export CCDB_CONNECTION=$JANA_CALIB_URL
    #export CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass2
else
    export VARIATION=calib
fi
export JANA_CALIB_CONTEXT="variation=$VARIATION" 

RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
mv data.evio data_link.evio
cp -v data_link.evio data.evio

# config
CALIB_PLUGINS=PS_timing,TAGH_timewalk,BCAL_attenlength_gainratio,BCAL_TDC_Timing
CALIB_OPTIONS="-PBCAL:USE_TDC=1"
PASS3_OUTPUT_FILENAME=hd_calib_pass3_Run${RUN}_${FILE}.root
# run
echo ==second pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS3_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
retval=$?

# save results
swif outfile $PASS3_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/${FILE}/$PASS3_OUTPUT_FILENAME

exit $retval
