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

from ROOT import TFile,TH1I,TH2I,TGraph


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
    OUTPUT_FILENAME = "out.root"

    BEGINRUN = 30000
    ENDRUN = 39999
    #BEGINRUN = 30596
    #ENDRUN = 30596

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
            runs_arr = array('f')
            runs_arr.fromlist(runs)
        except:
            e = sys.exc_info()[0]
            print "Could not connect to RCDB: " + str(e)


    tagm_rf_mean = []
    tagm_rf_sigma = []


    for x in xrange(150):
        tagm_rf_mean.append( array('f') ) 
        tagm_rf_sigma.append( array('f') ) 


    # Print to screen
    for run in runs:
        print "===%d==="%run

        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver12/rootfiles/hd_root_%06d.root"%run)
        f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver16/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        htagm = f.Get("/HLDetectorTiming/TRACKING/TAGM - RFBunch Time")

        try:
            n = htagm.GetNbinsX()
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue

        #htagm.Print("base")
        for i in xrange(1,htagm.GetNbinsX()+1):
            hy = htagm.ProjectionY("_%d"%i,i,i)
            #print i,hy.GetBinCenter(hy.GetMaximumBin())
            #print i,hy.GetBinLowEdge(hy.GetMaximumBin()+1)
            #tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)

            maximum = hy.GetBinCenter(hy.GetMaximumBin());
            fr = hy.Fit("gaus", "SQ", "", maximum - 0.3, maximum + 0.3);
            mean = fr.Parameter(1);
            sigma = fr.Parameter(2);

            tagm_rf_mean[i].append( mean )
            tagm_rf_sigma[i].append( sigma )
            
    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    for x in xrange(150):
        if len(tagm_rf_mean[x]) == 0:
            continue

        gr = TGraph(len(runs_arr), runs_arr, tagm_rf_mean[x])
        gr.SetName("tagm_rf_mean%d"%x)
        gr.SetTitle("TAGM - RF time mean, CCDB Index %d"%x)
        gr.Write()

        gr2 = TGraph(len(runs_arr), runs_arr, tagm_rf_sigma[x])
        gr2.SetName("tagm_rf_sigma%d"%x)
        gr2.SetTitle("TAGM - RF time sigma, CCDB Index %d"%x)
        gr2.Write()

    fout.Close()



## main function 
if __name__ == "__main__":
    main()
