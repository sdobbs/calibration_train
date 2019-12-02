#!/usr/bin/env python
# 
# Script for running online calibrations
# Author: Sean Dobbs (sdobbs@jlab.org), 2018
#
# DB: mysql -h hallddb -u calibInformer calibInfo
#
# mysql> describe online_info; 
# +---------------+------------+------+-----+---------+-------+
# | Field         | Type       | Null | Key | Default | Extra |
# +---------------+------------+------+-----+---------+-------+
# | run           | int(11)    | YES  |     | NULL    |       |
# | done          | tinyint(1) | YES  |     | NULL    |       |
# | rcdb_update   | tinyint(1) | YES  |     | NULL    |       |
# | launched_skim | tinyint(1) | YES  |     | NULL    |       |
# +---------------+------------+------+-----+---------+-------+
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
import multiprocessing
import glob
from optparse import OptionParser
import rcdb
import ccdb


def ProcessFilePass1(args):
    host_mapping = { 0: "gluon105", 1: "gluon106", 2: "gluon107" }

    run = args[0]
    fnum = args[1]
    cwd = args[2]

    print "sshing to %s"%host_mapping[fnum]
    cmd = "ssh %s 'cd %s; ./file_calib_pass1-primex.sh %06d %03d'"%(host_mapping[fnum],cwd,run,fnum)
    if DRY_RUN:
        print cmd
    else:
        os.system(cmd)


tagger_rr_ind = 0

#def ProcessTaggerCalibrations(args):
def ProcessTaggerCalibrations(run,cwd):
    global tagger_rr_ind
    #run = args[0]
    #cwd = args[1]

    #hosts = ["gluon111", "gluon112", "gluon113", "gluon114", "gluon115", "gluon116" ]
    hosts = [ "gluon112", "gluon113", "gluon114", "gluon115", "gluon116" ]
    hostname = hosts[tagger_rr_ind]
    if tagger_rr_ind+1 >= len(hosts):
        tagger_rr_ind = 0
    else:
        tagger_rr_ind += 1

    #cmd = "do_tagger.sh %d"%(run)
    cmd = "ssh %s 'cd %s; ./do_tagger.sh %d' > %s/log/calib.tagger.r%d.log"%(hostname,cwd,run,'/gluonwork1/Users/sdobbs/calibration_train/online',run)
    if DRY_RUN:
        print cmd
    else:
        #os.system(cmd)
        subprocess.call(cmd, shell=True)

def ProcessTest():
    cmd = "ssh gluon111 'ls -lh' > %s/log/test.r%d.log"%('/gluonwork1/Users/sdobbs/calibration_train/online',0)
    subprocess.call(cmd, shell=True)

def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "hdsys"  # to have a name in logs

    return provider

def get_fieldmap(current):
    if current < 30.:
        return "NoField"
    elif current > 1570:
        return "solenoid_1600A_poisson_20160222"
    else:
        ccdb_currents =  [ 50*(i+1) for i in xrange(31) ]
        delta = 1000000.
        best_current = 30.
        for el in xrange(len(ccdb_currents)):
            if abs(current-ccdb_currents[el]) < delta:
                best_current = ccdb_currents[el]
                delta = abs(current-ccdb_currents[el])
        return "solenoid_%04dA_poisson_20160222"%best_current

