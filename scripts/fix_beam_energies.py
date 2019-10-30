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
    RCDB_QUERY = "@is_2018production and @status_approved"
    VARIATION = "default"
    VERBOSE = 1

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-V","--variation", dest="variation",
                      help="CCDB variation to use")
    parser.add_option("-b","--begin_run", dest="begin_run",
                      help="Starting run when scanning RCDB")
    parser.add_option("-e","--end_run", dest="end_run",
                      help="Ending run when scanning RCDB")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 1):
        parser.print_help()
        sys.exit(0)

    if options.variation:
        VARIATION = options.variation
    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # Load RCDB                                                                                                                                   
    rcdb_conn = None
    try:
        rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
        runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY, BEGINRUN, ENDRUN) ]
    except:
        e = sys.exc_info()[0]
        print "Could not connect to RCDB: " + str(e)

    for run in runs:
        #print "===%d==="%run

        assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/endpoint_energy", run, VARIATION)
        data = assignment.constant_set.data_table

        #print "%d, %s"%(run,data[0][0])

        old_beam_energy = float(data[0][0])
        beam_energy = old_beam_energy*1.0025
        
        print "==changing beam energy for run %d from %6.4f to %6.4f=="%(run,old_beam_energy,beam_energy)

        ccdb_conn.create_assignment(
            data=[[beam_energy]],
            path="/PHOTON_BEAM/endpoint_energy",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="shift by 0.25% due to accelerator scale systematics")

## main function 
if __name__ == "__main__":
    main()
