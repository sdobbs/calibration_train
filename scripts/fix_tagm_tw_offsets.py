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
        if run == 30480 or run == 30300:
            continue

        print "===%d==="%run
        adc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/fadc_time_offsets", run, VARIATION)
        tdc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/tdc_time_offsets", run, VARIATION)
        #pp.pprint(tdc_toff_assignment.constant_set.data_table)
        adc_offsets = adc_toff_assignment.constant_set.data_table
        tdc_offsets = tdc_toff_assignment.constant_set.data_table

        # let's find the changes to make
        adc_run_chan_errors = {}
        tdc_run_chan_errors = {}

        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver23/rootfiles/hd_root_%06d.root"%run)
        f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver30/hists/Run%06d/hd_calib_verify_Run%06d_000.root"%(run,run))
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        htagm_adc = f.Get("/TAGM_TW/adc_rf_all")
        htagm_tdc = f.Get("/TAGM_TW/t_adc_all")

        try:
            n = htagm_adc.GetNbinsX()
        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue

        #htagm.Print("base")
        for i in xrange(1,htagm_adc.GetNbinsY()+1):

            if i-1 == 20 or i-1 == 27:
                continue

            hx = htagm_adc.ProjectionX("_%d"%i,i,i)
            #print i,hy.GetBinCenter(hy.GetMaximumBin())
            #print i,hy.GetBinLowEdge(hy.GetMaximumBin()+1)
            #tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)
            maximum = hx.GetBinCenter(hx.GetMaximumBin());
            try:
                fr = hx.Fit("gaus", "SQ", "", maximum - 0.3, maximum + 0.3);
                mean = fr.Parameter(1);
                sigma = fr.Parameter(2);
            except:
                continue
            tdiff = abs(mean)
        
            # no data in these channels
            #if tdiff < 0.2:
            #    continue

            #print i,tdiff

            # this channel is fine!
            if tdiff == 0.:
                continue

            # only look for non-zero shifts
            if math.fabs(tdiff) < 0.2:
                continue
            #if math.fabs(tdiff) < 2.:
            #if math.fabs(tdiff) < 4.:
            #    continue

            if math.fabs(tdiff) > 50.:
                continue

            ind = i-1
            if ind >= 84:
                ind += 20
            elif ind >= 71:
                ind += 15
            elif ind >= 22:
                ind += 10
            elif ind >= 9:
                ind += 5

            if adc_offsets[ind][1] == "0" and ind > 10:
                adc_offsets[ind][1] = str(ind)

            adc_run_chan_errors[ind] = tdiff

        for i in xrange(1,htagm_tdc.GetNbinsY()+1):

            if i-1 == 20 or i-1 == 27:
                continue

            # now look at TDCs
            hx = htagm_tdc.ProjectionX("_%d"%i,i,i)
            maximum = hx.GetBinCenter(hx.GetMaximumBin());
            try:
                fr = hx.Fit("gaus", "SQ", "", maximum - 0.3, maximum + 0.3);
                mean = fr.Parameter(1);
                sigma = fr.Parameter(2);
            except:
                continue
            tdc_tdiff = abs(mean)            
            print i,tdc_tdiff

            if tdc_tdiff == 0.:
                continue
            if math.fabs(tdc_tdiff) < 0.2:
                continue
            if math.fabs(tdc_tdiff) > 50.:
                continue

            ind = i-1
            if ind >= 84:
                ind += 20
            elif ind >= 71:
                ind += 15
            elif ind >= 22:
                ind += 10
            elif ind >= 9:
                ind += 5

            if tdc_offsets[ind][1] == '0' and ind > 10:
                tdc_offsets[ind][1] = str(ind)

            if ind in adc_run_chan_errors.keys():
                tdc_run_chan_errors[ind] = tdc_tdiff + adc_run_chan_errors[ind]
            else:
                tdc_run_chan_errors[ind] = tdc_tdiff
            #tdc_run_chan_errors[i-1] = tdc_tdiff 

        # don't need to do anything!
        if len(adc_run_chan_errors) == 0:
            continue
        if len(tdc_run_chan_errors) == 0:
            continue

        print "ADC shifts = "
        pp.pprint(adc_run_chan_errors)
        print "TDC shifts = "
        pp.pprint(tdc_run_chan_errors)

        #pp.pprint(tdc_offsets)

        #continue

        # let's apply the offsets
        for chan,tdiff in adc_run_chan_errors.iteritems():
            adc_offsets[chan][2] = str(float(adc_offsets[chan][2]) + tdiff)
        for chan,tdiff in tdc_run_chan_errors.iteritems():
            tdc_offsets[chan][2] = str(float(tdc_offsets[chan][2]) + tdiff)
     
        ccdb_conn.create_assignment(
                data=adc_offsets,
                path="/PHOTON_BEAM/microscope/fadc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad ADC/TDC shifts")
        ccdb_conn.create_assignment(
                data=tdc_offsets,
                path="/PHOTON_BEAM/microscope/tdc_time_offsets",
                variation_name=VARIATION,
                min_run=run,
                max_run=run,
                comment="Fixed calibrations due to bad ADC/TDC shifts")


## main function 
if __name__ == "__main__":
    main()
