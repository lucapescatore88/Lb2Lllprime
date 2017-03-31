## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script that sets up options to run a digitisation + clusterisation + comparison job

import os
repo = os.getenv("SCIFITESTBEAMSIMROOT")
home = os.getenv('HOME')
user = os.getenv('USER')
cmtuser = home+'/cmtuser/'

## FOR USERS

sample_to_compare = "TestBeam" ## G4 or TestBeam

## Obligatory paths to be set!

  # Output directory
work = '/afs/cern.ch/work/'+user[0]+'/'+user
outdir = work + '/SciFiTest/PhotonPerMeVScan_Improved'

  # Frameworks locations
gauss = cmtuser+'/GaussDev'
#boole = cmtuser+"/BooleDev_v30r1"
boole = work+"/SciFiDevelopment/BOOLE/BOOLE_v31r0/build.x86_64-slc6-gcc49-opt"


## Data to compare (don't change if not specifically needed)
#testbeam_data  = "/eos/lhcb/wg/SciFi/Simulation/Testbeam/TestbeamData/20160922/"    ## 2015
#testbeam_data  = "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Nov2016/renamed/"  ## 2016
testbeam_data  = "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Nov2016/renamed_sescher/"  ## 2016
g4_sim = "/afs/cern.ch/user/s/sescher/public/Simulation/crosstalk/"
simfiles = "/afs/cern.ch/work/p/pluca/public/SciFi/pguns_reduced/sim/"


