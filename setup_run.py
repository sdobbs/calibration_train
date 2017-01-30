#!/usr/bin/env python
#
# Configure files for a run period
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os,sys
import HDConfigFile
import HDJobConfig


class SetupRun:
    def __init__(self):
        # Directory to store job files
        self.basedir = "/work/halld/home/gxproj3/calib_jobs/"     # set this by hand for now
        # Where the auto-generated CCDB SQLite file lives
        self.ccdb_dir = "/group/halld/www/halldweb/html/dist"

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

    def Setup(self):
        """
        Do all the preliminary work to set up a new batch of jobs.  This includes
        - building job directories
        - building scripts and input files
        - archiving the current software configuration
        """
        
        # make directories - just archive some misc files here
        os.system("mkdir -p %s"%(self.basedir))
        job_dir = os.path.join(self.basedir,self.jobname)
        os.system("mkdir -p %s"%(os.path.join(job_dir,"log")))
        os.system("mkdir -p %s"%(os.path.join(job_dir,"config")))
        script_dir = os.path.join(job_dir,"scripts")
        os.system("mkdir -p %s"%(script_dir))
        #os.system("mkdir -p %s"%(os.path.join(job_dir,"output")))
        #os.system("mkdir -p %s"%(os.path.join(job_dir,"sqlite_ccdb")))

        # copy batch job files
        os.system("cp -R templates/* "+script_dir)
        #os.system("cp %s/ccdb.sqlite %s"%(self.ccdb_dir,job_dir))

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


# this part gets execute when this file is run on the command line 
if __name__ == "__main__":
    setup = SetupRun()
    setup.LoadConfig(sys.argv[1])
    setup.Setup()
