## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script to run a digitisation + clusterisation + comparison job
## N.B.: Options such as output directory, etc are set via job_options.py

from glob import glob
import subprocess as sb
from argparse import ArgumentParser
import os, sys, re
import job_config as jc
repo = os.getenv("SCIFITESTBEAMSIMROOT")

test = False
send = False
mail = os.getenv('USER')+"@cern.ch"

parser = ArgumentParser()
parser.add_argument("--outdir","-o",default=None)
parser.add_argument("--digiscript","-ds",default = jc.repo+'/python/digitisation/runDigitisationForTestbeam.py')
parser.add_argument("--plot",action='store_true')
parser.add_argument("--doprint",action='store_true')
parser.add_argument("--nodigi",action='store_true')
parser.add_argument("--gen",nargs=2,default=[])
parser.add_argument("--steps",default="Digi,Cluster,Comp")
opts = parser.parse_args()

outdir = opts.outdir
if opts.outdir is None :
    print "Using default outputdir"
    outdir = jc.outdir
digi_script = opts.digiscript

#Scripts locations
sim_script = jc.repo+'/python/simulation/gauss-pgun-job-scifionly.py'
cluster_script = jc.repo+"/build/bin/clusterAnalysis"
compare_script = jc.repo+"/python/analysis/PlotCompare.py" 

#Commands to launch
sim_cmd     = 'mkdir -p {outdir} && cd {outdir} && '+jc.gauss+'/run gaudirun.py {script} &> {outdir}/simlog_{name}'
digi_cmd    = 'mkdir -p {outdir} && cd {outdir} && '+jc.boole+'/run python {script} -f {f} -r {outdir} &> {outdir}/digilog_{name}'
cluster_cmd = 'mkdir -p {outdir} && cd {outdir} && source SetupProject.sh DaVinci v41r3 &> {outdir}/setuplog && {script} -f {f} -s 1 -o {outdir} &> {outdir}/clusterlog_{name} '
compare_cmd = 'mkdir -p {outdir} && cd {outdir} && source SetupProject.sh root &> {outdir}/setuplog && python {script} -d {outdir} '
compare_cmd += '-testbt btTree -g4f {g4f} -g4t statTree ' 
compare_cmd += '-testbf {tbf} -simf {simf}'
#if not opts.plot : compare_cmd += ' --noplot'
compare_cmd += ' &> {outdir}/comparelog'

## Start program

files = []
if len(opts.gen) > 0:

    poss = opts.gen[0].split(',')
    angs = opts.gen[1].split(',')
    for pos in poss :
        for ang in angs :
            
            os.system("sed 's|^execute(.*|execute(\"{pos}\",{ang})|g' -i {script}".format(pos=pos,ang=ang,script=sim_script))
            os.system("cp "+sim_script+" .")
            curcmd = sim_cmd.format(script=sim_script,outdir=outdir+"sim/",name='{}_{}'.format(pos,ang))
            if opts.doprint : print curcmd
             
            #sbtcmd = repo+"/job/utils/submit.py --noscript --interactive -d scifiGen -n {name} ".format(name='{}_{}'.format(pos,ang))
            sbtcmd = "python "+repo+"/job/utils/submit.py --noscript --local -d scifiGen -n {name} ".format(name='{}_{}'.format(pos,ang))
            sbtcmd += "-s 'source "+repo+"/job/setup.sh' "
            sbtcmd += "-in gauss-pgun-job-scifionly.py '"
            sbtcmd += jc.gauss+"/run gaudirun.py gauss-pgun-job-scifionly.py' "
            curcmd = sbtcmd
             
            if not test : sb.call(curcmd,shell=True)

    files = glob(outdir+"/sim/*.sim")
else :
    files = glob(jc.simfiles+"/*.sim")

#print files

if opts.nodigi :
    sys.exit()

## Digitising
if opts.doprint : print "Digitizing ", len(files), " .sim files."

for f in files :

    if not "Digi" in opts.steps :  continue

    name = os.path.basename(f)
    name = os.path.splitext(name)[0]
    curcmd = digi_cmd.format(script=digi_script,f=f,outdir=outdir+"/digitised/",name=name)
    if opts.doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)

## Clusterising
files = glob(outdir+"/digitised/testbeam*.root")
if opts.doprint : print "Clustering ", len(files), " files."

for f in files :

    if not "Cluster" in opts.steps :  continue

    name = os.path.basename(f)
    name = os.path.splitext(name)[0]
    curcmd = cluster_cmd.format(script=cluster_script,f=f,outdir=outdir+"/clusters/",name=name)
    if opts.doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)  

## Compring plots
files = glob(outdir+"/clusters/*.root")
if opts.doprint : print "Comparing ", len(files), " files."

for f in files :

    if "Comp" not in opts.steps : continue

    matches = re.match(".*?_(\d+)deg",f)
    ang = matches.groups()[0]
    pos = "A"
    if "position_c" in f : pos = "C"

    testbeam_file = jc.testbeam_data
    testbeam_file += "pos" + pos
    testbeam_file += "-angle" + ang
    testbeam_file += "_datarun_ntuple_corrected_clusterAnalyis.root"
    
    g4file = "'"+jc.g4_sim+"/statFile_CT_PosA_{ang}degreepi-_-120_20000_5,6_5,5.root'".format(ang=ang)

    curcmd = compare_cmd.format(script=compare_script,simf=f,outdir=outdir+"/comparisons/",g4f=g4file,tbf=testbeam_file)
    #curcmd = compare_cmd.format(script=compare_script,simf=f,outdir=outdir+"/comparisons/",tbf=testbeam_file)

    if opts.doprint : print curcmd
    if not test : sb.call(curcmd,shell=True)

# Pack everything into a tar and send it to "mail"
if not test and send :
    sb.call("tar -czf ~/SciFi_comparisons.tar -C comparisons "+outdir+"/comparisons/*.png",shell=True)
    sb.call('echo "TestBeam comparisons" | mutt -s "TestBeam" -a ~/SciFi_comparisons.tar -- '+mail,shell=True)


