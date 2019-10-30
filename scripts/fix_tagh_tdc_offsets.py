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

from ROOT import TFile,TH1I,TH2I


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
    #RCDB_QUERY = "@is_production and @status_approved"  
    #RCDB_QUERY = "@is_production"
    RCDB_QUERY = "@is_2018production and status!=0"
    VARIATION = "default"

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
        tdc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/hodoscope/tdc_time_offsets", run, VARIATION)
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        tdc_offsets = tdc_toff_assignment.constant_set.data_table

        # let's find the changes to make
        run_chan_errors = {}

        #f = TFile("/work/halld/data_monitoring/RunPeriod-2018-01/mon_ver06/rootfiles/hd_root_%06d.root"%run)
        f = TFile("/work/halld/data_monitoring/RunPeriod-2018-08/mon_ver13/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver01/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver17/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/cache/halld/RunPeriod-2018-01/calib/ver17/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/work/halld/home/sdobbs/calib/2018-01/hd_root.root")
        #f = TFile("/w/halld-scifs17exp/home/sdobbs/calib/2018-01/hd_root.root")
        #f = TFile("/group/halld/Users/sdobbs/hd_root.root")
        htagm = f.Get("/HLDetectorTiming/TAGH/TAGHHit TDC_ADC Difference")

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
            tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)
        
            # no data in these channels
            if tdiff < -38.:
                continue

            # this channel is fine!
            if tdiff == 0.:
                continue

            # only look for shifts > 1.ns in this
            #if math.fabs(tdiff) < 1.:
            #if math.fabs(tdiff) < 0.5:
            if math.fabs(tdiff) < 20.:
                continue

            run_chan_errors[i-1] = tdiff

        # don't need to do anything!
        if len(run_chan_errors) == 0:
            continue

        print "shifts = "
        pp.pprint(run_chan_errors)

        #continue

        # let's apply the offsets
        for chan,tdiff in run_chan_errors.iteritems():
            tdc_offsets[chan][1] = str(float(tdc_offsets[chan][1]) + tdiff)
    
        ccdb_conn.create_assignment(
                data=tdc_offsets,
                path="/PHOTON_BEAM/hodoscope/tdc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
#                min_run=40785,
#                max_run=ccdb.INFINITE_RUN,
                comment="Fixed calibrations due to bad ADC/TDC shifts")


## main function 
if __name__ == "__main__":
    main()
