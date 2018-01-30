#!/bin/bash
# Do a first pass of calibrations for a given run

# initialize CCDB before running
#cp ${BASEDIR}/sqlite_ccdb/ccdb_pass3.${RUN}.sqlite ccdb.sqlite
#cp -v ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite

export JANA_CALIB_URL=mysql://ccdb_user@hallddb.jlab.org/ccdb

#export JANA_CALIB_URL=sqlite:///`pwd`/ccdb.verify.sqlite                # run jobs off of SQLite
#export JANA_CALIB_URL=sqlite:///`pwd`/ccdb_pass2.sqlite                # run jobs off of SQLite
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    export CCDB_CONNECTION=$JANA_CALIB_URL
#    export CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ ! -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass3
else
    export VARIATION=calib
fi

#export JANA_CALIB_CONTEXT="variation=$VARIATION"
export JANA_CALIB_CONTEXT="variation=default" 

###################################################


# config
#CALIB_PLUGINS=HLDetectorTiming,monitoring_hists,PSPair_online,RF_online,TAGM_TW
CALIB_PLUGINS=TOF_TDC_shift,PSPair_online,RF_online,TAGM_TW
CALIB_OPTIONS=" -PEVENTS_TO_KEEP=500000 "
#CALIB_OPTIONS=" -PEVENTS_TO_KEEP=100000 "
#CALIB_OPTIONS=" -PHLDETECTORTIMING:DO_TRACK_BASED=1 -PPID:OUT_OF_TIME_CUT=1000 -PTRKFIT:HYPOTHESES_POSITIVE=8 -PTRKFIT:HYPOTHESES_NEGATIVE=9 "
RUN_OUTPUT_FILENAME=hd_calib_verify_Run${RUN}_${FILE}.root
# run
echo ==second pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$RUN_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
retval=$?

# set some general variables
RUNDIR=${OUTPUTDIR}/hists/Run${RUN}/

# process the results
echo ==make monitoring output==
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_CalorimeterTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_CalorimeterTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_PIDSystemTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_PIDSystemTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TrackMatchedTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackMatchedTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TaggerTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TrackingTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackingTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TaggerRFAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TaggerRFAlignment2 $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TaggerSCAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerSCAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_BCALReconstruction_p1  $HALLD_HOME/src/plugins/Analysis/monitoring_hists/HistMacro_BCALReconstruction_p1.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_BCALReconstruction_p2  $HALLD_HOME/src/plugins/Analysis/monitoring_hists/HistMacro_BCALReconstruction_p2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_FCALReconstruction_p1  $HALLD_HOME/src/plugins/Analysis/monitoring_hists/HistMacro_FCALReconstruction_p1.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_FCALReconstruction_p2  $HALLD_HOME/src/plugins/Analysis/monitoring_hists/HistMacro_FCALReconstruction_p2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_SCReconstruction_p2  $HALLD_HOME/src/plugins/Analysis/monitoring_hists/HistMacro_SCReconstruction_p2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_TOFReconstruction_p2  $HALLD_HOME/src/plugins/Analysis/monitoring_hists/HistMacro_TOFReconstruction_p2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_PSTimingAlignment  $HALLD_HOME/src/plugins/monitoring/PSPair_online/HistMacro_PSTimingAlignment.C
#python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_BCAL_pi0mass $HALLD_HOME/src/plugins/monitoring/BCAL_inv_mass/bcal_inv_mass.C
#python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_BCAL-FCAL_pi0mass $HALLD_HOME/src/plugins/monitoring/BCAL_inv_mass/bcal_fcal_inv_mass.C
#python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_p2pi $HALLD_HOME/src/plugins/Analysis/p2pi_hists/HistMacro_p2pi.C
#python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_p3pi $HALLD_HOME/src/plugins/Analysis/p3pi_hists/HistMacro_p3pi.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_RF1 $HALLD_HOME/src/plugins/monitoring/RF_online/HistMacro_RF_p1.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_RF2 $HALLD_HOME/src/plugins/monitoring/RF_online/HistMacro_RF_p2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O verify_RF3 $HALLD_HOME/src/plugins/monitoring/RF_online/HistMacro_RF_p3.C


# register output
echo ==register output files to SWIF==
mkdir -p ${RUNDIR}
cp -v $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/verify/
cp -v TOF_TDC_shift_${RUN}.txt ${SMALL_OUTPUTDIR}/Run${RUN}/verify/TOF_TDC_shift_${RUN}.txt
#swif outfile psc_tw_parms.out file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/psc_tw_parms.txt
#swif outfile sigmas.out  file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/psc_tw_sigmas.txt
#swif outfile st_time_res.txt  file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/st_time_resolution.txt
#swif outfile st_prop_timeCorr.txt  file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/st_propogation_time_corrections.txt
swif outfile verify_CalorimeterTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_CalorimeterTiming.png
swif outfile verify_PIDSystemTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_PIDSystemTiming.png
swif outfile verify_TrackMatchedTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TrackMatchedTiming.png
swif outfile verify_TaggerTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TaggerTiming.png
swif outfile verify_TrackingTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TrackingTiming.png
swif outfile verify_TaggerRFAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TaggerRFAlignment.png
swif outfile verify_TaggerRFAlignment2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TaggerRFAlignment2.png
swif outfile verify_TaggerSCAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TaggerSCAlignment.png
swif outfile verify_BCALReconstruction_p1.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_BCALReconstruction_p1.png
swif outfile verify_BCALReconstruction_p2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_BCALReconstruction_p2.png
swif outfile verify_FCALReconstruction_p1.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_FCALReconstruction_p1.png
swif outfile verify_FCALReconstruction_p2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_FCALReconstruction_p2.png
swif outfile verify_SCReconstruction_p2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_SCReconstruction_p2.png
swif outfile verify_TOFReconstruction_p2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_TOFReconstruction_p2.png
swif outfile verify_PSTimingAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_PSTimingAlignment.png
#swif outfile verify_BCAL_pi0mass.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_BCAL_pi0mass.png
#swif outfile verify_BCAL-FCAL_pi0mass.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_BCAL-FCAL_pi0mass.png
#swif outfile verify_p2pi.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_p2pi.png
#swif outfile verify_p3pi.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_p3pi.png
swif outfile verify_RF1.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_RF1.png
swif outfile verify_RF2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_RF2.png
swif outfile verify_RF3.png file:${SMALL_OUTPUTDIR}/Run${RUN}/verify/verify_RF3.png


## Cleanup
echo ==DEBUG==
ls -lhR

# generate CCDB SQLite for the next pass
#echo ==regenerate CCDB SQLite file==
#if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
#    cp ccdb.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_verify.${RUN}.sqlite
#    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_verify.sqlite
#else
#    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_verify.sqlite
#    cp ccdb_verify.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_verify.${RUN}.sqlite
#fi

# copy results to be web-accessible
#rsync -avx --exclude=log --exclude="*.root" --exclude="*.sqlite" ${BASEDIR}/ /work/halld2/data_monitoring/calibrations/${WORKFLOW}/

exit $retval
