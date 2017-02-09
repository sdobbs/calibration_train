#!/bin/bash
./file_calib_pass0.sh
./file_calib_pass1.sh
./run_calib_pass1.sh
./file_calib_pass1.5.sh
./run_calib_pass1.5.sh
./file_calib_pass2.sh
./run_calib_pass2.sh

#    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass0.sqlite
cp ccdb_pass2.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite
