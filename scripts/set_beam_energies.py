## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
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
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    return provider


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    RCDB_QUERY = "@is_production and @status_approved"
    VARIATION = "default"
    VERBOSE = 1

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-V","--variation", dest="variation", 
                      help="CCDB variation to use")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)

    FILENAME = args[1]

    if options.variation:
        VARIATION = options.variation

    # Load CCDB
    ccdb_conn = LoadCCDB()

    with open(FILENAME) as f:
        for line in f:
            tokens = line.strip().split()
            RUN = int(float(tokens[0]))
            #beam_energy = float(tokens[1])/1000.
            beam_energy = float(tokens[2])/1000.

            print "==setting beam energy for run %d as %f=="%(RUN,beam_energy)
        
            ccdb_conn.create_assignment(
                data=[[beam_energy]],
                path="/PHOTON_BEAM/endpoint_energy",
                variation_name=VARIATION,
                min_run=RUN,
                max_run=RUN,
                comment="value derived by Alexandre Deur")

## main function 
if __name__ == "__main__":
    main()
