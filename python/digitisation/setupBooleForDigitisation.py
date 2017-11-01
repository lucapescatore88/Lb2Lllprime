import pickle 

def setupBooleForDigitisation(params,digitype,thresholds) :

    from Configurables import SiPMResponse
    from Configurables import MCFTAttenuationTool
    from Configurables import MCFTPhotonTool
    from Configurables import MCFTDistributionChannelTool
    from Configurables import MCFTDistributionFibreTool
    from Configurables import MCFTPhotoelectronTool
    from Configurables import MCFTDepositCreator
    from Configurables import MCFTDigitCreator
    from Configurables import FTClusterCreator

    print "Setting Boole:"
    print "Parameters -> ", params
    print "Thresholds -> ", thresholds
    print "Simulation type -> ", digitype

    SiPMResponse().ElectronicsResponse = "flat"#Use flat SiPM time response 
    
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
    
    pe_tool = MCFTPhotoelectronTool()
    
    MCFTDepositCreator().SimulationType = digitype
    MCFTDepositCreator().SpillNames = ["/"]
    MCFTDepositCreator().SpillTimes = [0.0]
    MCFTDepositCreator().SimulateNoise = False
    MCFTDepositCreator().addTool(att)
    MCFTDepositCreator().addTool(photon_tool)
    MCFTDepositCreator().addTool(channel_tool)
    MCFTDepositCreator().addTool(fibre_tool)
    MCFTDepositCreator().addTool(pe_tool)
    
    tof = 25.4175840541
    MCFTDigitCreator().IntegrationOffset = [26 - tof, 28 - tof, 30 - tof]
    MCFTDigitCreator().ADCThreshold1 = thresholds[0]
    MCFTDigitCreator().ADCThreshold2 = thresholds[1]
    MCFTDigitCreator().ADCThreshold3 = thresholds[2]


def pickle_params(values, path="") :

    values = get_params(values)
    print values

    pklfile = open(path+"/params.pkl","w")
    pickle.dump(values,pklfile)
    pklfile.close()
    
    return path+"/params.pkl"

def get_params(values = {}) :

    if "PhotonWidth" not in values :
        values["PhotonWidth"] = 0.33
    #if "ShortAttLgh" not in values :
    #    values["ShortAttLgh"] = 455.6
    #if "LongAttLgh" not in values :
    #    values["LongAttLgh"] = 4716
    #if "ShortFraction" not in values :
    #    values["ShortFraction"] = 0.2506 
    if "CrossTalkProb" not in values :
        values["CrossTalkProb"] = 0.22 
    if "PhotonsPerMeV" not in values :
        values["PhotonsPerMeV"] = 127.
    if "MirrorRefl" not in values:
        values["MirrorRefl"] = 1.0

    return values
