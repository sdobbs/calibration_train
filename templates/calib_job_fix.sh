#!/bin/bash

# copy input file to local disk - SWIF only sets up a symbolic link to it
echo ==copy in file==
mv data.evio data_link.evio
cp -v data_link.evio data.evio
ls -lh data.evio

# calibrate RF
./file_calib_pass0.sh

# make sure that we create an SQLite file
$CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass0.sqlite
cp -v ccdb_pass0.sqlite ccdb_pass1.sqlite
#cp -v ccdb_pass0.sqlite ccdb_pass2.sqlite

# run the rest of the calibrations
./file_calib_pass1.sh
./run_calib_pass1.sh
#./file_calib_pass1.5.sh
#./run_calib_pass1.5.sh
./file_calib_pass2.sh
./run_calib_pass2.sh
./run_calib_verify.sh

# need to debug SQLite creation
#$CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass2.sqlite
#cp ccdb_pass2.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite
