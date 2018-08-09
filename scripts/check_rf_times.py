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
    provider.authentication.current_user_name = "anonymous"  # to have a name in logs

    return provider


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    OUTPUT_FILENAME = "out.root"
    RCDB_QUERY = "@is_production"
    VARIATION = "default"

    # Define command line options
    parser = OptionParser(usage = "check_rf_times.py")
    
    (options, args) = parser.parse_args(sys.argv)

    #if(len(args) < 2):
    #    parser.print_help()
    #    sys.exit(0)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # get run list
    runs = []

    # Load RCDB
    rcdb_conn = None
    try:
        rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
        runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY) ]
    except:
        e = sys.exc_info()[0]
        print "Could not connect to RCDB: " + str(e)
        exit(0)

    old_times = [0.,0.,0.,0.]

    # Print to screen
    for run in runs:
        assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/RF/time_offset", run, "default")

        found = False
        for x in xrange(len(old_times)):
            diff = abs(float(old_times[x]) - float(assignment.constant_set.data_table[0][x]))
            if diff > 1.:
                found = True
        
        if found == True:
            print "===%d==="%run
            pp.pprint(assignment.constant_set.data_table[0])
            old_times = assignment.constant_set.data_table[0]
    

## main function 
if __name__ == "__main__":
    main()
