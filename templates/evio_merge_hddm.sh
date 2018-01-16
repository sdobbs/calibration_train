#!/bin/bash
# Do a second pass of calibrations on an EVIO file

export BASEDIR=$1
if [ -z  $BASEDIR ]; then
    echo Need to pass base directory as first argument!
    exit 1
fi

export RUN_PERIOD=$2
if [ -z  $RUN_PERIOD ]; then
    echo Need to pass run period as second argument!
    exit 1
fi

export VERSION=$3
if [ -z  $VERSION ]; then
    echo Need to pass version as third argument!
    exit 1
fi

export RUN=$4
if [ -z  $RUN ]; then
    echo Need to pass run number as fourth argument!
    exit 1
fi

cp -vR $BASEDIR/scripts/* .

echo ==initial environment==
env
echo ==initial files==
ls -lh

# setup standard environment
source ./setup_jlab.sh

export NTHREADS=12

# initialize CCDB before running
export CCDB_CONNECTION=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
export JANA_CALIB_URL=mysql://ccdb_user@hallddb.jlab.org/ccdb    # save results in MySQL
export VARIATION=default
export JANA_CALIB_CONTEXT="variation=$VARIATION" 

RUNNUM=`echo ${RUN} | awk '{printf "%d\n",$0;}'`

# config
CALIB_PLUGINS=evio-hddm
CALIB_OPTIONS=" "
OUTPUT_FILENAME=/cache/halld/RunPeriod-${RUN_PERIOD}/sim/random_triggers/run${RUN}_random.hddm
# run
echo ==second pass==
echo Running these plugins: $CALIB_PLUGINS
hd_root --nthreads=$NTHREADS  -PEVIO:RUN_NUMBER=${RUNNUM} -PJANA:BATCH_MODE=1 -PPRINT_PLUGIN_PATHS=1 -PTHREAD_TIMEOUT=300 -POUTPUT_FILENAME=$OUTPUT_FILENAME -PPLUGINS=$CALIB_PLUGINS $CALIB_OPTIONS /cache/halld/RunPeriod-${RUN_PERIOD}/calib/${VERSION}/PS/Run${RUN}/*.evio
retval=$?

echo exit code: $retval
if [ "$retval" -eq "0" ]; then
    echo "DONE:SUCCESS"
else
    echo "DONE:FAILURE"
fi

echo ==ls -lhR after all processing==
ls -lhR

exit $retval

