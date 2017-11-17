import pickle 

def setupBooleForDigitisation(params,digitype,thresholds) :

    from Configurables import SiPMResponse
    from Configurables import MCFTG4AttenuationTool
    from Configurables import MCFTPhotonTool
    from Configurables import MCFTDistributionChannelTool
    from Configurables import MCFTDistributionFibreTool
    from Configurables import MCFTDepositCreator
    from Configurables import MCFTDigitCreator
    from Configurables import FTClusterCreator
    from Configurables import FTMCHitSpillMerger

    print "Setting Boole:"
    print "Parameters -> ", params
    print "Thresholds -> ", thresholds
    print "Simulation type -> ", digitype

    SiPMResponse().ElectronicsResponse = "flat" # Use flat SiPM time response 
    
    att = MCFTG4AttenuationTool()
    att.MirrorReflectivity = params["MirrorRefl"]
    
    photon_tool = MCFTPhotonTool()
    photon_tool.PhotonsPerMeV = params["PhotonsPerMeV"]
    
    channel_tool = MCFTDistributionChannelTool()
    #print "Usinng PhotonWidth ", params["PhotonWidth"]
    #channel_tool.GaussianSharingWidth = params["PhotonWidth"]
    #channel_tool.LightSharing = "gauss"
    
    fibre_tool = MCFTDistributionFibreTool()
    fibre_tool.CrossTalkProb = params["CrossTalkProb"]
        
    FTMCHitSpillMerger().InputLocation = ["/Event/MC/FT/Hits"]
    FTMCHitSpillMerger().SpillTimes = [0.0]

    from Configurables import MCFTPhotonMonitor
    MCFTDepositCreator().addTool(MCFTG4AttenuationTool, "MCFTG4AttenuationTool")
    MCFTPhotonMonitor().addTool(MCFTG4AttenuationTool, "MCFTG4AttenuationTool")
    
    MCFTDepositCreator().MCFTG4AttenuationTool.IrradiatedFibres = params['irrad']
    MCFTPhotonMonitor().MCFTG4AttenuationTool.IrradiatedFibres = params['irrad']
    
    MCFTDepositCreator().SimulationType = digitype
    MCFTDepositCreator().SimulateNoise = False
    MCFTDepositCreator().addTool(att)
    MCFTDepositCreator().addTool(photon_tool)
    MCFTDepositCreator().addTool(channel_tool)
    MCFTDepositCreator().addTool(fibre_tool)
    
    tof = 25.4175840541
    MCFTDigitCreator().IntegrationOffset = [26 - tof, 28 - tof, 30 - tof]
    MCFTDigitCreator().ADCThreshold1 = thresholds[0]
    MCFTDigitCreator().ADCThreshold2 = thresholds[1]
    MCFTDigitCreator().ADCThreshold3 = thresholds[2]

    FTClusterCreator().WriteFullClusters = True
    FTClusterCreator().ClusterMaxWidth = 99
    FTClusterCreator().LargeClusterSize = 99

#def pickle_params(values, path="") :
#
#    values = get_params(values)
#    print values
#
#    pklfile = open(path+"/params.pkl","w")
#    pickle.dump(values,pklfile)
#    pklfile.close()
#    
#    return path+"/params.pkl"

def get_params(values = {}) :

    if "irrad" not in values : 
        values['irrad'] = False
    if "PhotonWidth" not in values :
        values["PhotonWidth"] = 0.33
    if "CrossTalkProb" not in values :
        #values["CrossTalkProb"] = 0.164 
        values["CrossTalkProb"] = 0.145
    if "PhotonsPerMeV" not in values :
        values["PhotonsPerMeV"] = 6400
        #values["PhotonsPerMeV"] = 8000
    if "MirrorRefl" not in values:
        #values["MirrorRefl"] = 1.0
        values["MirrorRefl"] = 0.75

    return values
