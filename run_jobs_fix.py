import os,sys

RUNPERIOD = sys.argv[1]
FILENAME = sys.argv[2]

with open(FILENAME, "r") as f:
    for line in f:
        run = int(line.strip())
        #os.system("python HDSubmitCalibJobSWIF.py configs/primex.config %s fix %d 0"%(RUNPERIOD,run))
        #os.system("python HDSubmitCalibJobSWIF.py configs/primex.config %s fix-primex %d 0"%(RUNPERIOD,run))
        os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix %d 0"%(RUNPERIOD,run))
        #os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix-primex %d 1"%(RUNPERIOD,run))
        #os.system("jcache get  /mss/halld/RunPeriod-%s/rawdata/Run%06d/hd_rawdata_%06d_%03d.evio -D 30"%(RUNPERIOD,run,run,1))
        #os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix %d 0"%(RUNPERIOD,run))

        #for x in xrange(30):
            #print "python HDSubmitCalibJobSWIF.py configs/data.config %s fix-skim %d %d"%(RUNPERIOD,run,x)
            #os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix-skim %d %d"%(RUNPERIOD,run,x))
