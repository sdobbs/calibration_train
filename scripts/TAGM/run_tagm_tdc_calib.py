## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
import rcdb
from optparse import OptionParser
from array import array
import pprint
import math
import glob

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

from ROOT import TFile,TH1I,TH2I,TFitResultPtr,gROOT,TGraph


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
    #RCDB_QUERY = "@is_production"
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
    #ccdb_conn = LoadCCDB()

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

        print runs

    # Print to screen
    #for fname in glob.glob("/cache/halld/RunPeriod-2017-01/calib/ver02/hists/Run%06d/hd_calib_final_Run%06d_001.root"%(run,run))
    #for fname in glob.glob("/cache/halld/RunPeriod-2017-01/calib/ver02/hists/Run*/hd_calib_final_Run*_001.root"):
    for run in runs:
        print "===%d==="%run

        # cat cdc_new_ascale.txt 
        # ver01: 30000 - 30621
        # ver02: 30622 - 30959
        # ver03: 30960 - 

        #if run<30421:
        #    fname ="/cache/halld/RunPeriod-2017-01/calib/ver01/hists/Run%06d/hd_calib_final_Run%06d_001.root"%(run,run) 
        #elif run<=30477:
        #    fname ="/cache/halld/RunPeriod-2017-01/calib/ver02/hists/Run%06d/hd_calib_final_Run%06d_000.root"%(run,run) 
        #elif run<=30621:
        #    fname = "/cache/halld/RunPeriod-2017-01/calib/ver01/hists/Run%06d/hd_calib_final_Run%06d_001.root"%(run,run)
        #elif run<=30959:
        #    fname ="/cache/halld/RunPeriod-2017-01/calib/ver02/hists/Run%06d/hd_calib_final_Run%06d_001.root"%(run,run) 
        #else:
        #    fname = "/cache/halld/RunPeriod-2017-01/calib/ver03/hists/Run%06d/hd_calib_final_Run%06d_001.root"%(run,run) 
        #os.system("ls -lh %s"%fname)
        #f = TFile(fname)
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver12/rootfiles/hd_root_%06d.root"%run)
        #fname = "/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver15/rootfiles/hd_root_%06d.root"%run
        fname = "/cache/halld/RunPeriod-2017-01/calib/ver24/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run)
        #fname = "/home/gxproj3/volatile/2017-01/ver12/hd_root_%06d.root"%run

        #os.system("python timing.py -b %s %d rf default"%(fname,run))
        #os.system("ccdb add PHOTON_BEAM/microscope/fadc_time_offsets -v %s -r %d-%d adc_offsets-%d.txt"%("default",run,run,run))

        #sys.exit(1)

        try:
            print fname
            os.system("python timing.py -b %s %d self default"%(fname,run))
            os.system("ccdb add PHOTON_BEAM/microscope/tdc_time_offsets -v %s -r %d-%d tdc_offsets-%d.txt"%("default",run,run,run))

        except:
            print "problem with run %d, skipping..."%run
            continue

        #ccdb_conn.create_assignment(
        #        data= [ a_scales ],
        #        path="/CDC/digi_scales",
        #        variation_name=VARIATION,
        #        min_run=run,
        #        max_run=run,
        #        comment="Fixed calibrations due to bad alignment with RF")


    # save output
    #fout = TFile("cdc_a_scale.root", "recreate")
    #gr = TGraph(len(runs_arr), runs_arr, scale_factors)
    #gr.SetName("CDC_a_scale")
    #gr.Write()
    #fout.Close()

    #outscale_file.close()

## main function 
if __name__ == "__main__":
    main()
