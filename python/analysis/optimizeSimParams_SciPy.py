## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: Script to launch the digitisation to compaisons chain many times
## performing a grid search to find best parameters. Uses scipy.optimize.
## N.B.: Requires setting up the enviroment by source job/setup.sh

## This scripts is obsolete and not working any more. It is just kept for reference.

from param_config import configure_params
import os, time, shutil, sys
import subprocess as sb
import sys
from glob import glob
from scipy import optimize as opt
sys.path.append(os.environ["SCIFITESTBEAMSIMROOT"]+'/job/')
import job_config as jc

## Define scalar function to be minimised
def get_SciFiSim_chi2(pars) :
 
    print "\n******************\n Running analysis for point "
    print pars
  
    ## Setup the job 
    outdir = jc.outdir+"/opts"
    for i,p in enumerate(pars) :
        outdir += "_" +str(p)
    
    vdict = {
                "PhotonWidth"   : pars[0],
                "ShortAttLgh"   : pars[1],
                "LongAttLgh"    : pars[2],
                "ShortFraction" : pars[3]
            }

    if not os.path.exists(outdir) : os.mkdir(outdir)
    config_file = configure_params(vdict,outdir+"/")
    
    frun = open(outdir + "/run.sh","w")
    frun.write("source "+jc.repo+"/job/setup.sh &> setuplog\n")
    frun.write("python "+jc.repo+"/job/run.py " + outdir + "/ " + config_file)
    frun.close()

    ## Run the job
    launch(outdir,config_file)

    ## Get the chi2 out of the output
    chi2 = 0
    chi2files = glob(outdir+"/comparisons/chi2*.txt")
    for f in chi2files :
        line = open(f).readlines()[0]
        elements = line.split()
        chi2 += float(elements[0])
            
    chi2 /= len(chi2files)
    print "Chi2 -> ", chi2
    return chi2

def launch(outdir,config_file):

    print "python "+jc.repo+"/job/run.py " + outdir + "/ " + config_file
    sb.call("python "+jc.repo+"/job/run.py " + outdir + "/ " + config_file,shell=True)

### Start program
    
if os.path.exists(jc.outdir) :
    dirs = glob(jc.outdir+"/*")
    if len(dirs) > 0 :
        choice = raw_input("Chosen output dir is not empty. Want to clean it up before proceeding? [y/n]\n")
        if choice == 'y' :
            shutil.rmtree(jc.outdir)
            os.mkdir(jc.outdir)
else :
    os.mkdir(jc.outdir)

pars0 = [0.23,200,4800,0.27]
res = opt.minimize(get_SciFiSim_chi2,pars0,method='BFGS')
print res



