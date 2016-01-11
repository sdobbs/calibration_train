# Class to copy values for a table from one run/variation setting to another
# Uses standard CLI commands
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os 
import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet
from ccdb.cmd.console_context import ConsoleContext

from tempfile import NamedTemporaryFile

class HDCCDBCopierCLI:
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

        # we need to load the console CCDB interface if we want to use the CLI commands
        self.ccdb_connect_str = ccdb_connect_str
        self.console = ConsoleContext()        # main CLI class
        self.console.silent_exceptions = False                   
        self.console.theme = ccdb.cmd.themes.NoColorTheme()      
        self.console.connection_string = self.ccdb_connect_str
        self.console.user_name = ccdb_username
        self.console.register_utilities()      # initialization

        if self.VERBOSE>0:
            print "Created HDCCDBCopier object:"
            print "  CCDB: %s"%self.ccdb_connect_str
            print "  Source run = %d"%self.run
            print "  Source variation = %s"%self.variation


    def CopyTable(self,tablename,dest_minrun=0,dest_maxrun=None,dest_variation="default",dest_comment=None,src_run=None,src_variation=None):
        """
        Copy table from one run/variation to another using low-level API
        This is the default (and preferred method)
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
        fconst = NamedTemporaryFile(delete=False)
        tmpfile_name = fconst.name
        self.console.process_command_line("dump %s:%d:%s > %s"%(tablename,src_run,src_variation,fconst.name))
        fconst.flush()
        fconst.close()

        # copy it to the destination
        self.console.process_command_line("add %s -v %s -r %d-%d %s"%(tablename,dest_variation,dest_minrun,dest_maxrun,tmpfile_name))

        # cleanup
        os.system("rm %s"%(tmpfile_name))

if __name__ == "__main__":
    # what
    print "what"
