# Author: Julian Wishahi
# Date: 2016-09-23
# Description: Boole options to profile the digitisation. 
#   Run by calling
#     ./run gaudirun.py --profilerName=valgrindcallgrind --profilerExtraOptions="__instr-atstart=no -v __smc-check=all-non-file __dump-instr=yes __trace-jump=yes" ../SciFiTestbeamAnalysisAndSimulation/python/digitisation/runDigitisationForProfiling.py ../SciFiTestbeamAnalysisAndSimulation/python/inputfiles/PGunSim_20160922_jwishahi/posA_0deg.py
#   from a BooleDev directory (assuming lb-dev etc.)

from Gaudi.Configuration import *
from Configurables import Boole, LHCbApp, DDDBConf, CondDB

LHCbApp().Simulation = True
CondDB().Upgrade = True

Boole().DDDBtag = 'dddb-20160304'
Boole().CondDBtag = 'sim-20150716-vc-md100'

from Configurables import Boole

Boole().DataType   = "Upgrade"

Boole().DetectorDigi = ['VP', 'UT', 'FT', 'Magnet']
Boole().DetectorLink = ['VP', 'UT', 'Tr', 'FT', 'Magnet']
Boole().DetectorMoni = ['VP', 'UT', 'FT',  'Magnet']
Boole().EvtMax = 60

#===============================================================================
# Configure Digitization
#===============================================================================

#-------------------------------------------------------------------------------
# Deposit Creator
#-------------------------------------------------------------------------------
from Configurables import MCFTDepositCreator

MCFTDepositCreator().SpillVector = ["/"]
MCFTDepositCreator().SpillTimes = [0.0]
MCFTDepositCreator().SimulateNoise = False

# AttenuationTool
MCFTDepositCreator().UseAttenuation = True

from Configurables import MCFTAttenuationTool
attenuation_tool = MCFTAttenuationTool()
attenuation_tool.FractionShort = 0.234 # 0.18

# everything unirradiated
attenuation_tool.XMaxIrradiatedZone = 999999999999.#2000
attenuation_tool.YMaxIrradiatedZone = -1.#500


# DepositPathFracInFibreTool
MCFTDepositCreator().UsePathFracInFibre = True
MCFTDepositCreator().DistributeInFibres = True

from Configurables import MCFTDepositPathFracInFibreTool
path_frac_in_fibre_tool = MCFTDepositPathFracInFibreTool()
MCFTDepositCreator().addTool(path_frac_in_fibre_tool)


# DistributionTool
MCFTDepositCreator().UseDistributionTool = True

from Configurables import MCFTDepositDistributionTool

distribution_tool = MCFTDepositDistributionTool()
distribution_tool.WidthOfPhotonDistribution = 0.125

MCFTDepositCreator().addTool(distribution_tool)


#-------------------------------------------------------------------------------
# Digit Creator
#-------------------------------------------------------------------------------

from Configurables import SiPMResponse
SiPMResponse().useNewResponse = 2#Use flat SiPM time response 

from Configurables import MCFTDigitCreator
MCFTDigitCreator().Force2bitADC = 0

tof = 25.4175840541

MCFTDigitCreator().IntegrationOffset = [26 - tof, 28 - tof, 30 - tof]
MCFTDigitCreator().SiPMGain = sipm_gain = 1000.

#===============================================================================
# Profiling
#===============================================================================
def addProfile():
    from Configurables import CallgrindProfile
    p = CallgrindProfile('CallgrindProfile')
    p.StartFromEventN = 5
    p.StopAtEventN = 51
    p.DumpAtEventN = 50
    p.DumpName = 'callgrind.out'
    GaudiSequencer('DigiFTSeq').Members.insert(0, p)
from Gaudi.Configuration import appendPostConfigAction
appendPostConfigAction(addProfile)

