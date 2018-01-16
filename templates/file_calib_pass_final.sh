#!/bin/bash
# Do a final pass of calibrations on an EVIO file
# Do validations and generate outputs for others

# initialize CCDB before running
cp ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite ccdb.sqlite
export JANA_CALIB_URL=sqlite:///`pwd`/ccdb.sqlite                # run jobs off of SQLite
#export JANA_CALIB_URL=mysql://ccdb_user@hallddb.jlab.org/ccdb
if [ ! -z "$CALIB_CCDB_SQLITE_FILE" ]; then
    export CCDB_CONNECTION=$JANA_CALIB_URL
    #export CCDB_CONNECTION sqlite:///$CALIB_CCDB_SQLITE_FILE
else
    export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
fi
if [ ! -z "$CALIB_CHALLENGE" ]; then
    export VARIATION=calib_pass3
else
    export VARIATION=calib
fi
export JANA_CALIB_CONTEXT="variation=$VARIATION" 

RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# copy input file to local disk - SWIF only sets up a symbolic link to it
mv data.evio data_link.evio
cp -v data_link.evio data.evio

# config
# disabled = FCAL_TimingOffsets,BCAL_point_calib
#CALIB_PLUGINS=evio_writer,HLDetectorTiming,BCAL_attenlength_gainratio,CDC_amp,CDC_TimeToDistance,FCALpedestals,ST_Propagation_Time,imaging,pedestals,BCAL_LED,FCALpulsepeak,pi0fcalskim,pi0bcalskim,ps_skim,BCAL_inv_mass,p2pi_hists,p3pi_hists,trigger_skims,TOF_calib,BCAL_point_calib,BCAL_TDC_Timing,TrackingPulls
CALIB_PLUGINS=evio_writer,HLDetectorTiming,BCAL_attenlength_gainratio,CDC_amp,CDC_TimeToDistance,FCALpedestals,ST_Propagation_Time,imaging,pedestals,BCAL_LED,FCALpulsepeak,pi0fcalskim,pi0bcalskim,ps_skim,BCAL_inv_mass,p2pi_hists,p3pi_hists,trigger_skims,TOF_calib,TrackingPulls
CALIB_OPTIONS=" -PHLDETECTORTIMING:DO_VERIFY=1 "
PASSFINAL_OUTPUT_FILENAME=hd_calib_final_Run${RUN}_${FILE}.root
# run
echo ==validation pass==
echo Running these plugins: $CALIB_PLUGINS
#hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASSFINAL_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASSFINAL_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS ./data.evio
retval=$?

# save results
swif outfile $PASSFINAL_OUTPUT_FILENAME file:${OUTPUTDIR}/hists/Run${RUN}/$PASSFINAL_OUTPUT_FILENAME
# skims
#set SKIM_DIR=/cache/halld/${RUNPERIOD}/calib/${WORKFLOW}/
#SKIM_DIR=/cache/halld/${RUNPERIOD}/calib/pass2/  ## FIX
SKIM_DIR=$OUTPUTDIR
mkdir -p $SKIM_DIR
#
mkdir -p ${SKIM_DIR}/BCAL_pi0/Run${RUN}
swif outfile data.pi0bcalskim.evio file:${SKIM_DIR}/BCAL_pi0/Run${RUN}/hd_rawdata_${RUN}_${FILE}.pi0bcalskim.evio
mkdir -p ${SKIM_DIR}/FCAL_pi0/Run${RUN}
swif outfile data.pi0fcalskim.evio file:${SKIM_DIR}/FCAL_pi0/Run${RUN}/hd_rawdata_${RUN}_${FILE}.pi0fcalskim.evio
mkdir -p ${SKIM_DIR}/PS/Run${RUN}
swif outfile data.ps.evio file:${SKIM_DIR}/PS/Run${RUN}/hd_rawdata_${RUN}_${FILE}.ps.evio
mkdir -p ${SKIM_DIR}/TOF/Run${RUN}
swif outfile hd_root_tofcalib.root file:${SKIM_DIR}/TOF/Run${RUN}/hd_root_tofcalib_${RUN}_${FILE}.root
mkdir -p ${SKIM_DIR}/BCAL-LED/Run${RUN}
swif outfile data.BCAL-LED.evio file:${SKIM_DIR}/BCAL-LED/Run${RUN}/hd_rawdata_${RUN}_${FILE}.BCAL-LED.evio
mkdir -p ${SKIM_DIR}/FCAL-LED/Run${RUN}
swif outfile data.FCAL-LED.evio file:${SKIM_DIR}/FCAL-LED/Run${RUN}/hd_rawdata_${RUN}_${FILE}.FCAL-LED.evio
mkdir -p ${SKIM_DIR}/sync/Run${RUN}
swif outfile data.sync.evio file:${SKIM_DIR}/sync/Run${RUN}/hd_rawdata_${RUN}_${FILE}.sync.evio
mkdir -p ${SKIM_DIR}/random/Run${RUN}
swif outfile data.random.evio file:${SKIM_DIR}/random/Run${RUN}/hd_rawdata_${RUN}_${FILE}.random.evio
#swif outfile tree_p2gamma_hists.root file:${SKIM_DIR}/tree_p2gamma_hists_${RUN}_${FILE}.root

exit $retval
