#!/bin/bash
# Do a first pass of calibrations for a given run

# python2.7 needed for CCDB command line tool - this is the version needed for the CentOS7 nodes
export PATH=/apps/python/2.7.12/bin:$PATH
export LD_LIBRARY_PATH=/apps/python/2.7.12/lib:$LD_LIBRARY_PATH


# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
export JANA_CALIB_URL=sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    export CCDB_CONNECTION=$JANA_CALIB_URL
    #export CCDB_CONNECTION=sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ ! -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass2
else
    export VARIATION=calib
fi
export JANA_CALIB_CONTEXT="variation=$VARIATION" 

# Debug info
if [ ! -z "$CALIB_DEBUG" ]; then 
    echo ==starting CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass2
fi

###################################################

# set some general variables
#set RUNDIR=${BASEDIR}/Run${RUN}
RUNDIR=${OUTPUTDIR}/hists/${RUN}/

# merge results of per-file processing
#export PASS2_OUTPUT_FILENAME hd_calib_pass2_Run${RUN}_${FILE}.root
export RUN_OUTPUT_FILENAME=hd_calib_pass2_Run${RUN}.root
echo ==summing ROOT files==
#hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass2_*.root
# ONE JOB!
cp -v hd_calib_pass2_Run${RUN}_${FILE}.root hd_calib_pass2_Run${RUN}.root

# process the results
RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

echo ==second pass calibrations==
echo Running: HLDetectorTiming, ExtractTrackBasedTiming.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/FitScripts/ExtractTrackBasedTiming.C\(\"${RUN_OUTPUT_FILENAME}\",${RUNNUM},\"${VARIATION}\"\)
echo Running: CDC_amp, CDC_gains.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME $HALLD_HOME/src/plugins/Calibration/CDC_amp/CDC_gains.C\(1\)
#echo Running: BCAL_TDC_Timing, ExtractTimeWalk.C
#python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/BCAL_TDC_Timing/FitScripts/ExtractTimeWalk.C\(\"${RUN_OUTPUT_FILENAME}\"\)
#echo Running: PS_E_calib, PSEcorr.C
#python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_E_calib/PSEcorr.C\(\"${RUN_OUTPUT_FILENAME}\"\)
#python run_calib_pass2.py $RUN_OUTPUT_FILENAME

echo ==make monitoring output==
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_CalorimeterTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_CalorimeterTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_PIDSystemTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_PIDSystemTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_TrackMatchedTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackMatchedTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_TaggerTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_TrackingTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackingTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_TaggerRFAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_TaggerRFAlignment2 $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment2.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O pass2_TaggerSCAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerSCAlignment.C

# update CCDB
if [ ! -z "$CALIB_SUBMIT_CONSTANTS" ]; then
    echo ==update CCDB==
#    ccdb add /BCAL/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} bcal_base_time.txt
#    ccdb add /CDC/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} cdc_base_time.txt
#    ccdb add /FCAL/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} fcal_base_time.txt
    #ccdb add /FDC/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} fdc_base_time.txt
#    ccdb add /START_COUNTER/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} sc_base_time.txt
    ccdb add /PHOTON_BEAM/hodoscope/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} tagh_base_time.txt
    ccdb add /PHOTON_BEAM/microscope/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} tagm_base_time.txt
#    ccdb add /TOF/base_time_offset -v $VARIATION -r ${RUNNUM}-${RUNNUM} tof_base_time.txt
    #ccdb add /BCAL/ADC_timing_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} bcal_adc_timing_offsets.txt
    #ccdb add /BCAL/TDC_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} bcal_tdc_timing_offsets.txt
    #ccdb add /FCAL/timing_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} fcal_adc_timing_offsets.txt
