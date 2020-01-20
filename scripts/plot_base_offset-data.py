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

from ROOT import TFile,TH1I,TH2I,TFitResultPtr,TF1,TGraph


def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    return provider

def CalcFDCShifts(f):
    this1DHist = f.Get("/HLDetectorTiming/FDC/FDCHit Cathode time")
    firstBin = this1DHist.FindFirstBinAbove(1, 1)
    for i in xrange(16):
        if (firstBin + i) > 0:
            this1DHist.SetBinContent((firstBin + i), 0)
    maximum = this1DHist.GetBinCenter(this1DHist.GetMaximumBin())
    fn = TF1("f", "gaus")
    fn.SetParameters(100, maximum, 20)
    fr = this1DHist.Fit(fn, "QS", "", maximum - 10., maximum + 7.)
    mean = fr.Parameter(1)
    FDC_ADC_Offset = mean

    this1DHist = f.Get("/HLDetectorTiming/FDC/FDCHit Wire time")
    firstBin = this1DHist.FindFirstBinAbove(1, 1)
    for i in xrange(25):
        if (firstBin + i) > 0:
            this1DHist.SetBinContent((firstBin + i), 0)
    maximum = this1DHist.GetBinCenter(this1DHist.GetMaximumBin())
    fn = TF1("f", "gaus")
    fn.SetParameters(100, maximum, 20)
    fr = this1DHist.Fit(fn, "QS", "", maximum - 10., maximum + 5.)
    mean = fr.Parameter(1)
    FDC_TDC_Offset = mean

    FDC_ADC_TDC_Offset = FDC_ADC_Offset - FDC_TDC_Offset

    this1DHist = f.Get("/HLDetectorTiming/TRACKING/Earliest Flight-time Corrected FDC Time")
    maximum = this1DHist.GetBinCenter(this1DHist.GetMaximumBin())
    fr = this1DHist.Fit("landau", "SQ", "", maximum - 2.5, maximum + 4.)
    MPV = fr.Parameter(1)
    return ( MPV + FDC_ADC_TDC_Offset, MPV)


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    DETECTOR_SYSTEMS = [ "SC", "TOF", "FCAL", "BCAL", "FDC", "CDC", "TAGH", "TAGM" ]
    CCDB_TABLE_NAME = { "SC":   "/START_COUNTER/base_time_offset",
                        "TOF":  "/TOF/base_time_offset",
                        "FCAL": "/FCAL/base_time_offset",
                        "BCAL": "/BCAL/base_time_offset",
                        "FDC":  "/FDC/base_time_offset",
                        "CDC":  "/CDC/base_time_offset",
                        "TAGH": "/PHOTON_BEAM/hodoscope/base_time_offset",
                        "TAGM": "/PHOTON_BEAM/microscope/base_time_offset"  }
    FIT_RANGE = { "SC":   (0.3,0.3),
                  "TOF":  (0.15,0.15),
                  #"FCAL": (0.8,0.8),
                  "FCAL": (0.5,0.5),
                  "BCAL": (0.3,0.4),
                  "FDC":  (15.,10.),
                  "CDC":  (15.,10.),
                  "TAGH": (0.3,0.3),
                  "TAGM": (0.3,0.3)   }
    #TOLERANCE = { "SC":   0.020,
    TOLERANCE = { "SC":   0.040,
                  "TOF":  0.010,
                  "FCAL": 0.050,
                  #"BCAL": 0.020,
                  "BCAL": 0.010,
                  "FDC":  1.,
                  "CDC":  1.,
                  "TAGH": 0.030,
                  "TAGM": 0.030  }
