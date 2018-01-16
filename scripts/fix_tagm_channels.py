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
    
    outf = open("bad_channels.txt","w")

    # Print to screen
    for run in runs:
        print "===%d==="%run
        adc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/fadc_time_offsets", run, VARIATION)
        tdc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/tdc_time_offsets", run, VARIATION)
        adc_offsets = adc_toff_assignment.constant_set.data_table
        tdc_offsets = tdc_toff_assignment.constant_set.data_table

        print>>outf, "===%d==="%run
        f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver15/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver15/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        htagm = f.Get("/HLDetectorTiming/TRACKING/TAGM - RFBunch Time")

        try:
            n = htagm.GetNbinsX()
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue


        # let's find the changes to make
        known_bad_channels = [ 26, 48 ]
        run_chan_errors = {}

        #htagm.Print("base")
        pdf_fname = "tagm_rfalign_r%d.pdf"%run
        for i in xrange(1,htagm.GetNbinsX()+1):
            # don't plot individual columns
            if i>=10 and i<=14:
                continue
            if i>=33 and i<=37:
                continue
            if i>=92 and i<=96:
                continue
            if i>=115 and i<=119:
                continue
            if i in known_bad_channels:
                continue

            hy = htagm.ProjectionY("_%d"%i,i,i)
            #tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)
            maximum = hy.GetBinCenter(hy.GetMaximumBin());
            fr = hy.Fit("gaus", "QS", "", maximum - 0.3, maximum + 0.3);
            mean = fr.Parameter(1);
            tdiff = mean

            if tdiff < -18.:
                continue
            
            if abs(tdiff)>1.:
                print "bad channel = %d, shift = %5.2f"%(i,tdiff)
                print>>outf, "bad channel = %d"%i

                #if i == 64:
                #    tdiff = -100.

                run_chan_errors[i-1] = tdiff

        # don't need to do anything!
        if len(run_chan_errors) == 0:
            continue

        print "shifts = "
        pp.pprint(run_chan_errors)

        continue

        # let's apply the offsets
        for chan,tdiff in run_chan_errors.iteritems():
            adc_offsets[chan][2] = str(float(adc_offsets[chan][2]) + tdiff)
            tdc_offsets[chan][2] = str(float(tdc_offsets[chan][2]) + tdiff)
    
        ccdb_conn.create_assignment(
                data=adc_offsets,
                path="/PHOTON_BEAM/microscope/fadc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad RF shifts")
        ccdb_conn.create_assignment(
                data=tdc_offsets,
                path="/PHOTON_BEAM/microscope/tdc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad RF shifts")



            #hy.Draw()

            #if i==1:
            #    c1.Print(pdf_fname+"(")
            #if i==(htagm.GetNbinsX()):
            #    c1.Print(pdf_fname+")")
            #else:
            #    c1.Print(pdf_fname)
            


## main function 
if __name__ == "__main__":
    main()
