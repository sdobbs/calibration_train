#!/bin/tcsh
# Do a first pass of calibrations for a given run

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass1.sqlite ccdb.sqlite
setenv JANA_CALIB_URL sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLit
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION $JANA_CALIB_URL
    #setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass2
else
    setenv VARIATION calib
endif
setenv JANA_CALIB_CONTEXT "variation=$VARIATION" 

# Debug info
if ( $?CALIB_DEBUG ) then 
    echo ==starting CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass3
endif

###################################################

# set some general variables
set RUNDIR=${BASEDIR}/output/Run${RUN}

# merge results of per-file processing
#setenv PASS2_OUTPUT_FILENAME hd_calib_pass2_Run${RUN}_${FILE}.root
setenv RUN_OUTPUT_FILENAME hd_calib_pass3_Run${RUN}.root
echo ==summing ROOT files==
hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass3_*.root

# process the results
set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

echo ==third pass calibrations==
echo Running: BCAL_TDC_Timing, ExtractTimeOffsetsAndCEff.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/BCAL_TDC_Timing/FitScripts/ExtractTimeOffsetsAndCEff.C\(${RUNNUM},\"${RUN_OUTPUT_FILENAME}\"\)
#echo Running: PS_E_calib, PSEcorr.C
#python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_E_calib/PSEcorr.C\(\"${RUN_OUTPUT_FILENAME}\"\)
#python run_calib_pass2.py $RUN_OUTPUT_FILENAME
echo Running: PS_timing, fits.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_timing/scripts/fits.C\(\"${RUN_OUTPUT_FILENAME}\",true\)
echo Running: PS_timing, offsets.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_timing/scripts/offsets.C\(\"fits-csv\"\)
echo Running: TAGH_timewalk, gaussian_fits.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/TAGH_timewalk/scripts/gaussian_fits.C\(\"${RUN_OUTPUT_FILENAME}\",true\)
echo Running: TAGH_timewalk, timewalk_fits.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/TAGH_timewalk/scripts/timewalk_fits.C\(gaussian-fits-csv\)
# run some for BCAL_attenlength_gainratio

# update CCDB
if ( $?CALIB_SUBMIT_CONSTANTS ) then
    echo ==update CCDB==
    #ccdb add /PHOTON_BEAM/microscope/tdc_time_offsets -v $VARIATION -r ${RUN}-${RUN} tagm_tdc_timing_offsets.txt
    ccdb add /PHOTON_BEAM/hodoscope/tdc_timewalk -v $VARIATION -r ${RUN}-${RUN} tdc_timewalk.txt
    ccdb add /BCAL/channel_global_offset -v $VARIATION -r ${RUN}-${RUN} channel_global_offset_BCAL.txt
    ccdb add /BCAL/tdiff_u_d -v $VARIATION -r ${RUN}-${RUN} tdiff_u_d_BCAL.txt
    #ccdb add /PHOTON_BEAM/pair_spectrometer/fine/energy_corrections -v $VARIATION -r ${RUN}-${RUN} Eparms-TAGM.out
    ccdb add /PHOTON_BEAM/pair_spectrometer/base_time_offset -v $VARIATION -r ${RUN}-${RUN} offsets/base_time_offset.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/tdc_timing_offsets -v $VARIATION -r ${RUN}-${RUN} offsets/tdc_timing_offsets_psc.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/coarse/adc_timing_offsets -v $VARIATION -r ${RUN}-${RUN} offsets/adc_timing_offsets_psc.txt
    ccdb add /PHOTON_BEAM/pair_spectrometer/fine/adc_timing_offsets -v $VARIATION -r ${RUN}-${RUN} offsets/adc_timing_offsets_ps.txt
endif

# register output
echo ==register output files to SWIF==
swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${BASEDIR}/output/Run${RUN}/pass3/
swif outfile bcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/bcal_base_time.txt
swif outfile cdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/cdc_base_time.txt
swif outfile fcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/fcal_base_time.txt
#swif outfile fdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/fdc_base_time.txt
swif outfile sc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/sc_base_time.txt
swif outfile tagh_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/tagh_base_time.txt
swif outfile tagm_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/tagm_base_time.txt
swif outfile tof_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass3/tof_base_time.txt
#swif outfile bcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/bcal_adc_timing_offsets.txt
#swif outfile bcal_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/bcal_tdc_timing_offsets.txt
#swif outfile fcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/fcal_adc_timing_offsets.txt
swif outfile sc_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/sc_adc_timing_offsets.txt
swif outfile sc_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/sc_tdc_timing_offsets.txt
swif outfile tagm_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/tagm_adc_timing_offsets.txt
swif outfile tagm_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/tagm_tdc_timing_offsets.txt
swif outfile tagh_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/tagh_adc_timing_offsets.txt
swif outfile tagh_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/tagh_tdc_timing_offsets.txt
#swif outfile tof_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass3/tof_adc_timing_offsets.txt
swif outfile channel_global_offset_BCAL.txt file:${BASEDIR}/output/Run${RUN}/pass3/channel_global_offset_BCAL.txt
swif outfile tdiff_u_d_BCAL.txt file:${BASEDIR}/output/Run${RUN}/pass3/tdiff_u_d_BCAL.txt
#swif outfile  file:${BASEDIR}/output/Run${RUN}/pass3/
#swif outfile Eparms-TAGM.out file:${BASEDIR}/output/Run${RUN}/pass3/ps_ecalib.txt
swif outfile offsets/base_time_offset.txt file:${BASEDIR}/output/Run${RUN}/pass1/ps_base_time_offset.txt
swif outfile offsets/tdc_timing_offsets_psc.txt file:${BASEDIR}/output/Run${RUN}/pass1/psc_tdc_timing_offsets.txt
swif outfile offsets/adc_timing_offsets_psc.txt file:${BASEDIR}/output/Run${RUN}/pass1/psc_adc_timing_offsets.txt
swif outfile offsets/adc_timing_offsets_ps.txt file:${BASEDIR}/output/Run${RUN}/pass1/ps_adc_timing_offsets.txt

echo ==DEBUG==
ls -lhR

###################################################
## Cleanup

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp ccdb.sqlite ${BASEDIR}/ccdb_pass3.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass3.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass3.sqlite
    cp ccdb_pass3.sqlite ${BASEDIR}/ccdb_pass3.sqlite
endif

# Debug info
if ( $?CALIB_DEBUG ) then 
    echo ==ending CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass3
endif