#                  "TAGH": 0.050,
#                  "TAGM": 0.050  }
    
    #RCDB_QUERY = "@is_production and @status_approved"
    #RCDB_QUERY = "@is_production"
    RCDB_QUERY = "@is_2018production and status!=0"
    VARIATION = "default"
    DRY_RUN = False

    BEGINRUN = 40000
    ENDRUN = 49999
    

    # Define command line options
    parser = OptionParser(usage = "fix_sc_offsets.py ccdb_tablename")
    parser.add_option("-F","--run_file", dest="run_file", 
                      help="File of runs to look at")
    #parser.add_option("-V","--variation", dest="variation", 
    #                  help="CCDB variation to use")
    parser.add_option("-b","--begin_run", dest="begin_run",
                      help="Starting run when scanning RCDB")
    parser.add_option("-e","--end_run", dest="end_run",
                      help="Ending run when scanning RCDB")
    #parser.add_option("-Y","--dry_run", dest="dry_run", action="store_true",
    #                  help="Don't actually store constants.")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    #if(len(args) < 2):
    #    parser.print_help()
    #    sys.exit(0)

    #if options.variation:
    #    VARIATION = options.variation
    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)
    #if options.dry_run:
    #    DRY_RUN = True

    #detector = args[1]
    #if detector not in DETECTOR_SYSTEMS:
    #    print "invalid detector = " +detector
    #    sys.exit(0)

    #ccdbtable = CCDB_TABLE_NAME[detector]

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

    # arrays
    sc_runs = array('f')
    tof_runs = array('f')
    fcal_runs = array('f')
    bcal_runs = array('f')
    bcal_gam_runs = array('f')
    tagh_runs = array('f')
    tagm_runs = array('f')
    cdc_runs = array('f')
    fdc_adc_runs = array('f')
    fdc_tdc_runs = array('f')

    sc_run_offsets = array('f')
    tof_run_offsets = array('f')
    fcal_run_offsets = array('f')
    bcal_run_offsets = array('f')
    bcal_gam_run_offsets = array('f')
    tagh_run_offsets = array('f')
    tagm_run_offsets = array('f')
    cdc_run_offsets = array('f')
    fdc_adc_run_offsets = array('f')
    fdc_tdc_run_offsets = array('f')

    # Print to screen
    for run in runs:
        print "===%d==="%run
        #off_assignment = ccdb_conn.get_assignment(ccdbtable, run, VARIATION)
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        #base_offsets = off_assignment.constant_set.data_table

        # let's find the changes to make
        run_chan_errors = {}

        try:
            f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver30/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2016-02/mon_ver16/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver18/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver29/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver06/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
            #f = TFile("/group/halld/Users/sdobbs/hd_root.root")
            
            #if detector == "SC":
            locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/SC/DeltaTVsP_Pi-")
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")
            (low_limit, high_limit) = FIT_RANGE["SC"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                sc_runs.append(run)
                sc_run_offsets.append(mean)
            except:
                print "bad SC fit, skipping..."

            #elif detector == "TOF":
            locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/TOF/DeltaTVsP_Pi-")
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")
            (low_limit, high_limit) = FIT_RANGE["TOF"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                tof_runs.append(run)
                tof_run_offsets.append(mean)
            except:
                print "bad TOF fit, skipping..."

            #elif detector == "BCAL":
            locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/BCAL/DeltaTVsP_Pi-")
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")
            (low_limit, high_limit) = FIT_RANGE["BCAL"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                bcal_runs.append(run)
                bcal_run_offsets.append(mean)
            except:
                print "bad BCAL fit, skipping..."

            # neutral showers
            locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/BCAL/DeltaTVsShowerE_Photon")
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_Photon_1D", 20,250)
            (low_limit, high_limit) = FIT_RANGE["BCAL"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                bcal_gam_runs.append(run)
                bcal_gam_run_offsets.append(mean)
            except:
                print "bad BCAL fit, skipping..."

            #elif detector == "FCAL":
            locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/FCAL/DeltaTVsP_Pi-")
            #locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/FCAL/DeltaTVsShowerE_Photon")
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_Photon_1D")
            (low_limit, high_limit) = FIT_RANGE["FCAL"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                fcal_runs.append(run)
                fcal_run_offsets.append(mean)
            except:
                print "bad FCAL fit, skipping..."

            #elif detector == "TAGH":
            locHist = f.Get("/HLDetectorTiming/TRACKING/Tagger - RFBunch 1D Time")
            (low_limit, high_limit) = FIT_RANGE["TAGH"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                tagh_runs.append(run)
                tagh_run_offsets.append(mean)
            except:
                print "bad TAGH fit, skipping..."

            #elif detector == "TAGM":
            locHist = f.Get("/HLDetectorTiming/TRACKING/TAGM - RFBunch 1D Time")
            (low_limit, high_limit) = FIT_RANGE["TAGM"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                tagm_runs.append(run)
                tagm_run_offsets.append(mean)
            except:
                print "bad TAGM fit, skipping..."

            #elif detector == "CDC":
            locHist = f.Get("/HLDetectorTiming/TRACKING/Earliest CDC Time Minus Matched SC Time")
            (low_limit, high_limit) = FIT_RANGE["CDC"]
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                cdc_runs.append(run)
                cdc_run_offsets.append(mean)
            except:
                print "bad CDC fit, skipping..."

            #if detector == "FDC":
            (adc_shift, tdc_shift) = CalcFDCShifts(f)
            fdc_adc_runs.append(run)
            fdc_adc_run_offsets.append(adc_shift)
            fdc_tdc_runs.append(run)
            fdc_tdc_run_offsets.append(tdc_shift)

        except:
            print "error"
            pass

    # Initialize output file
    OUTPUT_FILENAME = "out.root"
    fout = TFile(OUTPUT_FILENAME, "recreate")

    gr2 = TGraph(len(sc_runs), sc_runs, sc_run_offsets)
    gr2.SetName("sc_run_offsetss")
    gr2.SetLineColor(1)
    gr2.SetMarkerColor(1)
    gr2.SetMarkerStyle(20)
    gr2.Write()
    
    gr2 = TGraph(len(tof_runs), tof_runs, tof_run_offsets)
    gr2.SetLineColor(2)
    gr2.SetMarkerColor(2)
    gr2.SetMarkerStyle(20)
    gr2.SetName("tof_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(bcal_runs), bcal_runs, bcal_run_offsets)
    gr2.SetLineColor(3)
    gr2.SetMarkerColor(3)
    gr2.SetMarkerStyle(20)
    gr2.SetName("bcal_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(bcal_gam_runs), bcal_gam_runs, bcal_gam_run_offsets)
    gr2.SetLineColor(4)
    gr2.SetMarkerColor(4)
    gr2.SetMarkerStyle(20)
    gr2.SetName("bcal_gam)run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(fcal_runs), fcal_runs, fcal_run_offsets)
    gr2.SetLineColor(4)
    gr2.SetMarkerColor(4)
    gr2.SetMarkerStyle(20)
    gr2.SetName("fcal_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(tagm_runs), tagm_runs, tagm_run_offsets)
    gr2.SetLineColor(5)
    gr2.SetMarkerColor(5)
    gr2.SetMarkerStyle(20)
    gr2.SetName("tagm_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(tagh_runs), tagh_runs, tagh_run_offsets)
    gr2.SetLineColor(6)
    gr2.SetMarkerColor(6)
    gr2.SetMarkerStyle(20)
    gr2.SetName("tagh_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(cdc_runs), cdc_runs, cdc_run_offsets)
    gr2.SetLineColor(7)
    gr2.SetMarkerColor(7)
    gr2.SetMarkerStyle(20)
    gr2.SetName("cdc_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(fdc_adc_runs), fdc_adc_runs, fdc_adc_run_offsets)
    gr2.SetLineColor(8)
    gr2.SetMarkerColor(8)
    gr2.SetMarkerStyle(20)
    gr2.SetName("fdc_adc_run_offsetss")
    gr2.Write()
    
    gr2 = TGraph(len(fdc_tdc_runs), fdc_tdc_runs, fdc_tdc_run_offsets)
    gr2.SetLineColor(9)
    gr2.SetMarkerColor(9)
    gr2.SetMarkerStyle(20)
    gr2.SetName("fdc_tdc_run_offsetss")
    gr2.Write()
    
    
    fout.Close()


## main function 
if __name__ == "__main__":
    main()
