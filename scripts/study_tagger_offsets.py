import glob
from ROOT import TFile,TH1I,TH2I
import math

VERBOSE=0

rootfiles = glob.glob("/cache/halld/RunPeriod-2017-01/calib/ver02/hists/Run*/hd_calib_verify_Run*_001.root")

tagh_chan_errors = {}
tagm_chan_errors = {}

nruns = 0

for fname in sorted(rootfiles):
    nruns += 1
    f = TFile(fname)
    run = int(fname[-14:-9])

    if VERBOSE>0:
        print "==run %d=="%run
    
    #if run > 30621:
    if run > 30795:
        break
        
    run_tagh_chan_errors = {}
    run_tagm_chan_errors = {}
    
    # CHECK TAGH
    htagh = f.Get("/HLDetectorTiming/TAGH/TAGHHit TDC_ADC Difference")
    #htagh.Print("base")
    for i in xrange(1,htagh.GetNbinsX()+1):
        hy = htagh.ProjectionY("_%d"%i,i,i)
        #print i,hy.GetBinCenter(hy.GetMaximumBin())
        #print i,hy.GetBinLowEdge(hy.GetMaximumBin()+1)
        tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)
        
        # no data in these channels
        if tdiff < -38.:
            continue

        if tdiff == 0.:
            continue

        # only look for shifts > 1.ns in this
        if math.fabs(tdiff) < 1.:
            continue

        if VERBOSE>0:
            print "tdiff in chan %d is %f5.3"%(i,tdiff)
    
        if i in run_tagh_chan_errors:
            run_tagh_chan_errors[i] += 1
        else:
            run_tagh_chan_errors[i] = 1

    # CHECK TAGM
    htagm = f.Get("/HLDetectorTiming/TAGM/TAGMHit TDC_ADC Difference")
    #htagm.Print("base")
    for i in xrange(1,htagm.GetNbinsX()+1):
        hy = htagm.ProjectionY("_%d"%i,i,i)
        #print i,hy.GetBinCenter(hy.GetMaximumBin())
        #print i,hy.GetBinLowEdge(hy.GetMaximumBin()+1)
        tdiff = hy.GetBinLowEdge(hy.GetMaximumBin()+1)
        
        # no data in these channels
        if tdiff < -38.:
            continue

        if tdiff == 0.:
            continue

        # only look for shifts > 1.ns in this
        if math.fabs(tdiff) < 1.:
            continue

        if VERBOSE>0:
            print "tdiff in chan %d is %f5.3"%(i,tdiff)

        if i in run_tagm_chan_errors:
            run_tagm_chan_errors[i] += 1
        else:
            run_tagm_chan_errors[i] = 1

    #print "==",run,"=="
    #print run_tagh_chan_errors
    #print run_tagm_chan_errors

    if len(run_tagh_chan_errors.keys()) < 80:
        for chan,count in sorted(run_tagh_chan_errors.iteritems()):
            if chan in tagh_chan_errors:
                tagh_chan_errors[chan] += count
            else:
                tagh_chan_errors[chan] = count
        #tagh_chan_errors.update(run_tagh_chan_errors)
    if len(run_tagm_chan_errors.keys()) < 80:
        for chan,count in sorted(run_tagm_chan_errors.iteritems()):
            if chan in tagm_chan_errors:
                tagm_chan_errors[chan] += count
            else:
                tagm_chan_errors[chan] = count
        #tagm_chan_errors.update(run_tagm_chan_errors)

    f.Close()

# report
print "for %d runs",nruns

print "TAGH problem channels:"
for chan,count in sorted(tagh_chan_errors.iteritems()):
    print "found channel %d shifted %d times"%(chan,count)

print "TAGM problem channels:"
for chan,count in sorted(tagm_chan_errors.iteritems()):
    print "found channel %d shifted %d times"%(chan,count)
