## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: Script to launch the digitisation to compaisons chain many times
## performing a grid search to find best parameters
## N.B.: Requires setting up the enviroment by source job/setup.sh
## N.B.: Options such as output directory, data to compare, etc are set via job/job_options.py

import os, time, shutil, sys
import subprocess as sb
from glob import glob
import ROOT, math
from array import array

repo = os.environ["SCIFITESTBEAMSIMROOT"]
if repo is None :
    print "Please setup the environment befire running!"
    sys.exit()

from param_config import configure_params
import job_config as jc
from job.utils.value import Value
from job.utils.wheel import Wheel
from job.utils.math_functions import *
from job.utils.submit import launch_interactive

wheel = Wheel()

class OptimizeParams :

    variables = {}
    grid = {}
    chi2_distr = []
    curiter = 0
    ntotpoints = 1
    launch_modes = ["local","interactive","batch"]

    def __init__(self,outdir = os.environ["PWD"], niter = 2, mode = "launch", launch_mode = "local") :
        self.outdir = outdir
        self.niterations = niter
        self.mode = mode
        self.launch_mode = launch_mode

    def set_launch_mode(self,mode) :
        if mode in self.launch_modes :
            self.launch_mode = mode
        else : 
            print "Attention: mode '"+mode+"' unknown. Possible modes are: ", self.launch_modes

    def add_variable(self,name,mini,maxi,nbins=9,limits = None) :
        
        if nbins%2==0 :
            print "The number of bins must be odd! Adding one bin."
            nbins += 1
        self.variables[name] = { "range" : [mini,maxi], "scanrange": [mini,maxi], "nbins" : nbins  }
        if limits : self.variables[name]["limit"] = limits
        self.ntotpoints *= (nbins+1)

    def define_grid(self, bestpoints) :

        if bestpoints is not None :
            for b,val in bestpoints.iteritems() :
                v = self.variables[b]
                step = mystep = (v["scanrange"][1] - v["scanrange"][0]) / float(v["nbins"])
                v["scanrange"][0] = val - step * (1 - 1. / v["nbins"])
                v["scanrange"][1] = val + step * (1 - 1. / v["nbins"])
                if "limit" not in v : continue
                if v["scanrange"][0] < v["limit"][0] : v["scanrange"][0] = v["limit"][0]
                if v["scanrange"][1] > v["limit"][1] : v["scanrange"][1] = v["limit"][1]

        for vn,v in self.variables.iteritems() :
            self.grid[vn] = []
            nbins = v["nbins"]
            mymin = v["scanrange"][0]
            mymax = v["scanrange"][1]
            mystep = (mymax - mymin) / float(nbins)
            v["step"] = mystep
            for i in range(nbins+1) :
                self.grid[vn].append( mymin + mystep * i  )

        ranges = [ self.grid[vn] for vn in self.vorder ]
        self.grid["grid"] = get_combinations(ranges)
        
    def launch(self,outdir,config_file = None):

        host = os.getenv("HOSTNAME")
        is_lxplus = ( "lxplus" in host )
        if not is_lxplus and "lphe" not in host :
            print "This script is made to run only on lxplus or EPFL cluster. Go there!"
        if not is_lxplus and self.launch_mode == "interactive" :
            print "Interactive mode is only possible on lxplus. Switching to batch."
            self.launch_mode = "batch"
         
        ## Command for local serial running
        if self.launch_mode == "local" :
            print "python "+repo+"/job/run.py --digiscript {cfile} {odir}".format(odir=outdir,cfile=config_file)
            sb.call("python "+repo+"/job/run.py --digiscript {cfile} {odir}".format(odir=outdir,cfile=config_file),shell=True)
            
        elif is_lxplus :
        
            ## Command for prallel running on lxplus bach system
            if self.launch_mode == "batch" :
                batch_cmd = "bsub -R 'pool>30000' -o {dir}/out -e {dir}/err -q {queue} -J {jname} < {dir}/run.sh"
                batch_cmd = batch_cmd.format(dir=outdir,queue="1nd",jname=outdir)
                sb.call(batch_cmd,shell=True)

            ## Command for parallel running on lxplus in interactive mode
            elif self.launch_mode == "interactive" :
                launch_interactive(outdir)

        else :
            print "You are not on Lxplus, you can't run in batch mode"

    def send_jobs(self) :

        if self.mode == "relaunch" and self.launch_mode != "local":
            dirs = glob(self.outdir+"/*/*")
            for d in dirs : 
                if len(glob(d+"/comparisons/chi*.txt")) == 6 : continue
                print "Resubmiting:", d
                self.launch(d)
            return

        for ip,p in enumerate(self.grid["grid"]) :
            outdir = self.outdir+"/"+str(self.curiter)+"/options"
            vdict = {}
            for i,d in enumerate(p) :
                vname = self.vorder[i]
                outdir += "_" + vname + "_" + str(d)
                vdict[vname] = d
            
            if not os.path.exists(outdir) : os.mkdir(outdir)
            config_file = configure_params(vdict,outdir+"/")
            
            hasoutput = int(len(glob(outdir+"/comparisons/chi*.txt")) == 6)
            if hasoutput and self.mode!="force"  : continue
            
            print "\n******************\n Running analysis for point ({0}/{1}): ".format(ip+1,self.ntotpoints)
            print vdict

            frun = open(outdir + "/run.sh","w")
            frun.write("source "+repo+"/job/setup.sh &> setuplog\n")
            frun.write("python "+repo+"/job/run.py --digiscript {cfile} {odir}".format(odir=outdir,cfile=config_file))
            frun.close()

            self.launch(outdir,config_file)
            
    def find_best(self) :

        chi2      = [ x[1] for x in self.chi2_distr ]
        minchi2   = min(chi2)
        minchi2pt = self.chi2_distr[ chi2.index(minchi2) ][0]
        print "Best chi2 --> ", minchi2, "at", 
        
        bestwitherr = []
        for iv,v in enumerate(self.vorder) :
            bestwitherr.append( Value( minchi2pt[iv], self.variables[v]["step"]) )
        print tuple(bestwitherr)

        bestpt = {}
        for vn,v in self.variables.iteritems() :
            bestpt[vn] = minchi2pt[ self.variables[vn]["key"] ]
            
        return bestpt 
     
    def collect_data(self) :
       
        while True :
            time.sleep(2)
            files = glob(self.outdir+"/"+str(self.curiter)+"/*/comparisons/chi2*.txt")
            nfiles = math.trunc( len(files) / 6.)
            w = wheel.increment()
            msg = "\r  "+w+"   Iteration {0}/{1}, jobs finished {2}/{3}"
            sys.stdout.write(msg.format(self.curiter,self.niterations,nfiles,self.ntotpoints))
            sys.stdout.flush()
            if nfiles > 0 and nfiles % int( self.ntotpoints ) == 0 : break

        print "\nIteration {0}/{1}. Production finished. Calculating chi2.......".format(self.curiter,self.niterations)
        for d in glob(self.outdir+"/"+str(self.curiter)+"/*") :
            values = []
            pos = d.find("options_")
            clean_name = d[pos+8:]
            vals = clean_name.split("_")
            for iv in range(len(vals)/2) :
                values.append(float(vals[2*iv+1]))
            
            chi2 = 0
            chi2files = glob(d+"/comparisons/chi2*.txt")
            if len(chi2files) == 0: print d
            for f in chi2files :
                
                if jc.sample_to_compare == "G4" :
                    line = open(f).readlines()[0]  ## G4-Boole chi2
                else :
                    line = open(f).readlines()[1]   ## Testbeam-Boole chi2
                elements = line.split()
                chi2 += float(elements[0])
            
            chi2 /= len(chi2files)
            self.chi2_distr.append( (tuple(values), chi2) )

    def optimize(self) :

        if os.path.exists(self.outdir) :
            dirs = glob(self.outdir+"/*")
            if len(dirs) > 0 :
                choice = raw_input("Chosen output dir is not empty. Want to clean it up before proceeding? [y/n]\n")
                if choice == 'y' :
                    shutil.rmtree(self.outdir)
                    os.mkdir(self.outdir)
        else :
            os.mkdir(self.outdir)

        self.vorder = []
        i = 0
        for v in self.variables :
            self.vorder.append(v)
            self.variables[v]["key"] = i
            i+=1

        bestpoints = None
        for i in range(self.niterations) :
            self.curiter += 1
            if not os.path.exists(self.outdir+"/"+str(self.curiter)) : 
                os.mkdir(self.outdir+"/"+str(self.curiter))
            self.define_grid(bestpoints)
            self.send_jobs()
            self.collect_data()
            bestpoints = self.find_best()
        
        print "\n\n** Optimization done! **\nBest point: "
        print bestpoints
        self.make_plot()

    def make_plot(self) :

        c = ROOT.TCanvas()
        rfile = ROOT.TFile("optimization.root","recreate")
        for i,v in enumerate(self.vorder) :
            chi21D = slice_best(i,self.chi2_distr)
            sorted_list = sorted( chi21D, key=lambda x:x[0][i] )
            x = array('f',[ e[0][i] for e in sorted_list ])
            y = array('f',[ e[1] for e in sorted_list ])
            hist = ROOT.TGraph(len(x),x,y)
            hist.Draw("APL")
            hist.GetXaxis().SetTitle(v)
            hist.GetYaxis().SetTitle("#chi^{2}")
            hist.SetTitle("")
            c.Print("chi2_vs_"+v+".pdf")
            hist.Write("chi2_vs_"+v)
        rfile.Close()

