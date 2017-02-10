# Class to run jobs on the local machine.  Can handle default
# data locations at JLab either inside the counting house at the batch farm
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os
from subprocess import Popen, PIPE, call

import HDJobUtils
import HDRunFileRAIDList

class HDJobSubmitterLocal:
    """
    def
    """

    def __init__(self,basedir):
        self.VERBOSE = 1
        self.basedir = basedir
        # job defaults
        self.nthreads = 1        # default to 1 thread

    def RunJobs(self, runfile_mapping, server_run_map):
        """
        Runs 

        The basic job flow is for each run
        - analyze all of the files in each run at once
        - run the calibrations 

        Note that for the first file in each run, we do a "pass 0" over a small sample of events
        for calibration tasks that don't require a full run's worth of data

        [Multiple passes coming in the future]
        """
        if self.workflow is None:
            raise RuntimeError("Tried to create unnamed workflow!")

    
        # Generate jobs for the first pass over the data
        for run in sorted(runfile_mapping.keys()):
            if self.VERBOSE>0:
                inputfiles="/%s/rawdata/volatile/%s/rawdata/Run%06d/hd_rawdata_*.evio"%(HDRunFileRAIDList.GetRAIDDirFromRun(run,server_run_map),HDJobUtils.GetRunPeriodFromRun(run),run)

                # PASS 0
                print "processing run %d, phase 0 ..."%(int(run))

                # set up command to execute
                if self.nthreads:
                    cmd += " %s/scripts/%s %s %s %06d %03d %d"%(self.basedir,"job_wrapper_local.csh","local_calib_pass0.csh",self.basedir,run,inputfiles,int(self.nthreads))
                else:
                    cmd += " %s/scripts/%s %s %s %06d %03d"%(self.basedir,"job_wrapper_local.csh","local_calib_pass0.csh",self.basedir,run,inputfiles)

                # run command
                os.system(cmd)

                # PASS 1
                print "processing run %d, phase 1 ..."%(int(run))

                # set up command to execute
                if self.nthreads:
                    cmd += " %s/scripts/%s %s %s %06d %03d %d"%(self.basedir,"job_wrapper_local.csh","local_calib_pass1.csh",self.basedir,run,inputfiles,int(self.nthreads))
                else:
                    cmd += " %s/scripts/%s %s %s %06d %03d"%(self.basedir,"job_wrapper_local.csh","local_calib_pass1.csh",self.basedir,run,inputfiles)

                # run command
                os.system(cmd)

