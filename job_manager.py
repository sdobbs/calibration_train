#!/usr/bin/env python
#
# Main driver program for job submission.
# Current supports the following commands:
#     job_manager.py init [configuration file]
#     job_manager.py build [configuration file] [run file]
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os,sys
from subprocess import Popen, PIPE
from optparse import OptionParser

import HDConfigFile
import HDJobConfig
import HDRunFileList
import HDRunFileRAIDList
import HDJobSubmitterSWIF
import HDJobSubmitterLocal
#import HDCCDBCopier
import HDCCDBCopierCLI

## TODO: function to delete a run

class HDJobManager:
    """
    Class to manage job bookkeeping and submission
    """

    def __init__(self):
        # Job definitions are stored in a configuration file
        self.config_mgr = None
        # Directory to store job conditions and output
        self.basedir = "/volatile/halld/home/gxproj3/calib_jobs"    # set this by hand for now
        #self.basedir = "/group/halld/Users/sdobbs/calib_jobs"    # set this by hand for now, counting house
        # Where the auto-generated CCDB SQLite file lives
        self.ccdb_dir = "/group/halld/www/halldweb/html/dist"
        self.use_batch_queue = True  # default to using batch queue

        self.ccdb_tables = []

    def LoadCCDBTableList(self,filename):
        tables = []
        with open(filename) as f:
            for line in f.readlines():
                line = line.strip()
                # skip comment lines
                if line[0] == '#':
                    continue
                if len(line)>0:
                    tables.append(line)
        return tables

    def LoadConfig(self,configfile):
        """
        Read configuration file that defines parameters for the current set of jobs
        """ 
        self.config_mgr = HDConfigFile.HDConfigFile(self.basedir,configfile)
        self.config_mgr.LoadConfig()

        # set some useful variables
        if 'jobname' not in self.config_mgr.config:
            print "Job information not loaded correctly!  Exiting..."
            sys.exit(0)
        self.jobname = self.config_mgr.config['jobname']

    def InitJobs(self):
        """
        Do all the preliminary work to set up a new batch of jobs.  This includes
        - building job directories
        - building scripts and input files
        - archiving the current software configuration
        """
        if self.jobname is None:
            print "Job name is not set! Exiting ..."
            sys.exit(0)
        if not os.path.isdir(self.basedir):
            raise RuntimeError("Base job directory not found!")
        
        # make directories
        os.system("mkdir -p %s"%(self.basedir))
        job_dir = os.path.join(self.basedir,self.jobname)
        os.system("mkdir -p %s"%(os.path.join(job_dir,"log")))
        os.system("mkdir -p %s"%(os.path.join(job_dir,"config")))
        script_dir = os.path.join(job_dir,"scripts")
        os.system("mkdir -p %s"%(script_dir))
        os.system("mkdir -p %s"%(os.path.join(job_dir,"output")))

        # copy files over
        os.system("cp -R templates/* "+script_dir)
        #os.system("cp %s/ccdb.sqlite %s"%(self.ccdb_dir,job_dir))

        # set up link to output in web area
        # web content available at  https://halldweb.jlab.org/calib_challenge
        os.system("ln -s %s/%s/output /group/halld/www/halldweb/html/calib_challenge/%s"%(self.basedir,self.jobname,self.jobname))

        # save configuration
        jc = HDJobConfig.HDJobConfig(os.path.join(job_dir,"config","version.xml"), os.path.join(script_dir,"setup_jlab.csh"))
        jc.BuildConfig()

        # load other config parameters
        if 'nthreads' in self.config_mgr.config:
            jc.nthreads = self.config_mgr.config['nthreads']
        if 'mem_requested' in self.config_mgr.config:
            jc.mem_requested = self.config_mgr.config['mem_requested']
        if 'disk_space' in self.config_mgr.config:
            jc.disk_space = self.config_mgr.config['disk_space']
        if 'time_limit' in self.config_mgr.config:
            jc.time_limit = self.config_mgr.config['time_limit']
        jc.DumpConfig()


    def BuildJobs(self, runlist_filename, init_tables=False, passes_to_run_str="all"):
        """
        Create the jobs and prepare them for submission.
        This function takes the name of a file that should contain a list of the runs to 
        submit jobs for, one per line.  We probe known sources to determine how many files
        we need to process per run.
        """
        if self.jobname is None:
            print "Job name is not set! Exiting ..."
            sys.exit(0)
        # read in list of runs that we want to submit jobs for
        runlist = []
        with open(runlist_filename) as inf:
            for line in inf.readlines():
                try:
                    runlist.append(int(line.strip()))
                except:
                    continue

        if len(runlist)==0:
            raise RuntimeError("No runs were passed to BuildJobs!")

        # Figure out how many files to run over for each run
        runfile_map = HDRunFileList.HDRunFileList()
        runfile_map.AddRuns(runlist)
        runfile_map.FillFiles()
        
        # submit some jobs
        # Note - for now we only support SWIF on the JLab batch farm
        job_dir = os.path.join(self.basedir,self.jobname)
        jsub = HDJobSubmitterSWIF.HDJobSubmitterSWIF(job_dir)
        jsub.workflow = self.config_mgr.config['jobname']
        if 'nthreads' in self.config_mgr.config:
            jsub.nthreads = self.config_mgr.config['nthreads']
        if 'mem_requested' in self.config_mgr.config:
            jsub.mem_requested = self.config_mgr.config['mem_requested']
        if 'disk_space' in self.config_mgr.config:
            jsub.disk_space = self.config_mgr.config['disk_space']
        if 'time_limit' in self.config_mgr.config:
            jsub.time_limit = self.config_mgr.config['time_limit']

        jsub.CreateJobs(runfile_map.files, passes_to_run_str)
        
        # show the current state of the workflow for some feedback
        print "Workflow status:"
        os.system("swif status -workflow %s"%jsub.workflow)
        print ""

        ### Now, if requested, we reset all the tables we're going to calibrate
        if init_tables:
            # figure out which CCDB instance to connect to
            if 'ccdb_connection' in self.config_mgr.config:
                CCDB_CONNECTION = self.config_mgr.config['ccdb_connection']
            else:
                CCDB_CONNECTION = os.environ['CCDB_CONNECTION']

            # these are the tables to reset
            self.ccdb_tables = self.LoadCCDBTableList(self.config_mgr.config['ccdb_table_file'])
            os.system("mkdir -p %s/config/"%self.basedir)
            print "cp %s %s/config/ccdb_tables"%(self.config_mgr.config['ccdb_table_file'],self.basedir)        
            os.system("cp %s %s/config/ccdb_tables"%(self.config_mgr.config['ccdb_table_file'],self.basedir))

            # defaults are stored in run = 0, variation = calib
            # initialize the variation for the first set of jobs
            #copier = HDCCDBCopier.HDCCDBCopier(CCDB_CONNECTION,run=0,variation="calib",ccdb_username="calib")
            #copier = HDCCDBCopier.HDCCDBCopier(CCDB_CONNECTION,run=0,variation="calib",ccdb_username="gxproj3")
            copier = HDCCDBCopierCLI.HDCCDBCopierCLI(CCDB_CONNECTION,run=0,variation="calib",ccdb_username="gxproj3")
            for table in self.ccdb_tables:
                for run in runlist:
                    copier.CopyTable(table,dest_minrun=run,dest_variation="calib_pass0")        
        

    def RunJobs(self):
        """
        Actually start the jobs running
        """
        if self.use_batch_queue:
            # use SWIF to run the jobs - just tell it to start
            #os.system("swif run -workflow %s -errorlimit none"%self.config_mgr.config['jobname'])
            job_dir = os.path.join(self.basedir,self.jobname)
            jsub = HDJobSubmitterSWIF.HDJobSubmitterSWIF(job_dir)
            jsub.workflow = self.config_mgr.config['jobname']
            jsub.Run()

            # show the current state of the workflow for some feedback
            os.system("swif status -workflow %s"%jsub.workflow)
        else:
            # if not, just run it locally
            runfile_map = HDRunFileRAIDList.HDRunFileRAIDList()
            runfile_map.AddRuns(runlist)
            runfile_map.FillFiles()

            #jrun = HDJobSubmitterLocal.HDJobSubmitterLocal(runfile_map.files, runfile_map.server_run_map) 
            #jrun.Run()
            jrun = HDJobSubmitterLocal.HDJobSubmitterLocal()
            jrun.Run(runfile_map.files, runfile_map.server_run_map) 


    def UsageStr(self):
        """
        Command line help output
       """
        str   = "usage: job_manager.py init [config_file]\n"
        str  += "       job_manager.py build [-z] [config_file] [run file]\n"
        str  += "       job_manager.py run [-L] [config_file]"
        return str


