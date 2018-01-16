## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TGraphErrors,TF1
import rcdb
from optparse import OptionParser
from array import array

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"     # to have a name in logs

    return provider


def main():
    # Defaults
    OUTPUT_FILENAME = "out.root"
    RCDB_QUERY = "@is_production and @status_approved"
    VARIATION = "default"
    BEGINRUN = 1
    ENDRUN = 100000000

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    parser.add_option("-b","--begin-run", dest="begin_run",
                     help="Starting run for output")
    parser.add_option("-e","--end-run", dest="end_run",
                     help="Ending run for output")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 1):
        parser.print_help()
        sys.exit(0)

    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)


    # Load CCDB
    #ccdb_conn = LoadCCDB()
    #table = ccdb_conn.get_type_table(CCDB_TABLE)
    #nentries = len(table.columns)
    #print (table)
    #print(table.path)
    #print(table.columns)
    #exit(0)

    # Load RCDB
    rcdb_conn = None
    try:
        rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
    except:
        e = sys.exc_info()[0]
        print "Could not connect to RCDB: " + str(e)
    
    # get run list
    runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY, BEGINRUN, ENDRUN) ]
    runs_arr = array('f')
    #runs_arr.fromlist(runs)
    x_err = array('f')

    #bcal_res = []
    #fcal_res = []
    #sc_res = []
    #tof_res = []
    bcal_res = array('f') 
    fcal_res = array('f') 
    sc_res = array('f') 
    tof_res = array('f') 
    tagh_res = array('f') 
    tagm_res = array('f') 

    bcal_mean = array('f') 
    fcal_mean = array('f') 
    sc_mean = array('f') 
    tof_mean = array('f') 
    tagh_mean = array('f') 
    tagm_mean = array('f') 

    cdc_mean = array('f') 
    fdc_mean = array('f') 

    bcal_res_err = array('f') 
    fcal_res_err = array('f') 
    sc_res_err = array('f') 
    tof_res_err = array('f') 
    tagh_res_err = array('f') 
    tagm_res_err = array('f') 

    bcal_mean_err = array('f') 
    fcal_mean_err = array('f') 
    sc_mean_err = array('f') 
    tof_mean_err = array('f') 
    tagh_mean_err = array('f') 
    tagm_mean_err = array('f') 

    cdc_mean_err = array('f') 
    fdc_mean_err = array('f') 

    # Fill data
    run = 30484
    #for run in runs:
    for fnum in xrange(135):
        print "==%d,%d=="%(run,fnum)
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver15/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver25/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        f = TFile("/cache/halld/offline_monitoring/RunPeriod-2017-01/ver24/hists/030484/hd_root_%06d_%03d.root"%(30484,fnum))

        #print "== /cache/halld/RunPeriod-2017-01/calib/ver14/hists/Run%06d/hd_calib_verify_Run%06d_001.root =="%(run,run)

        # BCAL
        try:
            locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/BCAL/DeltaTVsP_Pi-")
            locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")
        except:
            bcal_mean.append(0)
            bcal_res.append(0)
            fcal_mean.append(0)
            fcal_res.append(0)
            sc_mean.append(0)
            sc_res.append(0)
            tof_mean.append(0)
            tof_res.append(0)
            cdc_mean.append(0)
            fdc_mean.append(0)
            continue

        runs_arr.append(fnum)
        x_err.append(0)

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.3, maximum + 0.4)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        bcal_mean.append(mean)
        bcal_res.append(sigma)
        bcal_mean_err.append(fr.ParError(1))
        bcal_res_err.append(fr.ParError(2))

        # FCAL
        #locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/FCAL/DeltaTVsP_Pi-")
        #locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/FCAL/DeltaTVsShowerE_Photon")
        locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_Photon_1D")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        #fr = locHist.Fit("gaus", "S", "", maximum - 0.8, maximum + 0.8)
        fr = locHist.Fit("gaus", "S", "", maximum - 0.5, maximum + 0.5)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        fcal_mean.append(mean)
        fcal_res.append(sigma)
        fcal_mean_err.append(fr.ParError(1))
        fcal_res_err.append(fr.ParError(2))

        # SC
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/SC/DeltaTVsP_Pi-")
        locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.3, maximum + 0.3)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        sc_mean.append(mean)
        sc_res.append(sigma)
        sc_mean_err.append(fr.ParError(1))
        sc_res_err.append(fr.ParError(2))

        # TOF
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/TOF/DeltaTVsP_Pi-")
        locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.15, maximum + 0.15)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        tof_mean.append(mean)
        tof_res.append(sigma)
        tof_mean_err.append(fr.ParError(1))
        tof_res_err.append(fr.ParError(2))

        # TAGH
        locHist = f.Get("/HLDetectorTiming/TRACKING/Tagger - RFBunch 1D Time")
        try:
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            fr = locHist.Fit("gaus", "S", "", maximum - 0.2, maximum + 0.2)
            mean = fr.Parameter(1)
            sigma = fr.Parameter(2)
        
            tagh_mean.append(mean)
            tagh_res.append(sigma)
            tagh_mean_err.append(fr.ParError(1))
            tagh_res_err.append(fr.ParError(2))
        except:
            tagh_mean.append(0)
            tagh_res.append(0)
            tagh_mean_err.append(0)
            tagh_res_err.append(0)


        # TAGM
        locHist = f.Get("/HLDetectorTiming/TRACKING/TAGM - RFBunch 1D Time")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.2, maximum + 0.2)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        tagm_mean.append(mean)
        tagm_res.append(sigma)
        tagm_mean_err.append(fr.ParError(1))
        tagm_res_err.append(fr.ParError(2))


        # CDC
        try:
            locHist = f.Get("HLDetectorTiming/TRACKING/Earliest CDC Time Minus Matched SC Time")
            
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            fr = locHist.Fit("gaus", "S", "", maximum - 15., maximum + 10.)
            mean = fr.Parameter(1)
            
            cdc_mean.append(mean)
            cdc_mean_err.append(fr.ParError(1))

        # FDC
            locHist = f.Get("HLDetectorTiming/FDC/FDCHit Cathode time")

            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            # assume alignment is okay, look for the main peak, not the fake one near the beginning of the readout window
            if maximum<0.:
                firstbin = locHist.FindBin(0)
                maximum = locHist.GetBinCenter(firstbin)
                maxval = locHist.GetBinContent(firstbin)
                for x in xrange(firstbin+1,locHist.GetNbinsX()):
                    if maxval < locHist.GetBinContent(x):
                        maximum = locHist.GetBinCenter(x)
                        maxval = locHist.GetBinContent(x)

            fn = TF1("fn", "gaus")
            fn.SetParameters(100, maximum, 20)
            fn.FixParameter(1 , maximum)
            fr = locHist.Fit(fn, "S", "", maximum - 30, maximum + 20)
            #fr = locHist.Fit("gaus", "S", "", maximum - 15., maximum + 10.)
            mean = fr.Parameter(1)

            fdc_mean.append(mean)
            fdc_mean_err.append(fr.ParError(1))
        except:
            fdc_mean.append(0)
            fdc_mean_err.append(0)

    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    # write out graphs
    bcal_gr = TGraphErrors(len(runs_arr), runs_arr, bcal_res, x_err, bcal_res_err)
    bcal_gr.SetName("bcal_res")
    bcal_gr.SetTitle("BCAL time resolution vs. run number")
    bcal_gr.Write()

    fcal_gr = TGraphErrors(len(runs_arr), runs_arr, fcal_res, x_err, fcal_res_err)
    fcal_gr.SetName("fcal_res")
    fcal_gr.SetTitle("FCAL time resolution vs. run number")
    fcal_gr.Write()
    
    sc_gr = TGraphErrors(len(runs_arr), runs_arr, sc_res, x_err, sc_res_err)
    sc_gr.SetName("sc_res")
    sc_gr.SetTitle("SC time resolution vs. run number")
    sc_gr.Write()

    tof_gr = TGraphErrors(len(runs_arr), runs_arr, tof_res, x_err, tof_res_err)
    tof_gr.SetName("tof_res")
    tof_gr.SetTitle("TOF time resolution vs. run number")
    tof_gr.Write()

    bcal_mean_gr = TGraphErrors(len(runs_arr), runs_arr, bcal_mean, x_err, bcal_mean_err)
    bcal_mean_gr.SetName("bcal_mean")
    bcal_mean_gr.SetTitle("BCAL time mean vs. run number")
    bcal_mean_gr.Write()

    fcal_mean_gr = TGraphErrors(len(runs_arr), runs_arr, fcal_mean, x_err, fcal_mean_err)
    fcal_mean_gr.SetName("fcal_mean")
    fcal_mean_gr.SetTitle("FCAL time mean vs. run number")
    fcal_mean_gr.Write()
    
    sc_mean_gr = TGraphErrors(len(runs_arr), runs_arr, sc_mean, x_err, sc_mean_err)
    sc_mean_gr.SetName("sc_mean")
    sc_mean_gr.SetTitle("SC time mean vs. run number")
    sc_mean_gr.Write()

    tof_mean_gr = TGraphErrors(len(runs_arr), runs_arr, tof_mean, x_err, tof_mean_err)
    tof_mean_gr.SetName("tof_mean")
    tof_mean_gr.SetTitle("TOF time mean vs. run number")
    tof_mean_gr.Write()

    cdc_mean_gr = TGraphErrors(len(runs_arr), runs_arr, cdc_mean, x_err, cdc_mean_err)
    cdc_mean_gr.SetName("cdc_mean")
    cdc_mean_gr.SetTitle("CDC time mean vs. run number")
    cdc_mean_gr.Write()

    fdc_mean_gr = TGraphErrors(len(runs_arr), runs_arr, fdc_mean, x_err, fdc_mean_err)
    fdc_mean_gr.SetName("fdc_mean")
    fdc_mean_gr.SetTitle("FDC time mean vs. run number")
    fdc_mean_gr.Write()

    tagh_mean_gr = TGraphErrors(len(runs_arr), runs_arr, tagh_mean, x_err, tagh_mean_err)
    tagh_mean_gr.SetName("tagh_mean")
    tagh_mean_gr.SetTitle("TAGH time mean vs. run number")
    tagh_mean_gr.Write()

    tagh_res_gr = TGraphErrors(len(runs_arr), runs_arr, tagh_res, x_err, tagh_res_err)
    tagh_res_gr.SetName("tagh_res")
    tagh_res_gr.SetTitle("TAGH time res vs. run number")
    tagh_res_gr.Write()

    tagm_mean_gr = TGraphErrors(len(runs_arr), runs_arr, tagm_mean, x_err, tagm_mean_err)
    tagm_mean_gr.SetName("tagm_mean")
    tagm_mean_gr.SetTitle("TAGM time mean vs. run number")
    tagm_mean_gr.Write()

    tagm_res_gr = TGraphErrors(len(runs_arr), runs_arr, tagm_res, x_err, tagm_res_err)
    tagm_res_gr.SetName("tagm_res")
    tagm_res_gr.SetTitle("TAGM time res vs. run number")
    tagm_res_gr.Write()

    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
