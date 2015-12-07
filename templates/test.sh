#!/bin/bash

echo ==printing environment==
env

echo ==first argument==
echo $1

if [ -z $1 ]; then
    echo Need to pass base directory as first argument!
    exit 1
fi

if [ -z $2 ]; then
    echo Need to pass run number as second argument!
    exit 1
fi

if [ -z $3 ]; then
    echo Need to pass file number as third argument!
    exit 1
fi

set basedir=$1
set run=$2
set file=$3

echo ==hi there!==
ls -lh

ls -lh > ls-lh

#swif outfile ls-lh file:${basedir}/output/ls-lh.Run${run}.${file}

exit 0
