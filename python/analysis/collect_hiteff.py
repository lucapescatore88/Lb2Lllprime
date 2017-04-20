from ROOT import *
import os,re
from glob import glob
import numpy as np

gROOT.ProcessLine('.x ~/work/lhcbStyle.C')

base = "/afs/cern.ch/work/p/pluca/SciFiTest"
simbase = base+"/PhotonPerMeVScan/1"
simbase_tmp = base+"/PhotonPerMeVScan_{0}/1"
tbfile = os.getenv('SCIFITESTBEAMSIMROOT')+"/Stephan/efficiency_sum4,5_seed2,5.root"

c = TCanvas()

## make simulation plot

def collectSim(base) :
    simgr = TGraph()
    effs = []
    lgts = []
    eff_errs = []
    lgt_errs = []

    simfiles = glob(base+"/*/clusters/clusterlog*0deg*")
    for f in simfiles :
    
        text = open(f).read()
        light = re.search("Mean light yield: (\d+\.\d+) \+/- (\d+\.\d+)",text)
        eff = re.search("Rate of MCEvent producing one or more clusters: (\d+.\d+) \+/- (\d+.\d+)",text)

        effs.append(float(eff.groups()[0]))
        lgts.append(float(light.groups()[0]))
        eff_errs.append(float(eff.groups()[1]))
        lgt_errs.append(float(light.groups()[1]))
    
    print zip(effs,lgts)
    simg = TGraphErrors(len(effs),np.array(lgts),np.array(effs),np.array(lgt_errs),np.array(eff_errs))
    return simg

detailed  = collectSim(simbase)
improved  = collectSim(simbase_tmp.format("Improved"))
effective = collectSim(simbase_tmp.format("Effective"))

## Make testbeam plot
tbfile = TFile(tbfile)
tbtree = tbfile.Get("effTree")
n = tbtree.Draw("clusterCharge:efficiency:clusterChargeErr:efficiencyErrHigh","efficiency > 0.")
tbh = TGraphErrors(n,tbtree.GetV1(),tbtree.GetV2(),tbtree.GetV3(),tbtree.GetV4());



## Draw and final touchings

detailed.SetMarkerColor(4)
detailed.Draw("AP")
detailed.SetMarkerSize(0.8)

#detailed.GetYaxis().SetRangeUser(0.,1.3)
#detailed.GetYaxis().SetRangeUser(0.6,1.1)

#Stephan's limits
detailed.GetYaxis().SetRangeUser(0.67,1.02)
detailed.GetXaxis().SetRangeUser(8,24)

detailed.GetYaxis().SetTitle("Hit efficiency")
detailed.GetXaxis().SetTitle("Light yield")
improved.SetMarkerColor(2)
improved.SetMarkerSize(0.8)
improved.Draw("Psame")
effective.SetMarkerColor(3)
effective.SetMarkerSize(0.8)
effective.Draw("Psame")

tbh.Draw("Psame")
tbh.SetMarkerSize(0.8)

leg = TLegend(0.7,0.2,0.9,0.4)
leg.AddEntry(detailed,"Sim. Detailed","P")
leg.AddEntry(improved,"Sim. Improved","P")
leg.AddEntry(effective,"Sim. Effective","P")
leg.AddEntry(tbh,"Testbeam","P")
leg.Draw()

c.Print("hitEff_vs_lightYield.pdf")



