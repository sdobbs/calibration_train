# Environment and version management class
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os
from subprocess import Popen, PIPE

class HDJobConfig:
    """
    Stores information about the environment and software versions used for a set of jobs
    """

    def __init__(self,filename,config_filename):
        self.filename = filename
        self.config_filename = config_filename
        self.VERBOSE = 1
        self.config_loaded = False

    def ExtractVersionFromPath(self, prefix, tokens):
        """
        Input: list of directory derived from a full pathname (e.g. fullpathname.split('/'))
        Output: Version number

        Looks for a directory that begins with a specified prefix, and returns the rest
        of the directory name as the version number.  This works for all package names
        currently used in Hall D
        """
        prefix_length = len(prefix)
        for el in tokens[1].split('/'):
            if len(el)<prefix_length:
                continue
            if el[:prefix_length]==prefix:
                return el[prefix_length:]
                break
        return ""

    def BuildConfig(self):
        """
        Parse a standard Hall D Offline configuration file (e.g. setup_jlab.csh) and determine the 
        versions of the software that are being used from the environment variables that are being set
        """
        if self.VERBOSE>0:
            print "In BuildConfig..."
            print "  configuration file = " + self.config_filename

        process = Popen(['./print_env.csh',self.config_filename], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if self.VERBOSE>1:
            print stdout
        for line in stdout.split('\n'):
            tokens = line.split('=')
            if len(tokens) < 2:
                continue

            if tokens[0]=='HDDS_REV':
                self.hdds_ver=tokens[1]
            elif tokens[0]=='SIM_RECON_REV':
                self.sim_recon_ver=tokens[1]
            elif tokens[0]=='CERN_LEVEL':
                self.cern_level=tokens[1]
            elif tokens[0]=='JANA_HOME':
                self.jana_ver=self.ExtractVersionFromPath('jana_',tokens)
                #for el in tokens[1].split('/'):
                #    if len(el)<5:
                #        continue
                #    if el[:5]=='jana_':
                #        self.jana_ver = el[5:]
                #        break
            elif tokens[0]=='EVIOROOT':
                self.evio_ver=self.ExtractVersionFromPath('evio-',tokens)
            elif tokens[0]=='XERCESCROOT':
                self.xerces_ver=self.ExtractVersionFromPath('xerces-c-',tokens)
            elif tokens[0]=='ROOTSYS':
                self.root_ver=self.ExtractVersionFromPath('root_',tokens)
            elif tokens[0]=='CCDB_HOME':
                self.ccdb_ver=self.ExtractVersionFromPath('ccdb_',tokens)

            # we're done!
            self.config_loaded = True
        

    def DumpConfig(self):
        """ 
        Build an XML file that stores the versions of software that are being used
        and various other configuration settings for this set of jobs
        """
        if not self.config_loaded:
            print "Trying to dump config file before the configuration has been loaded, stopping..."
            return

        if self.VERBOSE>0:
            print "Building config file %s ..."%(self.filename)
        if os.path.isfile(self.filename):
            raise RuntimeError("Config file already exists!")

        output_str =  "<gversions>\n"
        output_str += "<package name=\"jana\" version=\"%s\"/>\n"%(self.jana_ver)
        output_str += "<package name=\"sim-recon\" version=\"%s\"/>\n"%(self.sim_recon_ver)
        output_str += "<package name=\"hdds\" version=\"%s\"/>\n"%(self.hdds_ver)
        output_str += "<package name=\"evio\" version=\"%s\"/>\n"%(self.evio_ver)
        output_str += "<package name=\"cernlib\" version=\"%s\" word_length=\"64-bit\"/>\n"%(self.cern_level)
        output_str += "<package name=\"xerces-c\" version=\"%s\"/>\n"%(self.xerces_ver)
        output_str += "<package name=\"root\" version=\"%s\"/>\n"%(self.root_ver)
        output_str += "<package name=\"ccdb\" version=\"%s\"/>\n"%(self.ccdb_ver)
        #output_str += "<package name=\"monitoring\" version=\"${plugins_ver}\"/>"
        output_str += "<!---\n"
        output_str += "<package name=\"clhep\" version=\"2.0.4.5\"/>\n"
        output_str += "<package name=\"geant4\" version=\"9.4\"/>\n"
        output_str += "-->\n"

        #<Variable name="nthreads" value="6"/>
        #<Email email="gxproj1@jlab.org" request="false" job="false"/>
        #<Project name="gluex"/>
        #<Track name="reconstruction"/>
        #<TimeLimit unit="minutes" time="720"/>
        #<DiskSpace space="40" unit="GB"/>
        #<Memory space="5000" unit="MB"/>
        #<CPU core="6"/>
        #<OS name="centos65"/>

        if self.nthreads:
            output_str += "<variable name=\"nthreads\" value=\"%s\"/>\n"%(self.nthreads)
        if self.mem_requested:
            output_str += "<variable name=\"mem_requested\" value=\"%s\" unit=\"GB\"/>\n"%(self.mem_requested)
        if self.disk_space:
            output_str += "<variable name=\"disk_space\" value=\"%s\" unit=\"GB\"/>\n"%(self.disk_space)
        if self.time_limit:
            output_str += "<variable name=\"time_limit\" value=\"%s\" unit=\"hour\"/>\n"%(self.time_limit)
        
        output_str += "</gversions>"

        if self.VERBOSE>0:
            print "------------------------------------------------"
            print "Contents of XML file:"
            print "------------------------------------------------"
            print output_str

        print "Creating version file %s ..."%self.filename
        with open(self.filename,"w") as f:
            print>>f,output_str


