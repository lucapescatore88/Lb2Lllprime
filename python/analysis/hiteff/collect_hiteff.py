from collect_hiteff_functions import *

folders = ['/afs/cern.ch/work/p/pluca/SciFiOptimisation/PhotonsPerMeV_Thrs_15_15_45/1/',
           '/afs/cern.ch/work/p/pluca/SciFiOptimisation/PhotonsPerMeV_Thrs_15_25_45/1/']
labels  = ['Thresholds (1.5,1.5,4.5)','Thresholds (1.5,2.5,4.5)']

makeHitEffPlots(folders, labels)


