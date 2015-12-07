# create report for calibration train

import os,sys
from math import sqrt

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

class HDCalibReport:
    """
    Generate some information to summarize the results of a calibration run

    Compare the newly calibrated run/variation set of constants against a refer
    """

    def __init__(self,table_filename,src_run,ref_run=None,src_variation="calib",ref_variation="default"):
        self.VERBOSE = 1
        # create CCDB api class
        self.provider = ccdb.AlchemyProvider()                          # this class has all CCDB manipulation functions
        self.provider.connect(os.environ['CCDB_CONNECTION'])            # use usual connection string to connect to database
        self.provider.authentication.current_user_name = "calib"        # to have a name in logs

        # configurations
        self.src_variation = src_variation
        self.ref_variation = ref_variation
        self.src_run = src_run
        if ref_run is None:        # default to comparing the same run
            self.ref_run = src_run
        else:
            self.ref_run = ref_run

        # load list of table names we should include in the report
        self.tables = []
        with open(table_filename) as f:
            for line in f:
                if line[0] != '#':
                    self.tables.append(line.strip())

    def GenerateReport(self):
        # print to screen for now
        print "Changes in constants from reference values:"
        print "( Deltas: new - reference )"

        for tablename in self.tables:
            if self.VERBOSE>0:
                print "processing %s ..."%tablename
            
            # get information for each table
            try:
                table = self.provider.get_type_table(tablename)
                assignment = self.provider.get_assignment(self.src_run, table, self.src_variation)
                data = assignment.constant_set.data_table
                ref_assignment = self.provider.get_assignment(self.ref_run, table, self.ref_variation)
                ref_data = ref_assignment.constant_set.data_table
            except:
                e = sys.exc_info()[0]
                print "Exception: " + str(e)
                continue

            #print str(data)
            #print str(ref_data)

            # we want to handle different types of tables differently
            
            # CASE 1:  a single row table
            # assume that it's one named constant per column
            if table.rows_count == 1:
                for x in xrange(len(table.columns)):
                    column_type = str(table.columns[x].type)
                    if column_type != "string" and column_type != "bool":
                        delta = float(data[0][x]) - float(ref_data[0][x])
                        print "%30s = %10.8f"%(table.columns[x].name,delta)

            # CASE 2:  a single column table
            # come up with some summary of the column
            elif len(table.columns) == 1:
                n = 0
                mean = 0 
                sigma = 0     # std. dev.
                # calculate mean
                for x in xrange(table.rows_count):
                    n += 1
                    mean += float(data[x][0])
                mean /= n
                # calculate standard deviation
                for x in xrange(table.rows_count):
                    n += 1
                    sigma += pow(float(data[x][0]) - mean,2)
                sigma /= sqrt(n)
                print "mean = %10.8f   std. dev. = %10.8f"%(mean,sigma)   


if __name__ == "__main__":
    reporter = HDCalibReport(sys.argv[1],sys.argv[2])
    reporter.GenerateReport()
