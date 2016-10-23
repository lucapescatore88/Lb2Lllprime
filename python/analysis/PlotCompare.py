#!/usr/bin/python
#Author : BELLEE Violaine
#Date : 2015/04/22                                                                                                                                           
#Used to compare cluster observables between the geant 4 'stand-alone' simulation and boole simulation

import argparse
import ROOT
import math

colors = [1,4,2]

def draw_compare_plot(outputdirectory, outputname, trees, observable, geant_observable, title, beginning, end, numbins, noplot):

    histos = {}
    for it,t in enumerate(trees) :
        name = t[0].replace(" ","")
        h = ROOT.TH1F(name,'',numbins, beginning, end)
        h.SetLineColor(colors[it])
        h.SetLineWidth(2)
        h.SetStats(False)
        h.SetMarkerStyle(20)
        h.SetMarkerColor(colors[it])
        h.Sumw2()
        h.SetOption("E")
        histos[name] = h

    leg = ROOT.TLegend(0.6,0.7,0.95,0.89)
    for i,t in enumerate(trees) :
        name = t[0].replace(" ","")
        if("Geant" not in t[0]) : t[1].Draw(observable+'>>'+name,)
        else : t[1].Draw(geant_observable+'>>'+name,)
        leg.AddEntry(histos[name],t[0],"l")

    chi2ndf = -1
    chi2ndf_testbeam = -1
    
    if "TestBeamdata" in histos :
        chi2ndf_testbeam = histos["TestBeamdata"].Chi2Test(histos["Boolesimulation"],"CHI2/NDF")
    if "Geant4simulation" in histos :
        chi2ndf = histos["Geant4simulation"].Chi2Test(histos["Boolesimulation"],"CHI2/NDF")

    if noplot : return chi2ndf, chi2ndf_testbeam, numbins, observable

    hs = ROOT.THStack ("hs",'')

    for hn,h in histos.iteritems() :
        h.Scale(1./h.Integral())
        hs.Add(h)

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

    return chi2ndf, chi2ndf_testbeam, numbins, observable

if __name__ == '__main__':

    ###Parser to use the file externally

    parser = argparse.ArgumentParser()

    parser.add_argument("-ni", "--nickname" , default="")
    parser.add_argument("-d" , "--outputdirectory" , default="")
    parser.add_argument("-testbf", "--testbf" , default=None, help = 'Name of the testbeam data file')
    parser.add_argument("-simf", "--simf" , default=None, required=True, help = 'Name of the simulation file')
    parser.add_argument("-g4f", "--g4f" , default=None , help = 'Name of the Geant4 simulation file')
    parser.add_argument("-testbt", "--testbt" , default="clusterAnalysis")
    parser.add_argument("-simt", "--simt" , default="clusterAnalysis")
    parser.add_argument("-g4t", "--g4t" , default="ClusterTree")
    parser.add_argument("--noplot" , action="store_true")
    args = parser.parse_args()

    features_and_properties = {'clusterSize'       : ('Cluster Size', 1, 7, 6, 'Clustersize'),
                               'sumCharge'         : ('Total cluster charge', 0, 80, 80, 'Clustercharge'), 
                               'maxCharge'         : ('Charge of the dominant channel in cluster', 0, 60, 60, 'highest_channel')}

    ### Define files to be read and beginning and end of the histograms

    outputname = (args.simf.split("/")[-1]).replace(".root", "_{0}".format(args.nickname))
    outputdirectory = args.outputdirectory
    
    trees = []

    if args.testbf is not None :
        trees.append( ( "Test Beam data", ROOT.TChain(args.testbt)) )
        trees[-1][1].AddFile(args.testbf)
    if args.simf is not None :
        trees.append( ("Boole simulation", ROOT.TChain(args.simt)) )
        trees[-1][1].AddFile(args.simf)
    if args.g4f is not None :
        trees.append( ("Geant4 simulation", ROOT.TChain(args.g4t)) )
        trees[-1][1].AddFile(args.g4f)

    chi2s = []
    for feature, properties in features_and_properties.iteritems():
        observable = feature
        title = properties[0]
        beginning = properties[1]
        end = properties[2]
        numbins = properties[3]
        geant_observable = properties[4]
        chi2s.append( draw_compare_plot(outputdirectory, outputname, trees, 
            observable, geant_observable, title, beginning, end, numbins, args.noplot) )

    print chi2s
    totchi2 = sum( [ v[0] * v[2] for v in chi2s ] ) / sum( [ v[2] for v in chi2s ] )
    totchi2_testbeam = sum( [ v[1] * v[2] for v in chi2s ] ) / sum( [ v[2] for v in chi2s ] )
    print "Overall chi2 Boole-G4 --> ", totchi2, ", Boole-Testbeam --> ", totchi2_testbeam
    of = open(outputdirectory+"/chi2_"+outputname+".txt","w")
    of.write(str(totchi2)+ "   Total\n")
    of.write(str(totchi2_testbeam)+ "   Total Testbeam\n")
    for v in chi2s : 
        of.write("{0} {1} {2}\n".format(v[0],v[2],[3]))
        of.write("{0} {1} {2} Testbeam\n".format(v[1],v[2],[3]))
    of.close()



