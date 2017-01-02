import os
import sys

if __name__ == "__main__":

    ccdb_home = os.environ["CCDB_HOME"]  # This environment variable should be set!

    # Set env. variable PYTHONPATH=$CCDB_HOME/python;$PYTHONPATH
    # or sys.path.append(os.path.join(ccdb_home, "python"))
    import ccdb
    from ccdb import Variation
    from sqlalchemy import desc

    sqlite_connect_str = "mysql://ccdb_user@hallddb.jlab.org/ccdb"

    # create CCDB api class
    provider = ccdb.AlchemyProvider()  # this class has all CCDB manipulation functions
    provider.connect(sqlite_connect_str)  # use usual connection string to connect to database
    provider.authentication.current_user_name = "sdobbs"  # to have a name in logs

    # update info
    variation = provider.get_variation(sys.argv[1])
    variation.comment = " ".join(sys.argv[2:])
    provider.update_variation(variation)
