#!/usr/bin/python
#Author : PESCATORE Luca
#Date : 2018/01/22                                                                                                                                           
#Used to give nice appearance to the root histos created by GenerateCompareSignal.sh     

import argparse
import ROOT
import math

if __name__ == '__main__':

    ###Parser to use the file externally

    parser = argparse.ArgumentParser()

    parser.add_argument("-ou", "--outputname" , default="compare" , action="store", type=str)
    parser.add_argument("-d" , "--outputdirectory" , default="/afs/cern.ch/work/v/vibellee/public/SciFiWorkshop/SciFiSimPlots/" , action="store", type=str)
    parser.add_argument("-i1", "--inputfile1" , default=None , action="store", type=str)
    parser.add_argument("-i2", "--inputfile2" , default=None , action="store", type=str)
    parser.add_argument("-t",  "--tree" , default="DecayTree" , action="store", type=str)
    parser.add_argument("-ob", "--observable" , default="" , action="store", type=str)
    parser.add_argument("-b",  "--beginning" , default=0.0 , action="store", type=float)
    parser.add_argument("-e",  "--end" , default=1.0 , action="store", type=float)
    parser.add_argument("-n",  "--numbins" , default=10 , action="store", type=int)
    parser.add_argument("-ti", "--title" , default="" , action="store", type=str)
    args = parser.parse_args()

    ### Define files to be read and start and stop of the histograms                                                                                          

    outputname = args.outputname
    outputdirectory = args.outputdirectory

    tree1 = ROOT.TChain(args.tree)
    tree1.AddFile(args.inputfile1)

    tree2 = ROOT.TChain(args.tree)
    tree2.AddFile(args.inputfile2)

    start = args.beginning
    stop = args.end
    nbins = args.numbins

    histo1 = ROOT.TH1F('histo1','',nbins, start, stop)
    histo1.SetLineColor(2)
    histo1.SetLineWidth(2)
    histo1.SetStats(False)
    histo1.SetMarkerStyle(20)
    histo1.Sumw2()
    histo1.SetOption("E")

    histo2 = ROOT.TH1F('histo2','',nbins, start, stop)
    histo2.SetLineColor(4)
    histo2.SetLineWidth(2)
    histo2.SetStats(False)
    histo2.SetMarkerStyle(20)
    histo2.Sumw2()
    histo2.SetOption("E")

    tree1.Draw(args.observable+'>>histo1',)
    tree2.Draw(args.observable+'>>histo2',)
#    leg = ROOT.TLegend(0.6,0.7,0.89,0.89)
    leg = ROOT.TLegend(0.75,0.7,0.95,0.89)
    leg.AddEntry(histo1,"Testbeam","l")
    leg.AddEntry(histo2,"Improved simulation","l")
#    leg.AddEntry(histo1,"Standard","l")
#    leg.AddEntry(histo2,"Improved","l")

    hs = ROOT.THStack ("hs",'')

    norm1 = 1/(histo1.Integral())
    histo1.Scale(norm1)                                                                                                                                      
    hs.Add(histo1)

    norm2 = 1/(histo2.Integral())                                                                                                                           
    histo2.Scale(norm2)                                                                                                                                      
    hs.Add(histo2)


    hs.Print()

    outfile = ROOT.TFile(outputdirectory+outputname+".root","RECREATE")
    canvas = ROOT.TCanvas("canvas","",1000,700)
    ROOT.gStyle.SetOptStat("")

    hs.Draw("nostack")
    hs.GetXaxis().SetTitle(args.title)
    hs.GetXaxis().SetTitleSize(0.045)

    bin = (stop-start)/nbins
    binstr = "%.2f" % bin

    hs.GetYaxis().SetTitle('A.U.')
    hs.GetYaxis().SetTitleOffset(1.1)
    hs.GetYaxis().SetTitleSize(0.045)


    leg.Draw("same")
    #ROOT.gPad.SetLogy()
    canvas.SaveAs(outputdirectory+outputname+'_'+args.observable+'.png')
    canvas.Write()
    outfile.Write()
    outfile.Close()


