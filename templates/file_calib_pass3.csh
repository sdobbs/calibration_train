#!/bin/tcsh
# Do a third pass of calibrations on an EVIO file

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass2.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
setenv JANA_CALIB_CONTEXT "variation=calib_pass3" 

# copy input file to local disk - SWIF only sets up a symbolic link to it
mv data.evio data_link.evio
cp -v data_link.evio data.evio

# config
set CALIB_PLUGINS=BCAL_attenlength_gainratio,TAGH_timewalk   # TAGM_timewalk,PS energies
set CALIB_OPTIONS="-PRF:SOURCE_SYSTEM=PSC"
set PASS3_OUTPUT_FILENAME=hd_calib_pass3_Run${RUN}_${FILE}.root

# run
echo ==third pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS3_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
set retval=$?

# save results
swif outfile $PASS3_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/${FILE}/$PASS3_OUTPUT_FILENAME

exit $retval
