# Class to automatically determine how many files per run exist, given a list of runs
# For running inside the counting house, reads files from the RAID disk
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os
import HDJobUtils

class HDRunFileRAIDList:
    """
    Class to automatically determine how many files per run exist.
    The list of runs is set using AddRuns() or SetRuns().
    Once the list of runs is defined, call FillFiles() to set up the
      list of files per run mapping
    The results can then be obtained by directly accessing the dictionary HDRunFileRAIDList.files
    """

    def __init__(self):
        self.files = {}  # mapping with run numbers as keys and list of file numbers as values
        
        # figure out which runs on which RAID disk
        self.server_run_map = {}
        raid_dirs = [ "gluonraid1", "gluonraid2" ]
        for the_raid_dir in raid_dirs:
            print "scanning %s..."%the_raid_dir
            runlist = []
            basedir = "/%s/rawdata/volatile"%the_raid_dir
            for the_run_period in [ d for d in os.listdir(basedir) if (d[:9]=="RunPeriod") ]:
                # look for folders containing EVIO files
                evio_dir = "%s/%s/rawdata"%(basedir,the_run_period)
                for dirname in [ d for d in os.listdir(evio_dir) if (d[:3]=="Run") ]:
                    # get run number from directories following the naming scheme "RunRRRRRR"
                    try:
                        run = int(dirname[3:9])
                        runlist.append(run)
                    except:
                        print "Skipping invalid run directory %s ..."%dirname
        self.server_run_map[the_raid_dir] = runlist

    def GetRAIDDirFromRun(run, server_run_map):
        for d in server_run_map.keys():
            if run in server_run_map[d]:
                return d
        return ""
       
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
            the_raid_dir = self.GetRAIDDirFromRun(run,self.server_run_map)
            if the_run_period is None:
                print "Could not find run period for run "+str(run)
            # count number of files on disk.  Note that these are in the volatile area, so 
            # more files might exist on tape
            evio_dir = "/%s/rawdata/volatile/%s/rawdata/Run%06d/"%(the_raid_dir,the_run_period,run)
            if not os.path.isdir(evio_dir):
                continue
            #evio_files = [ f for f in os.listdir(evio_dir) if f[-5:] == ".evio" ]
            try:
                evio_file_numbers = [ int(f[:-5].split("_")[3]) for f in os.listdir(evio_dir) if f[-5:] == ".evio" ]
                self.files[run] = sorted(evio_file_numbers)
            except:
                print "Error processing directory: "+str(evio_dir)
