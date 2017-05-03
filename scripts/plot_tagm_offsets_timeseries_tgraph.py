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

    adc_run_offsets = []
    tdc_run_offsets = []
    adc_tdc_diff_run_offsets = []

    for x in xrange(150):
        adc_run_offsets.append( array('f') ) 
        tdc_run_offsets.append( array('f') ) 
        adc_tdc_diff_run_offsets.append( array('f') ) 


    # Fill data
    for run in runs:
        print "==%d=="%run

        base_time_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/base_time_offset", run, VARIATION)
        base_time_offsets = base_time_assignment.constant_set.data_table
        
        pp.pprint(base_time_offsets)

        adc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/fadc_time_offsets", run, VARIATION)
        tdc_toff_assignment = ccdb_conn.get_assignment("/PHOTON_BEAM/microscope/tdc_time_offsets", run, VARIATION)
        adc_offsets = adc_toff_assignment.constant_set.data_table
        tdc_offsets = tdc_toff_assignment.constant_set.data_table

        for x in xrange(len(adc_offsets)):
            adc_run_offsets[x].append( float(adc_offsets[x][2]) - float(base_time_offsets[0][0]) )
            tdc_run_offsets[x].append( float(tdc_offsets[x][2]) - float(base_time_offsets[0][1]) )
            adc_tdc_diff_run_offsets[x].append( float(adc_offsets[x][2]) - float(base_time_offsets[0][0]) - (float(tdc_offsets[x][2]) - float(base_time_offsets[0][1])) )

    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    for x in xrange(150):
        if len(adc_run_offsets[x]) == 0:
            continue

        gr = TGraph(len(runs_arr), runs_arr, adc_run_offsets[x])
        gr.SetName("tagm_adc_offset%d"%x)
        gr.SetTitle("TAGM ADC offset, CCDB Index %d"%x)
        gr.Write()

        gr2 = TGraph(len(runs_arr), runs_arr, tdc_run_offsets[x])
        gr2.SetName("tagm_tdc_offset%d"%x)
        gr2.SetTitle("TAGM TDC offset, CCDB Index %d"%x)
        gr2.Write()

        gr3 = TGraph(len(runs_arr), runs_arr, adc_tdc_diff_run_offsets[x])
        gr3.SetName("tagm_adc_tdc_offset%d"%x)
        gr3.SetTitle("TAGM ADC - TDC offset, CCDB Index %d"%x)
        gr3.Write()
        
    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
