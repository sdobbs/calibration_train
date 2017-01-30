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
    RCDB_QUERY = "@is_production and @status_approved"
    DEST_VARIATION = "default"
    SRC_VARIATION = "default"
    MIN_RUN = 1
    MAX_RUN = ccdb.INFINITE_RUN
    VERBOSE = 1


    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    parser.add_option("-T","--table_file", dest="table_file", 
                      help="File of CCDB tables to copy")
    parser.add_option("-b","--begin-run", dest="begin_run", 
                      help="Beginning of the run range to copy to.")
    parser.add_option("-e","--end-run", dest="end_run", 
                      help="End of the run range to copy to.")
    parser.add_option("-D","--dest_variation", dest="dest_variation", 
                      help="Desitination CCDB variation to use")
    parser.add_option("-S","--src_variation", dest="src_variation", 
                      help="Source CCDB variation to use")

    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)


    src_run = args[1]

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
        CCDB_TABLES = args[2:]

    if CCDB_TABLES is None or len(CCDB_TABLES) == 0:
        CCDB_TABLES = []
        

    if options.dest_variation:
        DEST_VARIATION = options.dest_variation
    if options.src_variation:
        SRC_VARIATION = options.src_variation

    # Load CCDB
    ccdb_conn = LoadCCDB()


    if CCDB_TABLES is None or len(CCDB_TABLES)==0:
        print "no tables specified!"
        return

    # Print to screen
    #print "Printing table %s"%CCDB_TABLE
    for ccdb_table in CCDB_TABLES:
        if VERBOSE>0:
            print "==copying %s for run %d=="%(ccdb_table,run)
        # get source data
        assignment = ccdb_conn.get_assignment(ccdb_table, src_run, SRC_VARIATION)
        #pp.pprint(assignment.constant_set.data_table)
        # add to destination
        ccdb_conn.create_assignment(
            data=assignment.constant_set.data_table,
            path=ccdb_table,
            variation_name=DEST_VARIATION,
            min_run=MIN_RUN,
            max_run=MAX_RUN,
            comment="Copied from run \'%s\' variation \'%s\'"%(src_run,ccdb_table))
    #print "===%d==="%run
    #pp.pprint(assignment.constant_set.data_table)

    

## main function 
if __name__ == "__main__":
    main()
