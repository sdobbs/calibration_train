# Class to submit jobs to the JLab batch farm using SWIF
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os
from subprocess import Popen, PIPE, call
import json

import HDJobUtils

class HDJobSubmitterSWIF:
    """
    def
    """

    #def __init__(self,basedir,execfile):
    def __init__(self,basedir):
        self.VERBOSE = 1
        self.basedir = basedir
        self.current_phase = 1
        # Auger accounting settings
        self.project = "gluex"         # natch (for now?)
        self.track = "reconstruction"  # calibration jobs fall under this track
        # job defaults
        self.nthreads = 1        # default to 1 thread
        # the following variables should be set by the calling functions
        self.workflow = None
        self.disk_space = None
        self.mem_requested = None
        self.time_limit = None

        self.list_of_passes = ["pass0","pass1","pass2","pass3","final"]

    def DoesWorkflowExist(self, in_workflow):
        """
        Checks the list of workflows associated with this account to see
        if the currently defined workflow exists in SWIF or not
        """
        found = False
        # process info from swif
        process = Popen("swif list".split(), stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        for line in stdout.split('\n'):
            tokens = line.split()
            if len(tokens) < 3:
                continue
            if tokens[0] == "workflow_name" and tokens[2] == in_workflow:
                found = True
        return found

    def AddEVIOJobToSWIF(self,run,filenum,the_pass,command_to_run):
        """
        Fills in the information for a job that processes an EVIO file

        Arguments:
        run - the run number associated with the EVIO file
        file - the file number in the run associated with the EVIO file
        the_pass - text string describing which calibration pass this job is associated with
        command_to_run - the command that the job will execute
        """
        inputfile="/mss/halld/%s/rawdata/Run%06d/hd_rawdata_%06d_%03d.evio"%(HDJobUtils.GetRunPeriodFromRun(run),run,run,filenum)
        cmd = "swif add-job -workflow %s -project %s -track %s -phase %d"%(self.workflow,self.project,self.track,self.current_phase)
        cmd += " -os centos65 "
        # stage file from tape
        cmd += " -input data.evio mss:%s"%inputfile   
        cmd += " -stdout file:%s/log/log_%s_%06d_%03d"%(self.basedir,the_pass,run,filenum)
        cmd += " -stderr file:%s/log/err_%s_%06d_%03d"%(self.basedir,the_pass,run,filenum)
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
            cmd += " %s/scripts/%s %s %s %06d %03d %d"%(self.basedir,"job_wrapper.csh",command_to_run,self.basedir,run,filenum,int(self.nthreads))
        else:
            cmd += " %s/scripts/%s %s %s %06d %03d"%(self.basedir,"job_wrapper.csh",command_to_run,self.basedir,run,filenum)

        # submit job
        if self.VERBOSE>1:
            print "Running command: %s"%cmd
        #retval = os.system(cmd)
        retval = call(cmd, shell=True, stdout=None)
        if retval != 0:
            raise RuntimeError("Error running SWIF command: %s"%cmd)

    def AddJobToSWIF(self,run,filenum,the_pass,command_to_run,log_suffix="calib"):
        """
        Fills in the information for a job that does not process an EVIO file, so we don't need to stage anything from tape

        Arguments:
        run - the run number associated with the EVIO file
        file - the file number in the run associated with the EVIO file
        the_pass - text string describing which calibration pass this job is associated with
        command_to_run - the command that the job will execute
        """
        cmd = "swif add-job -workflow %s -project %s -track %s -phase %d"%(self.workflow,self.project,self.track,self.current_phase)
        cmd += " -os centos65 "
        # stage file from tape
        #cmd += " -input data.evio mss:%s"%inputfile   
        cmd += " -stdout file:%s/log/log_%s_%06d_%03d_%s"%(self.basedir,the_pass,run,filenum,log_suffix)
        cmd += " -stderr file:%s/log/err_%s_%06d_%03d_%s"%(self.basedir,the_pass,run,filenum,log_suffix)
        # keep these jobs single-threaded for now
        #if self.nthreads:
        #    cmd += " -cores %d"%int(self.nthreads)
        if self.disk_space:
            cmd += " -disk %dGB"%int(self.disk_space)
        if self.mem_requested:
            cmd += " -ram %dGB"%int(self.mem_requested)
        if self.time_limit:
            cmd += " -time %dhours"%int(self.time_limit)

        # add command to execute
        if self.nthreads:
            cmd += " %s/scripts/%s %s %s %06d %03d %d"%(self.basedir,"job_wrapper.csh",command_to_run,self.basedir,run,filenum,int(self.nthreads))
        else:
            cmd += " %s/scripts/%s %s %s %06d %03d"%(self.basedir,"job_wrapper.csh",command_to_run,self.basedir,run,filenum)

        # submit job
        if self.VERBOSE>1:
            print "Running command: %s"%cmd
        #retval = os.system(cmd)
        retval = call(cmd, shell=True, stdout=None)
        if retval != 0:
            raise RuntimeError("Error running SWIF command: %s"%cmd)


    def CreateJobs(self, runfile_mapping, passes_to_run_str="all"):
        """
        Builds the calibration jobs.  Leverages SWIF to do most of the bookkeeping

        The basic job flow is for each run
        - analyze all of the files in each run  (e.g. run hd_root over an EVIO file)
        - merge the results from each file, and run any calibrations needed
          (this is where the real heavy lifting happens!)

        Note that for the first file in each run, we do a "pass 0" over a small sample of events
        for calibration tasks that don't require a full run's worth of data
        """
        if self.workflow is None:
            raise RuntimeError("Tried to create unnamed workflow!")

        # check to see if workflow exists
        if not self.DoesWorkflowExist(self.workflow):
            # if not, initialize workflow
            cmd = "swif create -workflow %s"%(self.workflow)
            if self.VERBOSE>1:
                print "Running command: %s"%cmd
            retval = os.system(cmd)
            if retval != 0:
                raise RuntimeError("Error running SWIF command: %s"%cmd)
        else:
            # update phase information from SWIF
            p = Popen("swif status -workflow %s -display json"%(self.workflow),stdout=PIPE,shell=True)
            (stdout,stderr) = p.communicate()
            workflow_info = json.loads(stdout)
            if workflow_info["summary"]["phase"] is not None:
                self.current_phase  = workflow_info["summary"]["phase"]


        # allow for only running some passes
        passes_to_run = []
        if passes_to_run_str == "all":
            passes_to_run = self.list_of_passes
        else:
            passes_to_run = passes_to_run_str.split(',')

        # make CCDB SQLite file for initial run
        if self.VERBOSE>0:
            "Build CCDB SQLite file ..."
        if not os.path.exists(self.basedir):
            raise RuntimeError("Base directory does not exist: %s"%self.basedir)

        if "pass0" in passes_to_run:
            #os.system("%s/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 %s/ccdb_start.sqlite"%(os.environ['CCDB_HOME'],self.basedir))
            # hack - can't do anything with SQLite on Lustre file systems right now, 
            # so build the CCDB SQLite file on the scratch disk and move it over
            scratch_dir = "/scratch/%s"%os.environ['USER']
            os.system("rm -f %s/ccdb_start.sqlite"%scratch_dir)
            os.system("%s/scripts/mysql2sqlite/mysql2sqlite.sh -hhallddb.jlab.org -uccdb_user ccdb | sqlite3 %s/ccdb_start.sqlite"%(os.environ['CCDB_HOME'],scratch_dir))
            os.system("cp -v %s/ccdb_start.sqlite %s/ccdb_start.sqlite"%(scratch_dir,self.basedir))

        # PASS 0: run over first file to calibrate the RF signal
        if "pass0" in passes_to_run:
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>0:
                    print "submiting jobs for run %d, phase %d ..."%(int(run),self.current_phase)

                self.AddEVIOJobToSWIF(run,0,"pass0","file_calib_pass0.csh")

        # PASS 1: 
        # Generate jobs for the full pass over the data
        if "pass1" in passes_to_run:
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>0:
                    print "PASS 1: submiting jobs for run %d, phase %d ..."%(int(run),self.current_phase)

                # best practice is one job per EVIO file (Hall D std. size of 20 GB)
                for filenum in runfile_mapping[run]:
                    self.AddEVIOJobToSWIF(run,filenum,"pass1","file_calib_pass1.csh")

            # Now submit jobs to process all of the results for a given run
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>1:
                    print "PASS 1:   phase %d ..."%(self.current_phase)
                self.AddJobToSWIF(run,0,"pass1","run_calib_pass1.csh","fullrun")

        # PASS 2: 
        # Generate jobs for the full pass over the data
        if "pass2" in passes_to_run:
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>0:
                    print "PASS 2: submiting jobs for run %d, phase %d ..."%(int(run),self.current_phase)

                # best practice is one job per EVIO file (Hall D std. size of 20 GB)
                for filenum in runfile_mapping[run]:
                    self.AddEVIOJobToSWIF(run,filenum,"pass2","file_calib_pass2.csh")

            # Now submit jobs to process all of the results for a given run
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>1:
                    print "PASS 2:   phase %d ..."%(self.current_phase)
                self.AddJobToSWIF(run,0,"pass2","run_calib_pass2.csh","fullrun")


        # PASS 3: 
        # Generate jobs for the full pass over the data
        if "pass3" in passes_to_run:
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>0:
                    print "PASS 3: submiting jobs for run %d, phase %d ..."%(int(run),self.current_phase)

                # best practice is one job per EVIO file (Hall D std. size of 20 GB)
                for filenum in runfile_mapping[run]:
                    self.AddEVIOJobToSWIF(run,filenum,"pass3","file_calib_pass3.csh")

            # Now submit jobs to process all of the results for a given run
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>1:
                    print "PASS 3:   phase %d ..."%(self.current_phase)
                self.AddJobToSWIF(run,0,"pass3","run_calib_pass3.csh","fullrun")


        # FINAL PASS: 
        # Generate jobs for the full pass over the data
        if "final" in passes_to_run:
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                if self.VERBOSE>0:
                    print "PASS FINAL: submiting jobs for run %d, phase %d ..."%(int(run),self.current_phase)

                # best practice is one job per EVIO file (Hall D std. size of 20 GB)
                for filenum in runfile_mapping[run]:
                    self.AddEVIOJobToSWIF(run,filenum,"pass_final","file_calib_pass_final.csh")

            # Now submit jobs to process all of the results for a given run
            self.current_phase += 1
            for run in sorted(runfile_mapping.keys()):
                self.current_phase += 1
                if self.VERBOSE>1:
                    print "PASS FINAL:   phase %d ..."%(self.current_phase)
                self.AddJobToSWIF(run,0,"pass_final","run_calib_pass_final.csh","fullrun")


    def Run(self):
        if self.workflow:
            #os.system("swif run -workflow %s -errorlimit none"%self.workflow) 
            #cmd = "swif run -workflow %s -errorlimit none"%self.workflow   
            cmd = "swif run -workflow %s "%self.workflow   ## debugging
            retval = call(cmd, shell=True, stdout=None)
            if retval != 0:
                raise RuntimeError("Error running SWIF command: %s"%cmd)
            
