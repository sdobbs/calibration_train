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
    provider.authentication.current_user_name = "anonymous"  # to have a name in logs

    return provider


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    RCDB_QUERY = "@is_production and @status_approved"
    VARIATION = "calib"

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-F","--run_file", dest="run_file", 
                      help="File of runs to look at")
    parser.add_option("-V","--variation", dest="variation", 
                      help="CCDB variation to use")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    #if(len(args) < 1):
    #    parser.print_help()
    #    sys.exit(0)

    if options.variation:
        VARIATION = options.variation

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
            runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY) ]
        except:
            e = sys.exc_info()[0]
            print "Could not connect to RCDB: " + str(e)
    

    # Print to screen
    for run in runs:
        print "===%d==="%run
        adc_toff_assignment = ccdb_conn.get_assignment("/START_COUNTER/adc_timing_offsets", run, VARIATION)
        tdc_toff_assignment = ccdb_conn.get_assignment("/START_COUNTER/tdc_timing_offsets", run, VARIATION)
        #pp.pprint(adc_toff_assignment.constant_set.data_table)

        adc_offsets = adc_toff_assignment.constant_set.data_table
        tdc_offsets = tdc_toff_assignment.constant_set.data_table

        # fix 2ns offsets
        for x in xrange(len(adc_offsets)):
            if(float(adc_offsets[x][0]) > 2.):
                steps = int(float(adc_offsets[x][0]))/2
                adc_offsets[x][0] = str(float(adc_offsets[x][0]) - 2.*float(steps))
                tdc_offsets[x][0] = str(float(tdc_offsets[x][0]) - 2.*float(steps))
            if(float(adc_offsets[x][0]) < 2.):
                steps = int(-float(adc_offsets[x][0]))/2
                adc_offsets[x][0] = str(float(adc_offsets[x][0]) + 2.*float(steps))
                tdc_offsets[x][0] = str(float(tdc_offsets[x][0]) + 2.*float(steps))

    
        ccdb_conn.create_assignment(
                data=adc_offsets,
                path="/START_COUNTER/adc_timing_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to wrong RF buckets")
        ccdb_conn.create_assignment(
                data=tdc_offsets,
                path="/START_COUNTER/tdc_timing_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to wrong RF buckets")


## main function 
if __name__ == "__main__":
    main()
