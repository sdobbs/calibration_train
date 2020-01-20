## Hi
## Author: Sean Dobbs (s-dobbs@northwestern.edu)

import os,sys
import rcdb
from optparse import OptionParser
from array import array
import pprint
import math

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

from ROOT import TFile,TH1I,TH2I


def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    return provider


def main():
    pp = pprint.PrettyPrinter(indent=4)

    ccdb_conn = LoadCCDB()

    ccdb_assignment = ccdb_conn.get_assignment("/CDC/wire_gains", 42189, "default")
    print "comment"
    print ccdb_assignment.comment
    ccdb_assignment.comment = "used 42381, after noise reduction"

    ccdb_conn.update_assignment(ccdb_assignment)

    #ccdb_conn.create_assignment(
    #    data=tdc_offsets,
    #    path="/PHOTON_BEAM/hodoscope/fadc_time_offsets",
    #    variation_name=VARIATION,
    #    min_run=run,
    #    max_run=run,
    #    comment="Fixed calibrations due to bad ADC/TDC shifts")


## main function 
if __name__ == "__main__":
    main()
