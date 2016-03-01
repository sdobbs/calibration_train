#!/bin/tcsh
# Do a first pass of calibrations on an EVIO file

# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass3.${RUN}.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION $JANA_CALIB_URL
    #setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass3
else
    setenv VARIATION calib
endif
setenv JANA_CALIB_CONTEXT "variation=$VARIATION" 

set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio

# config
set CALIB_PLUGINS=st_tw_corr_auto
set CALIB_OPTIONS="-PSC:USE_TIMEWALK_CORRECTION=0 -PSC:HIT_TIME_WINDOW=5000. -PSC:DELTA_T_ADC_TDC_MAX=5000 -PEVENTS_TO_KEEP=1000000"
set PASS3_OUTPUT_FILENAME=hd_calib_pass3.5_Run${RUN}_${FILE}.root
# run
echo ==do ST timwalk calibrations after first pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS3_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
set retval=$?

# save results
swif outfile $PASS3_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/${FILE}/$PASS3_OUTPUT_FILENAME

exit $retval
