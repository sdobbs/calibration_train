#!/bin/tcsh
# Do a first pass of calibrations on an EVIO file

# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass0.${RUN}.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION $JANA_CALIB_URL
    #setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass1
else
    setenv VARIATION calib
endif
setenv JANA_CALIB_CONTEXT "variation=$VARIATION" 

set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio

# config
set CALIB_PLUGINS=HLDetectorTiming,TOF_TDC_shift
set CALIB_OPTIONS="-PHLDETECTORTIMING:DO_TDC_ADC_ALIGN=1 -PTOF:DELTA_T_ADC_TDC_MAX=1000 -PSC:HIT_TIME_WINDOW=1000 -PSC:DELTA_T_ADC_TDC_MAX=1000 -PTAGHHit:DELTA_T_ADC_TDC_MAX=1000 -PTAGMHit:DELTA_T_ADC_TDC_MAX=1000 -PEVENTS_TO_KEEP=500000"
set PASS1_OUTPUT_FILENAME=hd_calib_pass1_Run${RUN}_${FILE}.root
# run
echo ==first pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS1_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
set retval=$?

# save results
swif outfile $PASS1_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/${FILE}/$PASS1_OUTPUT_FILENAME

exit $retval
