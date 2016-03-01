#!/bin/tcsh
# Do a second pass of calibrations on an EVIO file

# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION $JANA_CALIB_URL
    #setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass2
else
    setenv VARIATION calib
endif
setenv JANA_CALIB_CONTEXT "variation=$VARIATION" 

set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio

# config
set CALIB_PLUGINS=HLDetectorTiming,BCAL_TDC_Timing
set CALIB_OPTIONS="-PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:MASS_HYPOTHESES_POSITIVE=0.14 -PTRKFIT:MASS_HYPOTHESES_NEGATIVE=0.14"
set PASS2_OUTPUT_FILENAME=hd_calib_pass2_Run${RUN}_${FILE}.root
# run
echo ==second pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS2_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
set retval=$?

# save results
swif outfile $PASS2_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/${FILE}/$PASS2_OUTPUT_FILENAME

exit $retval
