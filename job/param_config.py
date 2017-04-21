import os, pickle

def configure_params(values, path="", digifile = "runDigitisation_template.py") :

    values = get_params(values)

    templatefile = os.environ["SCIFITESTBEAMSIMROOT"]+"/python/digitisation/"+digifile
    config_template = open(templatefile).read()

    print values

    pyfile = open(path+"params_configuration.py","w")
    pyfile.write(config_template.format(**values))
    pyfile.close()
    
    return path+"params_configuration.py"


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