#!/bin/tcsh
# Do a final pass of calibrations on an EVIO file
# Do validations and generate outputs for others

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass3.sqlite ccdb.sqlite
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
mv data.evio data_link.evio
cp -v data_link.evio data.evio

# config
set CALIB_PLUGINS=HLDetectorTiming,PSC_TW,BCAL_gainmatrix,FCALgains,FCALpedestals,ST_Tresolution,ST_Propagation_Time,p2gamma_hists,imaging,pedestal_online,BCAL_LEDonline,TOF_calib
set CALIB_OPTIONS=""
set PASSFINAL_OUTPUT_FILENAME=hd_calib_passfinal_Run${RUN}_${FILE}.root
# run
echo ==validation pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASSFINAL_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
set retval=$?

# save results
swif outfile $PASSFINAL_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/${FILE}/$PASSFINAL_OUTPUT_FILENAME

exit $retval
