#!/bin/tcsh
# Do an initial output of calibrations on an EVIO file

###################################################

# do some pre-processing for tasks that need a small number of events
# config
set NEVENTS_ZEROTH_PASS=100000
set ZEROTH_CALIB_PLUGINS=RF_online
set PASS0_OUTPUT_FILENAME=hd_calib_pass0_Run${RUN}.root
# run
echo ==zeroth pass==
echo Running these plugins: $ZEROTH_CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS0_OUTPUT_FILENAME -PEVENTS_TO_KEEP=$NEVENTS_ZEROTH_PASS -PPLUGINS=$ZEROTH_CALIB_PLUGINS ${FILES}
# save results
cp $PASS0_OUTPUT_FILENAME file:${BASEDIR}/output/Run${RUN}/$PASS0_OUTPUT_FILENAME

###################################################

# process the results
python run_calib_pass0.py $PASS0_OUTPUT_FILENAME

# register output
