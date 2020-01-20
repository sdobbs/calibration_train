import os,sys
import glob

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    for line in f:
        run = int(line.strip())

        filelist = glob.glob("/mss/halld/RunPeriod-%s/rawdata/Run%06d/*.evio"%(RUNPERIOD,run))
        fnums = sorted([ int(num[-8:-5]) for num in filelist ])
        #print (fnums)

        for fnum in fnums:
            os.system("python HDSubmitCalibJobSWIF.py configs/random.config %s random %d %d"%(RUNPERIOD,run,fnum))
            #os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s skim %d %d"%(RUNPERIOD,run,fnum))
