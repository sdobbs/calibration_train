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

from ROOT import TFile,TH1I,TH2I,TFitResultPtr,TF1


def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////home/gxproj3/work/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    return provider

def CalcFDCShifts(f):
    this1DHist = f.Get("/HLDetectorTiming/FDC/FDCHit Cathode time")
    firstBin = this1DHist.FindFirstBinAbove(1, 1)
    #for i in xrange(16):
    for i in xrange(60):
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
    #MPV = 0
    return ( MPV + FDC_ADC_TDC_Offset, MPV)
    #return (MPV + FDC_ADC_Offset, MPV + FDC_TDC_Offset)
    #return (FDC_ADC_Offset - MPV, FDC_TDC_Offset - MPV)

def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    DETECTOR_SYSTEMS = [ "SC", "TOF", "FCAL", "BCAL", "CCAL", "FDC", "CDC", "TAGH", "TAGM", "PS" ]
    CCDB_TABLE_NAME = { "SC":   "/START_COUNTER/base_time_offset",
                        "TOF":  "/TOF/base_time_offset",
                        "FCAL": "/FCAL/base_time_offset",
                        "BCAL": "/BCAL/base_time_offset",
                        "CCAL": "/CCAL/base_time_offset",
                        "FDC":  "/FDC/base_time_offset",
                        "CDC":  "/CDC/base_time_offset",
                        "PS": "/PHOTON_BEAM/pair_spectrometer/base_time_offset",
                        "TAGH": "/PHOTON_BEAM/hodoscope/base_time_offset",
                        "TAGM": "/PHOTON_BEAM/microscope/base_time_offset"  }
    FIT_RANGE = { "SC":   (0.3,0.3),
                  "TOF":  (0.15,0.15),
                  #"FCAL": (0.8,0.8),
                  "FCAL": (0.5,0.5),
                  "CCAL": (0.5,0.5),
                  "BCAL": (0.3,0.4),
                  "FDC":  (15.,10.),
                  "CDC":  (15.,10.),
#                  "PS":   (0.2,0.2),
                  "PS":   (0.3,0.3),
                  "TAGH": (0.3,0.3),
                  "TAGM": (0.3,0.3)   }
    #TOLERANCE = { "SC":   0.020,
    TOLERANCE = { "SC":   0.040,
                  "TOF":  0.010,
                  "FCAL": 0.050,
                  "CCAL": 0.050,
                  #"BCAL": 0.020,
                  "BCAL": 0.010,
                  "FDC":  1.,
                  "CDC":  1.,
                  "PS":  1.,
#                  "PS":  0.30,
#                  "TAGH": 0.50,
                  "TAGH": 0.030,
                  "TAGM": 0.030  }
