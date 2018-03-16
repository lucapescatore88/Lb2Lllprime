#LbLogin.sh -c x86_64-slc6-gcc49-opt 
#source SetupProject.sh root

source setup_path.sh
export SCIFITESTBEAMSIMROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=$PYTHONPATH:$SCIFITESTBEAMSIMROOT:$SCIFITESTBEAMSIMROOT/job:$SCIFITESTBEAMSIMROOT/python/digitisation

alias optimiseSim='python $SCIFITESTBEAMSIMROOT/python/analysis/optimizeSimParams.py'

export GITCONDDBPATH=$SCIFITESTBEAMSIMROOT


