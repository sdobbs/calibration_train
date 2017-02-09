#!/bin/tcsh
# Do a final pass of calibrations on an EVIO file
# Do validations and generate outputs for others

# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
#setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
setenv JANA_CALIB_URL  mysql://ccdb_user@hallddb.jlab.org/ccdb
if ( $?CALIB_CCDB_SQLITE_FILE ) then
    setenv CCDB_CONNECTION $JANA_CALIB_URL
    #setenv CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    setenv CCDB_CONNECTION mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
endif
if ( $?CALIB_CHALLENGE ) then
    setenv VARIATION calib_pass3
else
    setenv VARIATION calib
endif
setenv JANA_CALIB_CONTEXT "variation=$VARIATION" 

set RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
mv data.evio data_link.evio
cp -v data_link.evio data.evio

# config
set CALIB_PLUGINS=evio_writer,HLDetectorTiming,BCAL_attenlength_gainratio,CDC_amp,CDC_TimeToDistance,FCALpedestals,ST_Propagation_Time,imaging,pedestals,BCAL_LED,FCAL_TimingOffsets,FCALpulsepeak,pi0fcalskim,pi0bcalskim,ps_skim,BCAL_inv_mass,p2pi_hists,p3pi_hists,trigger_skims,TOF_calib
set CALIB_OPTIONS=""
set PASSFINAL_OUTPUT_FILENAME=hd_calib_final_Run${RUN}_${FILE}.root
# run
echo ==validation pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASSFINAL_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
set retval=$?

# save results
swif outfile $PASSFINAL_OUTPUT_FILENAME file:${OUTPUTDIR}/hists/${RUN}/$PASSFINAL_OUTPUT_FILENAME
# skims
#set SKIM_DIR=/cache/halld/${RUNPERIOD}/calib/${WORKFLOW}/
set SKIM_DIR=/cache/halld/${RUNPERIOD}/calib/pass2/
mkdir -p $SKIM_DIR
#
mkdir -p ${SKIM_DIR}/BCAL_pi0/${RUN}
swif outfile data.pi0bcalskim.evio file:${SKIM_DIR}/BCAL_pi0/${RUN}/hd_rawdata_${RUN}_${FILE}.pi0bcalskim.evio
mkdir -p ${SKIM_DIR}/FCAL_pi0/${RUN}
swif outfile data.pi0fcalskim.evio file:${SKIM_DIR}/FCAL_pi0/${RUN}/hd_rawdata_${RUN}_${FILE}.pi0fcalskim.evio
mkdir -p ${SKIM_DIR}/PS/${RUN}
swif outfile data.ps.evio file:${SKIM_DIR}/PS/${RUN}/hd_rawdata_${RUN}_${FILE}.ps.evio
mkdir -p ${SKIM_DIR}/TOF/${RUN}
swif outfile hd_root_tofcalib.root file:${SKIM_DIR}/TOF/${RUN}/hd_root_tofcalib_${RUN}_${FILE}.root
mkdir -p ${SKIM_DIR}/BCAL-LED/${RUN}
swif outfile data.BCAL-LED.evio file:${SKIM_DIR}/BCAL-LED/${RUN}/hd_rawdata_${RUN}_${FILE}.BCAL-LED.evio
mkdir -p ${SKIM_DIR}/FCAL-LED/${RUN}
swif outfile data.FCAL-LED.evio file:${SKIM_DIR}/FCAL-LED/${RUN}/hd_rawdata_${RUN}_${FILE}.FCAL-LED.evio
mkdir -p ${SKIM_DIR}/sync/${RUN}
swif outfile data.sync.evio file:${SKIM_DIR}/sync/${RUN}/hd_rawdata_${RUN}_${FILE}.sync.evio
mkdir -p ${SKIM_DIR}/random/${RUN}
swif outfile data.random.evio file:${SKIM_DIR}/random/${RUN}/hd_rawdata_${RUN}_${FILE}.random.evio
#swif outfile tree_p2gamma_hists.root file:${SKIM_DIR}/tree_p2gamma_hists_${RUN}_${FILE}.root

exit $retval
