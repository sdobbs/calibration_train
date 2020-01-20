## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TGraph
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
    #RCDB_QUERY = "@is_production and @status_approved"
    RCDB_QUERY = "@is_2018production and status!=0"
    VARIATION = "default"
    #VARIATION = "calib"
    BEGINRUN = 1
    ENDRUN = 100000000

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    parser.add_option("-b","--begin-run", dest="begin_run",
                     help="Starting run for output")
    parser.add_option("-e","--end-run", dest="end_run",
                     help="Ending run for output")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)

    if options.begin_run:
        BEGINRUN = int(options.begin_run)
    if options.end_run:
        ENDRUN = int(options.end_run)

    CCDB_TABLE = args[1]
    CCDB_TABLE_ROOT = CCDB_TABLE.replace('/','_')

    # Load CCDB
    ccdb_conn = LoadCCDB()
    table = ccdb_conn.get_type_table(CCDB_TABLE)
    nentries = len(table.columns)
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

    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")

    # initialize
    ncols = len(table.columns)
    nrows = table.rows_count
    data = []
    data_names = []
    #print "rows = " + str(table.rows_count)
    for row in xrange(table.rows_count):
        i = 0
        for col in table.columns:
            i += 1
            print "working on " + col.name
            data.append( array('f') )
            if table.rows_count > 1:
                name = col.name+"_"+str(row*ncols+i)
                #print name
                #print "%d %d %d"%(row,ncols,i)
                data_names.append(name)
            else:
                data_names.append(col.name)

    # Fill data
    for run in runs:
        assignment = ccdb_conn.get_assignment(CCDB_TABLE, run, VARIATION)
        #print "===%d==="%run
        #print(assignment.constant_set.data_table)
        #print "%d %d"%(nrows,ncols)
        #print run,assignment.constant_set.data_table[0][0]
        print run,assignment.constant_set.data_table
        
        for row in xrange(nrows):
            for col in xrange(ncols):
                #print str(row*ncols+col)
                data[row*ncols+col].append(float(assignment.constant_set.data_table[row][col]) )

    # write out graphs
    for i in xrange(len(data)):
        gr = TGraph(len(runs_arr), runs_arr, data[i])
        gr.SetName(data_names[i])
        gr.Write()
    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
