To run the optimisation or just a scan in a variable

- source setup.sh
- Change job/job_config.py to give the location of your Boole (and Gauss if you need to geenrate) 
- Run: optimiseSim --digi detailed --local "[Var('PhotonsPerMeV',10,200,20)]"
    1. "--digi" lets you choose detailed/effective/improved
    2. "--local" runs locally, otherwise goes in batch mode
    3. The final argument will produce 20 jobs each one with PhotonsPerMeV between 10 and 200. 
        You can specify more than 1 variable and the scan will be done in n-D
        Available: PhotonsPerMeV, ShortAttLgh, LongAttLgh, ShortFraction, PhotonWidth, CrossTalkProb

Enjoy!


