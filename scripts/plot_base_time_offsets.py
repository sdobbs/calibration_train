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

    sc_adc_run_offsets = array('f')
    fcal_adc_run_offsets = array('f')
    cdc_adc_run_offsets = array('f')

    bcal_adc_run_offsets = array('f')
    bcal_tdc_run_offsets = array('f')
    tof_adc_run_offsets = array('f')
    tof_tdc_run_offsets = array('f')
    fdc_adc_run_offsets = array('f')
    fdc_tdc_run_offsets = array('f')

    tagh_adc_run_offsets = array('f')
    tagh_tdc_run_offsets = array('f')
    tagm_adc_run_offsets = array('f')
    tagm_tdc_run_offsets = array('f')


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

        #pp.pprint(sc_base_time_offsets)
        #print float(sc_base_time_offsets[0][0]) - float(sc_base_time_offsets[0][1])

        sc_tdc_base_offset = float(sc_base_time_offsets[0][1])

        sc_adc_run_offsets.append( float(sc_base_time_offsets[0][0]) - sc_tdc_base_offset)
        fcal_adc_run_offsets.append( float(fcal_base_time_offsets[0][0]) - sc_tdc_base_offset)
        cdc_adc_run_offsets.append( float(cdc_base_time_offsets[0][0]) - sc_tdc_base_offset)

        bcal_adc_run_offsets.append( float(bcal_base_time_offsets[0][0]) - sc_tdc_base_offset)
        bcal_tdc_run_offsets.append( float(bcal_base_time_offsets[0][1]) - sc_tdc_base_offset)
        tof_adc_run_offsets.append( float(tof_base_time_offsets[0][0]) - sc_tdc_base_offset)
        tof_tdc_run_offsets.append( float(tof_base_time_offsets[0][1]) - sc_tdc_base_offset)
        fdc_adc_run_offsets.append( float(fdc_base_time_offsets[0][0]) - sc_tdc_base_offset)
        fdc_tdc_run_offsets.append( float(fdc_base_time_offsets[0][1]) - sc_tdc_base_offset)

        tagh_adc_run_offsets.append( float(tagh_base_time_offsets[0][0]) - sc_tdc_base_offset)
        tagh_tdc_run_offsets.append( float(tagh_base_time_offsets[0][1]) - sc_tdc_base_offset)
        tagm_adc_run_offsets.append( float(tagm_base_time_offsets[0][0]) - sc_tdc_base_offset)
        tagm_tdc_run_offsets.append( float(tagm_base_time_offsets[0][1]) - sc_tdc_base_offset)

        if float(tagh_base_time_offsets[0][1]) - sc_tdc_base_offset < 300:
            print (float(tagh_base_time_offsets[0][1]) - sc_tdc_base_offset)

    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    gr = TGraph(len(runs_arr), runs_arr, sc_adc_run_offsets)
    gr.SetName("sc_adc_run_offsets")
    gr.SetTitle("(SC ADC) - (SC TDC) base time offsets")
    gr.Write()

    gr2 = TGraph(len(runs_arr), runs_arr, fcal_adc_run_offsets)
    gr2.SetName("fcal_adc_run_offsets")
    gr2.SetTitle("(FCAL ADC) - (SC TDC) base time offsets")
    gr2.Write()

    gr3 = TGraph(len(runs_arr), runs_arr, cdc_adc_run_offsets)
    gr3.SetName("cdc_adc_run_offsets")
    gr3.SetTitle("(CDC ADC) - (SC TDC) base time offsets")
    gr3.Write()

    gr4 = TGraph(len(runs_arr), runs_arr, bcal_adc_run_offsets)
    gr4.SetName("bcal_adc_run_offsets")
    gr4.SetTitle("(BCAL ADC) - (SC TDC) base time offsets")
    gr4.Write()

    gr5 = TGraph(len(runs_arr), runs_arr, bcal_tdc_run_offsets)
    gr5.SetName("bcal_tdc_run_offsets")
    gr5.SetTitle("(BCAL TDC) - (SC TDC) base time offsets")
    gr5.Write()

    gr6 = TGraph(len(runs_arr), runs_arr, tof_adc_run_offsets)
    gr6.SetName("tof_adc_run_offsets")
    gr6.SetTitle("(TOF ADC) - (SC TDC) base time offsets")
    gr6.Write()

    gr7 = TGraph(len(runs_arr), runs_arr, tof_tdc_run_offsets)
    gr7.SetName("tof_tdc_run_offsets")
    gr7.SetTitle("(TOF TDC) - (SC TDC) base time offsets")
    gr7.Write()

    gr8 = TGraph(len(runs_arr), runs_arr, fdc_adc_run_offsets)
    gr8.SetName("fdc_adc_run_offsets")
    gr8.SetTitle("(FDC ADC) - (SC TDC) base time offsets")
    gr8.Write()

    gr9 = TGraph(len(runs_arr), runs_arr, fdc_tdc_run_offsets)
    gr9.SetName("fdc_tdc_run_offsets")
    gr9.SetTitle("(FDC TDC) - (SC TDC) base time offsets")
    gr9.Write()

    gr10 = TGraph(len(runs_arr), runs_arr, tagh_adc_run_offsets)
    gr10.SetName("tagh_adc_run_offsets")
    gr10.SetTitle("(TAGH ADC) - (SC TDC) base time offsets")
    gr10.Write()

    gr11 = TGraph(len(runs_arr), runs_arr, tagh_tdc_run_offsets)
    gr11.SetName("tagh_tdc_run_offsets")
    gr11.SetTitle("(TAGH TDC) - (SC TDC) base time offsets")
    gr11.Write()

    gr12 = TGraph(len(runs_arr), runs_arr, tagm_adc_run_offsets)
    gr12.SetName("tagm_adc_run_offsets")
    gr12.SetTitle("(TAGM ADC) - (SC TDC) base time offsets")
    gr12.Write()

    gr13 = TGraph(len(runs_arr), runs_arr, tagm_tdc_run_offsets)
    gr13.SetName("tagm_tdc_run_offsets")
    gr13.SetTitle("(TAGM TDC) - (SC TDC) base time offsets")
    gr13.Write()

        
    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
