# To run this script:
# lb-run LHCb bash
# python -i findChannel.py
#
from Gaudi.Configuration import *
from Configurables import LHCbApp, CondDB
from GaudiPython.Bindings import gbl, AppMgr
import GaudiPython
import math

LHCbApp().DataType   = "Upgrade"
LHCbApp().Simulation = True
CondDB().Upgrade = True

LHCbApp().DDDBtag = "dddb-20160304"
LHCbApp().CondDBtag = "sim-20150716-vc-md100"

appMgr = AppMgr(outputlevel=4)
det = appMgr.detSvc()
FT = det['/dd/Structure/LHCb/AfterMagnetRegion/T/FT']

# TestBeam Position A in local coordinates (near mirror)
point_A = gbl.Gaudi.XYZPoint(-219.75,-1213.5+50,0)
# TestBeam Position C in lcoal coordinates (near SiPMs)
point_C = gbl.Gaudi.XYZPoint(-219.75,+1213.5-50,0)

# Choose layer, quarter, module, mat
layer_id = 0
quarter_id = 3
module_id = 0
mat_id = 0

fibremats = [fibremat for fibremat in FT.fibremats() if (fibremat.layer() is layer_id and fibremat.quarter() is quarter_id and fibremat.module() is module_id)]

if len(fibremats) != 1:
    print "Found more that one fibremat passing the requirements. Please check!"
    exit()

fibremat = fibremats[0]
print fibremat

points = {
           "A": point_A,
           "C": point_C
         }

for pos_name, pos_point in points.iteritems():
    print("===============================================================================")
    print("Getting info for testbeam position "+pos_name+".")
    point = pos_point
    global_point = fibremat.geometry().toGlobal(point)
    
    print "In the local frame the position is  ", point.x(), point.y(), point.z()
    print "In the global frame the position is ", global_point.x(), global_point.y(), global_point.z()
    
    mat_thickness = fibremat.fibreMatMaxZ() - fibremat.fibreMatMinZ()
    angle = 0 #10/180*3.14
    
    hit = gbl.LHCb.MCHit()
    hit_point_local = gbl.Gaudi.XYZPoint(point.x()-math.tan(angle)*mat_thickness/2.,point.y(),point.z()-(mat_thickness/2.)) 
    hit_point_global = fibremat.geometry().toGlobal(hit_point_local)
    hit.setEntry(hit_point_global)
    
    disp = gbl.Gaudi.XYZVector(math.sin(angle),0.,mat_thickness)
    hit.setDisplacement(disp)
    
    FTPair = gbl.std.pair(gbl.LHCb.FTChannelID,'double')
    ftpair = FTPair()
    
    fibremat.calculateMeanChannel(hit,ftpair)
    channel = ftpair.first
    fraction = ftpair.second

    print "Hit position = ",hit.entry().x(), hit.entry().y(),hit.entry().z()
    print "Hit channel: layer=",channel.layer(),
    print " quarter =", channel.quarter(),    
    print " module =",channel.module(),
    print " mat =",channel.mat(),
    print " sipm_id =",channel.sipmId(),
    print " cell_id =",channel.sipmCell(),
    print " channel_id =",channel.channelID()
    print "   fractional position w.r.t. center of channel=",fraction



   
