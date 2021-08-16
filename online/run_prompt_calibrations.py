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
from epics import caget,caput

def ProcessFilePass1(args):
    host_mapping = { 0: "gluon122", 1: "gluon123", 2: "gluon124" }

    run = args[0]
    fnum = args[1]
    cwd = args[2]

    print "sshing to %s"%host_mapping[fnum]
    cmd = "ssh %s 'cd %s; ./file_calib_pass1.sh %06d %03d'"%(host_mapping[fnum],cwd,run,fnum)
    if DRY_RUN:
        print cmd
    else:
        retval = os.system(cmd)
        if(retval != 0):
            print "ERROR in run %d file_calib_pass1.sh(%d): %d"%(run,fnum,retval)


tagger_rr_ind = 0

#def ProcessTaggerCalibrations(args):
def ProcessTaggerCalibrations(run,cwd):
    global tagger_rr_ind
    #run = args[0]
    #cwd = args[1]

    hosts = [ "gluon125", "gluon105", "gluon106", "gluon107" ]
    hostname = hosts[tagger_rr_ind]

    # do round robining of hosts
    tagger_rr_ind = tagger_rr_ind + 1
    if tagger_rr_ind >= len(hosts):
        tagger_rr_ind = 0
    else:
        tagger_rr_ind += 1

    #cmd = "do_tagger.sh %d"%(run)
    cmd = "ssh %s 'cd %s; ./do_tagger.sh %d' >& %s/log/calib.tagger.r%d.log"%(hostname,cwd,run,'/gluonwork1/Users/sdobbs/calibration_train/online',run)
    if DRY_RUN:
        print cmd
    else:
        #os.system(cmd)
        #retval = subprocess.call(cmd, shell=True)  # wait until command is done
        retval = subprocess.Popen(cmd, shell=True)  # let process run in the background
        #if(retval != 0):
        #    print "ERROR in run %d do_tagger.sh: %d"%(run,retval)

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

def update_cdc_gains(ccdb_conn, run):
    TOLERANCE = 1.e-5  # constant used for comparisons

    # get info from EPICS
    #print caget("RESET:i:GasPanelBarPress1")
    cdc_pressure = float(caget("RESET:i:GasPanelBarPress1"))
    cdc_temp_1 = float(caget("GAS:i::CDC_Temps-CDC_D1_Temp"))
    cdc_temp_2 = float(caget("GAS:i::CDC_Temps-CDC_D2_Temp"))
    cdc_temp_3 = float(caget("GAS:i::CDC_Temps-CDC_D3_Temp"))
    cdc_temp_4 = float(caget("GAS:i::CDC_Temps-CDC_D4_Temp"))
    cdc_temp_5 = float(caget("GAS:i::CDC_Temps-CDC_D5_Temp"))

    # check ranges to make sure things are not crazy
    if(cdc_pressure < 50. or cdc_pressure > 150.):
        return

    # average and check ranges
    ntemps = 0
    temp_avg = 0.
    temps = [cdc_temp_1, cdc_temp_2, cdc_temp_3, cdc_temp_4, cdc_temp_5]
    for temp in temps:
        if(temp > 20. and temp < 30.):
            ntemps += 1
            temp_avg += (temp+273.)  # don't forget to convert deg C -> deg K

    if ntemps == 0:
        return
    temp_avg /= float(ntemps)

    # do calc
    PoverT = cdc_pressure / temp_avg

    # from https://logbooks.jlab.org/entry/3759767
    #newgain = -0.9305 + 3.227 * PoverT
    # updated based on https://logbooks.jlab.org/entry/3781319 - sdobbs (2/10/2020)
    newgain =  -0.984748 + 3.36527 * PoverT

    # update CCDB for this run
    ccdb_conn.create_assignment(
        data=[["%5.3f"%newgain, 0.8]],
        path="/CDC/digi_scales",
        variation_name="default",
        min_run=run,
        max_run=run,
        comment="Online update based on EPICS")

# update the initial CDC time-to-distance calibrations based on the ambient pressure
# Naomi provided the following mapping:
# run    "kPa"   mmHg     
#71734  97.5318  739.87
#  741.61
#71735  97.9678  743.35 
# 746.915
#71672  98.8616 750.48
# 755.610
#72187  100.148  760.74
# 765.35
#71467  101.303 769.96
# 773.965
#71824  102.306  777.97

CDC_TTOD_TABLE = [ ] 
CDC_TTOD_TABLE.append( [ [ 1.02196, -0.0800837, 0, -0.110526, -0.462576, 0, 0.0038821, 0.289286, 0, 1.1, -0.08 ],
                         [ 1.02196, 0.0800837, 0, -0.110526, 0.462576, 0, 0.0038821, -0.289286, 0, 1.1, -0.08 ] ] )
