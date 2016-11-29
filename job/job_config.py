## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script that sets up options to run a digitisation + clusterisation + comparison job

import os
repo = os.environ["SCIFITESTBEAMSIMROOT"]
home = os.environ['HOME']
cmtuser = home+'/cmtuser/'

## FOR USER

sample_to_compare = "TestBeam" ## G4 or TestBeam


## Obligatory paths to be set!

  # Output directory
outdir = "/afs/cern.ch/work/p/pluca/SciFiSim/test"

  # Frameworks locations
gauss = cmtuser+'/GaussDev'
boole = "~/cmtuser/BooleNewGeom"


## Data to compare (don't change if not specifically needed)
testbeam_data  = "/eos/lhcb/wg/SciFi/Simulation/Testbeam/TestbeamData/20160922/"
g4_sim = "/afs/cern.ch/user/s/sescher/public/"
#simfiles = "/afs/cern.ch/work/j/jwishahi/public/SciFiDev/20161012/"
simfiles = "/afs/cern.ch/work/p/pluca/public/SciFi/pguns/sim/"

