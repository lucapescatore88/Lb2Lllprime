# the CondDB and DDDB tags for the 5x geometry require Gauss v50 or higher
#

import sys
import inspect
import os
from math import tan, radians

from Gauss.Configuration import *
from Configurables import Gauss, LHCbApp, CondDB
import GaudiKernel.SystemOfUnits as units

local_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(local_dir)

#from common import set_tags

from Configurables import LHCbApp, CondDB

def execute(pos="c", angle=0):
  importOptions("$APPCONFIGOPTS/Gauss/Beam7000GeV-md100-nu7.6-HorExtAngle.py")

  importOptions("$LBPYTHIA8ROOT/options/Pythia8.py")
  importOptions("$APPCONFIGOPTS/Gauss/G4PL_FTFP_BERT_EmNoCuts.py")
  importOptions("$APPCONFIGOPTS/Conditions/Upgrade.py")
  importOptions("$APPCONFIGOPTS/Persistency/Compression-ZLIB-1.py")

  # FTv5
  importOptions('$APPCONFIGOPTS/Gauss/Gauss-Upgrade-Baseline-20150522.py')
  

  outpath = "testbeam_simulation_position_" + pos  + '_at_' + str(angle) + 'deg'

  Gauss().DataType = "Upgrade"

  LHCbApp().DDDBtag = "dddb-20160304"
  LHCbApp().CondDBtag = "sim-20150716-vc-md100"
  CondDB().addLayer(dbFile = "/afs/cern.ch/work/j/jwishahi/public/SciFiDev/DDDB_FT60.db", dbName = "DDDB")
#  CondDB().addLayer(dbFile = "/project/bfys/jtilburg/DDDB_FT60.db", dbName = "DDDB")

  importOptions('$LBPGUNSROOT/options/PGuns.py')
  from Configurables import ParticleGun
  #ParticleGun().EventType = 52210010

  # Set momentum
  from Configurables import MaterialEval
  ParticleGun().addTool(MaterialEval, name="MaterialEval")
  ParticleGun().ParticleGunTool = "MaterialEval"

# test beam position jargon
#position a: 225.5 cm (near mirror) ~5 cm distance from mirror
#position b: 125.5 cm
#position c: 30.5 cm (near sipm) ~ 5 cm distance from sipm
#default y table position: 72.4 cm

  # The target is channelID 35 
  # of SiPM 1 in station 1, layer 0, quarter 3, module 0. The local and global coordinates are:
  # Position A (near mirror)
  #   local  = (-219.75-0.05,-1213.5+50, 0)
  #   global = (484.3, 49.378, 7783.242)
  # Position C (near SiPM)
  #   local  = (-219.75-0.05,-1213.5+50, 0)
  #   global = (484.3, 2376.362, 7791.622)   
  
#  posA = {
#          "x": 484.3,
#          "y": 49.378,
#          "z": 7783.242
#         }  
#  posC = {
#          "x" : 484.3,
#          "y" : 2376.362,
#          "z" : 7791.622
#         }

  posA = {
          "x": 2600.3,
          "y": 62.877,
          "z": 7783.290
         }  
  posC = {
          "x" : 2600.3,
          "y" : 2362.863,
          "z" : 7791.508
         }

  hit_pos = {}  
  if pos == "a":
      hit_pos = posA
  elif pos == "c":
      hit_pos = posC
  else:
      exit()
  
  # origin point
  orig_delta_z = 40. # origin is 4cm towards small z w.r.t. mat center 
  orig_x = hit_pos["x"] + orig_delta_z*tan(radians(angle))
  orig_y = hit_pos["y"]
  orig_z = hit_pos["z"] - orig_delta_z 


  ParticleGun().MaterialEval.Xorig = orig_x
  ParticleGun().MaterialEval.Yorig = orig_y
  ParticleGun().MaterialEval.Zorig = orig_z

  # target point
  target_delta_z = 1500.
  target_x = hit_pos["x"] - target_delta_z*tan(radians(angle))
  target_y = hit_pos["y"]
  target_z = hit_pos["z"] + target_delta_z  #9439. #7870. #9439. #just shoot somewhere far, far away

  ParticleGun().MaterialEval.ZPlane = target_z
  ParticleGun().MaterialEval.Xmin = target_x - 1.7
  ParticleGun().MaterialEval.Xmax = target_x + 1.7
  ParticleGun().MaterialEval.Ymin = target_y - 1.7
  ParticleGun().MaterialEval.Ymax = target_y + 1.7
  
  # particle options 
  ParticleGun().MaterialEval.PdgCode = 211
  ParticleGun().MaterialEval.ModP = 150000 #150GeV
  
  # Set min and max number of particles to produce in an event
  from Configurables import FlatNParticles
  ParticleGun().addTool(FlatNParticles, name="FlatNParticles")
  ParticleGun().NumberOfParticlesTool = "FlatNParticles"
  ParticleGun().FlatNParticles.MinNParticles = 1
  ParticleGun().FlatNParticles.MaxNParticles = 1

  GaussGen = GenInit("GaussGen")
  GaussGen.FirstEventNumber = 1
  GaussGen.RunNumber = 1082

  LHCbApp().EvtMax = 20

  HistogramPersistencySvc().OutputFile = outpath+'-GaussHistos.root'

  OutputStream("GaussTape").Output = "DATAFILE='PFN:%s.sim' TYP='POOL_ROOTTREE' OPT='RECREATE'"%outpath

execute("a",0)

