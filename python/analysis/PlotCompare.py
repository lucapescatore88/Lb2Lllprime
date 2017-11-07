#!/usr/bin/python
# Author : PESCATORE Luca, BELLEE Violaine
# Date : 2017/03/07                                                                                                                                           
#Used to compare cluster observables between the geant 4 'stand-alone' simulation and boole simulation

import argparse
from ROOT import *
import math, os

repo = os.getenv("SCIFITESTBEAMSIMROOT")
gROOT.ProcessLine('.x '+repo+'/job/lhcbStyle.C')

colors = [1,4,2,3,7,6,8,9]

def format_hist(h,it) :
    
    h.SetLineColor(colors[it])
    h.SetLineWidth(2)
    h.SetStats(False)
    h.SetMarkerStyle(20)
    h.SetMarkerColor(colors[it])
    #h.Sumw2()
    h.SetOption("E")
    h.Scale(1./h.Integral())

def get_tb_feature(f,fil,htmp) :

    tree = fil.Get("btTree")
    h = htmp.Clone("h"+f+"TestBeam")
    tree.Draw(f+">>"+h.GetName())
    return h

def get_sim_feature(f,fil) :
    
    return fil.Get("FTClusterMonitor/"+f)
       
def mychi2(h1,h2,xmin,xmax) :

    ndf = 0
    chi2 = 0
    for b in range(1,h1.GetNbinsX()+1) :

        x1 = h1.GetBinCenter(b)
        if x1 < xmin or x1 > xmax : continue
        
        y1 = h1.GetBinContent(b)
        y1err = h1.GetBinError(b)
        y2 = h2.GetBinContent(b)
        y2err = h2.GetBinError(b)

        if y1 <= 0 and y2 <= 0 : continue 
        chi2 += (y1-y2)*(y1-y2)/float(y1+y2)
        ndf += 1

    return chi2, ndf

if __name__ == '__main__':

    ### Parser to use the file externally

    parser = argparse.ArgumentParser()

    parser.add_argument("-ni", "--nickname" , default="")
    parser.add_argument("-d" , "--outdir" , default="")
    parser.add_argument("-testbf", "--testbf" , default=None, help = 'Name of the testbeam data file')
    parser.add_argument("-simf", "--simf" , default=None, help = 'Name of the simulation file')
    parser.add_argument("-simconfig", "--simconfig" , default=None, help = 'File contaiing config dictionary for more than one simulation')
    parser.add_argument("-testbt", "--testbt" , default="clusterAnalysis")
    parser.add_argument("--noplot" , action="store_true")
    args = parser.parse_args()

    features = { 'clusterSize'       : {'title' : 'Cluster Size', 'min' : 0, 'max' : 6, 'sim' : 'FullClusterSize'},
                 'clusterCharge'     : {'title' : 'Total cluster charge', 'min' : 5, 'max' : 40, 'sim' : 'FullClusterCharge'} }
    
    tbFile = TFile.Open(args.testbf)
    simFile = TFile.Open(args.simf)
    outfile = TFile(args.outdir+"comparisons.root","RECREATE")

    chi2s = []
    canvas = TCanvas()
    gStyle.SetOptStat("")
    for f,prop in features.iteritems() :

        leg = TLegend(0.6,0.7,0.93,0.89)
        
        hs  = get_sim_feature(prop['sim'],simFile)
        htb = get_tb_feature(f,tbFile,hs)

        format_hist(htb,1)
        print "TB Mean", f, os.path.basename(args.testbf).replace(".root",""), "---->", htb.GetMean(), htb.GetMeanError()
        format_hist(hs,2)
        print "Sim Mean", f, os.path.basename(args.testbf).replace(".root",""), "---->", hs.GetMean(), hs.GetMeanError()

        #chi2.append( (htb.Chi2Test(hs,"CHI2/NDF P WW"),htb.GetNbinsX(),prop[4],htb.KolmogorovTest(hs,"M")) ) 
        chi2, ndf = mychi2(htb,hs,prop['min'],prop['max'])
        chi2s.append( (chi2/float(ndf), ndf, prop['sim'], htb.KolmogorovTest(hs,"M")) ) 

        leg.AddEntry(htb,"Test Beam","p")
        leg.AddEntry(hs,"Simulation","p")

        htb.Draw()
        htb.GetXaxis().SetTitle(prop['title'])
        htb.GetYaxis().SetTitle('A.U.')
        hs.Draw("same")

        leg.Draw("same")
        cname = args.outdir+'comparison_{f}_{inpt}'.format(f=f,inpt=os.path.basename(args.testbf))
        canvas.Print(cname+'.pdf')
        canvas.Print(cname+'.C')
        canvas.Write()
        
    outfile.Close()

    ## Calculate total chi2 summing over features and write all out to a file
    
    totchi2 = sum( [ v[0] * v[1] for v in chi2s ] ) / float(sum( [ v[1] for v in chi2s ] ))
    totKolm = sum( [ v[3] * v[1] for v in chi2s ] ) / float(sum( [ v[1] for v in chi2s ] ))
    print "Chi2 Boole-Testbeam --> ", totchi2
    print "Kolmogorov Boole-Testbeam --> ", totchi2
   
    of = open(args.outdir+"/chi2_comparisons_{inpt}.txt".format(inpt=os.path.basename(args.testbf)),"w")
    of.write(str(totchi2)+ "   Total Chi2\n")
    of.write(str(totKolm)+ "   Total Kolmogorov\n")
    for v in chi2s : 
        of.write("Chi2 {0} {1} {2}\n".format(v[2],v[0],v[1]))
        of.write("Kolmogorov {0} {1} {2}\n".format(v[3],v[0],v[1]))
    of.close()



