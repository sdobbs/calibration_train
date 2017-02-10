#!/bin/bash 
# Do RF calibrations which only need a small number of events

# python2.7 needed for CCDB command line tool - this is the version needed for the CentOS7 nodes
export PATH=/apps/python/2.7.12/bin:$PATH
export LD_LIBRARY_PATH=/apps/python/2.7.12/lib:$LD_LIBRARY_PATH


# initialize CCDB before running
cp ${BASEDIR}/ccdb_start.sqlite ccdb.sqlite
#export JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
export JANA_CALIB_URL=mysql://ccdb_user@hallddb.jlab.org/ccdb
if [ -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    export CCDB_CONNECTION=$JANA_CALIB_URL
    #export CCDB_CONNECTION=sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass0
else
#    export VARIATION default  # hack around bad CCDB settings in calib var that need to be fixed
    export VARIATION=calib
fi

# Start by running over the current "default" calibrations
#export JANA_CALIB_CONTEXT "variation=$VARIATION"
export JANA_CALIB_CONTEXT="variation=default"

# copy input file to local disk - SWIF only sets up a symbolic link to it
#echo ==copy in file==
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio
#ls -lh data.evio


RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

##########################################################################
## STEP 1: basic timing validation

# config
NEVENTS_ZEROTH_PASS=100000
ZEROTH_CALIB_PLUGINS=RF_online
PASS0_OUTPUT_FILENAME=hd_calib_pass0.1_Run${RUN}.root
# run
echo ==zeroth pass, first step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
retval=$?
# save results
#mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/pass0/
#swif outfile $PASS0_OUTPUT_FILENAME file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
#mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/pass0/
#swif outfile $PASS0_OUTPUT_FILENAME file:${OUTPUTDIR}/hists/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
# backup
mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/
cp $PASS0_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$PASS0_OUTPUT_FILENAME

if [ "$retval" -ne "0" ]; then
    exit $retval
fi

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
mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/pass0/
#swif outfile pass0_RF_ROCTITimes.png file:${BASEDIR}/Run${RUN}/pass0/pass0_RF_ROCTITimes.png
swif outfile pass0_RF_TDCConversion.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/pass0_RF_TDCConversion.png
swif outfile pass0_RF_SignalPeriod.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/pass0_RF_SignalPeriod.png
swif outfile pass0_RF_BeamBunchPeriod.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/pass0_RF_BeamBunchPeriod.png


##########################################################################
## STEP 2: rough RF calibration, time_resolution_sq

# config
NEVENTS_ZEROTH_PASS=100000
ZEROTH_CALIB_PLUGINS=RF_online
PASS0_OUTPUT_FILENAME=hd_calib_pass0.2_Run${RUN}.root
# run
echo ==zeroth pass, second step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
retval=$?

# save results
#swif outfile $PASS0_OUTPUT_FILENAME file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
cp $PASS0_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$PASS0_OUTPUT_FILENAME

if [ "$retval" -ne "0" ]; then
    exit $retval
fi

# process the results
echo ==run calibrations==

echo Running: RF_online, RFMacro_SelfResolution.C
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_SelfResolution $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_SelfResolution.C
echo Running: RF_online, RFMacro_CoarseTimeOffsets.C
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_CoarseTimeOffsets $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_CoarseTimeOffsets.C\(${RUNNUM}\)

# register output from python script
swif outfile pass0_RF_SelfResolution.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/pass0_RF_SelfResolution.png
swif outfile pass0_RF_CoarseTimeOffsets.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/pass0_RF_CoarseTimeOffsets.png
swif outfile rf_coarse_time_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/rf_coarse_time_offsets.txt
swif outfile rf_time_resolution_sq.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/rf_time_resolution_sq.txt

# update CCDB for next step
if [ $?CALIB_SUBMIT_CONSTANTS ]; then
    ccdb add /PHOTON_BEAM/RF/time_off-v $VARIATION -r ${RUN}-${RUN} rf_coarse_time_offsets.txt #"coarse time offsets"
    ccdb add /PHOTON_BEAM/RF/time_resolution_sq -v $VARIATION -r ${RUN}-${RUN} rf_time_resolution_sq.txt #"time resolution squared"
fi

##########################################################################
## STEP 3: fine RF calibration, time_offset_var

# switch to calib variation
if [ -z "$CALIB_CHALLENGE" ]; then
    export VARIATION calib_pass0
else
#    export VARIATION default   # still hacking, need to figure this out
    export VARIATION calib
fi

# Now that we've started to recalibrate, run over the newly calibrated values
export JANA_CALIB_CONTEXT "variation=$VARIATION"

# config
NEVENTS_ZEROTH_PASS=100000
ZEROTH_CALIB_PLUGINS=RF_online
PASS0_OUTPUT_FILENAME=hd_calib_pass0.3_Run${RUN}.root
# run
echo ==zeroth pass, third step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 --PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
retval=$?

# save results
#swif outfile $PASS0_OUTPUT_FILENAME file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
cp $PASS0_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$PASS0_OUTPUT_FILENAME

if [ "$retval" -ne "0" ) then
    exit $retval
fi

# process the results
echo ==run calibrations==
#python run_calib_pass0.3.py $PASS0_OUTPUT_FILENAME
# error check?

echo Running: RF_online, RFMacro_FineTimeOffsets.C
#python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_FineTimeOffsets $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C\(${RUNNUM},\"calib_pass0\"\)
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_FineTimeOffsets $HALLD_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C\(${RUNNUM},\"${VARIATION}\"\) 

# register output
swif outfile pass0_RF_FineTimeOffsets.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/pass0_RF_FineTimeOffsets.png
swif outfile rf_fine_time_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/rf_fine_time_offsets.txt
swif outfile rf_time_offset_vars.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/rf_time_offset_vars.txt

# update CCDB
if [ -z "$CALIB_SUBMIT_CONSTANTS" ]; then
    ccdb add /PHOTON_BEAM/RF/time_off-v $VARIATION -r ${RUN}-${RUN} rf_fine_time_offsets.txt #"fine time offsets"
    ccdb add /PHOTON_BEAM/RF/time_offset_var -v $VARIATION -r ${RUN}-${RUN} rf_time_offset_vars.txt #"time offset variances"
fi

##################
## Cleanup

# generate CCDB SQLite for the next pass
if [ -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    mkdir -p $SQLITEDIR
    cp ccdb.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_pass0.${RUN}.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass0.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass0.sqlite
    #cp ccdb_pass0.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass0.${RUN}.sqlite
fi

# DEBUG 
#swif outfile ccdb.sqlite file:${BASEDIR}/Run${RUN}/pass0/ccdb_pass0.sqlite

echo ==done==
