import os,sys
from ROOT import TFile,TGraph,TCanvas

c1 = TCanvas("c1","c1",1200,600)
c1.SetMargin(0.10,0.05,0.15,0.05)

f = TFile("resolutions.root")

h = f.Get("bcal_res")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) resolution (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("bcal_res.png")

h = f.Get("fcal_res")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) resolution (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("fcal_res.png")

h = f.Get("sc_res")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) resolution (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("sc_res.png")

h = f.Get("tof_res")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) resolution (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("tof_res.png")


h = f.Get("bcal_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) mean (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("bcal_mean.png")

h = f.Get("fcal_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) mean (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("fcal_mean.png")

h = f.Get("sc_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) mean (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("sc_mean.png")

h = f.Get("tof_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("#Delta t(#pi^{-} ) mean (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("tof_mean.png")


h = f.Get("cdc_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("peak earliest CDC/SC matched time (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("cdc_mean.png")


h = f.Get("fdc_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("peak FDC hit time (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("fdc_mean.png")


h = f.Get("tagh_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("TAGGER - RF mean (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("tagh_mean.png")

h = f.Get("tagh_res")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("TAGGER - RF resolution (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("tagh_res.png")


h = f.Get("tagm_mean")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("TAGGER - RF mean (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("tagm_mean.png")

h = f.Get("tagm_res")
h.SetMarkerStyle(20)
h.SetMarkerColor(4)
h.GetXaxis().SetTitle("Run number")
h.GetYaxis().SetTitle("TAGGER - RF resolution (ns)")
h.GetXaxis().SetTitleSize(0.05)
h.GetYaxis().SetTitleSize(0.05)
h.GetXaxis().SetLabelSize(0.05)
h.GetYaxis().SetLabelSize(0.05)
h.Draw("ap")


c1.Print("tagm_res.png")

