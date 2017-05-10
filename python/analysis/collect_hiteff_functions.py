from ROOT import *
import os, re
from glob import glob
import numpy as np

gROOT.ProcessLine('.x ~/work/lhcbStyle.C')

## Make testbeam plot
tbfile = os.getenv('SCIFITESTBEAMSIMROOT')+"/Stephan/efficiency_sum4,5_seed2,5.root"
tbfile = TFile(tbfile)
tbtree = tbfile.Get("effTree")
n = tbtree.Draw("clusterCharge:efficiency:clusterChargeErr:efficiencyErrHigh","efficiency > 0.")
tbh = TGraphErrors(n,tbtree.GetV1(),tbtree.GetV2(),tbtree.GetV3(),tbtree.GetV4());

## make simulation plot

def makeHitEffPlots(folders, labels) :

    c = TCanvas()
    histos = []
    for folder in folders :
        histos.append(collectSim(folder))

    histos[0].SetMarkerColor(4) 
    histos[0].Draw("AP")
    histos[0].SetMarkerSize(0.8)

    #detailed.GetYaxis().SetRangeUser(0.,1.3)
    #detailed.GetYaxis().SetRangeUser(0.6,1.1)

    #Stephan's limits
    histos[0].GetYaxis().SetRangeUser(0.67,1.02)
    histos[0].GetXaxis().SetRangeUser(8,24)

    histos[0].GetYaxis().SetTitle("Hit efficiency")
    histos[0].GetXaxis().SetTitle("Light yield")

    tbh.Draw("Psame")
    tbh.SetMarkerSize(0.8)

    leg = TLegend(0.55,0.2,0.9,0.4)
    leg.AddEntry(histos[0],labels[0],"P")
    leg.AddEntry(tbh,"Test beam data","P")
    
    cols = [2,5,6,7,8,9,10]
    for i,h in enumerate(histos[1:]) :
        h.SetMarkerColor(cols[i]) 
        h.Draw("Psame")
        h.SetMarkerSize(0.8)
        leg.AddEntry(h,labels[i+1],"P")

    leg.Draw()
    c.Print("hitEff_vs_lightYield.pdf")


def collectSim(base) :

    simgr = TGraph()
    effs = []
    lgts = []
    eff_errs = []
    lgt_errs = []

    simfiles = glob(base+"/*/clusters/clusterlog*0deg*detailed")
    for f in simfiles :
    
        text = open(f).read()
        light = re.search("Mean light yield: (\d+\.\d+) \+/- (\d+\.\d+)",text)
        eff = re.search("Rate of MCEvent producing one or more clusters: (\d+.\d+) \+/- (\d+.\d+)",text)
        effs.append(float(eff.groups()[0]))
        lgts.append(float(light.groups()[0]))
        eff_errs.append(float(eff.groups()[1]))
        lgt_errs.append(float(light.groups()[1]))
    
    return TGraphErrors(len(effs),np.array(lgts),np.array(effs),np.array(lgt_errs),np.array(eff_errs))



