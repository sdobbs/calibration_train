#!/bin/tcsh
# Do a first pass of calibrations for a given run

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass3.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE )
    setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
setenv JANA_CALIB_CONTEXT "variation=calib_pass3" 

###################################################

# set some general variables
set RUNDIR=${BASEDIR}/output/Run${RUN}

# merge results of per-file processing
set FINAL_OUTPUT_FILENAME=hd_calib_final_Run${RUN}_${FILE}.root
set RUN_OUTPUT_FILENAME=hd_calib_final_Run${RUN}.root
echo ==summing ROOT files==
hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_final_*.root

# configure files for HLDetectorTiming
#set HLTIMING_DIR=Run${RUN}/
#set HLTIMING_CONST_DIR=Run${RUN}/constants/TDCADCTiming/
#mkdir -p $HLTIMING_DIR
#mkdir -p $HLTIMING_CONST_DIR
#cp $FINAL_OUTPUT_FILENAME $HLTIMINGDIR/TDCADCTiming.root

# process the results
echo ==first pass calibrations==
python run_calib_final.py $RUN_OUTPUT_FILENAME

# update CCDB
echo ==update CCDB==

# register output
echo ==register output files to SWIF==
swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${BASEDIR}/output/Run${RUN}/final/
swif outfile final_RF_TaggerComparison.png file:${BASEDIR}/output/Run${RUN}/final/final_RF_TaggerComparison.png
swif outfile final_HLDT_CalorimeterTiming.png file:${BASEDIR}/output/Run${RUN}/final/final_HLDT_CalorimeterTiming.png
swif outfile final_HLDT_PIDSystemTiming.png file:${BASEDIR}/output/Run${RUN}/final/final_HLDT_PIDSystemTiming.png
swif outfile final_HLDT_TaggerRFAlignment.png file:${BASEDIR}/output/Run${RUN}/final/final_HLDT_TaggerRFAlignment.png
swif outfile final_HLDT_TaggerSCAlignment.png file:${BASEDIR}/output/Run${RUN}/final/final_HLDT_TaggerSCAlignment.png
swif outfile final_HLDT_TaggerTiming.png file:${BASEDIR}/output/Run${RUN}/final/final_HLDT_TaggerTiming.png
swif outfile final_HLDT_TrackMatchedTiming.png file:${BASEDIR}/output/Run${RUN}/final/final_HLDT_TrackMatchedTiming.png
#swif outfile ${HLTIMING_CONST_DIR}/bcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/bcal_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/cdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/cdc_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/fcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/fcal_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/fdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/fdc_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/sc_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/sc_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/tagh_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tagh_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/tagm_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tagm_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/tof_base_time.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tof_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/bcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/bcal_adc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/bcal_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/bcal_tdc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/fcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/fcal_adc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/sc_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/sc_adc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/sc_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/sc_tdc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/tagm_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tagm_adc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/tagm_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tagm_tdc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/tagh_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tagh_adc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/tagh_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tagh_tdc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/tof_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/final/${HLTIMING_CONST_DIR}/tof_adc_timing_offsets.txt



###################################################
## Cleanup

# generate CCDB SQLite for the next pass
==regenerate CCDB SQLite file==
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_final.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_final.sqlite
    cp ccdb_final.sqlite ${BASEDIR}/ccdb_final.sqlite
endif
