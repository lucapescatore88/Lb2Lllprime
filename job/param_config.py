import os

def configure_params(values, path="", digifile = "runDigitisation_template.py") :

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

    templatefile = os.environ["SCIFITESTBEAMSIMROOT"]+"/python/digitisation/"+digifile
    config_template = open(templatefile).read()

    print values
    pyfile = open(path+"params_configuration.py","w")
    pyfile.write(config_template.format(**values))
    pyfile.close()
    
    return path+"params_configuration.py"



