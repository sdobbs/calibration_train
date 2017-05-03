from ROOT import TH1I,TFile,TFitResultPtr,TCanvas
import glob


#rootfiles = glob.glob("/cache/halld/RunPeriod-2017-01/calib/ver02/hists/Run*/hd_calib_verify_Run*.root")
rootfiles = glob.glob("/cache/halld/RunPeriod-2017-01/calib/ver01/hists/Run030592/hd_calib_final_*.root")

thestart = True
c1 = TCanvas("c1","c1",800,600)

outf = open("tagm_offsets.txt", "w")

for pathname in sorted(rootfiles):
    f = TFile(pathname)
    TAGM1DHist = f.Get("HLDetectorTiming/TRACKING/TAGM - RFBunch 1D Time")
    TAGMPeakPosition = TAGM1DHist.GetBinCenter(TAGM1DHist.GetMaximumBin())
    tagm_fr = TAGM1DHist.Fit("gaus", "SQ", "", TAGMPeakPosition-0.4, TAGMPeakPosition+0.4)
    tagm_shift = tagm_fr.Parameter(1)
        
    run = int(pathname[-15:-9])
    fnum = int(pathname[-8:-5])
    print run,fnum,tagm_shift
    print>>outf, run,fnum,tagm_shift

    TAGM1DHist.Draw()

    if thestart:
        c1.Print("out.pdf(")
    else:
        c1.Print("out.pdf")

    f.Close()

c1.Print("out.pdf)")
