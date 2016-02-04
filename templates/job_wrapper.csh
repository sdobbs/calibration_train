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

setenv FILE $4
if( $FILE == "" ) then
    echo Need to pass file number as fourth argument!
    exit 1
endif

setenv NTHREADS $5
if( $NTHREADS == "" ) then
    set NTHREADS 1
endif

# copy files over
cp -vR $BASEDIR/scripts/* .

echo ==initial environment==
env
echo ==initial files==
ls -lh

# setup standard environment
source setup_jlab.csh

# setup calibration configuration inside in each job
unsetenv CCDB_CONNECTION
unsetenv JANA_CALIB_URL
unsetenv JANA_CALIB_CONTEXT
# 
setenv CALIB_LIBDIR /work/halld/home/sdobbs/calib_lib
setenv CALIB_CCDB_SQLITE_FILE   # use local SQLite files
#setenv CALIB_CCDB_SQLITE_FILE /home/gxproj3/calib_challenge/ccdb.sqlite
#setenv CALIB_DEBUG
setenv CALIB_SUBMIT_CONSTANTS

echo ==printing environment==
env

# do the work
echo ==running command: $CALIB_COMMAND==
./${CALIB_COMMAND}

# check results
set retval=$?
echo exit code: $retval
if( $retval == 0 ) then
    echo "DONE:SUCCESS"
else
    echo "DONE:FAILURE"
endif

echo ==ls -lhR after all processing==
ls -lhR

exit $retval
