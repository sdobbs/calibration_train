#!/bin/tcsh
# Do a first pass of calibrations for a given run

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass1.sqlite ccdb.sqlite
setenv JANA_CALIB_URL sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLit
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
setenv JANA_CALIB_CONTEXT "variation=calib_pass2" 

# Debug info
if ( $?CALIB_DEBUG ) then 
    echo ==starting CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass2
endif

###################################################

# set some general variables
set RUNDIR=${BASEDIR}/output/Run${RUN}

# merge results of per-file processing
#setenv PASS2_OUTPUT_FILENAME hd_calib_pass2_Run${RUN}_${FILE}.root
setenv RUN_OUTPUT_FILENAME hd_calib_pass2_Run${RUN}.root
echo ==summing ROOT files==
#hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass2_*.root
cp ${RUNDIR}/$RUN_OUTPUT_FILENAME .

# configure files for HLDetectorTiming
set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`
set HLTIMING_DIR=Run${RUNNUM}/
set HLTIMING_CONST_DIR=Run${RUNNUM}/constants/TrackBasedTiming/
set HLTIMING_PASS1_CONST_DIR=Run${RUNNUM}/constants/TDCADCTiming/
mkdir -p $HLTIMING_DIR
mkdir -p $HLTIMING_CONST_DIR
mkdir -p $HLTIMING_PASS1_CONST_DIR
cp $RUN_OUTPUT_FILENAME $HLTIMING_DIR/TrackBasedTiming.root
# setup constans from previous pass - we should find a better way to do this
cp ${BASEDIR}/output/Run${RUN}/pass1/*.txt ${HLTIMING_PASS1_CONST_DIR}

# process the results
echo ==first pass calibrations==
echo Running: HLDetectorTiming, ExtractTrackBasedTiming.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/FitScripts/ExtractTrackBasedTiming.C\(${RUNNUM}\)
echo Running: BCAL_TDC_Timing, ExtractTimeWalk.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/BCAL_TDC_Timing/FitScripts/ExtractTimeWalk.C\(\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: BCAL_TDC_Timing, ExtractTimeOffsetsAndCEff.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/BCAL_TDC_Timing/FitScripts/ExtractTimeOffsetsAndCEff.C\(${RUNNUM},\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: st_tw_corr_auto, st_tw_fits.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/st_tw_corr_auto/macros/st_tw_fits.C\(\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: PSC_TW, tw_corr.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PSC_TW/tw_corr.C\(\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: PS_E_calib, PSEcorr.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PS_E_calib/PSEcorr.C\(\"${RUN_OUTPUT_FILENAME}\"\)
#python run_calib_pass2.py $RUN_OUTPUT_FILENAME

# update CCDB
echo ==update CCDB==
ccdb add /BCAL/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/bcal_base_time.txt
ccdb add /CDC/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/cdc_base_time.txt
ccdb add /FCAL/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/fcal_base_time.txt
#ccdb add /FDC/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/fdc_base_time.txt
ccdb add /START_COUNTER/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/sc_base_time.txt
ccdb add /PHOTON_BEAM/hodoscope/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagh_base_time.txt
ccdb add /PHOTON_BEAM/microscope/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagm_base_time.txt
ccdb add /TOF/base_time_offset -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tof_base_time.txt
#ccdb add /BCAL/ADC_timing_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/bcal_adc_timing_offsets.txt
#ccdb add /BCAL/TDC_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/bcal_tdc_timing_offsets.txt
#ccdb add /FCAL/timing_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/fcal_adc_timing_offsets.txt
ccdb add /START_COUNTER/adc_timing_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/sc_adc_timing_offsets.txt
ccdb add /START_COUNTER/tdc_timing_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/sc_tdc_timing_offsets.txt
ccdb add /PHOTON_BEAM/microscope/fadc_time_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagm_adc_timing_offsets.txt
ccdb add /PHOTON_BEAM/microscope/tdc_time_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagm_tdc_timing_offsets.txt
ccdb add /PHOTON_BEAM/hodoscope/fadc_time_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagh_adc_timing_offsets.txt
ccdb add /PHOTON_BEAM/hodoscope/tdc_time_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tagh_tdc_timing_offsets.txt
ccdb add /TOF/adc_timing_offsets -v calib_pass2 -r ${RUN}-${RUN} ${HLTIMING_CONST_DIR}/tof_adc_timing_offsets.txt
ccdb add /BCAL/timewalk_tdc -v calib_pass2 -r ${RUN}-${RUN} TimewalkBCAL.txt
ccdb add /BCAL/channel_global_offset -v calib_pass2 -r ${RUN}-${RUN} channel_global_offset_BCAL.txt
ccdb add /BCAL/tdiff_u_d -v calib_pass2 -r ${RUN}-${RUN} tdiff_u_d_BCAL.txt
ccdb add /PHOTON_BEAM/pair_spectrometer/tdc_timewalk_corrections -v calib_pass2 -r ${RUN}-${RUN} psc_tw_parms.out
ccdb add /PHOTON_BEAM/pair_spectrometer/fine/energy_corrections -v calib_pass2 -r ${RUN}-${RUN} Eparms-TAGM.out

# register output
echo ==register output files to SWIF==
swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${BASEDIR}/output/Run${RUN}/pass2/
swif outfile ${HLTIMING_CONST_DIR}/bcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/bcal_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/cdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/cdc_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/fcal_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/fcal_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/fdc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/fdc_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/sc_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/sc_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/tagh_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/tagh_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/tagm_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/tagm_base_time.txt
swif outfile ${HLTIMING_CONST_DIR}/tof_base_time.txt file:${BASEDIR}/output/Run${RUN}/pass2/tof_base_time.txt
#swif outfile ${HLTIMING_CONST_DIR}/bcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/bcal_adc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/bcal_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/bcal_tdc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/fcal_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/fcal_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/sc_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/sc_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/sc_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/sc_tdc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagm_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/tagm_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagm_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/tagm_tdc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagh_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/tagh_adc_timing_offsets.txt
swif outfile ${HLTIMING_CONST_DIR}/tagh_tdc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/tagh_tdc_timing_offsets.txt
#swif outfile ${HLTIMING_CONST_DIR}/tof_adc_timing_offsets.txt file:${BASEDIR}/output/Run${RUN}/pass2/tof_adc_timing_offsets.txt
swif outfile BCALTimewalk_Results.root file:${BASEDIR}/output/Run${RUN}/pass2/BCALTimewalk_Results.root
swif outfile TimewalkBCAL.txt file:${BASEDIR}/output/Run${RUN}/pass2/TimewalkBCAL.txt
swif outfile channel_global_offset_BCAL.txt file:${BASEDIR}/output/Run${RUN}/pass2/channel_global_offset_BCAL.txt
swif outfile tdiff_u_d_BCAL.txt file:${BASEDIR}/output/Run${RUN}/pass2/tdiff_u_d_BCAL.txt
#swif outfile  file:${BASEDIR}/output/Run${RUN}/pass2/
swif outfile results.txt file:${BASEDIR}/output/Run${RUN}/pass2/st_timewalks.txt
swif outfile psc_tw_parms.out file:${BASEDIR}/output/Run${RUN}/pass2/psc_tw_parms.txt
swif outfile sigmas.out  file:${BASEDIR}/output/Run${RUN}/pass2/psc_tw_sigmas.txt
swif outfile Eparms-TAGM.out file:${BASEDIR}/output/Run${RUN}/pass2/ps_ecalib.txt
# start counter monitoring
swif outfile stt_tw_plot_1.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan1.png
swif outfile stt_tw_plot_2.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan2.png
swif outfile stt_tw_plot_3.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan3.png
swif outfile stt_tw_plot_4.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan4.png
swif outfile stt_tw_plot_5.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan5.png
swif outfile stt_tw_plot_6.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan6.png
swif outfile stt_tw_plot_7.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan7.png
swif outfile stt_tw_plot_8.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan8.png
swif outfile stt_tw_plot_9.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan9.png
swif outfile stt_tw_plot_10.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan10.png
swif outfile stt_tw_plot_11.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan11.png
swif outfile stt_tw_plot_12.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan12.png
swif outfile stt_tw_plot_13.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan13.png
swif outfile stt_tw_plot_14.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan14.png
swif outfile stt_tw_plot_15.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan15.png
swif outfile stt_tw_plot_16.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan16.png
swif outfile stt_tw_plot_17.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan17.png
swif outfile stt_tw_plot_18.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan18.png
swif outfile stt_tw_plot_19.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan19.png
swif outfile stt_tw_plot_20.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan20.png
swif outfile stt_tw_plot_21.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan21.png
swif outfile stt_tw_plot_22.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan22.png
swif outfile stt_tw_plot_23.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan23.png
swif outfile stt_tw_plot_24.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan24.png
swif outfile stt_tw_plot_25.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan25.png
swif outfile stt_tw_plot_26.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan26.png
swif outfile stt_tw_plot_27.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan27.png
swif outfile stt_tw_plot_28.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan28.png
swif outfile stt_tw_plot_29.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan29.png
swif outfile stt_tw_plot_30.png file:${BASEDIR}/output/Run${RUN}/pass2/sc_tw_chan30.png

echo ==DEBUG==
ls -lhR

###################################################
## Cleanup

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass2.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass2.sqlite
    cp ccdb_pass2.sqlite ${BASEDIR}/ccdb_pass2.sqlite
endif

# Debug info
if ( $?CALIB_DEBUG ) then 
    echo ==ending CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass2
endif
