import ROOT as R

R.gROOT.ProcessLine('.x $SCIFITESTBEAMSIMROOT/job/lhcbStyle.C')
R.gStyle.SetOptStat(0)

ofile = R.TFile("hiteff_vs_channel.root","RECREATE")
fname = "/afs/cern.ch/work/a/adavis/public/for_luca/zeroDeg_3.5V_0cm/combined_ntuples_and_histograms/combined_ntuple_0deg.root"
f = R.TFile(fname)

f.ls()
tup = f.Get("TbSciFiTrackTuple/TbSciFiTrackTuple")

denom = R.TH1D("denom","Reconstructibles per channel",130,0,130)
num = R.TH1D("num","Reconstructed per channel",130,0,130)
denom_rad = R.TH1D("denom_rad","Reconstructibles per channel, irrad",130,0,130)
num_rad = R.TH1D("num_rad","Reconstructed per channel, irrad",130,0,130)

num.Sumw2()
denom.Sumw2()
num_rad.Sumw2()
denom_rad.Sumw2()

for e in tup:

    if e.track_chi2_no_dut>4: continue
    denom.Fill(e.track_at_dut1_channel)
    denom_rad.Fill(e.track_at_dut2_channel)
        
    for i in range(e.nHitsDUT1):
        if(e.dut1_x[i]-e.track_at_dut1_x < 1):
            num.Fill(e.track_at_dut1_channel)
            break
    for i in range(e.nHitsDUT2):
        if(e.dut2_x[i]-e.track_at_dut2_x < 1):
            num_rad.Fill(e.track_at_dut2_channel)
            break


ofile.cd()
c1 = R.TCanvas()
eff = num.Clone("eff_norad")
eff.Divide(denom)
eff.SetMarkerStyle(21)
eff.SetMarkerSize(0.8)
eff.SetMarkerColor(2)
eff.GetXaxis().SetTitle('Channel')
eff.GetYaxis().SetTitle('Hit efficiency')
eff.SetTitle('')
eff.GetYaxis().SetRangeUser(0.7,1.1)

eff.Draw("E")
c1.Print("hiteff_not_irrad.pdf")

eff.Fit('pol0')

eff_irrad = num_rad.Clone("eff_rad")
eff_irrad.Divide(denom_rad)
eff_irrad.SetMarkerStyle(21)
eff_irrad.SetMarkerSize(0.8)
eff_irrad.SetMarkerColor(2)
eff_irrad.GetXaxis().SetTitle('Channel')
eff_irrad.GetYaxis().SetTitle('Hit efficiency')
eff_irrad.SetTitle('')
eff_irrad.GetYaxis().SetRangeUser(0.6,1.1)
eff_irrad.Draw("E")
c1.Print("hiteff_irrad.pdf")

num.Write()
denom.Write()
num_rad.Write()
denom_rad.Write()
eff.Write()
eff_irrad.Write()

tup.Draw("dut2_charge:track_at_dut2_channel>>charge(130,0,130,100,0,16)","track_chi2_no_dut<4","prof")
charge_gr = R.gPad.GetPrimitive("charge").ProjectionX().Clone("charge_h")
charge_gr.GetXaxis().SetTitle('Channel')
charge_gr.GetYaxis().SetTitle('Light yield')
charge_gr.SetTitle('')
#charge_gr.GetYaxis().SetRangeUser(0.4,1.1)
c1.Print("charge_vs_channels.pdf")

gr = R.TGraphErrors()
for b in range(1,int(eff_irrad.GetNbinsX())) :
    #if b < 70 or b > 110 : continue
    if charge_gr.GetBinContent(b) < 10 or eff_irrad.GetBinContent(b) < 0.9 : continue 
    #print b, charge_gr.GetBinContent(b), eff_irrad.GetBinContent(b)
    gr.SetPoint(b-1,charge_gr.GetBinContent(b),eff_irrad.GetBinContent(b))
    gr.SetPointError(b-1,charge_gr.GetBinError(b),eff_irrad.GetBinError(b))


#################### Get simulation

from glob import glob
inpt = "/afs/cern.ch/work/p/pluca/SciFi/Optimisation/test_not_irrad/1/options_CrossTalkProb_0.325_PhotonsPerMeV_*/digitised/*tuple.root"
files = glob(inpt)

ngen = 10000
gr_sim = R.TGraphErrors()
for fi,fn in enumerate(files) :
    f = R.TFile.Open(fn)
    tup = f.Get("FTClusterTuple/FTClusterTuple")
    tup.Draw("chargeFull>>chargehisto","station==1 && motherMCHit==-99999 && layer==0")
    h = R.gPad.GetPrimitive("chargehisto")
    eff = h.GetEntries()/float(ngen)
    efferr = R.TMath.Sqrt(eff*(1.-eff)/ngen)
    print h.GetMean(), eff
    #gr_sim.SetPoint(fi,h.GetMean(),eff)
    #gr_sim.SetPointError(fi,h.GetMeanError(),efferr)





gr.Draw("AP")
gr.SetMarkerColor(2)
gr.SetMarkerStyle(22)
gr.SetMarkerSize(0.8)
gr.GetYaxis().SetRangeUser(0.8,1.1)
gr.GetXaxis().SetRangeUser(10,20)
gr.GetXaxis().SetTitle('Light yield')
gr.GetYaxis().SetTitle('Hit efficiency')

#gr_sim.Draw("P same")
#gr_sim.SetMarkerColor(4)
#gr_sim.SetMarkerStyle(23)
#gr_sim.SetMarkerSize(0.8)

c1.Print("hiteff_vs_charge.pdf")





