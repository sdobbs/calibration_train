import os,sys

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    for line in f:
        run = int(line.strip())
        #os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix %d 1"%(RUNPERIOD,run))
        os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix %d 0"%(RUNPERIOD,run))
