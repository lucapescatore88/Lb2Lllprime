## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script that sets up options to run a digitisation + clusterisation + comparison job

import os
repo = os.getenv("SCIFITESTBEAMSIMROOT")
home = os.getenv('HOME')
user = os.getenv('USER')
cmtuser = home+'/cmtuser/'

## FOR USERS

## Obligatory paths to be set!

  # Output directory
work = '/afs/cern.ch/work/'+user[0]+'/'+user
#outdir = work + '/SciFi/Optimisation/CrossTalkProb_PhotonsPerMeV_6500_MirrorRefl_0.75_TB2017'
#outdir = work + '/SciFi/Optimisation/2D_PhotonsPerMeV_CrossTalkProb_MirrorRefl_0.75_TB2017_irrad_3'
outdir = work + '/SciFi/Optimisation/test'

  # Frameworks locations
gauss = cmtuser+'/GaussDev'
boole = "/afs/cern.ch/work/p/pluca/SciFi/Dev/BOOLE/BOOLE_v31r3/build.x86_64-slc6-gcc62-opt"

## Data to compare (don't change if not specifically needed)
db = { '2015' : 
        { 'TB'  : "/eos/lhcb/wg/SciFi/Simulation/Testbeam/TestbeamData/20160922/",
          'sim' : "/afs/cern.ch/work/p/pluca/public/SciFi/pguns/sim_150GeVPions/*/*.sim" },
        '2016' : 
        { 'TB'  : "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Nov2016/renamed_sescher/",
          'sim' : "/afs/cern.ch/work/p/pluca/public/SciFi/pguns/sim_180GeVPions/*/*.sim" },
        '2017' : 
        { 'TB'  : "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Sep2017/",
          'sim' : "/afs/cern.ch/work/p/pluca/public/SciFi/pguns/sim_5GeVElectrons/*/*.sim" },
        '2017irrad' : 
        { 'TB'  : "/afs/cern.ch/work/p/pluca/public/SciFi/Testbeam_Sep2017/",
          'sim' : "/afs/cern.ch/work/p/pluca/public/SciFi/pguns/sim_5GeVElectrons_Irrad/*/*.sim" }
        }


#g4_sim = "/afs/cern.ch/user/s/sescher/public/Simulation/crosstalk/"