# this part gets execute when this file is run on the command line 
if __name__ == "__main__":
    parser = OptionParser(usage = "process_new_offline_data.py [root_command]")
    parser.add_option("-L", dest="run_local", action="store_true",
                      help="Run jobs locally, not on JLab batch farm.")
    parser.add_option("-z", dest="rezero_tables", action="store_true",
                      help="Initialize CCDB tables.")
    (options, args) = parser.parse_args(sys.argv)

    jm = HDJobManager()

    if len(args) < 2:
        print jm.UsageStr()
        sys.exit(0)

    # parse commands
    cmd = args[1]
    if cmd=="init":
        if len(args) < 3:
            print "Need to pass config file!"
            sys.exit(0)
        jm.LoadConfig(args[2])
        jm.InitJobs()
    elif cmd=="build":
        if len(args) < 3:
            print "Need to pass config file!"
            sys.exit(0)
        if len(args) < 4:
            print "Need to pass list of runs!"
            sys.exit(0)
        jm.LoadConfig(args[2])
        init_tables = False
        if options.rezero_tables:
            init_tables = True

        if len(args) > 4:
            passes = args[4]
        else:
            passes = "all"
        jm.BuildJobs(args[3],init_tables=init_tables,passes_to_run_str=passes)
    elif cmd=="run":
        num_args_needed = 3
        config_ind = 2
        if options.run_local:
            jm.use_batch_queue = False
        if len(args) < 3:
            print "Need to pass config file!"
            sys.exit(0)
        jm.LoadConfig(args[2])
        jm.RunJobs()
    else:   
        # if we were passed a command we don't understand, print out some help
        print jm.UsageStr()  
