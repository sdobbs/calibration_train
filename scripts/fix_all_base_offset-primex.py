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

from ROOT import TFile,TH1I,TH2I,TFitResultPtr


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
    RCDB_QUERY = ""
    #RCDB_QUERY = "@is_production and @status_approved"
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
        print "===%d==="%run

        cdc_base_time_assignment = ccdb_conn.get_assignment("/CDC/base_time_offset", run, VARIATION)
        cdc_base_time_offsets = cdc_base_time_assignment.constant_set.data_table
        fdc_base_time_assignment = ccdb_conn.get_assignment("/FDC/base_time_offset", run, VARIATION)
        fdc_base_time_offsets = fdc_base_time_assignment.constant_set.data_table

        fcal_base_time_assignment = ccdb_conn.get_assignment("/FCAL/base_time_offset", run, VARIATION)
        fcal_base_time_offsets = fcal_base_time_assignment.constant_set.data_table
        bcal_base_time_assignment = ccdb_conn.get_assignment("/BCAL/base_time_offset", run, VARIATION)
        bcal_base_time_offsets = bcal_base_time_assignment.constant_set.data_table
        #tof_base_time_assignment = ccdb_conn.get_assignment("/TOF/base_time_offset", run, VARIATION)
        #tof_base_time_offsets = tof_base_time_assignment.constant_set.data_table
        sc_base_time_assignment = ccdb_conn.get_assignment("/START_COUNTER/base_time_offset", run, VARIATION)
        sc_base_time_offsets = sc_base_time_assignment.constant_set.data_table

        tagh_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/hodoscope/base_time_offset", run, VARIATION)
        tagh_base_time_offsets = tagh_base_time_assignment.constant_set.data_table
        tagm_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/base_time_offset", run, VARIATION)
        tagm_base_time_offsets = tagm_base_time_assignment.constant_set.data_table

        ps_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/pair_spectrometer/base_time_offset", run, VARIATION)
        ps_base_time_offsets = ps_base_time_assignment.constant_set.data_table

        # let's find the changes to make
        run_chan_errors = {}

        #f = TFile("/cache/halld/RunPeriod-2017-01/calib/ver18/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        f = TFile("/cache/halld/RunPeriod-2018-08/calib/ver04/hists/Run%06d/hd_calib_verify_Run%06d_001.root"%(run,run))
        #f = TFile("/work/halld/data_monitoring/RunPeriod-2017-01/mon_ver11/rootfiles/hd_root_%06d.root"%run)
        #f = TFile("/lustre/expphy/work/halld/home/sdobbs/calib/2017-01/hd_root.root")
        locHist = f.Get("/HLDetectorTiming/TRACKING/Tagger - RFBunch 1D Time")

        try:
            maximum = locHist.GetBinCenter(locHist.GetMaximumBin());
            fr = locHist.Fit("gaus", "S", "", maximum - 0.3, maximum + 0.3);
            mean = fr.Parameter(1);

        except:
            print "file for run %d doesn't exit, skipping..."%run
            continue

        print "shift = " + str(mean)

        # fix if shifted more than 20 ps
        if abs(mean) < 0.020:
            continue


        # let's apply the offsets
        delta = mean

        new_sc_adc_run_offset = float(sc_base_time_offsets[0][0]) - delta
        new_sc_tdc_run_offset = float(sc_base_time_offsets[0][1]) - delta

        new_fcal_adc_run_offset = float(fcal_base_time_offsets[0][0]) - delta
        new_cdc_adc_run_offset = float(cdc_base_time_offsets[0][0]) - delta

        new_bcal_adc_run_offset = float(bcal_base_time_offsets[0][0]) - delta
        new_bcal_tdc_run_offset = float(bcal_base_time_offsets[0][1]) - delta
        #new_tof_adc_run_offset = float(tof_base_time_offsets[0][0]) - delta
        #new_tof_tdc_run_offset = float(tof_base_time_offsets[0][1]) - delta
        new_fdc_adc_run_offset = float(fdc_base_time_offsets[0][0]) - delta
        new_fdc_tdc_run_offset = float(fdc_base_time_offsets[0][1]) - delta

        new_tagh_adc_run_offset = float(tagh_base_time_offsets[0][0]) - delta
        new_tagh_tdc_run_offset = float(tagh_base_time_offsets[0][1]) - delta
        new_tagm_adc_run_offset = float(tagm_base_time_offsets[0][0]) - delta
        new_tagm_tdc_run_offset = float(tagm_base_time_offsets[0][1]) - delta

        new_ps_adc_run_offset = float(ps_base_time_offsets[0][2]) - delta
        new_psc_adc_run_offset = float(ps_base_time_offsets[0][0]) - delta
        new_psc_tdc_run_offset = float(ps_base_time_offsets[0][1]) - delta

        ccdb_conn.create_assignment(
            data=[ [new_sc_adc_run_offset, new_sc_tdc_run_offset] ],
            path="/START_COUNTER/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_cdc_adc_run_offset ] ],
            path="/CDC/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_fcal_adc_run_offset] ],
            path="/FCAL/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")

        ccdb_conn.create_assignment(
            data=[ [new_bcal_adc_run_offset, new_bcal_tdc_run_offset] ],
            path="/BCAL/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")
        #ccdb_conn.create_assignment(
        #    data=[ [new_tof_adc_run_offset, new_tof_tdc_run_offset] ],
        #    path="/TOF/base_time_offset",
        #    variation_name=VARIATION,
        #    min_run=run,
        #    max_run=run,
        #    comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_fdc_adc_run_offset, new_fdc_tdc_run_offset] ],
            path="/FDC/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")

        ccdb_conn.create_assignment(
            data=[ [new_tagh_adc_run_offset, new_tagh_tdc_run_offset] ],
            path="/PHOTON_BEAM/hodoscope/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_tagm_adc_run_offset, new_tagm_tdc_run_offset] ],
            path="/PHOTON_BEAM/microscope/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_psc_adc_run_offset, new_psc_tdc_run_offset, new_ps_adc_run_offset] ],
            path="/PHOTON_BEAM/pair_spectrometer/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")




## main function 
if __name__ == "__main__":
    main()
