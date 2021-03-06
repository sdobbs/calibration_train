#!/bin/bash
# Do a first pass of calibrations for a given run

# initialize CCDB before running
#cp ${BASEDIR}/sqlite_ccdb/ccdb_pass3.${RUN}.sqlite ccdb.sqlite
cp -v ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
export JANA_CALIB_URL=sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
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


###################################################

# set some general variables
RUNDIR=${OUTPUTDIR}/hists/Run${RUN}/
SUMMEDDIR=${OUTPUTDIR}/hists/summed/
mkdir -p $SUMMEDDIR

# merge results of per-file processing
FINAL_OUTPUT_FILENAME=hd_calib_final_Run${RUN}_${FILE}.root
RUN_OUTPUT_FILENAME=hd_calib_final_Run${RUN}.root
echo ==summing ROOT files==
hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/hd_calib_final_*.root
#hadd -f -k $RUN_OUTPUT_FILENAME  ${RUNDIR}/hd_calib_passfinal_*.root


# process the results
echo ==make monitoring output==
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_CalorimeterTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_CalorimeterTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_PIDSystemTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_PIDSystemTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TrackMatchedTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TrackMatchedTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TaggerTiming $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerTiming.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TaggerRFAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerRFAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_TaggerSCAlignment $HALLD_HOME/src/plugins/Calibration/HLDetectorTiming/HistMacro_TaggerSCAlignment.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_BCAL_pi0mass $HALLD_HOME/src/plugins/monitoring/BCAL_inv_mass/bcal_inv_mass.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_BCAL-FCAL_pi0mass $HALLD_HOME/src/plugins/monitoring/BCAL_inv_mass/bcal_fcal_inv_mass.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_p2pi $HALLD_HOME/src/plugins/Analysis/p2pi_hists/HistMacro_p2pi.C
python run_single_root_command.py -F $RUN_OUTPUT_FILENAME -O final_p3pi $HALLD_HOME/src/plugins/Analysis/p3pi_hists/HistMacro_p3pi.C


# update CCDB
#echo ==update CCDB==
#if ( $?CALIB_SUBMIT_CONSTANTS ) then
#    echo ==update CCDB==
#    ccdb add /PHOTON_BEAM/pair_spectrometer/tdc_timewalk_corrections -v $VARIATION -r ${RUNNUM}-${RUNNUM} psc_tw_parms.out
#endif

# register output
echo ==register output files to SWIF==
mkdir -p ${SUMMEDDIR}
cp -v $RUN_OUTPUT_FILENAME ${SUMMEDDIR}/$RUN_OUTPUT_FILENAME
swif outfile $RUN_OUTPUT_FILENAME file:${SUMMEDDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/final/
#swif outfile psc_tw_parms.out file:${SMALL_OUTPUTDIR}/Run${RUN}/final/psc_tw_parms.txt
#swif outfile sigmas.out  file:${SMALL_OUTPUTDIR}/Run${RUN}/final/psc_tw_sigmas.txt
#swif outfile st_time_res.txt  file:${SMALL_OUTPUTDIR}/Run${RUN}/final/st_time_resolution.txt
#swif outfile st_prop_timeCorr.txt  file:${SMALL_OUTPUTDIR}/Run${RUN}/final/st_propogation_time_corrections.txt
swif outfile final_CalorimeterTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_CalorimeterTiming.png
swif outfile final_PIDSystemTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_PIDSystemTiming.png
swif outfile final_TrackMatchedTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_TrackMatchedTiming.png
swif outfile final_TaggerTiming.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_TaggerTiming.png
swif outfile final_TaggerRFAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_TaggerRFAlignment.png
swif outfile final_TaggerSCAlignment.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_TaggerSCAlignment.png
swif outfile final_BCAL_pi0mass.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_BCAL_pi0mass.png
swif outfile final_BCAL-FCAL_pi0mass.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_BCAL-FCAL_pi0mass.png
swif outfile final_p2pi.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_p2pi.png
swif outfile final_p3pi.png file:${SMALL_OUTPUTDIR}/Run${RUN}/final/final_p3pi.png


## Cleanup
echo ==DEBUG==
ls -lhR

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    cp ccdb.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_final.${RUN}.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_final.sqlite
else
    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_final.sqlite
    #cp ccdb_final.sqlite ${SQLITEDIR}/sqlite_ccdb/ccdb_final.${RUN}.sqlite
    cp ccdb_final.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_final.${RUN}.sqlite
fi

# copy results to be web-accessible
#rsync -avx --exclude=log --exclude="*.root" --exclude="*.sqlite" ${BASEDIR}/ /work/halld2/data_monitoring/calibrations/${WORKFLOW}/

