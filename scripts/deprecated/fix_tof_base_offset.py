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

from ROOT import TFile,TH1I,TH2I,TFitResultPtr


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
        off_assignment = ccdb_conn.get_assignment("/TOF/base_time_offset", run, VARIATION)
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        base_offsets = off_assignment.constant_set.data_table

        # let's find the changes to make
        run_chan_errors = {}

        f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver19/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver11/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")        
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/TOF/DeltaTVsP_Pi-")

        try:
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")

            maximum = locHist.GetBinCenter(locHist.GetMaximumBin());
            fr = locHist.Fit("gaus", "SQ", "", maximum - 0.15, maximum + 0.15);
            mean = fr.Parameter(1);

        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue

        print "shift = " + str(mean)
        #continue

        # fix if shifted more than 10 ps
        if abs(mean) < 0.010:
            continue


        # let's apply the offsets
        base_offsets[0][0] = str(float(base_offsets[0][0]) - mean)
        base_offsets[0][1] = str(float(base_offsets[0][1]) - mean)

        ccdb_conn.create_assignment(
                data=base_offsets,
                path="/TOF/base_time_offset",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad alignment with RF")


## main function 
if __name__ == "__main__":
    main()
