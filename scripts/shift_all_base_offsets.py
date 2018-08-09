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
    #RCDB_QUERY = "@is_production and @status_approved"
    RCDB_QUERY = "@is_2018production"
    VARIATION = "default"
    VERBOSE = 1

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-V","--variation", dest="variation", 
                      help="CCDB variation to use")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 3):
        parser.print_help()
        sys.exit(0)

    #SUBDETECTOR = args[1]
    RUN = int(args[1])
    shift_val = float(args[2])

    if options.variation:
        VARIATION = options.variation

    # Load CCDB
    ccdb_conn = LoadCCDB()

    SUBDETECTORS = [ 'BCAL', 'CDC', 'FDC', 'FCAL', 'START_COUNTER', 'TOF', 'PHOTON_BEAM/hodoscope', 'PHOTON_BEAM/microscope', 'PHOTON_BEAM/pair_spectrometer' ]

    for detector in SUBDETECTORS:
        print "===run %d, %s/base_time_offset==="%(RUN,detector)
        assignment = ccdb_conn.get_assignment("/%s/base_time_offset"%detector, RUN, VARIATION)
        offsets = assignment.constant_set.data_table

        if VERBOSE>0:
            print "Before:"
            pp.pprint(offsets)

        for x in xrange(len(offsets[0])):
            offsets[0][x] = str(float(offsets[0][x]) - shift_val)
    
        if VERBOSE>0:
            print "After:"
            pp.pprint(offsets)

        ccdb_conn.create_assignment(
            data=offsets,
            path="/%s/base_time_offset"%detector,
            variation_name=VARIATION,
            min_run=RUN,
            max_run=ccdb.INFINITE_RUN,
            #max_run=RUN,
            comment="shift by %6.3f"%shift_val)

## main function 
if __name__ == "__main__":
    main()
