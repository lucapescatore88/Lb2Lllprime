## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script to run a digitisation + clusterisation + comparison job
## N.B.: Options such as output directory, etc are set via job_options.py


from glob import glob
import subprocess as sb
import os
import re
import sys

test = False
generate = False
doprint = False

send = False
mail = "pluca@cern.ch"
plot = False

if len(sys.argv) < 3 : sys.exit()
outdir = sys.argv[1]
digi_script = sys.argv[2]
if len(sys.argv) == 4 :
    if sys.argv[3] == "--plot" :
        plot = True

import job_config as jc
repo = os.environ["SCIFITESTBEAMSIMROOT"]

#Scripts locations
sim_script = jc.repo+'python/simulation/gauss-pgun-job.py'
cluster_script = jc.repo+"/build/bin/clusterAnalysis"
compare_script = jc.repo+"/python/analysis/PlotCompare.py" 

#Commands to launch
sim_cmd = 'cd '+jc.gauss+' && ./run gaudirun.py {script} &> simlog && mkdir -p {outdir} && cp *.sim {outdir} && cd -'
digi_cmd = 'cd '+jc.boole+' && mkdir -p {outdir} && ./run python {script} -f {f} -r {outdir} &> digilog && cd - &> setuplog'
#digi_cmd = 'cd '+jc.boole+' && mkdir -p {outdir} && ./run python {script} -f {f} -r {outdir}  && cd - &> setuplog'
cluster_cmd = 'source SetupProject.sh DaVinci &> setuplog && mkdir -p {outdir} && {script} -f {f} -s 1 -o {outdir} &> clusterlog '
compare_cmd = 'source SetupProject.sh root &> setuplog && mkdir -p {outdir} && python {script} -d {outdir} -g4f {g4f} -testbf {tbf} -simf {simf}'
if not plot : compare_cmd += ' --noplot'
compare_cmd += ' &> comparelog'

## Start program

files = []

if generate:
    curcmd = sim_cmd.format(script=sim_script,outdir=outdir+"sim/")
    if doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)
    files = glob(outdir+"sim/*.sim")
else :
    files = glob(jc.simfiles+"/*.sim")

## Digitising
if doprint : print "Digitizing ", len(files), " .sim files."

for f in files :
    curcmd = digi_cmd.format(script=digi_script,f=f,outdir=outdir+"digitised/")
    if doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)  

## Clusterising
files = glob(outdir+"digitised/*.root")
if doprint : print "Clasterising ", len(files), " files."

for f in files :
    curcmd = cluster_cmd.format(script=cluster_script,f=f,outdir=outdir+"clusters/")
    if doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)  

## Compring plots
files = glob(outdir+"clusters/*.root")
if doprint : print "Comparing ", len(files), " files."

for f in files :

    matches = re.match(".*?_(\d+)deg",f)
    ang = matches.groups()[0]
    pos = "A"
    if "position_c" in f : pos = "C"

    testbeam_file = jc.testbeam_data
    testbeam_file += "pos" + pos
    testbeam_file += "-angle" + ang
    testbeam_file += "_datarun_ntuple_corrected_clusterAnalyis.root"
    
    g4file = "'"+jc.g4_sim+"/ClusterFile({pos}_{ang}).root'".format(pos=pos,ang=ang)

    curcmd = compare_cmd.format(script=compare_script,simf=f,outdir=outdir+"comparisons/",g4f=g4file,tbf=testbeam_file)
    if doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)

# Pack everything into a tar and send it to "mail"
if not test and send:
    sb.call("tar -czf ~/SciFi_comparisons.tar -C comparisons "+outdir+"/comparisons/*.png",shell=True)
    sb.call('echo "TestBeam comparisons" | mutt -s "TestBeam" -a ~/SciFi_comparisons.tar -- '+mail,shell=True)