CDC_TTOD_TABLE.append( [ [ 1.0193, -0.0704149, 0, -0.107234, -0.476431, 0, 0.00335708, 0.286611, 0, 1.1, -0.08 ],  
                         [ 1.0193, 0.0704149, 0, -0.107234, 0.476431, 0, 0.00335708, -0.286611, 0, 1.1, -0.08 ] ] )
CDC_TTOD_TABLE.append( [ [ 1.01681, -0.0542194, 0, -0.105428, -0.502977, 0, 0.00345319, 0.301217, 0, 1.1, -0.08 ], 
                         [ 1.01681, 0.0542194, 0, -0.105428, 0.502977, 0, 0.00345319, -0.301217, 0, 1.1, -0.08 ] ] )
CDC_TTOD_TABLE.append( [ [ 1.0117, -0.0635804, 0, -0.101684, -0.465007, 0, 0.0052687, 0.227823, 0, 1.1, -0.08 ],   
                         [ 1.0117, 0.0635804, 0, -0.101684, 0.465007, 0, 0.0052687, -0.227823, 0, 1.1, -0.08 ] ] )
CDC_TTOD_TABLE.append( [ [ 1.00479, -0.0503435, 0, -0.0909644, -0.486412, 0, -0.00673478, 0.306132, 0, 1.1, -0.08 ],   
                         [ 1.00479, 0.0503435, 0, -0.0909644, 0.486412, 0, -0.00673478, -0.306132, 0, 1.1, -0.08 ] ] )
CDC_TTOD_TABLE.append( [ [ 0.998255, -0.0144274, 0, -0.0830508, -0.560996, 0, -0.00967542, 0.348271, 0, 1.1, -0.08 ],  
                         [ 0.998255, 0.0144274, 0, -0.0830508, 0.560996, 0, -0.00967542, -0.348271, 0, 1.1, -0.08 ] ] )


def update_cdc_ttod(ccdb_conn, run):
    TOLERANCE = 1.e-5  # constant used for comparisons
    plimits = [741.61, 746.915, 755.61, 765.35, 773.965]

    # get info from EPICS
    #print caget("RESET:i:GasPanelBarPress1")
    cdc_pressure = float(caget("RESET:i:GasPanelBarPress1"))

    # check ranges to make sure things are not crazy
    if(cdc_pressure < 50. or cdc_pressure > 150.):
        return

    # convert the pressure to to mmHg
    mmhg = 7.978*cdc_pressure - 38.23

    # figure out the index into the TtoD table
    ind = 0
    while mmhg > plimits[ind] and ind < len(plimits):
      ind += 1
      if ind == 5:
        break
      
    # update CCDB for this run
    ccdb_conn.create_assignment(
        data=CDC_TTOD_TABLE[ind],
        path="/CDC/drift_parameters",
        variation_name="default",
        min_run=run,
        max_run=run,
        comment="Online update based on EPICS")


def update_beam_currents(rcdb_conn, run):
    # get the start time for the run
    rundata = rcdb_conn.get_run(run)    
    if rundata.start_time is None and rundata.end_time is None:
        return

    run_start_time = rundata.start_time
    run_end_time = rundata.end_time
    if run_start_time is None:
        run_start_time = run_end_time
        if run_start_time.minute-5 < 0.:
            run_start_time = datetime.datetime(run_start_time.year,run_start_time.month,run_start_time.day,run_start_time.hour-1,run_start_time.minute-5+60,run_start_time.second)
    if run_end_time is None or run_end_time == run_start_time:
        run_end_time = run_start_time
        if run_end_time.minute+15. > 60.:
            run_end_time = datetime.datetime(run_end_time.year,run_end_time.month,run_end_time.day,run_end_time.hour+1,run_end_time.minute-60+15,run_end_time.second)
    if run_end_time == run_start_time:
        run_end_time = datetime.datetime(run_end_time.year,run_end_time.month,run_end_time.day,run_end_time.hour,run_end_time.minute+1,run_end_time.second)

    begintime = datetime.datetime.strftime(run_start_time, '%Y-%m-%d %H:%M:%S')
    # if the run has a set end time, then use that, otherwise use the current time
    if run_end_time:
        endtime = datetime.datetime.strftime(run_end_time, '%Y-%m-%d %H:%M:%S')
    else:
        endtime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')  # current date/time

    # Beam current - uses the primary BCM, IBCAD00CRCUR6
    conditions = {}
    # We could also use the following: IPM5C11.VAL,IPM5C11A.VAL,IPM5C11B.VAL,IPM5C11C.VAL
    try: 
        # save integrated beam current over the whole run
        # use MYA archive commands to calculate average

        # build myStats command
        cmds = []
        cmds.append("myStats")
        cmds.append("-b")
        cmds.append(begintime)
        cmds.append("-e")
        cmds.append(endtime)
        cmds.append("-l")
        cmds.append("IBCAD00CRCUR6")
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        # iterate over output
        n = 0
        for line in p.stdout:
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]    ## average value
            if key == "IBCAD00CRCUR6":
                conditions["beam_current"] = float(value)
    except:
        conditions["beam_current"] = -1.

    # now only do this when the current is on
    try: 
        # save integrated beam current over the whole run
        # use MYA archive commands to calculate average
        # build myStats command
        cmds = []
        cmds.append("myStats")
        cmds.append("-b")
        cmds.append(begintime)
        cmds.append("-e")
        cmds.append(endtime)
        cmds.append("-c")
        cmds.append("IBCAD00CRCUR6")
        cmds.append("-r")
        cmds.append("5:5000")        
        cmds.append("-l")
        cmds.append("IBCAD00CRCUR6")
        # execute external command
        p = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        # iterate over output
        n = 0
        for line in p.stdout:
            n += 1
            if n == 1:     # skip header
                continue 
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]    ## average value
            if key == "IBCAD00CRCUR6":
                conditions["beam_on_current"] = float(value)
    except:
        conditions["beam_on_current"] = -1.

    # Add all the values that we've determined to the RCDB
    rcdb_conn.add_conditions(run, conditions, replace=True)

