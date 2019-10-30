import os,sys

RUNPERIOD = sys.argv[1]
RUN = int(sys.argv[2])

for x in xrange(70):
    os.system("python HDSubmitCalibJobSWIF.py configs/data.config %s fix %d %d"%(RUNPERIOD,RUN,x))
