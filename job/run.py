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

send = False
mail = os.getenv('USER')+"@cern.ch"

parser = ArgumentParser()
parser.add_argument("-o","--outdir",     default=None)
parser.add_argument("-d","--digitype",   default = 'detailed')
parser.add_argument("-tb","--testbeam",  default = '2017')
parser.add_argument("-t","--thresholds", default="'[1.5,2.5,3.5]'")
parser.add_argument("--pacific",     action='store_true')
parser.add_argument("--plot",        action='store_true')
parser.add_argument("--doprint",     action='store_true')
parser.add_argument("--nodigi",      action='store_true')
parser.add_argument("--gen",         nargs=4, default=[])
parser.add_argument("--steps",       default="Digi,Comp")
parser.add_argument("--test",        action='store_true')
parser.add_argument("--params",      type=str, default="")
opts = parser.parse_args()

outdir = opts.outdir
if opts.outdir is None :
    print "Using default outputdir"
    outdir = jc.outdir

simfiles = jc.db[opts.testbeam]['sim']
testbeam_data = jc.db[opts.testbeam]['TB']

#Scripts locations
digi_script = jc.repo+'/python/digitisation/runDigitisationForTestBeam.py'
sim_script = jc.repo+'/python/simulation/gauss-pgun-job-scifionly.py'
compare_script = jc.repo+"/python/analysis/PlotCompare.py"

#Commands to launch

sim_cmd     = 'mkdir -p {outdir} && cd {outdir} && '+jc.gauss+'/run gaudirun.py {script} &> {outdir}/simlog_{name}'

digi_cmd    = 'mkdir -p {outdir} && cd {outdir} && LbLogin.sh -c x86_64-slc6-gcc62-opt && '+jc.boole+'/run python {script} -f {f} -r {outdir} --digitype {digitype} '
if opts.pacific : digi_cmd += '--pacific '
digi_cmd += "  --thresholds " + opts.thresholds
if opts.params != "" : digi_cmd += ' --params {pms} '.format(pms=opts.params)
digi_cmd += ' &> {outdir}/digilog_{name}'

compare_cmd = 'mkdir -p {outdir} && cd {outdir} && lb-run ROOT python {script} -d {outdir} '
compare_cmd += '-testbf {tbf} ' 
compare_cmd += '-simf {simf} '
#if not opts.plot : compare_cmd += ' --noplot'
compare_cmd += ' &>> {outdir}/comparelog_{pos}_{ang} '


## Start program

files = []
if len(opts.gen) > 0:

    poss = opts.gen[0].split(',')
    angs = opts.gen[1].split(',')
    eng  = opts.gen[2]
    part = opts.gen[3]
    for pos in poss :
        for ang in angs :
            
            os.system("sed 's|^execute(.*|execute(\"{pos}\",{ang},{eng},{part})|g' -i {script}".format(
                pos=pos,ang=ang,script=sim_script,eng=eng,part=part,irrad=irrad))
            os.system("cp "+sim_script+" .")
            curcmd = sim_cmd.format(script=sim_script,outdir=outdir+"sim/",name='{}_{}'.format(pos,ang))
            if opts.doprint : print curcmd
             
            sbtcmd = "python "+repo+"/job/utils/submit.py --abspath --local -d sim_{eng}GeV{part} -n {pos}_{ang} ".format(
                    pos=pos,ang=ang,eng=eng,part=part)
            sbtcmd += "-s 'source "+repo+"/setup.sh' "
            sbtcmd += "-in gauss-pgun-job-scifionly.py "
            sbtcmd += " -c '"+jc.gauss+"/run gaudirun.py gauss-pgun-job-scifionly.py' "
            curcmd = sbtcmd
            
            if not opts.test : sb.call(curcmd,shell=True)

    files = glob(outdir+"/*/*.sim")
else :
    files = glob(simfiles)

if opts.nodigi :
    sys.exit()

## Digitising
if opts.doprint : print "Digitizing ", len(files), " .sim files."
#print files
for f in files :

    if "Digi" not in opts.steps : continue

    name = os.path.basename(f)
    name = os.path.splitext(name)[0]
    curcmd = digi_cmd.format(script=digi_script,f=f,outdir=outdir+"/digitised/",name=name,digitype=opts.digitype)
    if 'irrad' in opts.testbeam : curcmd += " --irrad "
    if opts.doprint : print curcmd
    if not opts.test : sb.call(curcmd,shell=True)

## Comparing
files = glob(outdir+"/digitised/testbeam*histos.root")
if opts.doprint : print "Comparing ", len(files), " files."

for f in files :

    if "Comp" not in opts.steps : continue

    matches = re.findall("(\d+)deg",f)
    ang = matches[0]
    pos = "A"
    if "position_c" in f : pos = "C"

    testbeam_file = testbeam_data
    testbeam_file += "pos{pos}-angle{ang}".format(pos=pos,ang=ang)
    testbeam_file += ".root"
    
    curcmd = compare_cmd.format(script=compare_script,simf=f,outdir=outdir+"/comparisons/",
            tbf=testbeam_file,pos=pos,ang=ang)
    if 'irrad' in opts.testbeam : curcmd += " --irrad "

    if opts.doprint : print curcmd
    if not opts.test : sb.call(curcmd,shell=True)



