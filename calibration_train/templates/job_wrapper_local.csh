#!/bin/tcsh
# Wrapper script for calibration jobs
#
# Parse arguments
#
setenv CALIB_COMMAND $1
if( $CALIB_COMMAND == "" ) then
    echo Need to pass command name as first argument!
    exit 1
endif

setenv BASEDIR $2
if( $BASEDIR == "" ) then
    echo Need to pass base directory as second argument!
    exit 1
endif

setenv RUN $3
if( $RUN == "" ) then
    echo Need to pass run number as third argument!
    exit 1
endif

setenv FILES $4
if( $FILE == "" ) then
    echo Need to pass file paths as fourth argument!
    exit 1
endif

setenv NTHREADS $5
if( $NTHREADS == "" ) then
    set NTHREADS 1
endif

# copy files over
cp -v $BASEDIR/scripts/* .

echo ==initial environment==
env
echo ==initial files==
ls -lh

# setup standard environment
source setup_jlab.csh

# setup local CCDB copy
cp $BASEDIR/ccdb.sqlite .
setenv JANA_CALIB_URL  sqlite:///`pwd`/ccdb.sqlite 
setenv CCDB_CONNECTION sqlite:///`pwd`/ccdb.sqlite 
setenv JANA_CALIB_CONTEXT "calibtime=2015-10-01"    ## update!
# 
setenv CALIB_LIBDIR /work/halld/home/sdobbs/calib_lib

echo ==printing environment==
env

# do the work
echo ==running command: $CALIB_COMMAND==
./${CALIB_COMMAND}

# check results
set status=$?
if( status == 0 ) then
    echo "DONE:SUCCESS"
else
    echo "DONE:FAILURE"
endif

echo ==ls after all processing==
ls -lh

exit $status
