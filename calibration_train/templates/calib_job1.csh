#!/bin/tcsh 
./file_calib_pass0.csh
./file_calib_pass1.csh
./run_calib_pass1.csh
./file_calib_pass1.5.csh
./run_calib_pass1.5.csh
./file_calib_pass2.csh
./run_calib_pass2.csh

#    $CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 ccdb_pass0.sqlite
cp ccdb_pass2.sqlite ${BASEDIR}/sqlite_ccdb/ccdb_pass1.${RUN}.sqlite
