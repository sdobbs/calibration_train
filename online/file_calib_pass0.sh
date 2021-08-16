#!/bin/bash 
# Do RF calibrations which only need a small number of events

RUN=$1

source setup_gluex.sh

echo ==START PASS0==
date

# python2.7 needed for CCDB command line tool - this is the version needed for the CentOS7 nodes
#export PATH=/apps/python/2.7.12/bin:$PATH
#export LD_LIBRARY_PATH=/apps/python/2.7.12/lib:$LD_LIBRARY_PATH

# initialize CCDB before running - should get this working at some point?
#cp ${BASEDIR}/ccdb_start.sqlite ccdb.sqlite
#export JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
export JANA_CALIB_URL=mysql://ccdb_user@hallddb.jlab.org/ccdb
export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
export VARIATION=calib

# Start by running over the current "default" calibrations
#export JANA_CALIB_CONTEXT="variation=$VARIATION"
export JANA_CALIB_CONTEXT="variation=default"

# copy input file to local disk - SWIF only sets up a symbolic link to it
#echo ==copy in file==
#mv data.evio data_link.evio
#cp -v data_link.evio data.evio
#ls -lh data.evio

ln -s data/hd_rawdata_${RUN}_001.evio data.evio

RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

echo ==start run ${RUNNUM}== >> message.txt
echo running pass0 ... >> message.txt

##########################################################################
## STEP 1: basic timing validation

# config
NEVENTS_ZEROTH_PASS=100000
ZEROTH_CALIB_PLUGINS=RF_online
PASS0_OUTPUT_FILENAME=hd_calib_pass0.1_Run${RUN}.root
# run
echo ==zeroth pass, first step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
#hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
echo hd_root  -PEVENTS_TO_SKIP=100  --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS  ./data/hd_rawdata_${RUN}_000.evio
timeout 1200 hd_root  -PEVENTS_TO_SKIP=100  --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS  ./data/hd_rawdata_${RUN}_000.evio #./data.evio
retval=$?
# save results
#mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/pass0/
#swif outfile $PASS0_OUTPUT_FILENAME file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
#mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/pass0/
#swif outfile $PASS0_OUTPUT_FILENAME file:${OUTPUTDIR}/hists/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
# backup
#mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/
#cp $PASS0_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$PASS0_OUTPUT_FILENAME

if [ "$retval" -ne "0" ]; then
    exit $retval
fi

# process the results
echo ==run calibrations==

echo Running: RF_online, RFMacro_ROCTITimes.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_ROCTITimes $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_ROCTITimes.C
echo Running: RF_online, RFMacro_TDCConversion.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_TDCConversion $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_TDCConversion.C
echo Running: RF_online, RFMacro_SignalPeriod.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_SignalPeriod $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_SignalPeriod.C
echo Running: RF_online, RFMacro_BeamBunchPeriod.C
python run_single_root_command.py -F $PASS0_OUTPUT_FILENAME -O pass0_RF_BeamBunchPeriod $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_BeamBunchPeriod.C


##########################################################################
## STEP 3: fine RF calibration, time_offset_var

export VARIATION=calib

# Now that we've started to recalibrate, run over the newly calibrated values
export JANA_CALIB_CONTEXT="variation=$VARIATION"

# config
NEVENTS_ZEROTH_PASS=100000
ZEROTH_CALIB_PLUGINS=RF_online
PASS0_OUTPUT_FILENAME=hd_calib_pass0.3_Run${RUN}.root
# run
echo ==zeroth pass, third step==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
#hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} --PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
echo hd_root  -PEVENTS_TO_SKIP=100  --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 --PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS   ./data/hd_rawdata_${RUN}_000.evio 
timeout 1200 hd_root  -PEVENTS_TO_SKIP=100  --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 --PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS   ./data/hd_rawdata_${RUN}_000.evio  #./data.evio
retval=$?

# save results
#swif outfile $PASS0_OUTPUT_FILENAME file:${SMALL_OUTPUTDIR}/Run${RUN}/pass0/$PASS0_OUTPUT_FILENAME
#cp $PASS0_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$PASS0_OUTPUT_FILENAME

if [ "$retval" -ne "0" ]; then
    exit $retval
fi

# process the results
echo ==run calibrations==
#python run_calib_pass0.3.py $PASS0_OUTPUT_FILENAME
# error check?

echo Running: RF_online, RFMacro_FineTimeOffsets.C
#python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_FineTimeOffsets $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C\(${RUNNUM},\"calib_pass0\"\)
python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O pass0_RF_FineTimeOffsets $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/calib_scripts/RFMacro_FineTimeOffsets.C\(${RUNNUM},\"${VARIATION}\"\) 

# update CCDB
ccdb add /PHOTON_BEAM/RF/time_offset -v $VARIATION -r ${RUN}-${RUN} rf_fine_time_offsets.txt #"fine time offsets"
ccdb add /PHOTON_BEAM/RF/time_offset_var -v $VARIATION -r ${RUN}-${RUN} rf_time_offset_vars.txt #"time offset variances"


##########################################################################
## STEP 4: Monitoring

# config
#NEVENTS_ZEROTH_PASS=100000
#ZEROTH_CALIB_PLUGINS=RF_online
#PASS0_OUTPUT_FILENAME=hd_calib_pass0.4_Run${RUN}.root
# run
#echo ==zeroth pass, last step==
#echo Running these plugins: $ZEROTH_CALIB_PLUGINS
#hd_root --nthreads=$NTHREADS -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 --PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ./data.evio
#retval=$?
#
#if [ "$retval" -ne "0" ]; then
#    exit $retval
#fi
#
# process the results
#echo ==run calibrations==
#echo Running: RF_online, RFMacro_FineTimeOffsets.C
#python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O verify_RF1 $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/HistMacro_RF_p1.C
#python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O verify_RF2 $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/HistMacro_RF_p2.C
#python run_single_root_command.py -F  $PASS0_OUTPUT_FILENAME -O verify_RF3 $HALLD_RECON_HOME/src/plugins/monitoring/RF_online/HistMacro_RF_p3.C

echo ==done==
date

exit 0
