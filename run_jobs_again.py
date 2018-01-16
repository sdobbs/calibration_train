import os,sys

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    for line in f:
        run = int(line.strip())
        print run
        #os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s pass1 %d 1"%(RUNPERIOD,run))
        #os.system("swif retry-jobs -workflow GXCalib-2017-01-pass1 -resurrect -names GXCalib-2017-01-pass1_%06d_001"%run)
        os.system("swif retry-jobs -workflow GXCalib-2017-01-fix -resurrect -names GXCalib-2017-01-fix_%06d_001"%run)
