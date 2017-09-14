#source SetupProject.sh DaVinci v41r3

export SCIFITESTBEAMSIMROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$SCIFITESTBEAMSIMROOT:$SCIFITESTBEAMSIMROOT/job:$SCIFITESTBEAMSIMROOT/python/digitisation

alias optimiseSim='python $SCIFITESTBEAMSIMROOT/python/analysis/optimizeSimParams.py'

alias run_cmake='cmake $SCIFITESTBEAMSIMROOT -DCMAKE_C_COMPILER=/afs/cern.ch/sw/lcg/releases/LCG_84/gcc/4.9.3/x86_64-slc6/bin/gcc -DCMAKE_CXX_COMPILER=/afs/cern.ch/sw/lcg/releases/LCG_84/gcc/4.9.3/x86_64-slc6/bin/g++'

