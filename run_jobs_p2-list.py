import os,sys
import glob

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    for line in f:
        tokens = line.strip().split()
        run = int(tokens[0])
        fnum = int(tokens[1])

        print "%d %d"%(run,fnum)
        #continue

        os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s skim %d %d"%(RUNPERIOD,run,fnum))
