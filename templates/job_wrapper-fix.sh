#!/bin/bash
# Wrapper script for calibration jobs
#
# Parse arguments
#
export CALIB_COMMAND=$1
if [ -z  $CALIB_COMMAND ]; then
    echo Need to pass command name as first argument!
    exit 1
fi

export BASEDIR=$2
if [ -z  $BASEDIR ]; then
    echo Need to pass base directory as second argument!
    exit 1
fi

export RUN=$3
if [ -z  $RUN ]; then
    echo Need to pass run number as third argument!
    exit 1
fi

export FILE=$4
if [ -z  $FILE ]; then
    echo Need to pass file number as fourth argument!
    exit 1
fi

export NTHREADS=$5
if [ -z  $NTHREADS ]; then
    export NTHREADS 1
fi

#export WORKFLOW=$5
#if [ -z  $WORKFLOW == "" ]; then
#    echo Need to pass workflow as fifth argument!
#    exit 1
#fi

####### CONFIGURATION PARAMETERS ######

export RUNPERIOD=RunPeriod-2018-01
export VERSION=ver02

######################################

# copy files over
cp -vR $BASEDIR/scripts/* .

echo ==initial environment==
env
echo ==initial files==
ls -lh

# setup standard environment
source ./setup_jlab.sh

# setup calibration configuration inside in each job
unset CCDB_CONNECTION
unset JANA_CALIB_URL
unset JANA_CALIB_CONTEXT
#
# ROOT files
#export OUTPUTDIR         /cache/halld/${RUNPERIOD}/calib/${WORKFLOW}/
export OUTPUTDIR=/cache/halld/${RUNPERIOD}/calib/${VERSION}
#export SMALL_OUTPUTDIR=/work/halld2/home/${USER}/calib_jobs/${RUNPERIOD}/${VERSION}
export SMALL_OUTPUTDIR=/work/halld2/calibration/${RUNPERIOD}/${VERSION}
export SQLITEDIR=/volatile/halld/home/${USER}/calib_jobs/${RUNPERIOD}/${VERSION}
#
export CALIB_LIBDIR=/work/halld/home/${USER}/calib_lib
#export CALIB_CCDB_SQLITE_FILE   # use local SQLite files
#export CALIB_CCDB_SQLITE_FILE /home/gxproj3/calib_challenge/ccdb.sqlite
#export CALIB_DEBUG
export CALIB_SUBMIT_CONSTANTS="yes"
#export CALIB_CHALLENGE

echo ==printing environment==
env

echo ==check python version==
which python

# do the work
echo ==running command: $CALIB_COMMAND==
./${CALIB_COMMAND}

# check results
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
