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

from ROOT import TFile,TH1I,TH2I,TCanvas


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

    c1 = TCanvas("c1","c1",800,600)

    # Defaults
    RCDB_QUERY = "@is_production and @status_approved"
    VARIATION = "default"

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
        except:
            e = sys.exc_info()[0]
            print "Could not connect to RCDB: " + str(e)
    
    #outf = open("bad_tdc_adc_channels.txt","w")
    c1.Print("tagm_tdc_adc_all.pdf[")
    c1.Print("tagm_t_adc_all.pdf[")
    c1.Print("tagm_adc_rf_all.pdf[")

    # Print to screen
    for run in runs:
        print "===%d==="%run
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver25/rootfiles/hd_root_%06d.root"%run)
        f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver32/hists/Run%06d/hd_calib_verify_Run%06d_000.root"%(run,run))
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        #f = TFile("/lustre/expphy/work/halld/home/gxproj3/hd_root.root")
        htagm_adc_rf = f.Get("/TAGM_TW/adc_rf_all")
        htagm_tdc_adc = f.Get("/TAGM_TW/tdc_adc_all")
        htagm_t_adc = f.Get("/TAGM_TW/t_adc_all")

        try:
            n = htagm_adc_rf.GetNbinsX()
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue

        
        htagm_adc_rf.SetTitle("Run %d"%run)
        htagm_adc_rf.Draw("COLZ")
        c1.Print("tagm_adc_rf_all.pdf")

        htagm_tdc_adc.SetTitle("Run %d"%run)
        htagm_tdc_adc.GetXaxis().SetRangeUser(-6,6)
        htagm_tdc_adc.Draw("COLZ")
        c1.Print("tagm_tdc_adc_all.pdf")

        htagm_t_adc.SetTitle("Run %d"%run)
        htagm_t_adc.GetXaxis().SetRangeUser(-6,6)
        htagm_t_adc.Draw("COLZ")
        c1.Print("tagm_t_adc_all.pdf")

            
    c1.Print("tagm_tdc_adc_all.pdf]")
    c1.Print("tagm_t_adc_all.pdf]")
    c1.Print("tagm_adc_rf_all.pdf]")


## main function 
if __name__ == "__main__":
    main()
