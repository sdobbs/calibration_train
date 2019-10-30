## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TTree
import rcdb
from optparse import OptionParser
from array import array
import pprint

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "gxproj3"    # to have a name in logs

    return provider



def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    OUTPUT_FILENAME = "out.root"
    #RCDB_QUERY = "@is_production and @status_approved"
    #RCDB_QUERY = "@is_2018production"
    RCDB_QUERY = "@is_2018production and @status_approved"
    SRC_VARIATION = "calib"
    DEST_VARIATION = "default"
    VERBOSE = 1

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    parser.add_option("-T","--table_file", dest="table_file", 
                      help="File of CCDB tables to copy")
    parser.add_option("-F","--run_file", dest="run_file", 
                      help="File of runs to look at")
    parser.add_option("-R","--run", dest="run", 
                      help="Process this particular run")
    parser.add_option("-D","--dest_variation", dest="dest_variation", 
                      help="Desitination CCDB variation to use")
    parser.add_option("-S","--src_variation", dest="src_variation", 
                      help="Source CCDB variation to use")

    (options, args) = parser.parse_args(sys.argv)


    CCDB_TABLES = None
    if options.table_file:
        CCDB_TABLES = []
        with open(options.table_file) as f:
            for line in f:
                try:
                    CCDB_TABLES.append(line.strip())
                except:
                    #print "Error: " + sys.exc_info()[0]
                    print "Ignoring line: "+line.strip()
    else:
        CCDB_TABLES = args[1:]

    if CCDB_TABLES is None or len(CCDB_TABLES) == 0:
        CCDB_TABLES = []
        

    if options.dest_variation:
        DEST_VARIATION = options.dest_variation
    if options.src_variation:
        SRC_VARIATION = options.src_variation

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # get run list
    runs = None

    if options.run_file:
        runs = []
        with open(options.run_file) as f:
            for line in f:
                try:
                    runs.append(int(line.strip()))
                except:
                    print "Ignoring line: "+line.strip()
    elif options.run:
        runs = [ int(options.run) ]
#    else:
#        # Load RCDB
#        rcdb_conn = None
#        try:
#            rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
#            runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY) ]
#        except:
#            e = sys.exc_info()[0]
#            print "Could not connect to RCDB: " + str(e)
    
    if runs is None:
        print "no runs specified!"
        return
    if CCDB_TABLES is None or len(CCDB_TABLES)==0:
        print "no tables specified!"
        return

    # Print to screen
    #print "Printing table %s"%CCDB_TABLE
    for run in runs:
        for ccdb_table in CCDB_TABLES:
            if VERBOSE>0:
                print "==copying %s for run %d=="%(ccdb_table,run)
            # get source data
                print ccdb_table, run, SRC_VARIATION
            assignment = ccdb_conn.get_assignment(ccdb_table, run, SRC_VARIATION)
            #pp.pprint(assignment.constant_set.data_table)
            # add to destination
            ccdb_conn.create_assignment(
                data=assignment.constant_set.data_table,
                path=ccdb_table,
                variation_name=DEST_VARIATION,
                #min_run=run,
                min_run=60556,
                #max_run=run,
                max_run=ccdb.INFINITE_RUN,
                comment="Copied from variation \'%s\'"%ccdb_table)
        #print "===%d==="%run
        #pp.pprint(assignment.constant_set.data_table)

    

## main function 
if __name__ == "__main__":
    main()
