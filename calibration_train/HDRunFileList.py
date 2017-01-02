# Class to automatically determine how many files per run exist, given a list of runs
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os
import HDJobUtils

class HDRunFileList:
    """
    Class to automatically determine how many files per run exist.
    The list of runs is set using AddRuns() or SetRuns().
    Once the list of runs is defined, call FillFiles() to set up the
      list of files per run mapping
    The results can then be obtained by directly accessing the dictionary HDRunFileList.files
    """

    def __init__(self):
        self.files = {}  # mapping with run numbers as keys and list of file numbers as values
        
    def Clear(self):
        del self.files
        self.files = {}

    def AddRuns(self, runlist):
        for run in runlist:
            try:
                self.files[int(run)] = []
            except TypeError:
                print "Invalid run number in RunFileList.SetRuns(): "+str(run)

    def SetRuns(self, runlist):
        self.Clear()
        self.AddRuns(runlist)

    def FillFiles(self):
        for run in self.files.keys():
            # figure out run period
            the_run_period = HDJobUtils.GetRunPeriodFromRun(run)
            if the_run_period is None:
                print "Could not find run period for run "+str(run)
            # look at /mss stub files to determine how many files each run containes
            evio_dir = "/mss/halld/%s/rawdata/Run%06d/"%(the_run_period,run)
            if not os.path.isdir(evio_dir):
                continue
            #evio_files = [ f for f in os.listdir(evio_dir) if f[-5:] == ".evio" ]
            try:
                evio_file_numbers = [ int(f[:-5].split("_")[3]) for f in os.listdir(evio_dir) if f[-5:] == ".evio" ]
                self.files[run] = sorted(evio_file_numbers)
            except:
                print "Error processing directory: "+str(evio_dir)
