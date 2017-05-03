## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TGraph,TF1
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
    runs_arr.fromlist(runs)

    #bcal_res = []
    #fcal_res = []
    #sc_res = []
    #tof_res = []
    bcal_res = array('f') 
    fcal_res = array('f') 
    sc_res = array('f') 
    tof_res = array('f') 

    bcal_mean = array('f') 
    fcal_mean = array('f') 
    sc_mean = array('f') 
    tof_mean = array('f') 

    cdc_mean = array('f') 
    fdc_mean = array('f') 

    # Fill data
    for run in runs:
        print "==%d=="%run
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver13/rootfiles/hd_root_%06d.root"%run)
        f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver16/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))

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


        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.3, maximum + 0.4)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        bcal_mean.append(mean)
        bcal_res.append(sigma)

        # FCAL
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/FCAL/DeltaTVsP_Pi-")
        locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.8, maximum + 0.8)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        fcal_mean.append(mean)
        fcal_res.append(sigma)

        # SC
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/SC/DeltaTVsP_Pi-")
        locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.3, maximum + 0.3)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        sc_mean.append(mean)
        sc_res.append(sigma)

        # TOF
        locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/TOF/DeltaTVsP_Pi-")
        locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")

        maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
        fr = locHist.Fit("gaus", "S", "", maximum - 0.15, maximum + 0.15)
        mean = fr.Parameter(1)
        sigma = fr.Parameter(2)
        
        tof_mean.append(mean)
        tof_res.append(sigma)

        # CDC
        try:
            locHist = f.Get("HLDetectorTiming/TRACKING/Earliest CDC Time Minus Matched SC Time")
            
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin())
            fr = locHist.Fit("gaus", "S", "", maximum - 15., maximum + 10.)
            mean = fr.Parameter(1)
            
            cdc_mean.append(mean)

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
        except:
            fdc_mean.append(0)

    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    # write out graphs
    bcal_gr = TGraph(len(runs_arr), runs_arr, bcal_res)
    bcal_gr.SetName("bcal_res")
    bcal_gr.SetTitle("BCAL time resolution vs. run number")
    bcal_gr.Write()

    fcal_gr = TGraph(len(runs_arr), runs_arr, fcal_res)
    fcal_gr.SetName("fcal_res")
    fcal_gr.SetTitle("FCAL time resolution vs. run number")
    fcal_gr.Write()
    
    sc_gr = TGraph(len(runs_arr), runs_arr, sc_res)
    sc_gr.SetName("sc_res")
    sc_gr.SetTitle("SC time resolution vs. run number")
    sc_gr.Write()

    tof_gr = TGraph(len(runs_arr), runs_arr, tof_res)
    tof_gr.SetName("tof_res")
    tof_gr.SetTitle("TOF time resolution vs. run number")
    tof_gr.Write()

    bcal_mean_gr = TGraph(len(runs_arr), runs_arr, bcal_mean)
    bcal_mean_gr.SetName("bcal_mean")
    bcal_mean_gr.SetTitle("BCAL time mean vs. run number")
    bcal_mean_gr.Write()

    fcal_mean_gr = TGraph(len(runs_arr), runs_arr, fcal_mean)
    fcal_mean_gr.SetName("fcal_mean")
    fcal_mean_gr.SetTitle("FCAL time mean vs. run number")
    fcal_mean_gr.Write()
    
    sc_mean_gr = TGraph(len(runs_arr), runs_arr, sc_mean)
    sc_mean_gr.SetName("sc_mean")
    sc_mean_gr.SetTitle("SC time mean vs. run number")
    sc_mean_gr.Write()

    tof_mean_gr = TGraph(len(runs_arr), runs_arr, tof_mean)
    tof_mean_gr.SetName("tof_mean")
    tof_mean_gr.SetTitle("TOF time mean vs. run number")
    tof_mean_gr.Write()

    cdc_mean_gr = TGraph(len(runs_arr), runs_arr, cdc_mean)
    cdc_mean_gr.SetName("cdc_mean")
    cdc_mean_gr.SetTitle("CDC time mean vs. run number")
    cdc_mean_gr.Write()

    fdc_mean_gr = TGraph(len(runs_arr), runs_arr, fdc_mean)
    fdc_mean_gr.SetName("fdc_mean")
    fdc_mean_gr.SetTitle("FDC time mean vs. run number")
    fdc_mean_gr.Write()

    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
