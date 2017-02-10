import os
import glob

with open("run_lists/f16_runs.all", "r") as f:
    for line in f:
        run = int(line.strip())

        filelist = glob.glob("/mss/halld/RunPeriod-2016-10/rawdata/Run%06d/*.evio"%run)
        fnums = sorted([ int(num[-8:-5]) for num in filelist ])
        #print (fnums)

        for fnum in fnums:
            os.system("python HDSubmitCalibJobSWIF.py configs/data.config 2016-10 pass2 %d %d"%(run,fnum))
