import os, sys, re
from argparse import ArgumentParser
import subprocess as sb
import job_config as jc

parser = ArgumentParser()
parser.add_argument("--config",default="sim.cfg")
parser.add_argument("--G4",action="store_true")
opts = parser.parse_args()

compare_cmd = 'source SetupProject.sh root && python $SCIFITESTBEAMSIMROOT/python/analysis/PlotCompare.py -d . '
if opts.G4 : compare_cmd += '-g4f {g4f} -g4t statTree ' 
compare_cmd += '-testbt btTree -testbf {tbf} -simconfig {sim}'


testbeam_file = jc.testbeam_data
g4file = "'"+jc.g4_sim

simfiles =  eval(open(opts.config).read())
for l,f in simfiles.iteritems() :
    print f
    matches = re.match(".*?_(\d+)deg",f)
    ang = matches.groups()[0]
    pos = "A"
    if "position_c" in f : pos = "C"

    testbeam_file += "pos" + pos
    testbeam_file += "-angle" + ang
    testbeam_file += "_datarun_ntuple_corrected_clusterAnalyis.root"
    
    g4file += "/statFile_CT_PosA_{ang}degreepi-_-120_20000_5,6_5,5.root'".format(ang=ang)
    break

cmd = compare_cmd.format(sim=opts.config,g4f=g4file,tbf=testbeam_file)

print cmd
sb.call(cmd,shell=True)


