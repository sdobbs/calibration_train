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
    #RCDB_QUERY = "@is_production and @status_approved"
    RCDB_QUERY = "@is_2018production"
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
    
    outf = open("bad_tdc_adc_channels.txt","w")

    # Print to screen
    for run in runs:
        print "===%d==="%run
        print>>outf, "===%d==="%run
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-08/mon_ver07/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver17/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver16/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        f = TFile("/work/halld/home/sdobbs/calib/2018-01/hd_root.root")
        #f = TFile("/lustre/expphy/work/halld/home/gxproj3/hd_root.root")
        #f = TFile("/lustre/expphy/work/halld/home/gxproj5/test/hd_root.root")
        #f = TFile("/home/gxproj3/work/TAGM/hd_root.root")
        #htagm = f.Get("/HLDetectorTiming/TAGH/TAGHHit TDC_ADC Difference")

        htagh_hit_time = f.Get("/TAGH/Hit/Hit_TimeVsSlotID")
        htagh_hit_tdctime = f.Get("/TAGH/Hit/Hit_tdcTimeVsSlotID")
        htagh_digi_tdc = f.Get("/TAGH/DigiHit/DigiHit_tdcTimeVsSlotID")
        htagh_digi_fadc = f.Get("/TAGH/DigiHit/DigiHit_fadcTimeVsSlotID")
        htagh_digi_fadcpeak = f.Get("/TAGH/DigiHit/DigiHit_PeakVsSlotID")

        try:
            n = htagh_hit_time.GetNbinsX()
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue


        #hhtagh_hit_time.Print("base")

        pdf_fname = "/work/halld/home/gxproj3/tagm_plots/tagh_tdcadc_r%d.pdf"%run
        pdf_adc_fname = "/work/halld/home/gxproj3/tagm_plots/tagh_adc_t_r%d.pdf"%run
        pdf_adc_peak_fname = "/work/halld/home/gxproj3/tagm_plots/tagh_adc_peak_r%d.pdf"%run
        pdf_tdc_fname = "/work/halld/home/gxproj3/tagm_plots/tagh_tdc_t_r%d.pdf"%run
        pdf_time_fname = "/work/halld/home/gxproj3/tagm_plots/tagh_time_r%d.pdf"%run
        pdf_tdctime_fname = "/work/halld/home/gxproj3/tagm_plots/tagh_tdctime_r%d.pdf"%run
        for i in xrange(1,htagh_hit_time.GetNbinsX()+1):
            print "channel = " + str(i)
            
            hy = htagh_hit_time.ProjectionY("_%d"%i,i,i)
            tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)

            if tdiff>1.:
                print "bad channel = %d"%i
                print>>outf, "bad channel = %d"%i
            hy.Draw()

            if i==1:
                c1.Print(pdf_fname+"(")
            if i==(htagh_hit_time.GetNbinsX()):
                c1.Print(pdf_fname+")")
            else:
                c1.Print(pdf_fname)
            

            hy = htagh_digi_fadc.ProjectionY("_%d"%i,i,i)
            hy.Rebin(10)
            try:
                maximum = hy.GetBinCenter(hy.GetMaximumBin())
                fr = hy.Fit("gaus", "SQ", "", maximum - 12, maximum + 12)
                mean = fr.Parameter(1)
                print "ADC time = %6.3f"%mean
            except:
                pass

            hy.Draw()
            if i==1:
                c1.Print(pdf_adc_fname+"(")
            if i==(htagh_hit_time.GetNbinsX()):
                c1.Print(pdf_adc_fname+")")
            else:
                c1.Print(pdf_adc_fname)            
            
            hy = htagh_digi_tdc.ProjectionY("_%d"%i,i,i)
            hy.Rebin(10)
            try:
                maximum = hy.GetBinCenter(hy.GetMaximumBin())
                fr = hy.Fit("gaus", "SQ", "", maximum - 12, maximum + 12)
                mean = fr.Parameter(1)
                print "TDC time = %6.3f"%mean
            except:
                pass

            hy.Draw()
            if i==1:
                c1.Print(pdf_tdc_fname+"(")
            if i==(htagh_hit_time.GetNbinsX()):
                c1.Print(pdf_tdc_fname+")")
            else:
                c1.Print(pdf_tdc_fname)

            hy = htagh_digi_fadcpeak.ProjectionY("_%d"%i,i,i)
            hy.Draw()
            if i==1:
                c1.Print(pdf_adc_peak_fname+"(")
            if i==(htagh_hit_time.GetNbinsX()):
                c1.Print(pdf_adc_peak_fname+")")
            else:
                c1.Print(pdf_adc_peak_fname)
            
            hy = htagh_hit_time.ProjectionY("_%d"%i,i,i)
            hy.Draw()
            if i==1:
                c1.Print(pdf_time_fname+"(")
            if i==(htagh_hit_time.GetNbinsX()):
                c1.Print(pdf_time_fname+")")
            else:
                c1.Print(pdf_time_fname)

            hy = htagh_hit_tdctime.ProjectionY("_%d"%i,i,i)
            hy.Draw()
            if i==1:
                c1.Print(pdf_tdctime_fname+"(")
            if i==(htagh_hit_time.GetNbinsX()):
                c1.Print(pdf_tdctime_fname+")")
            else:
                c1.Print(pdf_tdctime_fname)
            
            


## main function 
if __name__ == "__main__":
    main()
