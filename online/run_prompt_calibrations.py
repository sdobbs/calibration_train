#!/usr/bin/env python
# 
# Script for running online calibrations
# Author: Sean Dobbs (sdobbs@jlab.org), 2018
#
# DB: mysql -h hallddb -u calibInformer calibInfo
#
# mysql> describe online_info;
#+-------+------------+------+-----+---------+-------+
#| Field | Type       | Null | Key | Default | Extra |
#+-------+------------+------+-----+---------+-------+
#| run   | int(11)    | YES  |     | NULL    |       |
#| done  | tinyint(1) | YES  |     | NULL    |       |
#+-------+------------+------+-----+---------+-------+
#
#


import mysql.connector
from mysql.connector import errorcode
import sqlite3 as lite
import sys
import os
import re
import datetime
import time
import subprocess
import glob
from optparse import OptionParser
import rcdb
import ccdb




# this part gets executed when this file is run on the command line 
if __name__ == "__main__":

    # Parse command line arguments
    CALIBDB_HOST     = 'hallddb'
    CALIBDB_USER     = 'calibInformer'
    CALIBDB_NAME     = 'calibInfo'
    RCDB_FILENAME    = ''
    #RCDB_HOST        = 'hallddb'
    RCDB_HOST        = 'gluondb1'
    RCDB_USER        = 'rcdb'
    RCDB_PASS        = 'GlueX_2come'
    #RCDB_PASS        = ''
    RUNS             = ''
    RUN_PERIOD       = 'RunPeriod-2018-01'
    RCDB_PRODUCTION_SEARCH = "@is_2018production"
    RCDB_SEARCH_MIN  = 40000
    RCDB_SEARCH_MAX  = 50000

    SCRIPT_DIR = "/gluonwork1/Users/sdobbs/calibration_train/online"
    BASE_DIR = "/gluonwork1/Users/sdobbs/calibrations/%s"%RUN_PERIOD
    DRY_RUN = False

    parser = OptionParser(usage = "run_prompt_calibrations.py ")
    parser.add_option("-Y", dest="dry_run", action="store_true",
                      help="Don't actually run any commands")
    (options, args) = parser.parse_args(sys.argv)
    if options.dry_run:
        DRY_RUN = True

    if(len(args) > 1):
        RUNS=args[1]

    # Connect to RCDB
    try:
        if RCDB_FILENAME=='':
            # MySQL RCDB server
            RCDB = 'mysql://' + RCDB_USER + ':' + RCDB_PASS + '@' + RCDB_HOST + '/rcdb'
            cnx = mysql.connector.connect(user=RCDB_USER, password=RCDB_PASS, host=RCDB_HOST, database='rcdb')
            #cnx = mysql.connector.connect(user=RCDB_USER, host=RCDB_HOST, database='rcdb')
            cur = cnx.cursor()  
            #cur = cnx.cursor(dictionary=True)  # make dictionary style cursor
        else:
            # SQLite RCDB file
            RCDB = RCDB_FILENAME
            con = lite.connect(RCDB_FILENAME)
            con.row_factory = lite.Row  # make next cursor dictionary style
            cur = con.cursor()
    except Exception as e:
        print 'Error connectiong to RCDB: ' + RCDB
        print str(e)
        sys.exit(-1)

    # Get run range to process
    if '-' in RUNS:
        pos = RUNS.find('-')
        if len(RUNS[0:pos]) > 0:
            RUN_MIN = int(RUNS[0:pos])
        else:
            RUN_MIN = RCDB_SEARCH_MIN
        if len(RUNS[pos+1:]) > 0:
            RUN_MAX = int(RUNS[pos+1:])
        else:
            RUN_MAX = RCDB_SEARCH_MAX
    elif RUNS!='':
        RUN_MIN = RUNS
        RUN_MAX = RUNS
    else:
        # No run range given. Find it for last day
        sql = 'SELECT min(number) AS RUN_MIN,max(number) AS RUN_MAX FROM runs WHERE '
        if RCDB.startswith('mysql') :
            sql += 'UNIX_TIMESTAMP(NOW())-UNIX_TIMESTAMP(finished) <24*3600'
        else:
            sql += 'strftime("%s","now")-strftime("%s",finished) <24*3600'
        cur.execute(sql)
        c_rows = cur.fetchall()
        if len(c_rows)==0 :
            print 'No runs specified and unable to find any in DB for last 24 hours'
            sys.exit(0)
        RUN_MIN = c_rows[0][0]
        RUN_MAX = c_rows[0][1]
        print 'No run range specified. Processing runs completed in last 24 hours: ' + str(RUN_MIN) + '-' + str(RUN_MAX)


    # select list of runs from RCDB
    RCDB_RUNS = []
    sql = 'SELECT number FROM runs WHERE number >= %d AND number <= %d'%(RUN_MIN,RUN_MAX)
    cur.execute(sql)
    c_rows = cur.fetchall()
    if len(c_rows)==0 :
        print 'No runs found in the specified run range'
        sys.exit(0)

    RCDB_RUNS = [ c_rows[row][0] for row in xrange(len(c_rows)) ]

    # pull list of production runs
    rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb/rcdb")
    runs = rcdb_conn.select_runs(RCDB_PRODUCTION_SEARCH, RCDB_SEARCH_MIN, RCDB_SEARCH_MAX)
    RCDB_PRODUCTION_RUNS = [ run.number for run in runs ]

    # connect to calibration tracking DB
    try:
        calibdb_cnx = mysql.connector.connect(user=CALIBDB_USER, 
                                              host=CALIBDB_HOST,
                                              database=CALIBDB_NAME)
        calibdb_cursor = calibdb_cnx.cursor()
    except mysql.connector.Error as err:
        #if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        #    print("Something is wrong with your user name or password")
        #elif err.errno == errorcode.ER_BAD_DB_ERROR:
        #    print("Database does not exist")
        #else:
        print(err)
    #else:
    #    print "Problem opening calibration tracking DB, exiting..."
    #    calibdb_cnx.close()
    #    sys.exit(0)
        

    for run in RCDB_RUNS:
        print "Processing Run %d"%run
        if not run in RCDB_PRODUCTION_RUNS:
            print "Not a production run, skipping..."
            continue

        # make sure run is in calibration tracking DB
        query = "SELECT run FROM online_info WHERE run='%s'"%run 
        calibdb_cursor.execute(query)
        run_info = calibdb_cursor.fetchone()
        if run_info is None or run_info[0] is None:
            query = "INSERT INTO online_info (run,done) VALUES (%s,FALSE)"%run
            calibdb_cursor.execute(query)
            calibdb_cnx.commit()

        # see if the run has been processed already
        query = "SELECT done FROM online_info WHERE run='%s'"%run 
        calibdb_cursor.execute(query)
        run_info = calibdb_cursor.fetchone()
        if run_info is None or run_info[0] is None:
            print "Problem accessing DB, skipping run..."
            continue
        if run_info[0]==1:
            print "Already processed this run, skipping..."
            continue

        # check to make sure that the first file exists, to correctly handle the current run
        if not os.path.exists("/gluonraid2/rawdata/volatile/%s/rawdata/Run%06d/hd_rawdata_%06d_000.evio"%(RUN_PERIOD,run,run)):
            continue

        # do calibrations
        rundir = "%s/Run%06d"%(BASE_DIR,run)
        if not os.path.exists(rundir):
            os.makedirs(rundir)
        os.chdir(rundir)
        os.system("cp -v %s/*.sh %s"%(SCRIPT_DIR,rundir))
        os.system("cp -v %s/*.py %s"%(SCRIPT_DIR,rundir))
        os.system("cp -v %s/online_ccdb_tables_to_push %s"%(SCRIPT_DIR,rundir))
        os.system("ln -s /gluonraid2/rawdata/volatile/%s/rawdata/Run%06d ./data"%(RUN_PERIOD,run))

        # calibrate RF
        cmd = "./file_calib_pass0.sh %06d"%run
        if DRY_RUN:
            print cmd
        else:
            os.system(cmd)

        # run over one file, adjust timing alignments
        # plugins: HLDetectorTiming, CDC_amp, TOF_TDC_shift
        cmd = "./file_calib_pass1.sh %06d"%run
        if DRY_RUN:
            print cmd
        else:
            os.system(cmd)
        cmd = "./run_calib_pass1.sh %06d"%run
        if DRY_RUN:
            print cmd
        else:
            os.system(cmd)
                  
        # update calibration status
        if not DRY_RUN:
            query = "UPDATE online_info SET done=TRUE WHERE run='%s'"%run
            calibdb_cursor.execute(query)
        

    # finish and clean up
    calibdb_cursor.close()
    calibdb_cnx.close()
