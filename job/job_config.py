## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script that sets up options to run a digitisation + clusterisation + comparison job

import os

#host = os.environ["HOSTNAME"] ## Detects if you are on lxplus
host = "lxplus"
repo = os.environ["SCIFITESTBEAMSIMROOT"]

## Add here optional paths

home = os.environ['HOME']
cmtuser = home+'/cmtuser/'

if "lxplus" in host :
    work = os.environ['WORK']
    
## Obligatory paths

sample_to_compare = "TestBeam" ## G4 or TestBeam

outdir = "/panfs/pescator/SciFiSim/optimise/"
if "lxplus" in host :
    outdir = work + "/SciFiSim/optimise/4D_TestBeam"
#     outdir = work + "/SciFiSim/optimise/BFGS/"

#Frameworks locations
gauss = cmtuser+'/GaussDev'
boole = "~/cmtuser/BooleDev_v30r2/"

#Data to compare
if "lxplus" in host :
    testbeam_data  = "/eos/lhcb/wg/SciFi/Simulation/Testbeam/TestbeamData/20160922/"
    g4_sim = "/afs/cern.ch/user/s/sescher/public/"
    simfiles = "/afs/cern.ch/work/j/jwishahi/public/SciFiDev/20161012/"
else :
    testbeam_data  = "/panfs/pescator/SciFiSim/data/TestBeamData/"
    g4_sim = "/panfs/pescator/SciFiSim/data/G4Data/"
    simfiles = "/panfs/pescator/SciFiSim/data/SimFiles/"



