source SetupProject.sh DaVinci v41r3
#source SetupProject.sh root
export SCIFITESTBEAMSIMROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
export PYTHONPATH=$PYTHONPATH:$SCIFITESTBEAMSIMROOT:$SCIFITESTBEAMSIMROOT/job

alias optimiseSim='python $SCIFITESTBEAMSIMROOT/python/analysis/optimizeSimParams.py'
