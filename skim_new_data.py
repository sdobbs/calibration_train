#!/usr/bin/env python
#
# Script for skimming data as it hits tape
# Assumes that basic calibrations are done online, checks a DB for this
#
# Author: Sean Dobbs (sdobbs@jlab.org), 2018
#
#


import mysql.connector
from mysql.connector import errorcode
import sys, os
from optparse import OptionParser
import rcdb
import pprint
import glob

# this part gets executed when this file is run on the command line 
if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    SCRIPT_DIR = "/home/gxproj3/calibration_train"
    RUNPERIOD = "2019-11"

    # Parse command line arguments
    CALIBDB_HOST     = 'hallddb'
    CALIBDB_USER     = 'calibInformer'
    CALIBDB_NAME     = 'calibInfo'
    RCDB_FILENAME    = ''
    RCDB_HOST        = 'hallddb'
    RCDB_USER        = 'rcdb'
    #RCDB_PASS        = 'GlueX_2come'
    RCDB_PASS        = ''
    RUNS             = ''
    RCDB_PRODUCTION_SEARCH = "@is_dirc_production"
    #RCDB_PRODUCTION_SEARCH = 'daq_config=="FCAL_BCAL_PS_DIRC_m9.conf" or daq_config=="FCAL_BCAL_PS_DIRC_m10.conf"'
    RCDB_SEARCH_MIN  = 70100  ## NEED TO FIX THESE RANGES
    RCDB_SEARCH_MAX  = 79000
    #RCDB_SEARCH_MIN  = 50000
    #RCDB_SEARCH_MAX  = 70000
    DRY_RUN          = False

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

    #print "HI"
    print RUN_MIN," ",RUN_MAX
    print RCDB_SEARCH_MIN," ",RCDB_SEARCH_MAX



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

    print RCDB_RUNS
    print RCDB_PRODUCTION_RUNS

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
            print "Run %d not in tracking DB, skipping..."%run

        # see if the run has been processed already
        query = "SELECT done,launched_skim FROM online_info WHERE run='%s'"%run 
        calibdb_cursor.execute(query)
        run_info = calibdb_cursor.fetchone()
        if run_info is None or run_info[0] is None:
            # TEMP, just add in the run
            query = "INSERT INTO online_info (run,done,rcdb_update,launched_skim) VALUES (%s,FALSE,FALSE,FALSE)"%run
            calibdb_cursor.execute(query)
            calibdb_cnx.commit()

            #print "Problem accessing DB, skipping run..."
            #continue


        # TEMP - assume online calibrations are fine, and run anyway
        """
        # check status of runs
        if run_info[0]==0:
            print "Run still being calibrated online ..."
            continue
        if run_info[1] is not None and run_info[1]==1:
            print "Already processed this run, skipping..."
            continue
        """

        if DRY_RUN:
            print "Skim run %d"%run
            continue

        # make SQLite CCDB
        os.system("$CCDB_HOME/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 /work/halld/home/gxproj3/calib_jobs/RunPeriod-%s/sqlite_ccdb/ccdb_pass1.%06d.sqlite"%(RUNPERIOD,run))

        # now actually start the skim jobs
        filelist = glob.glob("/mss/halld/RunPeriod-%s/rawdata/Run%06d/*.evio"%(RUNPERIOD,run))
        fnums = sorted([ int(num[-8:-5]) for num in filelist ])

        for fnum in fnums:            
            cmd = "python HDSubmitCalibJobSWIF.py configs/data.config %s pass2 %d %d"%(RUNPERIOD,run,fnum)
            if DRY_RUN:
                print "run: "+cmd
            else:
                os.system(cmd)

        # update calibration status
        if not DRY_RUN:
            query = "UPDATE online_info SET launched_skim=TRUE WHERE run='%s'"%run
            print query
            calibdb_cursor.execute(query)
            calibdb_cnx.commit()

        # see if we should stop earlier
        if os.path.exists("%s/force.stop"%SCRIPT_DIR):
            print "stopping early..."
            break

    # finish and clean up
    calibdb_cursor.close()
    calibdb_cnx.close()
