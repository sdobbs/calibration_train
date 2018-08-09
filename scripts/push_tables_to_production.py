## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
from ROOT import TFile,TTree
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
    provider.authentication.current_user_name = "gxproj3"    # to have a name in logs

    return provider


# assumes both are same table format
def check_out_of_tolerance(table1,table2,tolerance,verbose=0):
    result = False
    max_diff = 0
    # I hope these are all non-strings...
    for row in xrange(len(table1)):
        for col in xrange(len(table1[row])):
            #print float(table1[row][col]),float(table2[row][col])
            diff = abs(float(table1[row][col])-float(table2[row][col]))
            if diff > tolerance:
                if diff > max_diff:
                    max_diff = diff
                result = True

    # we're all good
    if verbose>0 and result:
        print "max delta = ",max_diff
    return result


def main():
    pp = pprint.PrettyPrinter(indent=4)

    # Defaults
    OUTPUT_FILENAME = "out.root"
    #RCDB_QUERY = "@is_production and @status_approved"
    RCDB_QUERY = "@is_2018production"
    SRC_VARIATION = "calib"
    DEST_VARIATION = "default"
    BEGIN_RUN = 1
    END_RUN = 10000000
    VERBOSE = 1
    DUMMY_RUN = False

    # Define command line options
    parser = OptionParser(usage = "dump_timeseries.py ccdb_tablename")
    #parser.add_option("-T","--table_file", dest="table_file", 
    #                  help="File of CCDB tables to copy")
    parser.add_option("-F","--run_file", dest="run_file", 
                      help="File of runs to look at")
    parser.add_option("-b","--begin-run", dest="begin_run",
                     help="Starting run for output")
    parser.add_option("-e","--end-run", dest="end_run",
                     help="Ending run for output")
    parser.add_option("-D","--dest_variation", dest="dest_variation", 
                      help="Desitination CCDB variation to use")
    parser.add_option("-S","--src_variation", dest="src_variation", 
                      help="Source CCDB variation to use")
    parser.add_option("-M","--dummy-run", dest="dummy_run", action="store_true",
                      help="Do everything but actually committing changes to the CCDB")

    (options, args) = parser.parse_args(sys.argv)

    if(len(args) < 2):
        parser.print_help()
        sys.exit(0)

    CCDB_TABLES = []
    CCDB_TOLERANCES = {}
    with open(args[1]) as f:
        for line in f:
            if len(line.strip()) == 0:
                continue
            if line.strip()[0] == '#':
                continue
            try:
                tokens = line.strip().split()
                CCDB_TABLES.append(tokens[0])
                CCDB_TOLERANCES[tokens[0]] = float(tokens[1])
            except:
                print "Ignoring line: "+line.strip()

    if options.dest_variation:
        DEST_VARIATION = options.dest_variation
    if options.src_variation:
        SRC_VARIATION = options.src_variation
    if options.begin_run:
        BEGIN_RUN = options.begin_run
    if options.end_run:
        END_RUN = options.end_run
    if options.dummy_run:
        DUMMY_RUN = True

    if VERBOSE>0:
        print "CCDB_TABLES:"
        pp.pprint(CCDB_TABLES)
        print "CCDB_TOLERANCES:"
        pp.pprint(CCDB_TOLERANCES)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    # get run list
    runs = None

    if options.run_file:
        runs = []
        with open(options.run_file) as f:
            for line in f:
                try:
                    runs.append(int(line.strip()))
                except:
                    print "Ignoring line: "+line.strip()
    else:
        # Load RCDB
        rcdb_conn = None
        try:
            rcdb_conn = rcdb.RCDBProvider("mysql://rcdb@hallddb.jlab.org/rcdb")
            runs = [ r.number for r in rcdb_conn.select_runs(RCDB_QUERY,BEGIN_RUN,END_RUN) ]
        except:
            e = sys.exc_info()[0]
            print "Could not connect to RCDB: " + str(e)
    
    if runs is None:
        print "no runs specified!"
        return
    if CCDB_TABLES is None or len(CCDB_TABLES)==0:
        print "no tables specified!"
        return

    print runs

    for run in runs:
        print "===Checking run %d==="%run
        for ccdb_table in CCDB_TABLES:
            if VERBOSE>1:
                print "==copying %s for run %d=="%(ccdb_table,run)
            # get source data
            assignment = ccdb_conn.get_assignment(ccdb_table, run, SRC_VARIATION)
            reference_assignment = ccdb_conn.get_assignment(ccdb_table, run, DEST_VARIATION)
            #pp.pprint(assignment.constant_set.data_table)

            if not check_out_of_tolerance(assignment.constant_set.data_table, reference_assignment.constant_set.data_table, CCDB_TOLERANCES[ccdb_table], verbose=VERBOSE):
                continue
                                      
            print "copying ",ccdb_table
            if DUMMY_RUN:
                continue

            # add to destination
            ccdb_conn.create_assignment(
                data=assignment.constant_set.data_table,
                path=ccdb_table,
                variation_name=DEST_VARIATION,
                min_run=run,
                max_run=ccdb.INFINITE_RUN,
                comment="Copied from variation \'%s\'"%ccdb_table)


            # HANDLE SOME SPECIAL CASES
            if ccdb_table == "/PHOTON_BEAM/RF/time_offset":
                ccdb_table = "/PHOTON_BEAM/RF/time_offset_var"
                assignment = ccdb_conn.get_assignment(ccdb_table, run, SRC_VARIATION)
                ccdb_conn.create_assignment(
                    data=assignment.constant_set.data_table,
                    path=ccdb_table,
                    variation_name=DEST_VARIATION,
                    min_run=run,
                    max_run=ccdb.INFINITE_RUN,
                    comment="Copied from variation \'%s\'"%ccdb_table)

        #print "===%d==="%run
        #pp.pprint(assignment.constant_set.data_table)

    

## main function 
if __name__ == "__main__":
    main()