def get_solenoid_current(rcdb_conn, run):
    return rcdb_conn.get_condition(run, "solenoid_current").value


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
    RUN_PERIOD       = 'RunPeriod-2019-01'
    #RCDB_PRODUCTION_SEARCH = "@is_2018production"
    RCDB_PRODUCTION_SEARCH = "daq_run == 'PHYSICS_PRIMEX' and event_count > 1000000 and collimator_diameter != 'Blocking'"
    #RCDB_PRODUCTION_SEARCH = "daq_config in ['FCAL_BCAL_PS_DIRC_m9.conf', 'FCAL_BCAL_PS_DIRC_m10.conf']  and event_count > 10000000"
    #RCDB_SEARCH_MIN  = 40000
    #RCDB_SEARCH_MIN  = 41857
    RCDB_SEARCH_MIN  = 60550
    RCDB_SEARCH_MAX  = 70000
    GLUONRAID = "gluonraid2"

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

    ## SSH TESTS
    #p = multiprocessing.Process(target=ProcessTest, args=())
    #p = multiprocessing.Process(target=ProcessTaggerCalibrations, args=(52715,os.getcwd()))
    #p.start()
    ##p.join()
    #tagger_threads.append(p)

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

    print "%d %d"%(RUN_MIN,RUN_MAX)

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
        
    tagger_threads = []
        
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
            query = "INSERT INTO online_info (run,done,rcdb_update,launched_skim) VALUES (%s,FALSE,FALSE,FALSE)"%run
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

        query = "SELECT rcdb_update FROM online_info WHERE run='%s'"%run 
        calibdb_cursor.execute(query)
        rcdb_info = calibdb_cursor.fetchone()
        if run_info is None or run_info[0] is None:
            print "Problem accessing DB (rcdb_update), skipping run..."
        else:
            if rcdb_info[0]==0:
                # update some CCDB info
                ccdb_conn = LoadCCDB()
                solenoid_map_assignment = ccdb_conn.get_assignment("/Magnets/Solenoid/solenoid_map", run, "default")
                current_solenoid_map = solenoid_map_assignment.constant_set.data_table[0][0]

                solenoid_current = get_solenoid_current(rcdb_conn, run)
                new_solenoid_map = "Magnets/Solenoid/"+get_fieldmap(solenoid_current)

                print " old solenoid map = %s   new solenoid map = %s"%(current_solenoid_map,new_solenoid_map)

                if not DRY_RUN and current_solenoid_map != new_solenoid_map:
                    print "Updating solenoid map!"
                    print "not yet"
                    """
                    ccdb_conn.create_assignment(
                        data=[[new_solenoid_map]],
                        path="/Magnets/Solenoid/solenoid_map",
                        variation_name="default",
                        min_run=run,
                        max_run=ccdb.INFINITE_RUN,
                        comment="Online updates based on RCDB")

                    #if not DRY_RUN:
                    query = "UPDATE online_info SET rcdb_update=TRUE WHERE run='%s'"%run
                    calibdb_cursor.execute(query)            
                    calibdb_cnx.commit()
                    """
        #continue

        # check to make sure that the first file exists, to correctly handle the current run
        if not os.path.exists("/%s/rawdata/volatile/%s/rawdata/Run%06d/hd_rawdata_%06d_000.evio"%(GLUONRAID,RUN_PERIOD,run,run)):
            print "Cant't find /%s/rawdata/volatile/%s/rawdata/Run%06d/hd_rawdata_%06d_000.evio"%(GLUONRAID,RUN_PERIOD,run,run)
            continue
        # and I guess the other two?  we need to run multiple processes, it's easier if we are running over multiple files
        # or maybe handle short runs?  be more smart about this

        # do calibrations
        rundir = "%s/Run%06d"%(BASE_DIR,run)
        if not os.path.exists(rundir):
            os.makedirs(rundir)
        os.chdir(rundir)
        os.system("cp -v %s/*.sh %s"%(SCRIPT_DIR,rundir))
        os.system("cp -v %s/*.py %s"%(SCRIPT_DIR,rundir))
        os.system("cp -v %s/*.C %s"%(SCRIPT_DIR,rundir))
        os.system("cp -v %s/online_ccdb_tables_to_push %s"%(SCRIPT_DIR,rundir))
        os.system("cp -v %s/online_ccdb_tables_to_push.tagm %s"%(SCRIPT_DIR,rundir))
        os.system("ln -s /%s/rawdata/volatile/%s/rawdata/Run%06d ./data"%(GLUONRAID,RUN_PERIOD,run))

        # calibrate RF
        cmd = "./file_calib_pass0.sh %06d"%run
        # write log file!
        if DRY_RUN:
            print cmd
        else:
            os.system(cmd)

        # run over one file, adjust timing alignments
        # plugins: HLDetectorTiming, CDC_amp, TOF_TDC_shift
        p = multiprocessing.Pool(3)
        args = []
        args.append( (run, 0, os.getcwd()) )
        args.append( (run, 1, os.getcwd()) )
        args.append( (run, 2, os.getcwd()) )
        p.map(ProcessFilePass1, args)

        # merge and run over the results
        # write log file!
        cmd = "./run_calib_pass1-primex.sh %06d %s"%(run,os.getcwd())
        if DRY_RUN:
            print cmd
        else:
            os.system(cmd)

        # start up tagger calibrations
        # TAGH timewalks depend on HLDT (ADC/TDC alignment)
        ptag = multiprocessing.Process(target=ProcessTaggerCalibrations, args=(run,os.getcwd()))
        ptag.start()
        tagger_threads.append(ptag)
                  
        # update calibration status
        if not DRY_RUN:
            query = "UPDATE online_info SET done=TRUE WHERE run='%s'"%run
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
    for thr in tagger_threads:
        thr.join()
