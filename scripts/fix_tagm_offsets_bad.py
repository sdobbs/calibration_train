## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
import rcdb
from optparse import OptionParser
from array import array
import pprint
import math

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

from ROOT import TFile,TH1I,TH2I


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

    BEGINRUN = 30000
    ENDRUN = 39999

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-F","--run_file", dest="run_file", 
                      help="File of runs to look at")
    parser.add_option("-V","--variation", dest="variation", 
                      help="CCDB variation to use")
    parser.add_option("-b","--begin_run", dest="begin_run",
                      help="Starting run when scanning RCDB")
    parser.add_option("-e","--end_run", dest="end_run",
                      help="Ending run when scanning RCDB")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    #if(len(args) < 1):
    #    parser.print_help()
    #    sys.exit(0)

    if options.variation:
        VARIATION = options.variation
    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # get run list
    runs = []

    if options.run_file:
        with open(options.run_file) as f:
            for line in f:
                try:
                    runs.append(int(line.strip()))
                except:
                    print "Ignoring line: "+line
    else:
        # Load RCDB
        rcdb_conn = None
        try:
            rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
            runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY, BEGINRUN, ENDRUN) ]
        except:
            e = sys.exc_info()[0]
            print "Could not connect to RCDB: " + str(e)
    

    # Print to screen
    for run in runs:
        print "===%d==="%run
        adc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/fadc_time_offsets", run, VARIATION)
        tdc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/tdc_time_offsets", run, VARIATION)
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        adc_offsets = adc_toff_assignment.constant_set.data_table
        tdc_offsets = tdc_toff_assignment.constant_set.data_table

        modified = False
        for i in xrange(len(adc_offsets)):
            if abs(float(adc_offsets[i][1])) > 100.:
                adc_offsets[i][1] = "0"
                print "bad channel = %d"%(i+1)
                modified = True
            if abs(float(tdc_offsets[i][1])) > 100.:
                tdc_offsets[i][1] = "0"
                print "bad channel = %d"%(i+1)
                modified = True

        if modified:
            print "updating CCDB"
            ccdb_conn.create_assignment(
                data=adc_offsets,
                path="/PHOTON_BEAM/microscope/fadc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad (very large) offsets")
            ccdb_conn.create_assignment(
                data=tdc_offsets,
                path="/PHOTON_BEAM/microscope/tdc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad (very large) offsets")


## main function 
if __name__ == "__main__":
    main()
