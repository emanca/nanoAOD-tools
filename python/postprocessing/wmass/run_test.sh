#!/bin/sh

python postproc.py --isMC 1 --passall 0 --dataYear 2016 --maxEvents 1000 -redojec 0
python postproc.py --isMC 1 --passall 0 --dataYear 2016 --maxEvents 1000 -redojec 1
python postproc.py --isMC 0 --passall 0 --dataYear 2016 --maxEvents 10000 -redojec 0
python postproc.py --isMC 0 --passall 0 --dataYear 2016 --maxEvents 10000 -redojec 1
python postproc.py --isMC 1 --passall 0 --dataYear 2017 --maxEvents 1000 -redojec 0
python postproc.py --isMC 1 --passall 0 --dataYear 2017 --maxEvents 1000 -redojec 1
python postproc.py --isMC 0 --passall 0 --dataYear 2017 --maxEvents 10000 -redojec 0
python postproc.py --isMC 0 --passall 0 --dataYear 2017 --maxEvents 10000 -redojec 1
