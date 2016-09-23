from Configurables import LHCbApp, CondDB, Boole

LHCbApp().Simulation = True
CondDB().Upgrade = True
Boole().DDDBtag = 'dddb-20160304'
Boole().CondDBtag = 'sim-20150716-vc-md100'
