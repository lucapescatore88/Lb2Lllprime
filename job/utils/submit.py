#! /usr/bin/env python
## Author: Luca Pescatore
## Mail: pluca@cern.ch
## Description: script to submit jobs (mostly done for lxplus but for local submissions works anywhere)
## N.B.: Needs an environment variable "JOBDIR" which is the location to put jobs outputs

import os, sys
from string import *
import re
from argparse import ArgumentParser
import subprocess as sub
import random
from datetime import datetime

## Rutines

def getRdmNode() :

    node = 'lxplus{0:04d}'.format(random.randint(1,500))
    out = sub.check_output("ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no %s 'ls $HOME/.tcshrc' 2> /dev/null | wc -l" % node, shell = True)
    return [node, out]

def getAliveNode() :
    
    node, out = getRdmNode()
    while int(out) != 1 :
        node, out = getRdmNode()
    return [node, out]

def launch_interactive(dirname) :

    print "Searching for an alive node..."
    node, out = getAliveNode()
    print "Submitting to ", node
    os.system('ssh -o StrictHostKeyChecking=no %s "cd ' % node + dirname  + '; chmod +x run.sh ; ./run.sh" &')
    print "Start: ", datetime.now()


def launch_job(opts) :

    random.seed()
    exe, execname = None, None
    commands = opts.command.split(' ')

    if(len(commands) < 1) : print "Not enough arguments"
    elif "." in commands[0] : 
        execname = commands[0].replace('./','')
        args = commands[1:]
    elif len(commands) > 1 : 
        execname = commands[1]
        exe      = commands[0]
        args = commands[2:]
    else : sys.exit()
    if(opts.jobname == "") :
        jobname = re.sub(r'\..*',"", execname.replace('./',''))
   
    ## Make the needed folders and copy the executable and everything else needed in them

    subdirname = opts.basedir
    if opts.subdir != "" :
        subdirname += "/"+opts.subdir
    dirname = subdirname+"/"+opts.jobname

    if opts.run > -1 :
        dirname += "_"+str(opts.run)

    if os.path.exists(dirname) and opts.clean :
        os.system("rm -fr " + dirname+"/*")
    os.system("mkdir -p " + dirname)

    if(opts.unique) : copyto = subdirname
    else : copyto = dirname
    
    if not opts.abspath :
        os.system("cp " + execname + " " + copyto )
    #print("cp " + execname + " " + copyto )
    
    for arg in opts.infiles.split() :
        os.system("cp " + arg + " " + copyto )
        if opts.unique :
            os.system("ln -s {f1} {f2}".format(f1=copyto+'/'+arg,f2=dirname+'/'+arg))
    
    ## Create the run.sh file containing the information about how the executable is run

    os.system( "cd " + dirname )
    runfile = open(dirname+"/run.sh","w")
    if opts.shell != "" :                   ### Settings    
        runfile.write(opts.shell + "\n")
    runfile.write( "cd " + dirname + "\n")
    if opts.setup != "" :
        runfile.write(opts.setup + "\n")

    if opts.abspath :
        runfile.write( opts.command )
    else :
        if '/' in execname:
            pos = execname[::-1].find("/")
            execshortname = execname[len(execname)-pos:]
        else : execshortname = execname
        if exe is None :   ### Ensure executable
            runfile.write("chmod 755 " + copyto + "/" +execshortname +'\n')

        if exe is None:
            runfile.write( '{dir} {args}'.format(dir=copyto+"/"+execshortname,args=' '.join(args)) )
        else :
            runfile.write( '{exe} {dir} {args}'.format(exe=exe,dir=copyto+"/"+execshortname,args=' '.join(args)) )

    ### Output
    runfile.write( " >& " + dirname + "/out " )
    runfile.close()
    os.system( "chmod 755 " + dirname + "/run.sh" )

    ## Run executable in local, interactive or batch mode
    
    if(opts.subdir != "") :
        opts.subdir=(re.sub("^.*/","",opts.subdir)+"_")
    
    if opts.local :                           ## Local
        print "Running local"
        os.system( "cd " + dirname )
        os.system( dirname + "/run.sh &" )

    elif "lxplus" in os.getenv("HOSTNAME") :  ## Batch for lxplus
        if opts.interactive :
            launch_interactive(dirname)
        else :
            home = os.getenv('HOME') 
            cmd = "bsub -R 'pool>10000' -o "+home+"/out -e "+home+"/err \
                    -q {queue} {mail} -J {jname} < {dir}/run.sh".format(
                        dir=dirname,queue=opts.queue,
                        mail=opts.mail,jname=opts.subdir+opts.jobname)
            os.system(cmd)

    elif 'lphe' in os.getenv("HOSTNAME") :    ## Batch for EPFL
        cmd = "sbatch run_batch_job.sh"
        fo = open("run_batch_job.sh","w")
        fo.write("#!/bin/bash -fx\n")                       
        fo.write("#SBATCH -o "+dirname+"/out\n")
        fo.write("#SBATCH -e "+dirname+"/err\n")
        fo.write("#SBATCH --mem  5000\n")
        fo.write("#SBATCH -t 12:00:00\n")
        fo.write("#SBATCH -J "+opts.subdir+opts.jobname+"\n")
        fo.write("srun bash "+dirname+"/run.sh\n")
        fo.close()
        os.system(cmd)

    else :
        print "Can run in batch mode only on lxplus or the EPFL cluster. Go there or run with '--local'"


