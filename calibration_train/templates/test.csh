#!/bin/tcsh

echo ==printing environment==
env

echo ==first argument==
echo $1

set basedir=$1
if( $basedir == "" ) then
    echo Need to pass base directory as first argument!
    exit 1
endif

set run=$2
if( $run == "" ) then
    echo Need to pass run number as second argument!
    exit 1
endif

set file=$3
if( $file == "" ) then
    echo Need to pass file number as third argument!
    exit 1
endif

echo ==hi there!==
ls -lh

ls -lh > ls-lh

swif outfile ls-lh file:${basedir}/output/ls-lh.Run${run}.${file}

exit 0
