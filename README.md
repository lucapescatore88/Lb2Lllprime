# SciFiTestbeamAndSimulation

To setup 
```
source setup.sh
```

To produce testbeam simulated samples
```
python job/run.py --gen {a,c} {ang1,ang2,...} {Energy in GeV} {Particle}
```

To run a digitisation job with comparisons:
```
python job/run.py --testbeam {2015,2016,2017,2017irrad}
```

To run an optimisation on parameters please look at README\_OPTIMISATION.

## Structure

 - python/simulation: contains scripts to find a channel far from gaps and launch the pgun
 - python/digitisation: contains scripts to run the digitisation
 - python/anaylsis: contains scrpts to compare testbeam in data and run the gridscan optimisation



