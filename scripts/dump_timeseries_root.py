## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TTree
import rcdb
from optparse import OptionParser
from array import array

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

def LoadCCDB():
    #sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "anonymous"  # to have a name in logs

    return provider


def main():
    # Defaults
    OUTPUT_FILENAME = "out.root"
    RCDB_QUERY = "@is_production and @status_approved"
    VARIATION = "default"

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    #parser.add_option("-p","--disable_plots", dest="disable_plotting", action="store_true",
    #                 help="Don't make PNG files for web display")
    
    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)

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
    runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY) ]


    # Initialize output file
    fout = TFile(OUTPUT_FILENAME, "recreate")
    T = TTree(CCDB_TABLE_ROOT, CCDB_TABLE_ROOT)

    # initialize tree
    RunNum = array('i', [0])
    T.Branch( 'run', RunNum, "run/I" )

    ncols = len(table.columns)
    nrows = table.rows_count
    data = []
    print "rows = " + str(table.rows_count)
    for row in xrange(table.rows_count):
        i = 0
        for col in table.columns:
            i += 1
            d = array( 'f', [ 0. ] )
            data.append( d )
            #print "making branch " + col.name
            if table.rows_count > 1:
                name = col.name+"_"+str(row*ncols+i)
                print name
                print "%d %d %d"%(row,ncols,i)
                T.Branch( name, data[row*ncols+i-1], name+"/F" )
            else:
                T.Branch( col.name, data[row*ncols+i-1], col.name+"/F" )

    # Fill tree
    for run in runs:
        assignment = ccdb_conn.get_assignment(CCDB_TABLE, run, VARIATION)
        #print "===%d==="%run
        #print(assignment.constant_set.data_table)
        RunNum[0] = run
        print "%d %d"%(nrows,ncols)
        for row in xrange(nrows):
            for col in xrange(ncols):
                #print str(row*ncols+col)
                data[row*ncols+col] = assignment.constant_set.data_table[row][col]
        T.Fill()

    # cleanup
    T.Write()
    fout.Close()

    

## main function 
if __name__ == "__main__":
    main()
