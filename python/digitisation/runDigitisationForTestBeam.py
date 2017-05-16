# Run Boole with the standard implementation (using the -s option)
# or the improved implementation

import argparse, pickle
from glob import glob
from setupBooleForDigitisation import *

parser = argparse.ArgumentParser(description='Plot cluster properties from data and simulation.')
parser.add_argument('-f', '--files', type=str, help="Path and name of the input .sim file, the * can be used as in /home/files/njob*/file.sim",
                    default="/home/vbellee/ImprovedBoole2017_01_30/testbeamRefFiles/testbeam_simulation_position_a_at_0deg.sim")
parser.add_argument('-i', '--interactive', action = "store_true", default=False)
parser.add_argument('-s', '--storeTestbeam', action = "store_true", default=False)
parser.add_argument('-t', '--digitype', type=str, default="improved")
parser.add_argument('-x', '--params', type=str, default="")
parser.add_argument('-p', '--pacific', action="store_true")
parser.add_argument('-ths', '--thresholds', type=str, default="[1.5,2.5,4.5]")
parser.add_argument('-r', '--resultPath', type=str, default="")
parser.add_argument('-d', '--DDDBtag', type=str, default='dddb-20160304')
parser.add_argument('-c', '--CondDBtag', type=str, default='sim-20150716-vc-md100')

cfg = parser.parse_args()
if cfg.params == "" : params = get_params()
else : params = pickle.load(open(cfg.params))

files = glob(cfg.files)
resultPath = cfg.resultPath
fileName = (files[0].split("/")[-1]).replace(".sim", "_{0}.root".format(cfg.digitype))
print("Outputfile: " + fileName)

import GaudiPython as GP
from GaudiConf import IOHelper
from Gaudi.Configuration import *
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc, Boole
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import CondDB, DDDBConf

#Temporary
#Boole().DataType   = "Upgrade"

# ROOT persistency for histograms
importOptions('$STDOPTS/RootHist.opts')
from Configurables import RootHistCnv__PersSvc
RootHistCnv__PersSvc('RootHistCnv').ForceAlphaIds = True
# RootHistSvc('RootHistSvc').OutputFile = 'histo.root'
HistogramPersistencySvc().OutputFile = fileName.replace(".root","")+'_histos.root'


from LinkerInstances.eventassoc import *
import ROOT as R
import array


def resetSipmVals(sipimValPtr):
  for layer in sipimValPtr:
    for adcID in layer:
      for adcChan in layer[adcID]:
        adcChan[0] = 0

LHCbApp().Simulation = True
#LHCbApp().Histograms = 'Default'
CondDB().Upgrade = True
## New numbering scheme. Remove when FT60 is in nominal CondDB.
#CondDB().addLayer(dbFile = "/afs/cern.ch/work/j/jwishahi/public/SciFiDev/DDDB_FT60.db", dbName = "DDDB")
#CondDB().addLayer(dbFile = "/home/vbellee/ImprovedBoole2017_01_30/testbeamRefFiles/DDDB_FT61_noEndplug.db", dbName = "DDDB")
CondDB().addLayer(dbFile = "/eos/lhcb/wg/SciFi/Custom_Geoms_Upgrade/databases/DDDB_FT61_noEndplug.db", dbName = "DDDB")


LHCbApp().DDDBtag = cfg.DDDBtag
LHCbApp().CondDBtag = cfg.CondDBtag

# Configure all the unpacking, algorithms, tags and input files
appConf = ApplicationMgr()
appConf.ExtSvc+= [
                  'ToolSvc'
                  ,'DataOnDemandSvc'
                  #,'NTupleSvc'
                  ]
appConf.TopAlg += ["MCFTDepositCreator",
                   "MCFTDepositMonitor",
                   "MCFTDigitCreator",
                   "FTClusterCreator",
                   #"FTNtupleMaker"
                   ]


######################################
#Configure Boole
######################################

setupBooleForDigitisation(params,cfg.digitype,eval(cfg.thresholds))

s = SimConf()
#SimConf().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon']
SimConf().Detectors = ['VP', 'FT']
SimConf().EnableUnpack = True
SimConf().EnablePack = False

d = DigiConf()
#DigiConf().Detectors = ['VP', 'UT', 'FT', 'Rich1Pmt', 'Rich2Pmt', 'Ecal', 'Hcal', 'Muon']
DigiConf().Detectors = ['VP', 'FT']
DigiConf().EnableUnpack = True
DigiConf().EnablePack = False

#dre = DecodeRawEvent()
#dre.DataOnDemand = True

lhcbApp = LHCbApp()
lhcbApp.Simulation = True

IOHelper('ROOT').inputFiles(files)


######################################
# Configuration done, run time!
######################################

appMgr = GP.AppMgr()
evt = appMgr.evtsvc()
det = appMgr.detsvc()
hist = appMgr.histSvc()

hist.dump()

## Create trees and variables
outputFile = R.TFile(resultPath + fileName, "RECREATE")
layers = range(0,1)
sipmIDs = range(0,16)
sipmValPtr = []
outputTrees = []
outputFile.cd()
for layerNumber in layers:
    outputTrees.append(R.TTree("layer_" + str(layerNumber), "layer_" + str(layerNumber) ) )
    sipmValPtr_thisLayer = {}
    for sipmID in sipmIDs:
        arr = []
        for sipmChan in xrange(128):
            arr.append(array.array("f", [0]))
        sipmValPtr_thisLayer[sipmID] = arr
        for adcChan in xrange(128):
            name = "Uplink_" + str(sipmID) +"_adc_" + str(adcChan+1)
            outputTrees[-1].Branch(name, sipmValPtr_thisLayer[sipmID][adcChan] ,name + "/F")
    sipmValPtr.append(sipmValPtr_thisLayer)

## Main loop on events
nHits = 0
while True:
    appMgr.run(1)

    if not evt['MC/Particles']:
        print "no more particles"
        break

    nHits += len(evt["MC/FT/Hits"])
    digits = evt['/Event/MC/FT/Digits'].containedObjects()
    for digit in digits:
    
        jump = False
        hits = digit.deposit().mcHitVec()
        for h in hits :
            mother = h.mcParticle().mother()
            if "NULL" not in mother.__str__() : 
                jump = True
                break
        
        if jump : continue 
        channel = digit.channelID()

        ## If PACIFIC use bits: 1,2,3
        adc = digit.photoElectrons()
        if cfg.pacific : adc = digit.adcCount()

        if channel.layer() in layers and channel.sipm() in sipmIDs and channel.module() == 4 and channel.quarter() == 3 and channel.station() == 1 and channel.mat()==0:
            sipmValPtr[channel.layer()][channel.sipm()][channel.channel()][0] = adc
 
    for t in outputTrees: t.Fill()
    resetSipmVals(sipmValPtr)

## Write output
outputFile.cd()
for t in outputTrees: t.Write()
outputFile.Close()


