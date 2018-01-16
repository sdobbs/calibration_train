import os,sys
import glob

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    for line in f:
        tokens = line.strip().split('_')
        run = int(tokens[2])
        fnum = int(tokens[3][0:3])

        print "%d %d"%(run,fnum)
        #continue

        os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s skim %d %d"%(RUNPERIOD,run,fnum))
