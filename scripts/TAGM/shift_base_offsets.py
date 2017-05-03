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

    SUBDETECTOR = "/PHOTON_BEAM/microscope"
    datafilename = args[1]

    if options.variation:
        VARIATION = options.variation

    # Load CCDB
    ccdb_conn = LoadCCDB()

    with open(datafilename) as f:
        for line in f:
            (run_val, shift_val) = line.strip().split()
            RUN = int(run_val)
            SHIFT = float(shift_val)
            print "===run %d, %s/base_time_offset, shift = %f==="%(RUN,SUBDETECTOR,SHIFT)
            assignment = ccdb_conn.get_assignment("%s/base_time_offset"%SUBDETECTOR, RUN, VARIATION)
            offsets = assignment.constant_set.data_table

            if VERBOSE>0:
                print "Before:"
                pp.pprint(offsets)

            for x in xrange(len(offsets[0])):
                #print x
                offsets[0][x] = str(float(offsets[0][x]) - SHIFT)
    
            if VERBOSE>0:
                print "After:"
                pp.pprint(offsets)
                
            ccdb_conn.create_assignment(
                data=offsets,
                path="%s/base_time_offset"%SUBDETECTOR,
                variation_name=VARIATION,
                min_run=RUN,
                max_run=RUN,
                comment="shift by %6.3f"%SHIFT)

## main function 
if __name__ == "__main__":
    main()