parser = ArgumentParser()
parser.add_argument("-d", default="", dest="subdir", 
     help="Folder of the job, notice that the job is created anyway in a folder called as the jobname, so this is intended to group jobs")
parser.add_argument("-r", default=-1, dest="run", help="Add run number")
parser.add_argument("-D", default=os.getenv('HOME'), dest="basedir",
    help="This option bypasses the JOBDIR environment variable and creates the job's folder in the specified folder")
parser.add_argument("-n", default="", dest="jobname", 
    help="Give a name to the job. The job will be also created in a folder with its name (default is the executable name)")
parser.add_argument("--abspath", action="store_true", help="Uses script without copying it")
parser.add_argument("--bash", dest="shell", default = "", action="store_const", const = "#!/usr/bin/env bash",
    help="Initialize a new bash shell before launching" )
parser.add_argument("--tcsh", dest="shell", default = "", action="store_const", const = "#!/usr/bin/env tcsh",
    help="Initialize a new tcsh shell before launching" )
parser.add_argument("-q", dest="queue", default = "8nh", help="Choose bach queue (default 8nh)" )
parser.add_argument("-s", dest="setup", default = "", help="Add a setup line to the launching script" )
parser.add_argument("--noClean", dest="clean", action="store_false",
    help="If the job folder already exists by default it cleans it up. This option bypasses the cleaning up" )
parser.add_argument("--interactive", dest="interactive", action="store_true",
    help="Submits on lxplus without using the batch system" )
parser.add_argument("--uexe", dest="unique", action="store_true",
    help="Copy the executable only once in the top folder (and not in each job folders)" )
parser.add_argument("--local", dest="local",  action="store_true",
     help="Launch the jobs locally (and not in the batch system)" )
parser.add_argument("-m", dest="mail", default = "", action="store_const", const = "-u "+os.environ["USER"]+"@cern.ch",
     help="When job finished sends a mail to USER@cern.ch" )
parser.add_argument("-in", dest="infiles", default = "", help="Files to copy over")
parser.add_argument("-c","--command", default="", help="Command to launch")


## Main

if __name__ == "__main__" :

    basedir = os.getenv("JOBDIR")
    print basedir
    opts = parser.parse_args()
    if basedir is not None :
        parser.basedir = basedir

    launch_job(opts)