def slice_best(i,mylist) :

    minchi2 = min( [ x[1] for x in mylist ] )
    bestpt = ()
    for x in mylist :
        if x[1] == minchi2 :
            bestpt = x[0]

    mybest = {}
    for vi in range(len(bestpt)) :
        if vi == i : continue
        mybest[vi] = bestpt[vi]

    best_list = []
    for e in mylist :
        keep = True
        for vi in range(len(bestpt)) :
            if vi == i : continue
            if e[0][vi] != mybest[vi] :
                keep = False
                break
        if keep : best_list.append(e)

    return best_list

if __name__ == '__main__': 

    print "Optimizing..."

    optimizer = OptimizeParams(jc.outdir,niter = 1)
    optimizer.set_launch_mode("interactive")
    #optimizer.set_launch_mode("local")
    
    #optimizer.add_variable("PhotonWidth",0.,0.7,3, limits=[0.,2.])
    
    #optimizer.add_variable("ShortAttLgh",100,1000,3, limits=[0.,500.])
    #optimizer.add_variable("LongAttLgh",4000,5500,3, limits=[3000.,6000.])
    #optimizer.add_variable("ShortFraction",0.,0.7,3, limits=[0.,1.])
    
    optimizer.add_variable("CrossTalkProb",0.,0.7,3, limits=[0.,1.])

    optimizer.optimize()


