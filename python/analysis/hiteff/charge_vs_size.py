from argparse import ArgumentParser
from ROOT import *
import re
from glob import glob

parser = ArgumentParser()
parser.add_argument('sim')
parser.add_argument('tb')
args = parser.parse_args()

c = TCanvas()
gStyle.SetOptStat(0)
ofile = TFile("charge_vs_channel.root","RECREATE")

sim = []
for f in glob(args.sim+"/*/digitised/*tuple.root") :
 
    print f
    fsim = TFile.Open(f)
    FTClusterTuple = fsim.Get("FTClusterTuple/FTClusterTuple") 
    FTClusterTuple.Draw("sizeFull:chargeFull>>grsim_"+f,"","prof")
    grsim = gPad.GetPrimitive("grsim_"+f)

    ofile.cd()
    proj = grsim.ProjectionX().Clone(f)
    #grsim.Write()
    #proj.Write()
    
    sim.append(proj)
    
ftb = TFile.Open(args.tb)
FTClusterTupleTB = ftb.Get("TbSciFiTrackTuple/TbSciFiTrackTuple")
FTClusterTupleTB.Draw("dut1_clus_size:dut1_charge>>grtb","track_chi2_no_dut < 4 && nHitsDUT1==1","prof")
grtb = gPad.GetPrimitive("grtb")
grtb = grtb.ProjectionX()

grtb.Draw("")
grtb.GetXaxis().SetRangeUser(0,100)
grtb.GetXaxis().SetTitle("Cluster charge")
grtb.GetYaxis().SetTitle("Cluster size")
grtb.SetTitle("")
grtb.SetMarkerStyle(20)
grtb.SetMarkerSize(1)
grtb.SetMarkerColor(1)

leg = TLegend(0.15,0.65,0.5,0.9)
leg.AddEntry(grtb,"Test beam 2017 not irr.","P")

ofile.cd()
for i,gr in enumerate(sim) :

    ppmev = re.findall("PhotonsPerMeV_(\d+)",gr.GetName())
    ct    = re.findall("CrossTalkProb_(\d+.\d+)",gr.GetName())
    print ppmev, ct
    #if float(ppmev[0]) != 6800 : continue

    gr.Draw("same")
    gr.SetMarkerColor(2)
    gr.SetMarkerStyle(21+i)
    gr.SetMarkerSize(1)
    
    label = "Simulation"
    if len(ppmev) > 0 : label += " PPMEV "+ppmev[0]
    if len(ct) > 0 : label += " CT "+ct[0]
    leg.AddEntry(gr,label,"P")
    gr.Write(label)


leg.Draw()

c.Print("size_vs_charge.pdf")
ofile.Close()
print "HERE"