#                  "TAGH": 0.050,
#                  "TAGM": 0.050  }
    
    #RCDB_QUERY = "@is_production and @status_approved"
    #RCDB_QUERY = "@is_2018production and @status_approved"
    #RCDB_QUERY = "@is_production"
    RCDB_QUERY = "@is_primex_production"
    #RCDB_QUERY = "@is_2018production and status!=0"
    VARIATION = "default"
    DRY_RUN = False

    BEGINRUN = 40000
    ENDRUN = 49999
    

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
    parser.add_option("-Y","--dry_run", dest="dry_run", action="store_true",
                      help="Don't actually store constants.")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)

    if options.variation:
        VARIATION = options.variation
    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)
    if options.dry_run:
        DRY_RUN = True

    detector = args[1]
    if detector not in DETECTOR_SYSTEMS:
        print "invalid detector = " +detector
        sys.exit(0)

    ccdbtable = CCDB_TABLE_NAME[detector]

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
        off_assignment = ccdb_conn.get_assignment(ccdbtable, run, VARIATION)
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        base_offsets = off_assignment.constant_set.data_table

        # let's find the changes to make
        run_chan_errors = {}

        try:
            f = TFile("/cache/halld/RunPeriod-2019-01/calib/ver08/hists/Run%06d/hd_calib_verify_Run%06d_000.root"%(run,run))
            #f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver26/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
            #f = TFile("/cache/halld/RunPeriod-2018-08/calib/ver05/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2016-02/mon_ver17/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver18/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver34/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver01/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver18/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver21/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-08/mon_ver10/rootfiles/hd_root_%06d.root"%run)
            #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
            #f = TFile("/w/halld-scifs17exp/home/sdobbs/calib/2018-01/hd_root.root")
            #f = TFile("/group/halld/Users/sdobbs/hd_root.root")
            
            if detector == "SC":
                locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/SC/DeltaTVsP_Pi-")
                #locHist_DeltaTVsP_PiPlus.Print("base")
                locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D", 25, 250)
            elif detector == "TOF":
                locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/TOF/DeltaTVsP_Pi-")
                #locHist_DeltaTVsP_PiPlus.Print("base")
                locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D", 35, 250)
            elif detector == "BCAL":
                locHist = f.Get("/HLDetectorTiming/TRACKING/BCAL - RF Time (Neutral)")
            elif detector == "CCAL":
                locHist = f.Get("/HLDetectorTiming/TRACKING/CCAL - RF Time (Neutral)")
            elif detector == "FCAL":
                locHist = f.Get("/HLDetectorTiming/TRACKING/FCAL - RF Time (Neutral)")
            elif detector == "TAGH":
                locHist = f.Get("/HLDetectorTiming/TRACKING/Tagger - RFBunch 1D Time")
            elif detector == "TAGM":
                locHist = f.Get("/HLDetectorTiming/TRACKING/TAGM - RFBunch 1D Time")
            elif detector == "CDC":
                locHist = f.Get("/HLDetectorTiming/TRACKING/Earliest CDC Time Minus Matched SC Time")
            elif detector == "FDC":
                locHist = f.Get("/HLDetectorTiming/FDC/FDCHit Cathode time")
            elif detector == "PS":
                locHist_PSTAGH_tdiffVsEdiff = f.Get("PSPair/PSC_PS_TAGH/PSTAGH_tdiffVsEdiff")
                locHist = locHist_PSTAGH_tdiffVsEdiff.ProjectionY("tdiffVsEdiff_1D")
                locHist_TAGH = f.Get("/HLDetectorTiming/TRACKING/Tagger - RFBunch 1D Time")

            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue

        (low_limit, high_limit) = FIT_RANGE[detector]
        if detector == "FDC":
            (adc_shift, tdc_shift) = CalcFDCShifts(f)
            print "shift = %6.3f, %6.3f"%(adc_shift,tdc_shift)
 
            if DRY_RUN:
                continue

            # fix if shifted more than a certain value
            #if abs(adc_shift) < TOLERANCE[detector] and abs(tdc_shift) < TOLERANCE[detector]:
            #    continue

            # let's apply the offsets
            base_offsets[0][0] = "%7.3f"%(float(base_offsets[0][0]) - adc_shift)
            base_offsets[0][1] = "%7.3f"%(float(base_offsets[0][1]) - tdc_shift)
        else:
            try:
                fr = locHist.Fit("gaus", "SQ", "", maximum - low_limit, maximum + high_limit)
                mean = fr.Parameter(1)
                #print "shift = %6.3f"%mean
                
                if detector == "PS":
                    # we are fitting the PS-TAGH time distribution, so get rid of the TAGH contribution
                    maximum_tagh = locHist_TAGH.GetBinCenter(locHist_TAGH.GetMaximumBin())
                    fr = locHist_TAGH.Fit("gaus", "SQ", "", maximum_tagh - low_limit, maximum_tagh + high_limit)
                    print  "TAGH shift = %6.3f"%fr.Parameter(1)
                    mean = mean + fr.Parameter(1)
                    
            except:
                print "bad fit, skipping..."
                continue

            # fix if shifted more than a certain value
            if abs(mean) < TOLERANCE[detector]:
                continue

            print "shift = %6.3f"%mean

            if DRY_RUN:
                continue

            # let's apply the offsets
            for x in xrange(len(base_offsets[0])):
                base_offsets[0][x] = "%7.3f"%(float(base_offsets[0][x]) - mean)

        pp.pprint(base_offsets)

        ccdb_conn.create_assignment(
                data=base_offsets,
                path=ccdbtable,
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
#                min_run=40785,
#                max_run=ccdb.INFINITE_RUN,
                comment="Fixed calibrations due to bad alignment with RF")


## main function 
if __name__ == "__main__":
    main()
