# Run Boole with the standard implementation (using the -s option)
# or the improved implementation

import argparse
from glob import glob

parser = argparse.ArgumentParser(description='Plot cluster properties from data and simulation.')
parser.add_argument('-f', '--files', type=str, help="Path and name of the input .sim file, the * can be used as in /home/files/njob*/file.sim",
                    default="/afs/cern.ch/work/j/jwishahi/public/forViolaine/20160615_testbeam_ttekampe/1/*/output/testbeam_simulation_position*.sim")
parser.add_argument('-i', '--interactive', action = "store_true", default=False)
parser.add_argument('-s', '--storeTestbeam', action = "store_true", default=False)
parser.add_argument('-n', '--nickname', type=str, default="")
parser.add_argument('-r', '--resultPath', type=str, default="")
parser.add_argument('-d', '--DDDBtag', type=str, default='dddb-20160304')
parser.add_argument('-c', '--CondDBtag', type=str, default='sim-20150716-vc-md100')

cfg = parser.parse_args()

import GaudiPython as GP
from GaudiConf import IOHelper
from Gaudi.Configuration import *
from Configurables import LHCbApp, ApplicationMgr, DataOnDemandSvc, Boole
from Configurables import SimConf, DigiConf, DecodeRawEvent
from Configurables import CondDB, DDDBConf

#Temporary
#Boole().DataType   = "Upgrade"
#print dir(Boole())
#Boole().Simulation   = True

# ROOT persistency for histograms
importOptions('$STDOPTS/RootHist.opts')
from Configurables import RootHistCnv__PersSvc
RootHistCnv__PersSvc('RootHistCnv').ForceAlphaIds = True
# should be provided by the user script, otherwise big confusion between Gaudi and ROOT
# RootHistSvc('RootHistSvc').OutputFile = 'histo.root'
HistogramPersistencySvc().OutputFile = 'histo.root'

import array

from LinkerInstances.eventassoc import *

import ROOT as R

def resetSipmVals(sipimValPtr):
  for layer in sipimValPtr:
    for adcID in layer:
      for adcChan in layer[adcID]:
        adcChan[0] = 0

LHCbApp().Simulation = True
#LHCbApp().Histograms = 'Default'
CondDB().Upgrade = True
## New numbering scheme. Remove when FT60 is in nominal CondDB.
CondDB().addLayer(dbFile = "/afs/cern.ch/work/j/jwishahi/public/SciFiDev/databases/DDDB_FT60_noEndPlug.db", dbName = "DDDB")
#CondDB().addLayer(dbFile = "/eos/lhcb/wg/SciFi/Custom_Geoms_Upgrade/databases/DDDB_FT61.db", dbName = "DDDB")
#CondDB().addLayer(dbFile = "/eos/lhcb/wg/SciFi/Custom_Geoms_Upgrade/databases/DDDB_FT60.db", dbName = "DDDB")

LHCbApp().DDDBtag = cfg.DDDBtag
LHCbApp().CondDBtag = cfg.CondDBtag

# Configure all the unpacking, algorithms, tags and input files
appConf = ApplicationMgr()
appConf.ExtSvc+= [
                  'ToolSvc'
                  ,'DataOnDemandSvc'
                  #,'NTupleSvc'
                  ]
appConf.TopAlg += [
                   "MCFTDepositCreator",
                   "MCFTDepositMonitor",
                   "MCFTDigitCreator",
                   "FTClusterCreator",
                   #"FTNtupleMaker"
                   ]


######################################
#Configure Boole
######################################


from Configurables import SiPMResponse
SiPMResponse().useNewResponse = 2#Use flat SiPM time response 

from Configurables import MCFTAttenuationTool
att = MCFTAttenuationTool()
att.ShortAttenuationLength = 682.5 # 200mm  # TestBeam: HD1 468.6, HD2 896.3
att.LongAttenuationLength = 4796   # 4700mm  # TestBeam: HD1 4688, HD2 4904
att.FractionShort = 0.34           # 0.18 # TestBeam: HD1 0.273, HD2 0.406

