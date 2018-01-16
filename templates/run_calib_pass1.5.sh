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
    #export CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ ! -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass1
else
    export VARIATION=calib
#    export VARIATION=calib_study
fi
export JANA_CALIB_CONTEXT="variation=$VARIATION" 

# Debug info
if [ ! -z "$CALIB_DEBUG" ]; then 
    echo ==starting CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass1
fi

###################################################

# set some general variables
#set RUNDIR=${BASEDIR}/output/Run${RUN}
RUNDIR=${OUTPUTDIR}/hists/${RUN}/

# merge results of per-file processing
#set PASS1_OUTPUT_FILENAME=hd_calib_pass1_Run${RUN}_${FILE}.root
export RUN_OUTPUT_FILENAME=hd_calib_pass1.5_Run${RUN}.root
echo ==summing ROOT files==
#hadd -f -k -v 0 $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass1_*.root
#hadd -f -k  $RUN_OUTPUT_FILENAME  ${RUNDIR}/*/hd_calib_pass1.5_*.root
# ONE JOB!
cp -v hd_calib_pass1.5_Run${RUN}_${FILE}.root hd_calib_pass1.5_Run${RUN}.root

# process the results
RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

echo ==first pass calibrations==
#python run_calib_pass1.py $RUN_OUTPUT_FILENAME
echo Running: st_tw_corr_auto, st_tw_fits.C
python run_single_root_command.py $HALLD_HOME/src/plugins/Calibration/st_tw_corr_auto/macros/st_tw_fits.C\(\"${RUN_OUTPUT_FILENAME}\"\)

# update CCDB
#if [ ! -z $CALIB_SUBMIT_CONSTANTS ] then
#    echo ==update CCDB==
#    ccdb add /START_COUNTER/timewalk_parms_v2 -v $VARIATION -r ${RUN}-${RUN} st_timewalks.txt
#endif

# register output
echo ==register output files to SWIF==
mkdir -p ${SMALL_OUTPUTDIR}/Run${RUN}/pass1/
#swif outfile $RUN_OUTPUT_FILENAME file:${RUNDIR}/$RUN_OUTPUT_FILENAME
mkdir -p ${OUTPUTDIR}/hists/Run${RUN}/
cp $RUN_OUTPUT_FILENAME ${OUTPUTDIR}/hists/Run${RUN}/$RUN_OUTPUT_FILENAME
swif outfile st_timewalks.txt file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/st_timewalks.txt
# start counter monitoring
swif outfile stt_tw_plot_1.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan1.png
swif outfile stt_tw_plot_2.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan2.png
swif outfile stt_tw_plot_3.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan3.png
swif outfile stt_tw_plot_4.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan4.png
swif outfile stt_tw_plot_5.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan5.png
swif outfile stt_tw_plot_6.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan6.png
swif outfile stt_tw_plot_7.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan7.png
swif outfile stt_tw_plot_8.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan8.png
swif outfile stt_tw_plot_9.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan9.png
swif outfile stt_tw_plot_10.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan10.png
swif outfile stt_tw_plot_11.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan11.png
swif outfile stt_tw_plot_12.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan12.png
swif outfile stt_tw_plot_13.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan13.png
swif outfile stt_tw_plot_14.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan14.png
swif outfile stt_tw_plot_15.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan15.png
swif outfile stt_tw_plot_16.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan16.png
swif outfile stt_tw_plot_17.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan17.png
swif outfile stt_tw_plot_18.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan18.png
swif outfile stt_tw_plot_19.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan19.png
swif outfile stt_tw_plot_20.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan20.png
swif outfile stt_tw_plot_21.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan21.png
swif outfile stt_tw_plot_22.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan22.png
swif outfile stt_tw_plot_23.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan23.png
swif outfile stt_tw_plot_24.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan24.png
swif outfile stt_tw_plot_25.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan25.png
swif outfile stt_tw_plot_26.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan26.png
swif outfile stt_tw_plot_27.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan27.png
swif outfile stt_tw_plot_28.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan28.png
swif outfile stt_tw_plot_29.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan29.png
swif outfile stt_tw_plot_30.png file:${SMALL_OUTPUTDIR}/Run${RUN}/pass1/sc_tw_chan30.png


###################################################
## Cleanup

# generate CCDB SQLite for the next pass
echo ==regenerate CCDB SQLite file==
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    cp ccdb.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite
    #cp $CALIB_CCDB_SQLITE_FILE ${BASEDIR}/ccdb_pass1.sqlite
#else
#    rm -f ccdb_pass1.sqlite
#    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass1.sqlite
#    cp ccdb_pass1.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite
fi

# Debug info
if [ ! -z "$CALIB_DEBUG" ]; then 
    echo ==ending CCDB info==
    python cat_ccdb_tables.py ccdb_tables_pass1.5
fi

