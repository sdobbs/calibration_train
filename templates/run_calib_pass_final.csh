#!/bin/tcsh
# Do a first pass of calibrations for a given run

# initialize CCDB before running
#cp ${BASEDIR}/sqlite_ccdb/ccdb_pass3.${RUN}.sqlite ccdb.sqlite
cp -v ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
setenv JANA_CALIB_URL sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
if ( $?CALIB_CCDB_SQLITE_FILE ) then
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
set RUNDIR=${OUTPUTDIR}/hists/${RUN}/
set SUMMEDDIR=${OUTPUTDIR}/hists/summed/
mkdir -p $SUMMEDDIR

# merge results of per-file processing
set FINAL_OUTPUT_FILENAME=hd_calib_final_Run${RUN}_${FILE}.root
set RUN_OUTPUT_FILENAME=hd_calib_final_Run${RUN}.root
echo ==summing ROOT files==
#hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_final_*.root
hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/hd_calib_passfinal_*.root


# process the results
echo ==make monitoring output==
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_CalorimeterTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_CalorimeterTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_PIDSystemTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_PIDSystemTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TrackMatchedTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackMatchedTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TaggerTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TaggerRFAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TaggerSCAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerSCAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_BCAL_pi0mass $HALLD_HOME/src/plugins/monitoring/BCAL_inv_mass/bcal_inv_mass.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_BCAL-FCAL_pi0mass $HALLD_HOME/src/plugins/monitoring/BCAL_inv_mass/bcal__fcal_inv_mass.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_p2pi_preco $HALLD_HOME/src/plugins/Analysis/p2pi_hists/HistMacro_p2pi_preco1.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_p3pi_preco_FCAL-BCAL $HALLD_HOME/src/plugins/Analysis/p3pi_hists/HistMacro_p3pi_preco_FCAL-BCAL.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_p3pi_preco_2FCAL $HALLD_HOME/src/plugins/Analysis/p3pi_hists/HistMacro_p3pi_preco_2FCAL.C


# update CCDB
#echo ==update CCDB==
#if ( $?CALIB_SUBMIT_CONSTANTS ) then
#    echo ==update CCDB==
#    ccdb add /PHOTON_BEAM/pair_spectrometer/tdc_timewalk_corrections -v $VARIATION -r ${RUN}-${RUN} psc_tw_parms.out
#endif

# register output
echo ==register output files to SWIF==
swif outfile $RUN_OUTPUT_FILENAME file:${SUMMEDDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${SMALL_OUTPUTDIR}/output/Run${RUN}/final/
swif outfile psc_tw_parms.out file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/psc_tw_parms.txt
swif outfile sigmas.out  file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/psc_tw_sigmas.txt
swif outfile st_time_res.txt  file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/st_time_resolution.txt
swif outfile st_prop_timeCorr.txt  file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/st_propogation_time_corrections.txt
swif outfile final_CalorimeterTiming.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_CalorimeterTiming.png
swif outfile final_PIDSystemTiming.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_PIDSystemTiming.png
swif outfile final_TrackMatchedTiming.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_TrackMatchedTiming.png
swif outfile final_TaggerTiming.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_TaggerTiming.png
swif outfile final_TaggerRFAlignment.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_TaggerRFAlignment.png
swif outfile final_TaggerSCAlignment.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_TaggerSCAlignment.png
swif outfile final_BCAL_pi0mass.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_BCAL_pi0mass.png
swif outfile final_BCAL-FCAL_pi0mass.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_BCAL-FCAL_pi0mass.png
swif outfile final_p2pi_preco1.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_p2pi_preco1.png
swif outfile final_p3pi_preco_2FCAL.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_p3pi_preco_2FCAL.png
swif outfile final_p3pi_preco_FCAL-BCAL.png file:${SMALL_OUTPUTDIR}/output/Run${RUN}/final/final_p3pi_preco_FCAL-BCAL.png


## Cleanup
echo ==DEBUG==
ls -lhR

exit 69

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    cp ccdb.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_final.${RUN}.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_final.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_final.sqlite
    cp ccdb_final.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_final.${RUN}.sqlite
endif

# copy results to be web-accessible
#rsync -avx --exclude=log --exclude="*.root" --exclude="*.sqlite" ${BASEDIR}/ /work/halld2/data_monitoring/calibrations/${WORKFLOW}/

