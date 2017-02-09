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
outdir = '/afs/cern.ch/work/'+user[0]+'/'+user
#outdir += '/SciFi_Optimisation/CrossTalk_8Fibers_Fix_PhotonWidth0.25'
outdir += '/public/SciFi/digi_PhotonPerMeV_forDisplay'

  # Frameworks locations
gauss = cmtuser+'/GaussDev'
boole = cmtuser+"/BooleDev_v30r1"


## Data to compare (don't change if not specifically needed)
#testbeam_data  = "/eos/lhcb/wg/SciFi/Simulation/Testbeam/TestbeamData/20160922/"    ## 2015
#testbeam_data  = "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Nov2016/renamed/"  ## 2016
testbeam_data  = "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Nov2016/renamed_sescher/"  ## 2016
g4_sim = "/afs/cern.ch/user/s/sescher/public/Simulation/crosstalk/"
simfiles = "/afs/cern.ch/work/p/pluca/public/SciFi/pguns_reduced/sim/"


