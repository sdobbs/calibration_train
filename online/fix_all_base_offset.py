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
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "hdsys"  # to have a name in logs

    return provider


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    RCDB_QUERY = ""
    VARIATION = "default"

    # Define command line options
    parser = OptionParser(usage = "fix_all_base_offset.py [RUN] [ROOT_FILE]")
    parser.add_option("-V","--variation", dest="variation", 
                      help="CCDB variation to use")

    (options, args) = parser.parse_args(sys.argv)
    if options.variation:
        VARIATION = options.variation

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # get argument
    run = int(args[1])
    fname = args[2]
    
    f = TFile(fname)

    # get current constants
    cdc_base_time_assignment = ccdb_conn.get_assignment("/CDC/base_time_offset", run, VARIATION)
    cdc_base_time_offsets = cdc_base_time_assignment.constant_set.data_table
    fdc_base_time_assignment = ccdb_conn.get_assignment("/FDC/base_time_offset", run, VARIATION)
    fdc_base_time_offsets = fdc_base_time_assignment.constant_set.data_table

    fcal_base_time_assignment = ccdb_conn.get_assignment("/FCAL/base_time_offset", run, VARIATION)
    fcal_base_time_offsets = fcal_base_time_assignment.constant_set.data_table
    bcal_base_time_assignment = ccdb_conn.get_assignment("/BCAL/base_time_offset", run, VARIATION)
    bcal_base_time_offsets = bcal_base_time_assignment.constant_set.data_table
    tof_base_time_assignment = ccdb_conn.get_assignment("/TOF2/base_time_offset", run, VARIATION)
    tof_base_time_offsets = tof_base_time_assignment.constant_set.data_table
    sc_base_time_assignment = ccdb_conn.get_assignment("/START_COUNTER/base_time_offset", run, VARIATION)
    sc_base_time_offsets = sc_base_time_assignment.constant_set.data_table

    tagh_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/hodoscope/base_time_offset", run, VARIATION)
    tagh_base_time_offsets = tagh_base_time_assignment.constant_set.data_table
    tagm_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/base_time_offset", run, VARIATION)
    tagm_base_time_offsets = tagm_base_time_assignment.constant_set.data_table

    ps_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/pair_spectrometer/base_time_offset", run, VARIATION)
    ps_base_time_offsets = ps_base_time_assignment.constant_set.data_table

    # let's see if there's a 2ns shift
    #try:
    #locHist_DeltaTVsP_PiPlus = f.Get("Independent/Hist_DetectorPID/SC/DeltaTVsP_Pi-")
    #locHist = locHist_DeltaTVsP_PiPlus.ProjectionY("DeltaTVsP_PiMinus_1D")
    locHist = f.Get("HLDetectorTiming/TRACKING/SC - RF Time")

    maximum = locHist.GetBinCenter(locHist.GetMaximumBin());
    fr = locHist.Fit("gaus", "SQ", "", maximum - 0.3, maximum + 0.3);
    mean = fr.Parameter(1);


    print "shift = " + str(mean)
    #continue

    # check that the mean is ~2ns 
    if abs(mean) > 1.2 and abs(mean) < 2.5:
        #os.system("echo correcting for 2ns shift for %s variation ... >> message.txt"%VARIATION)
        print "correcting for 2ns shift for %s variation ..."

        if mean > 0:
            mean = 2.
        else:
            mean = -2.

        # let's apply the offsets
        delta = round(mean)

        new_sc_adc_run_offset = float(sc_base_time_offsets[0][0]) - delta
        new_sc_tdc_run_offset = float(sc_base_time_offsets[0][1]) - delta

        new_fcal_adc_run_offset = float(fcal_base_time_offsets[0][0]) - delta
        new_cdc_adc_run_offset = float(cdc_base_time_offsets[0][0]) - delta

        new_bcal_adc_run_offset = float(bcal_base_time_offsets[0][0]) - delta
        new_bcal_tdc_run_offset = float(bcal_base_time_offsets[0][1]) - delta
        new_tof_adc_run_offset = float(tof_base_time_offsets[0][0]) - delta
        new_tof_tdc_run_offset = float(tof_base_time_offsets[0][1]) - delta
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

        ccdb_conn.create_assignment(
            data=[ [new_tof_adc_run_offset, new_tof_tdc_run_offset] ],
            path="/TOF2/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            #max_run=run,
            max_run=ccdb.INFINITE_RUN,
            comment="Manual shift, from SC alignment")


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
    else:
        print "no correction needed ..."


## main function 
if __name__ == "__main__":
    main()
