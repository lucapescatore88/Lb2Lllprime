# To run this script:
# lb-run LHCb bash
# python -i findChannel.py
#
from Gaudi.Configuration import *
from Configurables import LHCbApp, CondDB
from GaudiPython.Bindings import gbl, AppMgr
import GaudiPython
import math
import ROOT

LHCbApp().DataType   = "Upgrade"
LHCbApp().Simulation = True
CondDB().Upgrade = True

LHCbApp().DDDBtag = "dddb-20160304"
LHCbApp().CondDBtag = "sim-20150716-vc-md100"

## New numbering scheme. Remove when FT60 is in nominal CondDB.
#CondDB().addLayer(dbFile = "/eos/lhcb/wg/SciFi/Custom_Geoms_Upgrade/databases/DDDB_FT60.db", dbName = "DDDB")
CondDB().addLayer(dbFile = "/afs/cern.ch/work/j/jwishahi/public/SciFiDev/databases/DDDB_FT60_noEndPlug.db", dbName = "DDDB")

appMgr = AppMgr(outputlevel=4)
det = appMgr.detSvc()
FT = det['/dd/Structure/LHCb/AfterMagnetRegion/T/FT']

# TestBeam Position A in local coordinates (near mirror)
point_A = gbl.Gaudi.XYZPoint(-219.75-0.05,-1200.0+50,0)
# TestBeam Position C in lcoal coordinates (near SiPMs)
point_C = gbl.Gaudi.XYZPoint(-219.75-0.05,+1200.0-50,0)

# Choose station, layer, quarter, module, mat
station_id = 1  # first station
layer_id = 0    # first layer
quarter_id = 3  # upper left quarter
module_id = 4   # outer most module
mat_id = 0

#fibremodules = [fibremodule for fibremodule in FT.fibremodules() if (fibremodule.layer() is layer_id and fibremodule.quarter() is quarter_id and fibremodule.module() is module_id)]
#
#if len(fibremodules) != 1:
#    print "Found more that one fibremodule passing the requirements. Please check!"
#    exit()
#
#fibremodule = fibremodules[0]
#print fibremodule

channel_in_target_module = gbl.LHCb.FTChannelID(station_id, layer_id, quarter_id, module_id, 0, 0)
fibremodule = FT.findModule(channel_in_target_module)

points = {
           "A": point_A,
           "C": point_C
         }

for pos_name, pos_point in points.iteritems():
    print("===============================================================================")
    print("Getting info for testbeam position "+pos_name+".")
    point = pos_point
    global_point = fibremodule.geometry().toGlobal(point)
    
    print "In the local frame the position is  ", point.x(), point.y(), point.z()
    print "In the global frame the position is ", global_point.x(), global_point.y(), global_point.z()
    
    #mat_thickness = fibremodule.fibremoduleMaxZ() - fibremodule.fibremoduleMinZ()
    mat_thickness = 0.130
    angle = 0 #10/180*3.14
    
    hit = gbl.LHCb.MCHit()
    hit_point_local = gbl.Gaudi.XYZPoint(point.x()-math.tan(angle)*mat_thickness/2.,point.y(),point.z()-(mat_thickness/2.)) 
    hit_point_global = fibremodule.geometry().toGlobal(hit_point_local)
    hit.setEntry(hit_point_global)
    
    disp = gbl.Gaudi.XYZVector(math.sin(angle),0.,mat_thickness)
    hit.setDisplacement(disp)
    
    fraction = ROOT.Double(0.0) # needed fro pass-by-ref of doubles
    channel = fibremodule.calculateChannelAndFrac(point.x(), fraction) 

    print "Hit position = ",hit.entry().x(), hit.entry().y(),hit.entry().z()
    print "Hit channel:"
    print " station =", channel.station(),
    print " layer =", channel.layer(),
    print " quarter =", channel.quarter(),    
    print " module =",channel.module(),
    #print " mat =",channel.mat(),
    #print " sipm_id =",channel.sipmId(),
    print " sipm_id =",channel.sipm(),
    print " channel_id =",channel.channel()
    print "   fractional position w.r.t. center of channel=",fraction



   
