
def configure_params(values,path="") :

    if "PhotonWidth" not in values :
        values["PhotonWidth"] = 0.3457 
    if "ShortAttLgh" not in values :
        values["ShortAttLgh"] = 455.6
    if "LongAttLgh" not in values :
        values["LongAttLgh"] = 4716
    if "ShortFraction" not in values :
        values["ShortFraction"] = 0.2506 
    if "CrossTalkProb" not in values :
        values["CrossTalkProb"] = 0.04 


    templatefile = os.environ["SCIFITESTBEAMSIMROOT"]+"/python/digitisation/runDigitisation_template.py"
    config_template = open(templatefile).read()

    pyfile = open(path+"params_configuration.py","w")
    pyfile.write(config_template.format(**values))
    pyfile.close()
    
    return path+"params_configuration.py"



