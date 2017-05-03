## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TGraph
import rcdb
from optparse import OptionParser
from array import array

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"     # to have a name in logs

    return provider


def main():
    # Defaults
    OUTPUT_FILENAME = "out.root"
    RCDB_QUERY = "@is_production and @status_approved"
    VARIATION1 = "default"
    VARIATION2 = "calib"
    BEGINRUN = 1
    ENDRUN = 100000000

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    parser.add_option("-b","--begin-run", dest="begin_run",
                     help="Starting run for output")
    parser.add_option("-e","--end-run", dest="end_run",
                     help="Ending run for output")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 1):
        parser.print_help()
        sys.exit(0)

    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)

    CCDB_TABLE = "/CDC/digi_scales"
    CCDB_TABLE_ROOT = CCDB_TABLE.replace('/','_')

    # Load CCDB
    ccdb_conn = LoadCCDB()
    table = ccdb_conn.get_type_table(CCDB_TABLE)

    # Load RCDB
    rcdb_conn = None
    try:
        rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    except:
        e = sys.exc_info()[0]
        print "Could not connect to RCDB: " + str(e)
    
    # get run list
    runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY, BEGINRUN, ENDRUN) ]
    runs_arr = array('f')
    runs_arr.fromlist(runs)

    diffs = array('f')

    # Fill data
    for run in runs:
        print "==%d=="%run
        assignment1 = ccdb_conn.get_assignment(CCDB_TABLE, run, VARIATION1)
        assignment2 = ccdb_conn.get_assignment(CCDB_TABLE, run, VARIATION2)
        data1 = assignment1.constant_set.data_table
        data2 = assignment2.constant_set.data_table

        diff = float(data1[0][0]) - float(data2[0][0])

        diffs.append(diff)

    # write out graphs
    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")
    gr = TGraph(len(runs_arr), runs_arr, diffs)
    gr.SetName("CDC_ascale_differences")
    gr.Write()
    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
