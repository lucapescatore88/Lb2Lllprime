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

def findMax(tree,variable) :

    tree.Draw(variable+">>htest")
    h = gPad.GetPrimitive("htest")
    binmax = h.GetMaximumBin()
    return h.GetXaxis().GetBinCenter(binmax)

def draw_compare_plot(outputdirectory, outputname, trees, observable, geant_observable, title, beginning, end, numbins, noplot):

    ## Create teplate histograms

    histos = {}
    boolehisto = None
    for it,t in enumerate(trees) :
        key = t[0].replace(" ","")
        name = key+observable
        h = TH1F(name,name,numbins, beginning, end)
        h.SetLineColor(colors[it])
        h.SetLineWidth(2)
        h.SetStats(False)
        h.SetMarkerStyle(20)
        h.SetMarkerColor(colors[it])
        h.Sumw2()
        h.SetOption("E")
        histos[key] = h
        if 'Boole' in name and boolehisto is None :
            boolehisto = h
            print "Simulaiton histogram for comparisons is", name.replace(observable,"")

    ## Fill histrograms
    leg = TLegend(0.6,0.7,0.93,0.89)
    for i,t in enumerate(trees) :
        name = t[0].replace(" ","")+observable
        if "Geant" in t[0] : t[1].Draw(geant_observable+'>>'+name)
        elif "Beam" in t[0] :
            #curmax = findMax(t[1],"distance_from_track")
            t[1].Draw(geant_observable+'>>'+name)#,"abs(distance_from_track - {curmax}) < 100".format(curmax=curmax))
        else : t[1].Draw(observable+'>>'+name)
        leg.AddEntry(histos[name.replace(observable,"")],t[0].replace('Beam','beam'),"l")

    ## Calculate chi2 TB/Boole and G4/Boole   
    chi2ndf = -1
    chi2ndf_testbeam = -1

    if "TestBeamdata" in histos and boolehisto is not None :
        chi2ndf_testbeam = histos["TestBeamdata"].Chi2Test(boolehisto,"CHI2/NDF")
    if "Geant4simulation" in histos and boolehisto is not None :
        chi2ndf = histos["Geant4simulation"].Chi2Test(boolehisto,"CHI2/NDF")

    if noplot : return chi2ndf, chi2ndf_testbeam, numbins, observable

    ## Plot

    hs = THStack ("hs",'')
    for hn,h in histos.iteritems() :
        h.Scale(1./h.Integral())
        hs.Add(h)
    hs.Print()

    outfile = TFile(outputdirectory+outputname+"_"+observable+".root","RECREATE")
    canvas = TCanvas()
    gStyle.SetOptStat("")

    hs.Draw("nostack")
    hs.GetXaxis().SetTitle(title)
    hs.GetYaxis().SetTitle('A.U.')

    leg.Draw("same")
    canvas.Print(outputdirectory+outputname+'_'+observable+'.png')
    canvas.Print(outputdirectory+outputname+'_'+observable+'.C')
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
    parser.add_argument("-simf", "--simf" , default=None, help = 'Name of the simulation file')
    parser.add_argument("-simconfig", "--simconfig" , default=None, help = 'File contaiing config dictionary for more than one simulation')
    parser.add_argument("-g4f", "--g4f" , default=None , help = 'Name of the Geant4 simulation file')
    parser.add_argument("-testbt", "--testbt" , default="clusterAnalysis")
    parser.add_argument("-simt", "--simt" , default="clusterAnalysis")
    parser.add_argument("-g4t", "--g4t" , default="ClusterTree")
    parser.add_argument("--noplot" , action="store_true")
    args = parser.parse_args()

    #features_and_properties = {'clusterSize'       : ('Cluster Size', 1, 7, 6, 'Clustersize'),
    #                           'sumCharge'         : ('Total cluster charge', 0, 80, 80, 'Clustercharge'), 
    #                           'maxCharge'         : ('Charge of the dominant channel in cluster', 0, 60, 60, 'highest_channel')}
    features_and_properties = { 'clusterSize'       : ('Cluster Size', 1, 7, 6, 'clusterSize'),
                                'sumCharge'         : ('Total cluster charge', 0, 80, 80, 'clusterCharge') }


    ### Define files to be read and the range of the histograms

    outputname = "comparison"
    outputdirectory = args.outputdirectory
    
    trees = []

    if args.testbf is not None :
        trees.append( ( "Test Beam data", TChain(args.testbt)) )
        trees[-1][1].AddFile(args.testbf)
        
    if args.simf is not None :
        trees.append( ("Boole simulation", TChain(args.simt)) )
        #trees.append( ("Simulation", TChain(args.simt)) )
        trees[-1][1].AddFile(args.simf)
        outputname = (args.simf.split("/")[-1]).replace(".root", "_{0}".format(args.nickname))
    elif args.simconfig is not None:
        simfiles =  eval(open(args.simconfig).read())
        for lab,f in simfiles.iteritems() :
            trees.append( (lab, TChain(args.simt)) )
            trees[-1][1].AddFile(f)
            outputname = (f.split("/")[-1]).replace(".root", "_{0}".format(args.nickname))

    if args.g4f is not None :
        trees.append( ("Geant4 simulation", TChain(args.g4t)) )
        trees[-1][1].AddFile(args.g4f)

    ## Make plots and retireve chi2

    chi2s = []
    for obs, (title,start,end,nbins,g4obs) in features_and_properties.iteritems(): 
        chi2s.append( draw_compare_plot(outputdirectory, outputname, trees, 
            obs, g4obs, title, start, end, nbins, args.noplot) )

    ## Calculate total chi2 summing over features and write all out to a file

    totchi2 = sum( [ v[0] * v[2] for v in chi2s ] ) / sum( [ v[2] for v in chi2s ] )
    totchi2_testbeam = sum( [ v[1] * v[2] for v in chi2s ] ) / sum( [ v[2] for v in chi2s ] )
    print "Overall chi2 Boole-G4 --> ", totchi2, ", Boole-Testbeam --> ", totchi2_testbeam
    
    of = open(outputdirectory+"/chi2_"+outputname+".txt","w")
    of.write(str(totchi2)+ "   Total\n")
    of.write(str(totchi2_testbeam)+ "   Total Testbeam\n")
    for v in chi2s : 
        of.write("{0} {1} {2}\n".format(v[0],v[2],v[3]))
        of.write("{0} {1} {2} Testbeam\n".format(v[1],v[2],v[3]))
    of.close()