####################################################################################

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
    RUN_PERIOD       = 'RunPeriod-2019-11'
    #RCDB_PRODUCTION_SEARCH = "@is_dirc_production"
    RCDB_PRODUCTION_SEARCH = "daq_run=='PHYSICS_DIRC' and event_count > 5000000"
    #RCDB_PRODUCTION_SEARCH = "daq_run=='PHYSICS_DIRC' and event_count > 5000000 and solenoid_current > 100 and collimator_diameter != 'Blocking'"
    #RCDB_PRODUCTION_SEARCH = "daq_run=='PHYSICS_DIRC' and beam_current > 10. and event_count > 5000000 and solenoid_current > 100 and collimator_diameter != 'Blocking'"
    #RCDB_PRODUCTION_SEARCH = "daq_run=='PHYSICS_DIRC_TRD' and beam_current > 10. and event_count > 5000000 and solenoid_current > 100 and collimator_diameter != 'Blocking'"
    #3RCDB_PRODUCTION_SEARCH = "daq_run=='PHYSICS_DIRC_TRD' and event_count > 5000000"
    #RCDB_SEARCH_MIN  = 40000
    #RCDB_SEARCH_MIN  = 41857
    RCDB_SEARCH_MIN  = 71500
    RCDB_SEARCH_MAX  = 79000
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
    rcdb_conn = rcdb.RCDBProvider(RCDB)
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

                # calculate a first guess for the CDC gain scale by looking at the current temperature and pressure
                update_cdc_gains(ccdb_conn, run)
                
                # and make a first guess for the CDC time to distance, since this depends on pressure
                update_cdc_ttod(ccdb_conn, run)

                # beam current calculations are not updating well into the RCDB, so let's do them again
                update_beam_currents(rcdb_conn, run)
                #update_beam_currents(cnx, run)

                # update the solenoid map based on the
                solenoid_map_assignment = ccdb_conn.get_assignment("/Magnets/Solenoid/solenoid_map", run, "default")
                current_solenoid_map = solenoid_map_assignment.constant_set.data_table[0][0]

                try:
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
                except:
                    print "Problem checking solenoid current, skipping..."
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
        os.system("touch %s/updated_tables.txt"%(rundir))

        # calibrate RF
        cmd = "./file_calib_pass0.sh %06d"%run
        # write log file!
        if DRY_RUN:
            print cmd
        else:
            retval = os.system(cmd)
            if(retval != 0):
                print "ERROR in run %d file_calib_pass0.sh: %d"%(run,retval)

        # check for 2ns shfits
        cmd = "./file_calib_check2ns_shift.sh %06d 000"%run
        # write log file!
        if DRY_RUN:
            print cmd
        else:
            retval = os.system(cmd)
            if(retval != 0):
                print "ERROR in run %d file_calib_check2ns_shift.sh: %d"%(run,retval)

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
        cmd = "./run_calib_pass1.sh %06d %s"%(run,os.getcwd())
        if DRY_RUN:
            print cmd
        else:
            os.system(cmd)

        # update calibration status
        if not DRY_RUN:
            query = "UPDATE online_info SET done=TRUE WHERE run='%s'"%run
            print query
            calibdb_cursor.execute(query)
            calibdb_cnx.commit()

        # start up tagger calibrations
        # TAGH timewalks depend on HLDT (ADC/TDC alignment)
        ProcessTaggerCalibrations(run,os.getcwd())
        #ptag = multiprocessing.Process(target=ProcessTaggerCalibrations, args=(run,os.getcwd()))
        #ptag.start()
        #tagger_threads.append(ptag)

       

        # see if we should stop earlier
        if os.path.exists("%s/force.stop"%SCRIPT_DIR):
            print "stopping early..."
            break

    # finish and clean up
    calibdb_cursor.close()
    calibdb_cnx.close()
    #for thr in tagger_threads:
    #    thr.join()
