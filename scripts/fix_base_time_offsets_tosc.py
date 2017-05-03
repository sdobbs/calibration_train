## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TGraph
import rcdb
from optparse import OptionParser
from array import array
import pprint

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

    pp = pprint.PrettyPrinter(indent=4)

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
    ccdb_conn = LoadCCDB()

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


    # Fill data
    for run in runs:
        print "==%d=="%run

        # peg all the times to the SC TDC timing
        #base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/base_time_offset", run, VARIATION)
        #base_time_offsets = base_time_assignment.constant_set.data_table

        cdc_base_time_assignment = ccdb_conn.get_assignment("/CDC/base_time_offset", run, VARIATION)
        cdc_base_time_offsets = cdc_base_time_assignment.constant_set.data_table
        fdc_base_time_assignment = ccdb_conn.get_assignment("/FDC/base_time_offset", run, VARIATION)
        fdc_base_time_offsets = fdc_base_time_assignment.constant_set.data_table

        fcal_base_time_assignment = ccdb_conn.get_assignment("/FCAL/base_time_offset", run, VARIATION)
        fcal_base_time_offsets = fcal_base_time_assignment.constant_set.data_table
        bcal_base_time_assignment = ccdb_conn.get_assignment("/BCAL/base_time_offset", run, VARIATION)
        bcal_base_time_offsets = bcal_base_time_assignment.constant_set.data_table
        tof_base_time_assignment = ccdb_conn.get_assignment("/TOF/base_time_offset", run, VARIATION)
        tof_base_time_offsets = tof_base_time_assignment.constant_set.data_table
        sc_base_time_assignment = ccdb_conn.get_assignment("/START_COUNTER/base_time_offset", run, VARIATION)
        sc_base_time_offsets = sc_base_time_assignment.constant_set.data_table

        tagh_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/hodoscope/base_time_offset", run, VARIATION)
        tagh_base_time_offsets = tagh_base_time_assignment.constant_set.data_table
        tagm_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/base_time_offset", run, VARIATION)
        tagm_base_time_offsets = tagm_base_time_assignment.constant_set.data_table

        ps_base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/pair_spectrometer/base_time_offset", run, VARIATION)
        ps_base_time_offsets = ps_base_time_assignment.constant_set.data_table

        #pp.pprint(sc_base_time_offsets)
        #print float(sc_base_time_offsets[0][0]) - float(sc_base_time_offsets[0][1])

        sc_tdc_base_offset = float(sc_base_time_offsets[0][1])
        delta =  sc_tdc_base_offset - (-423.)

        # fix SC time to -423 ns
        print "%5.3f  %5.3f"%(sc_tdc_base_offset,delta)


        new_sc_adc_run_offset = float(sc_base_time_offsets[0][0]) - delta
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
            data=[ [new_sc_adc_run_offset, sc_tdc_base_offset-delta] ],
            path="/START_COUNTER/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_cdc_adc_run_offset ] ],
            path="/CDC/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_fcal_adc_run_offset] ],
            path="/FCAL/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")


        ccdb_conn.create_assignment(
            data=[ [new_bcal_adc_run_offset, new_bcal_tdc_run_offset] ],
            path="/BCAL/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_tof_adc_run_offset, new_tof_tdc_run_offset] ],
            path="/TOF/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_fdc_adc_run_offset, new_fdc_tdc_run_offset] ],
            path="/FDC/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")

        ccdb_conn.create_assignment(
            data=[ [new_tagh_adc_run_offset, new_tagh_tdc_run_offset] ],
            path="/PHOTON_BEAM/hodoscope/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_tagm_adc_run_offset, new_tagm_tdc_run_offset] ],
            path="/PHOTON_BEAM/microscope/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")
        ccdb_conn.create_assignment(
            data=[ [new_psc_adc_run_offset, new_psc_tdc_run_offset, new_ps_adc_run_offset] ],
            path="/PHOTON_BEAM/pair_spectrometer/base_time_offset",
            variation_name=VARIATION,
            min_run=run,
            max_run=run,
            comment="Manual shift, from SC alignment")

    

## main function 
if __name__ == "__main__":
    main()
