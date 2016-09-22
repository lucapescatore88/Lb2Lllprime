# SetupProject gauss v46r7p2
#

import sys
import inspect
import os
from math import tan, radians

from Gauss.Configuration import *
#from Gaudi.Configuration import *
from Configurables import Gauss, LHCbApp
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

  # The target is FTChannelID 160, which is the gross cell ID 33 (cell ID 32) 
  # of SiPM 1 in layer 0, module 0, mat 0. The local and global coordinates are:
  # Position A: 
  #   local  = (-219.75,1213.5-50,0)
  #   global = (2689.75, 2376.98, 7864.01) 
  # Position C:
  #   local  = (-219.75,-1213.5+50,0)
  #   global = (2689.75,   50.00, 7855.63)
  # The minimum z of the mat should be 7854.8 mm.

  posA = {
          "x" : 2689.75,
          "y" : 2376.98
         }
  posC = {
          "x": 2689.75,
          "y": 50,
         }  
  
  target_pos = {}  
  if pos == "a":
      target_pos = posA
  elif pos == "c":
      target_pos = posC
  else:
      exit()
  
  # origin point
  Delta_z = 20.
  orig_z = 7854.8-Delta_z # 2 cm towards small z w.r.t. minimum mat z
  orig_x = target_pos["x"] + Delta_z*tan(radians(angle))
  orig_y = target_pos["y"]

  ParticleGun().MaterialEval.Xorig = orig_x
  ParticleGun().MaterialEval.Yorig = orig_y
  ParticleGun().MaterialEval.Zorig = orig_z

  # target point
  target_x = target_pos["x"]
  target_y = target_pos["y"]
  target_z =  9439. #7870. #9439. #just shoot somewhere far, far away

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

  LHCbApp().EvtMax = 2000

  HistogramPersistencySvc().OutputFile = outpath+'-GaussHistos.root'

  OutputStream("GaussTape").Output = "DATAFILE='PFN:%s.sim' TYP='POOL_ROOTTREE' OPT='RECREATE'"%outpath

#execute("a",20)

