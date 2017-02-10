# Class to copy values for a table from one run/variation setting to another
# Uses low-level CCDB API
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet
from ccdb.cmd.console_context import ConsoleContext


class HDCCDBCopier:
    def __init__(self,ccdb_connect_str=None,run=0,variation="default",verbosity=None,ccdb_username=None):        
        if verbosity is None:
            self.VERBOSE = 1
        else:
            self.VERBOSE = verbosity
        if ccdb_username is None:
            # not going to save this for now
            ccdb_username = "anonymous"

        # save defaults for copy command
        self.run = run
        self.variation = variation


        # force users to set the CCDB connection by hand
        # so that we don't accidentally hit the MySQL master too hard
        if ccdb_connect_str is None:
            raise RuntimeError("Need to set CCDB connection!")
            
        # create CCDB api class
        self.ccdb_connect_str = ccdb_connect_str
        self.provider = ccdb.AlchemyProvider()                          # this class has all CCDB manipulation functions
        self.provider.connect(ccdb_connect_str)                         # use usual connection string to connect to database
        self.provider.authentication.current_user_name = ccdb_username  # to have a name in logs
        
        if self.VERBOSE>0:
            print "Created HDCCDBCopier object:"
            print "  CCDB: %s"%self.ccdb_connect_str
            print "  Source run = %d"%self.run
            print "  Source variation = %s"%self.variation


    def CopyTable(self,tablename,dest_minrun=0,dest_maxrun=None,dest_variation="default",dest_comment=None,src_run=None,src_variation=None):
        """
        Copy table from one run/variation to another using low-level API
        """
       # set destination defaults
        if dest_comment is None:
            dest_comment =""
        if dest_maxrun is None:
            dest_maxrun = dest_minrun
        # allow overriding source defaults
        if src_run is None:
            src_run = self.run
        if src_variation is None:
            src_variation = self.variation

        if self.VERBOSE>0:
            print "copying %s:%d:%s -> %s:%d:%s"%(tablename,src_run,src_variation,tablename,dest_minrun,dest_variation)

        # get the source table
        src_assignment = self.provider.get_assignment(tablename, src_run, src_variation)

        if self.VERBOSE>1:
            print str(src_assignment)
            if self.VERBOSE>2:
                print(src_assignment.constant_set.data_table)

        # copy it to the destination
        self.provider.create_assignment(data=src_assignment.constant_set.data_table,
                                        path=tablename,
                                        variation_name=dest_variation,
                                        min_run=dest_minrun,
                                        max_run=dest_maxrun,
                                        comment=dest_comment)


if __name__ == "__main__":
    # what
    print "what"
