#!/bin/tcsh
# Do a first pass of calibrations for a given run

# initialize CCDB before running
cp ${BASEDIR}/ccdb_pass3.sqlite ccdb.sqlite
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE )
    setenv CCDB_CONNECTION $JANA_CALIB_URL
#    setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass3
else
    setenv VARIATION calib
endif


###################################################

# set some general variables
set RUNDIR=${BASEDIR}/output/Run${RUN}

# merge results of per-file processing
set FINAL_OUTPUT_FILENAME=hd_calib_final_Run${RUN}_${FILE}.root
set RUN_OUTPUT_FILENAME=hd_calib_final_Run${RUN}.root
echo ==summing ROOT files==
hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_final_*.root


# process the results
echo ==final pass calibrations==
echo Running: PSC_TW, tw_corr.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/PSC_TW/tw_corr.C\(\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: ST_Tresolution, st_time_resolution.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/ST_Tresolution/macros/st_time_resolution.C\(\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: ST_Propagation_Time, st_prop_time_corr_v1.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/ST_Propagation_Time/macros/st_prop_time_corr_v1.C\(\"${RUN_OUTPUT_FILENAME}\"\)
echo Running: ST_Propagation_Time, st_prop_time_corr_v1.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/ST_Propagation_Time/macros/st_prop_time_corr_v1.C\(\"${RUN_OUTPUT_FILENAME}\"\)


# update CCDB
echo ==update CCDB==
if ( $?CALIB_SUBMIT_CONSTANTS ) then
    echo ==update CCDB==
    ccdb add /PHOTON_BEAM/pair_spectrometer/tdc_timewalk_corrections -v $VARIATION -r ${RUN}-${RUN} psc_tw_parms.out
endif

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
swif outfile psc_tw_parms.out file:${BASEDIR}/output/Run${RUN}/final/psc_tw_parms.txt
swif outfile sigmas.out  file:${BASEDIR}/output/Run${RUN}/final/psc_tw_sigmas.txt
swif outfile st_time_res.txt  file:${BASEDIR}/output/Run${RUN}/final/st_time_resolution.txt
swif outfile st_prop_timeCorr.txt  file:${BASEDIR}/output/Run${RUN}/final/st_propogation_time_corrections.txt

## Cleanup
echo ==DEBUG==
ls -lhR


# generate CCDB SQLite for the next pass
==regenerate CCDB SQLite file==
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp ccdb.sqlite ${BASEDIR}/ccdb_final.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_final.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_final.sqlite
    cp ccdb_final.sqlite ${BASEDIR}/ccdb_final.sqlite
endif
