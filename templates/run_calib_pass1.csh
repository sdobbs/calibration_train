#!/bin/tcsh
# Do a first pass of calibrations for a given run

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass0.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
setenv JANA_CALIB_CONTEXT "variation=calib_pass1" 

# Debug info
if ( $?CALIB_DEBUG ) then 
    echo ==starting CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass1
endif

# copy input file to local disk - SWIF only sets up a symbolic link to it
mv data.evio data_link.evio
cp -v data_link.evio data.evio

###################################################

# set some general variables
set RUNDIR=${BASEDIR}/output/Run${RUN}

# merge results of per-file processing
#set PASS1_OUTPUT_FILENAME=hd_calib_pass1_Run${RUN}_${FILE}.root
setenv RUN_OUTPUT_FILENAME hd_calib_pass1_Run${RUN}.root
echo ==summing ROOT files==
#hadd -f -k -v 0 $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass1_*.root
hadd -f -k  $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass1_*.root

# configure files for HLDetectorTiming
set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`
set HLTIMING_DIR=Run${RUNNUM}/
set HLTIMING_CONST_DIR=Run${RUNNUM}/constants/TDCADCTiming/
mkdir -p $HLTIMING_DIR
mkdir -p $HLTIMING_CONST_DIR
cp -v $RUN_OUTPUT_FILENAME $HLTIMING_DIR/TDCADCTiming.root

#echo ==ls -lR before running scripts==
#ls -lRh

# process the results
echo ==first pass calibrations==
#python run_calib_pass1.py $RUN_OUTPUT_FILENAME
echo Running: HLDetectorTiming, ExtractTDCADCTiming.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/FitScripts/ExtractTDCADCTiming.C\(${RUNNUM}\)
echo Running: PS_timing, fits.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_timing/scripts/fits.C\(\"${RUN_OUTPUT_FILENAME}\",true\)
echo Running: PS_timing, offsets.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_timing/scripts/offsets.C\(\"fits-csv\"\)

# update CCDB
if ( $?CALIB_SUBMIT_CONSTANTS ) then
    echo ==update CCDB==
    ccdb add /BCAL/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/bcal_base_time.txt
    ccdb add /CDC/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/cdc_base_time.txt
    ccdb add /FCAL/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/fcal_base_time.txt
    ccdb add /FDC/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/fdc_base_time.txt
    ccdb add /START_COUNTER/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/sc_base_time.txt
    ccdb add /PHOTON_BEAM/hodoscope/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagh_base_time.txt
    ccdb add /PHOTON_BEAM/microscope/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagm_base_time.txt
    ccdb add /TOF/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tof_base_time.txt
    ccdb add /BCAL/ADC_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/bcal_adc_timing_offsets.txt
    ccdb add /BCAL/TDC_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/bcal_tdc_timing_offsets.txt
    ccdb add /FCAL/timing_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/fcal_adc_timing_offsets.txt
    ccdb add /START_COUNTER/adc_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/sc_adc_timing_offsets.txt
    ccdb add /START_COUNTER/tdc_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/sc_tdc_timing_offsets.txt
    ccdb add /PHOTON_BEAM/microscope/fadc_time_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagm_adc_timing_offsets.txt
    ccdb add /PHOTON_BEAM/microscope/tdc_time_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagm_tdc_timing_offsets.txt
    ccdb add /PHOTON_BEAM/hodoscope/fadc_time_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagh_adc_timing_offsets.txt
    ccdb add /PHOTON_BEAM/hodoscope/tdc_time_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagh_tdc_timing_offsets.txt
    ccdb add /TOF/adc_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tof_adc_timing_offsets.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/base_time_offset -v calib_pass1 -r ${RUN}-${RUN} offsets/base_time_offset.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/tdc_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} offsets/tdc_timing_offsets_psc.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/adc_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} offsets/adc_timing_offsets_psc.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/fine/adc_timing_offsets -v calib_pass1 -r ${RUN}-${RUN} offsets/adc_timing_offsets_ps.txt
endif

# register output
echo ==register output files to SWIF==
swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${BASEDIR}/output/Run${RUN}/pass1/
swif outfile ${HLTIMING_CONST_DIR}/bcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/bcal_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/cdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/cdc_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/fcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/fcal_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/fdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/fdc_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/sc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/sc_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/tagh_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/tagh_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/tagm_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/tagm_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/tof_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass1/tof_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/bcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/bcal_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/bcal_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/bcal_tdc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/fcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/fcal_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/sc_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/sc_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/sc_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/sc_tdc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagm_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/tagm_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagm_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/tagm_tdc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagh_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/tagh_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagh_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/tagh_tdc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tof_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass1/tof_adc_timing_offsets.txt
swif outfile offsets/base_time_offset.txt file:${BASEDIR}/output/Run${RUN}/pass1/ps_base_time_offset.txt
swif outfile offsets/tdc_timing_offsets_psc.txt file:${BASEDIR}/output/Run${RUN}/pass1/psc_tdc_timing_offsets.txt
swif outfile offsets/adc_timing_offsets_psc.txt file:${BASEDIR}/output/Run${RUN}/pass1/psc_adc_timing_offsets.txt
swif outfile offsets/adc_timing_offsets_ps.txt file:${BASEDIR}/output/Run${RUN}/pass1/ps_adc_timing_offsets.txt


###################################################
## Cleanup

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass1.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass1.sqlite
    cp ccdb_pass1.sqlite ${BASEDIR}/ccdb_pass1.sqlite
endif

# Debug info
if ( $?CALIB_DEBUG ) then 
    echo ==ending CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass1
endif

