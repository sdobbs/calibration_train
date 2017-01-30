import os,sys
from ROOT import TFile,TTree
from array import array
import pprint

import ccdb
from ccdb import Directory, TypeTable, Assignment, ConstantSet

def LoadCCDB():
    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"
    #sqlite_connect_str = "sqlite:////scratch/gxproj3/ccdb.sqlite"
    #sqlite_connect_str = "sqlite:////group/halld/www/halldweb/html/dist/ccdb.sqlite"
    provider = ccdb.AlchemyProvider()                        # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)                     # use usual connection string to connect to database
    provider.authentication.current_user_name = "anonymous"  # to have a name in logs

    return provider

## main function 
if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)

    # Load CCDB
    ccdb_conn = LoadCCDB()

    run = 21942
    SRC_VARIATION = "calib"
    DEST_VARIATION = "default"
    ccdb_table = "/BCAL/base_time_offset"

    assignment = ccdb_conn.get_assignment(ccdb_table, run, SRC_VARIATION)
    pp.pprint(assignment.constant_set.data_table)

    ccdb_conn.create_assignment(
        data=assignment.constant_set.data_table,
        path=ccdb_table,
        variation_name=DEST_VARIATION,
        min_run=run,
        max_run=run,
        comment="Copied from variation \'%s\'"%ccdb_table)

