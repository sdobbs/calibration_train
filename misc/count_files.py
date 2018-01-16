import os,sys
import glob

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    total_files = 0
    for line in f:
        run = int(line.strip())

        filelist = glob.glob("/mss/halld/RunPeriod-%s/rawdata/Run%06d/*.evio"%(RUNPERIOD,run))
        total_files += len(filelist)

print "total number of files = %d"%total_files