# Make sure I always hit unirradiated zone
att.XMaxIrradiatedZone = 999999999999.#2000
att.YMaxIrradiatedZone = -1.#500

from Configurables import MCFTDepositPathFracInFibreTool
pathtool = MCFTDepositPathFracInFibreTool()
pathtool.CrossTalkProb = 0.04

from Configurables import MCFTDepositDistributionTool

distributiontool = MCFTDepositDistributionTool()
distributiontool.MinFractionForSignalDeposit = 0.005
distributiontool.ImprovedDigitisation = True
distributiontool.NumOfNeighbouringChannels = 3
distributiontool.LightSharing = "Gaussian"
#distributiontool.GaussianSharingWidth = 0.5
distributiontool.GaussianSharingWidth = 0.5
#The above option corresponds to the fraction of the channel width
#covered by the gaussian distribution of photons at the end of the
#fibre, it corresponds to a width of 125um.
#Options if old light sharing is used
distributiontool.OldLightSharingCentral = 0.68
distributiontool.OldLightSharingEdge = 0.5
distributiontool.addTool(pathtool)

from Configurables import MCFTDepositCreator

MCFTDepositCreator().SpillVector = ["/"]
MCFTDepositCreator().SpillTimes = [0.0]
MCFTDepositCreator().addTool(att)
MCFTDepositCreator().addTool(distributiontool)
MCFTDepositCreator().UseAttenuation = True
MCFTDepositCreator().SimulateNoise = False
MCFTDepositCreator().PhotonsPerMeV = 120.

from Configurables import MCFTDigitCreator
tof = 25.4175840541
MCFTDigitCreator().IntegrationOffset = [26 - tof, 28 - tof, 30 - tof]


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

dre = DecodeRawEvent()
dre.DataOnDemand = True

lhcbApp = LHCbApp()
lhcbApp.Simulation = True


files = []
#For position A and 10degrees, the ganga job number is 1. Change this number to access different beam positions
files.extend(glob(cfg.files))
IOHelper('ROOT').inputFiles(files)


# Configuration done, run time!
appMgr = GP.AppMgr()
evt = appMgr.evtsvc()
det = appMgr.detsvc()
hist = appMgr.histSvc()

hist.dump()

resultPath = cfg.resultPath

fileName = (files[0].split("/")[-1]).replace(".sim", "_{0}.root".format(cfg.nickname))

print("Outputfile: " + fileName)

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
      outputTrees[-1].Branch("Uplink_" + str(sipmID) +"_adc_" + str(adcChan+1), sipmValPtr_thisLayer[sipmID][adcChan] ,"Uplink_" + str(sipmID) +"_adc_" + str(adcChan+1) + "/F")
  sipmValPtr.append(sipmValPtr_thisLayer)

nHits = 0
while True:
  appMgr.run(1)

  if not evt['MC/Particles']:
    print "no more particles"
    break

  nHits += len(evt["MC/FT/Hits"])
#  hits = evt["MC/FT/Hits"]
#  for hit in hits:
#    print hit.entry().Z()
#    z_mc_hit[0] = float(hit.entry().Z())
#    y_mc_hit[0] = float(hit.entry().Y())
#    x_mc_hit[0] = float(hit.entry().X())
#    tree_hits.Fill()

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
    if channel.layer() in layers and channel.sipm() in sipmIDs and channel.module() == 4 and channel.quarter() == 3 and channel.station() == 1 :
      sipmValPtr[channel.layer()][channel.sipm()][channel.channel()][0] = digit.photoElectrons()
 
  for t in outputTrees:
    t.Fill()
  resetSipmVals(sipmValPtr)

outputFile.cd()
for t in outputTrees:
  t.Write()
outputFile.Close()

#outputFileHits.cd()
#tree_hits.Write()
#outputFileHits.Close()



print("number of hits found: {0}".format(nHits))
