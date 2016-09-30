#!/usr/bin/python
#Author : BELLEE Violaine
#Date : 2015/04/22                                                                                                                                           
#Used to give nice appearance to the root histos created by GenerateCompareSignal.sh     

import argparse
import ROOT
import math

def draw_compare_plot(outputdirectory, outputname, tree1, tree2, observable, geant_observable, title, beginning, end, numbins):


    histo1 = ROOT.TH1F('histo1','',numbins, beginning, end)
    histo1.SetLineColor(2)
    histo1.SetLineWidth(2)
    histo1.SetStats(False)
    histo1.SetMarkerStyle(20)
    histo1.Sumw2()
    histo1.SetOption("E")

    histo2 = ROOT.TH1F('histo2','',numbins, beginning, end)
    histo2.SetLineColor(4)
    histo2.SetLineWidth(2)
    histo2.SetStats(False)
    histo2.SetMarkerStyle(20)
    histo2.Sumw2()
    histo2.SetOption("E")

    tree1.Draw(geant_observable+'>>histo1',)
    tree2.Draw(observable+'>>histo2',)
    leg = ROOT.TLegend(0.75,0.7,0.95,0.89)
    leg.AddEntry(histo1,"Geant 4 simulation","l")
    leg.AddEntry(histo2,"Boole simulation","l")

    hs = ROOT.THStack ("hs",'')

    norm1 = 1/(histo1.Integral())
    histo1.Scale(norm1)                                                                                                                                      
    hs.Add(histo1)

    norm2 = 1/(histo2.Integral())                                                                                                                           
    histo2.Scale(norm2)                                                                                                                                      
    hs.Add(histo2)


    hs.Print()

    outfile = ROOT.TFile(outputdirectory+outputname+"_"+observable+".root","RECREATE")
    canvas = ROOT.TCanvas("canvas","",1000,700)
    ROOT.gStyle.SetOptStat("")

    hs.Draw("nostack")
    hs.GetXaxis().SetTitle(title)
    hs.GetXaxis().SetTitleSize(0.045)

    bin = (end-beginning)/numbins
    binstr = "%.2f" % bin

    hs.GetYaxis().SetTitle('A.U.')
    hs.GetYaxis().SetTitleOffset(1.1)
    hs.GetYaxis().SetTitleSize(0.045)


    leg.Draw("same")
    canvas.SaveAs(outputdirectory+outputname+'_'+observable+'.png')
    canvas.Write()
    outfile.Write()
    outfile.Close()


if __name__ == '__main__':

    ###Parser to use the file externally

    parser = argparse.ArgumentParser()

    parser.add_argument("-ni", "--nickname" , default="compareGeant4" , action="store", type=str)
    parser.add_argument("-d" , "--outputdirectory" , default="" , action="store", type=str)
    parser.add_argument("-i1", "--inputfile1" , default=None , action="store", type=str, help = 'Name of the testbeam data file')
    parser.add_argument("-i2", "--inputfile2" , default=None , action="store", type=str, help = 'Name of the simulation file')
    parser.add_argument("-t1", "--tree1" , default="ClusterTree" , action="store", type=str)
    parser.add_argument("-t2", "--tree2" , default="clusterAnalysis" , action="store", type=str)
    args = parser.parse_args()

    features_and_properties = {'clusterSize'       : ('Cluster Size', 1, 7, 6, 'Clustersize'),
                               'sumCharge'         : ('Total cluster charge', 0, 80, 80, 'Clustercharge'), 
                               'maxCharge'         : ('Charge of the dominant channel in cluster', 0, 60, 60, 'highest_channel')}


    ### Define files to be read and beginning and end of the histograms                                                                                          

    outputname = (args.inputfile2.split("/")[-1]).replace(".root", "_{0}".format(args.nickname))
    outputdirectory = args.outputdirectory

    tree1 = ROOT.TChain(args.tree1)
    tree1.AddFile(args.inputfile1)

    tree2 = ROOT.TChain(args.tree2)
    tree2.AddFile(args.inputfile2)

    for feature, properties in features_and_properties.iteritems():
        observable = feature
        title = properties[0]
        beginning = properties[1]
        end = properties[2]
        numbins = properties[3]
        geant_observable = properties[4]
        draw_compare_plot(outputdirectory, outputname, tree1, tree2, observable, geant_observable, title, beginning, end, numbins)
