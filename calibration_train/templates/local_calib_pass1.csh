#!/bin/tcsh
# Do a first pass of calibrations on an EVIO file

# config
set CALIB_PLUGINS=RF_online
set PASS1_OUTPUT_FILENAME=hd_calib_pass1_Run${RUN}_${FILE}.root
# run
echo ==first pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$PASS1_OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $FILES

# process the results
python run_calib_pass1.py $RUN_OUTPUT_FILENAME


