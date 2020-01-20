import os,sys
import glob

RUNPERIOD = sys.argv[1]
#VERSION = sys.argv[2]
VERSION = "ver01"

#for dirname in sorted(glob.glob("/cache/halld/RunPeriod-%s/calib/%s/PS/*"%(RUNPERIOD,VERSION))):
#for dirname in sorted(glob.glob("/cache/halld/RunPeriod-%s/calib/%s/random/*"%(RUNPERIOD,VERSION))):
    #run = int(dirname[-5:])
    #print dirname    
with open(sys.argv[2]) as f:
    for line in f:
        run = int(line.strip())
        print run
        os.system("rm /cache/halld/gluex_simulations/random_triggers/recon-2018_01-ver02/run%06d_random.hddm"%run)
        #os.system("python HDSubmitHDDMJobSWIF.py configs/random.config %s %s %d"%(RUNPERIOD,VERSION,run))
    """
    prefixes = []
    for fname in sorted(glob.glob(dirname+"/*")):
        #print fname
        tokens = fname.split('/')[-1].split('_')
        prefix = tokens[3][:2]
        if prefix not in prefixes:
            prefixes.append(prefix)

    #print prefixes
    for prefix in prefixes:
        os.system("python HDSubmitHDDMJobSWIF.py configs/random.config %s %s %d %s"%(RUNPERIOD,VERSION,run,prefix))
    """
