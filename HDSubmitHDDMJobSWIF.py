#!/usr/bin/env python
#
# Class to submit jobs to the JLab batch farm using SWIF
# This versions uses multiple workflows
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2016


import os,sys
from subprocess import Popen, PIPE, call
import json

import HDJobUtils
import HDConfigFile

class HDSubmitCalibJobSWIF:
    def __init__(self,run_period):
        self.VERBOSE = 1
        # be lazy and hardcode this
        self.basedir = "/work/halld/home/gxproj3/calib_jobs/RunPeriod-%s"%run_period
        self.run_period = run_period
        # Auger accounting settings
        self.project = "gluex"         # natch (for now?)
        self.track = "reconstruction"  # calibration jobs fall under this track
        # job defaults
        self.nthreads = 1          # default to 1 thread
        #self.swif_nthreads = 24    # set this to always run on the exclusive nodes
        self.workflow = None
        self.disk_space = None
        self.mem_requested = None
        self.time_limit = None

        # for redirecting output to /dev/null
        self.DEVNULL = open(os.devnull, 'wb')

    def __del__(self):
        self.DEVNULL.close()


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

        # set configurations
        self.nthreads = self.config_mgr.config['nthreads']
        self.disk_space = self.config_mgr.config['disk_space']
        self.mem_requested = self.config_mgr.config['mem_requested']
        self.time_limit = self.config_mgr.config['time_limit']
        

    def AddEVIOJobToSWIF(self,run_period,version,run,command_to_run):
        """
        Fills in the information for a job that processes an EVIO file

        Arguments:
        run - the run number associated with the EVIO file
        file - the file number in the run associated with the EVIO file
        the_pass - text string describing which calibration pass this job is associated with
        command_to_run - the command that the job will execute
        """
        # make directory for log
        logdir = "%s/log/%06d"%(self.basedir,run)
        if(not os.path.exists(logdir)):
            os.system("mkdir -p %s"%logdir)

        # prepare command
        cmd = "swif add-job -workflow %s -project %s -track %s "%(self.workflow,self.project,self.track)
        #cmd += " -name %s_%06d_%03d_centos65"%(self.workflow,run,filenum)
        #cmd += " -os centos65 "
        cmd += " -name %s_%06d"%(self.workflow,run)
        cmd += " -os centos7 "
        # stage file from tape
        #cmd += " -input data.evio mss:%s"%inputfile   
        cmd += " -stdout file:%s/log/%06d/log_%s_%06d"%(self.basedir,run,"merge",run)
        cmd += " -stderr file:%s/log/%06d/err_%s_%06d"%(self.basedir,run,"merge",run)
        cmd += " -cores %d"%int(self.nthreads)  
        cmd += " -tag run %d"%(run)
        if self.nthreads:
            cmd += " -cores %d"%int(self.nthreads)
        if self.disk_space:
            cmd += " -disk %dGB"%int(self.disk_space)
        if self.mem_requested:
            cmd += " -ram %dGB"%int(self.mem_requested)
        if self.time_limit:
            cmd += " -time %dhours"%int(self.time_limit)

        # add command to execute
        cmd += " %s/scripts/%s %s %s %s %06d "%(self.basedir,command_to_run,self.basedir,run_period,version,run)

        # submit job
        if self.VERBOSE>1:
            print "Running command: %s"%cmd
        #retval = os.system(cmd)
        retval = call(cmd, shell=True, stdout=None)
        if retval != 0:
            raise RuntimeError("Error running SWIF command: %s"%cmd)
        # check return value


    def AddEVIOSubJobToSWIF(self,run_period,version,run,command_to_run,fileprefix):
        """
        Fills in the information for a job that processes an EVIO file

        Arguments:
        run - the run number associated with the EVIO file
        file - the file number in the run associated with the EVIO file
        the_pass - text string describing which calibration pass this job is associated with
        command_to_run - the command that the job will execute
        """
        # make directory for log
        logdir = "%s/log/%06d"%(self.basedir,run)
        if(not os.path.exists(logdir)):
            os.system("mkdir -p %s"%logdir)

        # prepare command
        cmd = "swif add-job -workflow %s -project %s -track %s "%(self.workflow,self.project,self.track)
        #cmd += " -name %s_%06d_%03d_centos65"%(self.workflow,run,filenum)
        #cmd += " -os centos65 "
        cmd += " -name %s_%06d-%s"%(self.workflow,run,fileprefix)
        cmd += " -os centos7 "
        # stage file from tape
        #cmd += " -input data.evio mss:%s"%inputfile   
        cmd += " -stdout file:%s/log/%06d/log_%s_%06d-%s"%(self.basedir,run,"merge",run,fileprefix)
        cmd += " -stderr file:%s/log/%06d/err_%s_%06d-%s"%(self.basedir,run,"merge",run,fileprefix)
        cmd += " -cores %d"%int(self.nthreads)  
        cmd += " -tag run %d"%(run)
        if self.nthreads:
            cmd += " -cores %d"%int(self.nthreads)
        if self.disk_space:
            cmd += " -disk %dGB"%int(self.disk_space)
        if self.mem_requested:
            cmd += " -ram %dGB"%int(self.mem_requested)
        if self.time_limit:
            cmd += " -time %dhours"%int(self.time_limit)

        # add command to execute
        cmd += " %s/scripts/%s %s %s %s %06d %s"%(self.basedir,command_to_run,self.basedir,run_period,version,run,fileprefix)

        # submit job
        if self.VERBOSE>1:
            print "Running command: %s"%cmd
        #retval = os.system(cmd)
        retval = call(cmd, shell=True, stdout=None)
        if retval != 0:
            raise RuntimeError("Error running SWIF command: %s"%cmd)
        # check return value


    def SubmitJob(self, run_period, version, run):
        self.workflow = "GXCalib-%s-random"%run_period
        self.AddEVIOJobToSWIF(run_period,version,run,"evio_merge_hddm.sh")

    def SubmitSubJob(self, run_period, version, run, fileprefix):
        self.workflow = "GXCalib-%s-random"%run_period
        self.AddEVIOSubJobToSWIF(run_period,version,run,"evio_merge_hddm-ps.sh",fileprefix)

# this part gets execute when this file is run on the command line 
if __name__ == "__main__":
    # example:  HDSubmitCalibJobSWIF.py config/random.config 2016-10 ver01 11529
    submitter = HDSubmitCalibJobSWIF(sys.argv[2])
    submitter.LoadConfig(sys.argv[1])
    if len(sys.argv)==6:
        submitter.SubmitSubJob(sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5])
    else:
        submitter.SubmitJob(sys.argv[2], sys.argv[3], int(sys.argv[4]))