#    ccdb add /START_COUNTER/adc_timing_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} sc_adc_timing_offsets.txt
#    ccdb add /START_COUNTER/tdc_timing_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} sc_tdc_timing_offsets.txt
#    ccdb add /PHOTON_BEAM/microscope/fadc_time_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} tagm_adc_timing_offsets.txt
#    ccdb add /PHOTON_BEAM/microscope/tdc_time_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} tagm_tdc_timing_offsets.txt
#    ccdb add /PHOTON_BEAM/hodoscope/fadc_time_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} tagh_adc_timing_offsets.txt
#    ccdb add /PHOTON_BEAM/hodoscope/tdc_time_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} tagh_tdc_timing_offsets.txt
    #ccdb add /TOF/adc_timing_offsets -v $VARIATION -r ${RUNNUM}-${RUNNUM} tof_adc_timing_offsets.txt
    #ccdb add /BCAL/timewalk_tdc -v $VARIATION -r ${RUNNUM}-${RUNNUM} TimewalkBCAL.txt
    #ccdb add /PHOTON_BEAM/pair_spectrometer/fine/energy_corrections -v $VARIATION -r ${RUNNUM}-${RUNNUM} Eparms-TAGM.out
#    ccdb add /CDC/digi_scales -v $VARIATION -r ${RUNNUM}-${RUNNUM} cdc_new_ascale.txt
fi

# register output
echo ==register output files to SWIF==
#swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/
cp $RUN_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$RUN_OUTPUT_FILENAME
mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/pass2/
swif outfile bcal_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/bcal_base_time.txt
swif outfile cdc_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/cdc_base_time.txt
swif outfile fcal_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/fcal_base_time.txt
#swif outfile fdc_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/fdc_base_time.txt
swif outfile sc_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/sc_base_time.txt
swif outfile tagh_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tagh_base_time.txt
swif outfile tagm_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tagm_base_time.txt
swif outfile tof_base_time.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tof_base_time.txt
#swif outfile bcal_adc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/bcal_adc_timing_offsets.txt
#swif outfile bcal_tdc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/bcal_tdc_timing_offsets.txt
#swif outfile fcal_adc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/fcal_adc_timing_offsets.txt
swif outfile sc_adc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/sc_adc_timing_offsets.txt
swif outfile sc_tdc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/sc_tdc_timing_offsets.txt
swif outfile tagm_adc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tagm_adc_timing_offsets.txt
swif outfile tagm_tdc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tagm_tdc_timing_offsets.txt
swif outfile tagh_adc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tagh_adc_timing_offsets.txt
swif outfile tagh_tdc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tagh_tdc_timing_offsets.txt
#swif outfile tof_adc_timing_offsets.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/tof_adc_timing_offsets.txt
#swif outfile BCALTimewalk_Results.root file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/BCALTimewalk_Results.root
#swif outfile TimewalkBCAL.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/TimewalkBCAL.txt
#swif outfile  file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/
#swif outfile Eparms-TAGM.out file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/ps_ecalib.txt
swif outfile pass2_CalorimeterTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_CalorimeterTiming.png
swif outfile pass2_PIDSystemTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_PIDSystemTiming.png
swif outfile pass2_TrackMatchedTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_TrackMatchedTiming.png
swif outfile pass2_TaggerTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_TaggerTiming.png
swif outfile pass2_TrackingTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_TrackingTiming.png
swif outfile pass2_TaggerRFAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_TaggerRFAlignment.png
swif outfile pass2_TaggerRFAlignment2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_TaggerRFAlignment2.png
swif outfile pass2_TaggerSCAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/pass2_TaggerSCAlignment.png
swif outfile cdc_new_ascale.txt  file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/cdc_new_ascale.txt
swif outfile cdc_amphistos.root  file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/cdc_amphistos.root
#swif outfile   file:${SMALL_OUTPUTDIR}/Run${RUN}/pass2/

echo ==DEBUG==
ls -lhR

###################################################
## Cleanup

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    cp ccdb.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_pass2.${RUN}.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass2.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass2.sqlite
    #cp ccdb_pass2.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass2.${RUN}.sqlite
fi

# Debug info
if [ ! -z "$CALIB_DEBUG" ]; then 
    echo ==ending CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass2
fi
