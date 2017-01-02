# Configuration file manager
#
# Author: Sean Dobbs (s-dobbs@northwestern.edu), 2015

import os
from subprocess import Popen, PIPE

class HDConfigFile:
    """
    Configuration file manager.
    This class reads in files containing "key = value" pairs, and stores them 
    in the HDConfigFile.config dictionary.
    """

    def __init__(self,basedir,filename):
        self.basedir = basedir
        self.filename = filename
        self.config = {}
        self.VERBOSE = 0

    def LoadConfig(self):
        """
        Loads files of format

        KEY [sep] VALUE

        where [sep] is =,:
        Keys are stored as lowercase
        """
        if self.VERBOSE>0:
            print "Loading configuration file..."

        with open(self.filename) as f:
            for line in f.readlines():
                line.strip()
                # skip comment lines
                if line[0] == '#':
                    continue
                tokens = line.split()
                if len(tokens)<3:
                    continue
                if tokens[1]=='=' or tokens[1]==':':
                    self.config[ tokens[0].lower() ] = " ".join(tokens[2:])
                    if self.VERBOSE>0:
                        print "loaded  key = %s  value = %s"%(tokens[0].lower()," ".join(tokens[2:]))
