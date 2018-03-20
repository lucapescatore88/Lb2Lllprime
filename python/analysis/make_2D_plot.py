from ROOT import *
from glob import glob
import re

files = glob('/afs/cern.ch/work/p/pluca/SciFi/Optimisation/2D_FXT_ChXT/1/*/comparisons/chi2_comparisons_posA-angle0.txt')

d = []

for f in files :

    vals = re.findall('ChannelXTalkProb_(\d+\.\d+)_CrossTalkProb_(\d+\.\d+)/',f)
    txt = open(f).readlines()
    chi2 = float(txt[0].split()[0])

#    print vals, chi2
    d.append((float(vals[0][0]),float(vals[0][1]),chi2))

x = list(set([e[0] for e in d]))
y = list(set([e[1] for e in d]))
x.sort()
y.sort()

xstep = x[1] - x[0]
ystep = y[1] - y[0]
xmin = float(x[0]-xstep/2.)
xmax = float(x[len(x)-1]+xstep/2.)
ymin = float(y[0]-ystep/2.)
ymax = float(y[len(y)-1]+ystep/2.)


h = TH2F("h","",len(y),ymin,ymax,len(x),xmin,xmax)

for p in d :
    
    b = h.FindBin(p[1],p[0])
    h.SetBinContent(b,p[2])

c = TCanvas()
gStyle.SetOptStat(0)
h.GetXaxis().SetTitle("FiberXTalkProb")
h.GetYaxis().SetTitle("ChannelXTalkProb")
h.Draw("colz")
c.Print("test.pdf")











