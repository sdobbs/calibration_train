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
        #self.workflow = None
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
        

    def AddEVIOJobToSWIF(self,run,filenum,the_pass,command_to_run):
        """
        Fills in the information for a job that processes an EVIO file

        Arguments:
        run - the run number associated with the EVIO file
        file - the file number in the run associated with the EVIO file
        the_pass - text string describing which calibration pass this job is associated with
        command_to_run - the command that the job will execute
        """
        #inputfile="/mss/halld/%s/rawdata/Run%06d/hd_rawdata_%06d_%03d.evio"%(HDJobUtils.GetRunPeriodFromRun(run),run,run,filenum)
        inputfile="/mss/halld/RunPeriod-%s/rawdata/Run%06d/hd_rawdata_%06d_%03d.evio"%(self.run_period,run,run,filenum)
        cmd = "swif add-job -workflow %s -project %s -track %s "%(self.workflow,self.project,self.track)
        #cmd += " -name %s_%06d_%03d_centos65"%(self.workflow,run,filenum)
        #cmd += " -os centos65 "
        cmd += " -name %s_%06d_%03d"%(self.workflow,run,filenum)
        cmd += " -os centos7 "
        # stage file from tape
        cmd += " -input data.evio mss:%s"%inputfile   
        cmd += " -stdout file:%s/log/log_%s_%06d_%03d"%(self.basedir,the_pass,run,filenum)
        cmd += " -stderr file:%s/log/err_%s_%06d_%03d"%(self.basedir,the_pass,run,filenum)
        cmd += " -cores %d"%int(self.nthreads)  
        cmd += " -tag run %d"%(run)
        cmd += " -tag file %d"%(filenum)
        cmd += " -tag pass %s"%(the_pass)
        if self.nthreads:
            cmd += " -cores %d"%int(self.nthreads)
        if self.disk_space:
            cmd += " -disk %dGB"%int(self.disk_space)
        if self.mem_requested:
            cmd += " -ram %dGB"%int(self.mem_requested)
        if self.time_limit:
            cmd += " -time %dhours"%int(self.time_limit)

        # add command to execute
        if self.nthreads:
            cmd += " %s/scripts/%s %s %s %06d %03d %s %d"%(self.basedir,"job_wrapper.sh",command_to_run,self.basedir,run,filenum,int(self.nthreads))
        else:
            cmd += " %s/scripts/%s %s %s %06d %03d %s "%(self.basedir,"job_wrapper.sh",command_to_run,self.basedir,run,filenum)

        # submit job
        if self.VERBOSE>1:
            print "Running command: %s"%cmd
        #retval = os.system(cmd)
        retval = call(cmd, shell=True, stdout=None)
        if retval != 0:
            raise RuntimeError("Error running SWIF command: %s"%cmd)
        # check return value

    #def AddJobToSWIF(self,run,filenum,the_pass,command_to_run,log_suffix="calib"):
    def AddJobToSWIF(self,run,filenum,the_pass,command_to_run):
        """
        Fills in the information for a job that does not process an EVIO file, so we don't need to stage anything from tape

        Arguments:
        run - the run number associated with the EVIO file
        file - the file number in the run associated with the EVIO file
        the_pass - text string describing which calibration pass this job is associated with
        command_to_run - the command that the job will execute
        """
        #cmd = "swif add-job -workflow %s -project %s -track %s "%(self.workflow,self.project,self.track)
        cmd = "swif add-job -workflow %s -project %s -track %s "%(self.workflow,self.project,"debug")
        cmd += " -os centos7 "
        cmd += " -stdout file:%s/log/log_%s_%06d_%03d"%(self.basedir,the_pass,run,filenum)
        cmd += " -stderr file:%s/log/err_%s_%06d_%03d"%(self.basedir,the_pass,run,filenum)
        #cmd += " -stdout file:%s/log/log_%s_%06d_%03d_%s"%(self.basedir,the_pass,run,filenum,log_suffix)
        #cmd += " -stderr file:%s/log/err_%s_%06d_%03d_%s"%(self.basedir,the_pass,run,filenum,log_suffix)
        cmd += " -tag run %d"%(run)
        cmd += " -tag file %s"%("all")
        cmd += " -tag pass %s"%(the_pass)
        # keep these jobs single-threaded for now
        if self.nthreads:
            cmd += " -cores %d"%int(self.nthreads)
        if self.disk_space:
            cmd += " -disk %dGB"%int(self.disk_space)
        if self.mem_requested:
            cmd += " -ram %dGB"%int(self.mem_requested)
        if self.time_limit:
            cmd += " -time %dhours"%int(self.time_limit)

        # add command to execute
        if self.nthreads:
            cmd += " %s/scripts/%s %s %s %06d %03d %s %d"%(self.basedir,"job_wrapper.csh",command_to_run,self.basedir,run,filenum,int(self.nthreads))
        else:
            cmd += " %s/scripts/%s %s %s %06d %03d %s"%(self.basedir,"job_wrapper.csh",command_to_run,self.basedir,run,filenum)

        # submit job
        if self.VERBOSE>1:
            print "Running command: %s"%cmd
        #retval = os.system(cmd)
        retval = call(cmd, shell=True, stdout=None)
        if retval != 0:
            raise RuntimeError("Error running SWIF command: %s"%cmd)

    def SubmitJob(self, run_period, the_pass, run, filenum=1):
        self.workflow = "GXCalib-%s-%s"%(run_period,the_pass)
        if the_pass == "pass1":
            self.AddEVIOJobToSWIF(run,filenum,the_pass,"calib_job1.sh")
        elif the_pass == "pass2":
            self.AddEVIOJobToSWIF(run,filenum,the_pass,"file_calib_pass_final.sh")
        elif the_pass == "pass2-sum":
            self.AddJobToSWIF(run,filenum,the_pass,"run_calib_pass_final.sh")

# this part gets execute when this file is run on the command line 
if __name__ == "__main__":
    # example:  HDSubmitCalibJobSWIF.py config/data.config 2016-10 pass1 11529 1
    submitter = HDSubmitCalibJobSWIF(sys.argv[2])
    submitter.LoadConfig(sys.argv[1])
    if len(sys.argv)<=5:
        submitter.SubmitJob(sys.argv[2], sys.argv[3], int(sys.argv[4]))
    else:
        submitter.SubmitJob(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]))
