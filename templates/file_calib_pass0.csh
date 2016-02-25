#!/bin/tcsh 
# Do RF calibrations which only need a small number of events

# initialize CCDB before running
cp ${BASEDIR}/ccdb_start.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION $JANA_CALIB_URL
    #setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass0
else
    setenv VARIATION default
endif
setenv JANA_CALIB_CONTEXT "variation=$VARIATION"

# copy input file to local disk - SWIF only sets up a symbolic link to it
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio

set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

##########################################################################
## STEP 1: basic timing validation

# config
set NEVENTS_ZEROTH_PASS=100000
set ZEROTH_CALIB_PLUGINS=RF_online
set PASS0_OUTPUT_FILENAME=hd_calib_pass0.1_Run${RUN}.root
# run
echo ==zeroth pass, first step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
set retval=$?

# save results
swif outfile $PASS0_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME

if ( $retval != 0 ) then
    exit $retval
endif

# process the results
echo ==run calibrations==

echo Running: RF_online, RFMacro_ROCTITimes.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_ROCTITimes $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_ROCTITimes.C
echo Running: RF_online, RFMacro_TDCConversion.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_TDCConversion $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_TDCConversion.C
echo Running: RF_online, RFMacro_SignalPeriod.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_SignalPeriod $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_SignalPeriod.C
echo Running: RF_online, RFMacro_BeamBunchPeriod.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_BeamBunchPeriod $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_BeamBunchPeriod.C

# register output from python script
mkdir -p ${BASEDIR}/output/Run${RUN}/pass0/
swif outfile pass0_RF_ROCTITimes.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_ROCTITimes.png
swif outfile pass0_RF_TDCConversion.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_TDCConversion.png
swif outfile pass0_RF_SignalPeriod.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_SignalPeriod.png
swif outfile pass0_RF_BeamBunchPeriod.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_BeamBunchPeriod.png


##########################################################################
## STEP 2: rough RF calibration, time_resolution_sq

# config
set NEVENTS_ZEROTH_PASS=100000
set ZEROTH_CALIB_PLUGINS=RF_online
set PASS0_OUTPUT_FILENAME=hd_calib_pass0.2_Run${RUN}.root
# run
echo ==zeroth pass, second step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
set retval=$?

# save results
swif outfile $PASS0_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME

if ( $retval != 0 ) then
    exit $retval
endif

# process the results
echo ==run calibrations==

echo Running: RF_online, RFMacro_SelfResolution.C
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_SelfResolution $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_SelfResolution.C
echo Running: RF_online, RFMacro_CoarseTimeOffsets.C
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_CoarseTimeOffsets $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_CoarseTimeOffsets.C\(${RUNNUM}\)

# register output from python script
swif outfile pass0_RF_SelfResolution.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_SelfResolution.png
swif outfile pass0_RF_CoarseTimeOffsets.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_CoarseTimeOffsets.png
swif outfile rf_coarse_time_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass0/rf_coarse_time_offsets.txt
swif outfile rf_time_resolution_sq.txt file:${BASEDIR}/output/Run${RUN}/pass0/rf_time_resolution_sq.txt

# update CCDB for next step
if ( $?CALIB_SUBMIT_CONSTANTS ) then
    ccdb add /PHOTON_BEAM/RF/time_offset -v $VARIATION -r ${RUN}-${RUN} rf_coarse_time_offsets.txt #"coarse time offsets"
    ccdb add /PHOTON_BEAM/RF/time_resolution_sq -v $VARIATION -r ${RUN}-${RUN} rf_time_resolution_sq.txt #"time resolution squared"
endif

##########################################################################
## STEP 3: fine RF calibration, time_offset_var

# switch to calib variation
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass0
else
    setenv VARIATION calib
endif

# config
set NEVENTS_ZEROTH_PASS=100000
set ZEROTH_CALIB_PLUGINS=RF_online
set PASS0_OUTPUT_FILENAME=hd_calib_pass0.3_Run${RUN}.root
# run
echo ==zeroth pass, third step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 --PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
set retval=$?

# save results
swif outfile $PASS0_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME

if ( $retval != 0 ) then
    exit $retval
endif

# process the results
echo ==run calibrations==
#python run_calib_pass0.3.py $PASS0_OUTPUT_FILENAME
# error check?

echo Running: RF_online, RFMacro_FineTimeOffsets.C
#python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_FineTimeOffsets $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C\(${RUNNUM},\"calib_pass0\"\)
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_FineTimeOffsets $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C\(${RUNNUM},\"calib\"\)  # hack until ccdb command line tool has fallbacks fixed

# register output
swif outfile pass0_RF_FineTimeOffsets.png file:${BASEDIR}/output/Run${RUN}/pass0/pass0_RF_FineTimeOffsets.png
swif outfile rf_fine_time_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass0/rf_fine_time_offsets.txt
swif outfile rf_time_offset_vars.txt file:${BASEDIR}/output/Run${RUN}/pass0/rf_time_offset_vars.txt

# update CCDB
if ( $?CALIB_SUBMIT_CONSTANTS ) then
    ccdb add /PHOTON_BEAM/RF/time_offset -v $VARIATION -r ${RUN}-${RUN} rf_fine_time_offsets.txt #"fine time offsets"
    ccdb add /PHOTON_BEAM/RF/time_offset_var -v $VARIATION -r ${RUN}-${RUN} rf_time_offset_vars.txt #"time offset variances"
endif

##################
## Cleanup

# generate CCDB SQLite for the next pass
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp ccdb.sqlite ${BASEDIR}/ccdb_pass0.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass0.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass0.sqlite
    cp ccdb_pass0.sqlite ${BASEDIR}/ccdb_pass0.sqlite
endif

# DEBUG 
#swif outfile ccdb.sqlite file:${BASEDIR}/output/Run${RUN}/pass0/ccdb_pass0.sqlite

echo ==done==
