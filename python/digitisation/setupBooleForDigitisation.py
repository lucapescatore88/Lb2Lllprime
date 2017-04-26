from Configurables import SiPMResponse
from Configurables import MCFTAttenuationTool
from Configurables import MCFTPhotonTool
from Configurables import MCFTDistributionChannelTool
from Configurables import MCFTDistributionFibreTool
from Configurables import MCFTPhotoelectronTool
from Configurables import MCFTDepositCreator
from Configurables import MCFTDigitCreator
from Configurables import FTClusterCreator

def setupBooleForDigitisation(params,digitype,pacific) :

    print "Setting Boole:"
    print "Parameters -> ", params
    print "PACIFIC digits -> ", pacific
    print "Simulation type -> ", digitype

    SiPMResponse().ElectronicsResponse = "flat"#Use flat SiPM time response 
    
    att = MCFTAttenuationTool()
    att.ShortAttenuationLength = params["ShortAttLgh"]
    att.LongAttenuationLength = params["LongAttLgh"]
    att.FractionShort = params["ShortFraction"]
    
    # Make sure I always hit unirradiated zone
    att.XMaxIrradiatedZone = 999999999999.#2000
    att.YMaxIrradiatedZone = -1.#500
    
    photon_tool = MCFTPhotonTool()
    photon_tool.PhotonsPerMeV = params["PhotonsPerMeV"]
    
    channel_tool = MCFTDistributionChannelTool()
    channel_tool.GaussianSharingWidth = params["PhotonWidth"]
    #channel_tool.LightSharing = "old"
    
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

    #if pacific : 
    #    print "Activating PACIFIC"
    #    FTClusterCreator().StorePECharge = False
    #    FTClusterCreator().UsePENotADC = False


def get_params(values = {}) :

    if "PhotonWidth" not in values :
        values["PhotonWidth"] = 0.33
    if "ShortAttLgh" not in values :
        values["ShortAttLgh"] = 455.6
    if "LongAttLgh" not in values :
        values["LongAttLgh"] = 4716
    if "ShortFraction" not in values :
        values["ShortFraction"] = 0.2506 
    if "CrossTalkProb" not in values :
        values["CrossTalkProb"] = 0.22 
    if "PhotonsPerMeV" not in values :
        values["PhotonsPerMeV"] = 126.

    return values