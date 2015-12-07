# script to print contents of CCDB tables to screen
# uses CCDB CLI command

import os,sys

if len(sys.argv)<2:
    print "Need to pass filename to cat_ccdb_tables.py!"
    exit(0)

with open(sys.argv[1]) as f:
    for line in f:
        if line[0] != '#':
            tablename = line.strip()
            print tablename + ":"
            os.system("ccdb cat %s"%tablename)
