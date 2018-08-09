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

from ROOT import TFile,TH1I,TH2I,TCanvas,TF1


def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    return provider


def FindFDCPackageChamber(plane):
    package = plane / 6 + 1
    chamber = plane % 6
    if(chamber == 0):
        chamber = 6
        package -= 1
  
    return (package, chamber)


def main():
    pp = pprint.PrettyPrinter(indent=4)
    c1 = TCanvas("c1", "", 800, 600)

    # Defaults
    RCDB_QUERY = ""
    #RCDB_QUERY = "@is_2018production and status != 0"
    #RCDB_QUERY = "@is_2018production"
    #RCDB_QUERY = "@is_2018production and @status_approved"
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

        # find the offset relative to the base FDC time
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver01/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver06/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver03/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        f = TFile("/group/halld/Users/sdobbs/hd_calib_pass1_Run041989.root")

        # see if the files exists
        try:
            hfdctdc = f.Get("HLDetectorTiming/FDC/FDCHit Wire time vs. module")
            maximum = hfdctdc.GetBinCenter(hfdctdc.GetMaximumBin());
        except:
            print "fail 1"
            continue

        c1.Print("out.pdf[")

        fdcTimeHist = f.Get("/HLDetectorTiming/TRACKING/Earliest Flight-time Corrected FDC Time")
        MPV = 0;
        try:
            maximum = fdcTimeHist.GetBinCenter(fdcTimeHist.GetMaximumBin());
            fr = fdcTimeHist.Fit("landau", "S", "", maximum - 3.5, maximum + 6);
            MPV = fr.Parameter(1);

            fdcTimeHist.Draw()
            c1.Print("out.pdf")
        except:
            print "fail 2"
            pass

        #c1.Print("out.pdf[")

        for plane in xrange(1,hfdctdc.GetNbinsX()+1):
            projY = hfdctdc.ProjectionY("temp_%d"%plane, plane, plane);
            maximum = projY.GetBinCenter(projY.GetMaximumBin());
            projY.Draw()

            fn = TF1("f", "gaus")
            fn.SetParameters(100, maximum, 20)
            projY.Fit(fn, "S", "", maximum - 10, maximum + 10)

            c1.Print("out.pdf")

        c1.Print("out.pdf]")

## main function 
if __name__ == "__main__":
    main()
