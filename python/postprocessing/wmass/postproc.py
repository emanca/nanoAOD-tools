#!/usr/bin/env python
import os, sys
import ROOT
import argparse
import subprocess

ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor

from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.muonScaleResProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.lepSFProducer import *

from PhysicsTools.NanoAODTools.postprocessing.wmass.preSelection import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.additionalVariables import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.lepSelection import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.CSVariables import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.genWproducer import *
from PhysicsTools.NanoAODTools.postprocessing.wmass.recoZproducer import *

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

parser = argparse.ArgumentParser("")
parser.add_argument('-jobNum',    '--jobNum',   type=int, default=1,      help="")
parser.add_argument('-crab',      '--crab',     type=int, default=0,      help="")
parser.add_argument('-passall',   '--passall',  type=int, default=0,      help="")
parser.add_argument('-isMC',      '--isMC',     type=int, default=1,      help="")
parser.add_argument('-maxEvents', '--maxEvents',type=int, default=-1,	  help="")
parser.add_argument('-dataYear',  '--dataYear', type=int, default=2016,   help="")
parser.add_argument('-jesUncert', '--jesUncert',type=str, default="Total",help="")
parser.add_argument('-redojec',   '--redojec',  type=int, default=0,      help="")
parser.add_argument('-runPeriod', '--runPeriod',type=str, default="B",    help="")
args = parser.parse_args()
isMC      = args.isMC
crab      = args.crab
passall   = args.passall
dataYear  = args.dataYear
maxEvents = args.maxEvents
runPeriod = args.runPeriod
redojec   = args.redojec
jesUncert = args.jesUncert

print "isMC =", bcolors.OKGREEN, isMC, bcolors.ENDC, \
    "crab =", bcolors.OKGREEN, crab, bcolors.ENDC, \
    "passall =", bcolors.OKGREEN, passall,  bcolors.ENDC, \
    "dataYear =",  bcolors.OKGREEN,  dataYear,  bcolors.ENDC, \
    "maxEvents =", bcolors.OKGREEN, maxEvents, bcolors.ENDC 

# run with crab
if crab:
    from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis

################################################ JEC
# JEC for MET
jecTagsMC = {'2016' : 'Summer16_07Aug2017_V11_MC', '2017' : 'Fall17_17Nov2017_V32_MC'}

jecTagsDATA = { '2016B' : 'Summer16_07Aug2017BCD_V11_DATA', 
                '2016C' : 'Summer16_07Aug2017BCD_V11_DATA', 
                '2016D' : 'Summer16_07Aug2017BCD_V11_DATA', 
                '2016E' : 'Summer16_07Aug2017EF_V11_DATA', 
                '2016F' : 'Summer16_07Aug2017EF_V11_DATA', 
                '2016G' : 'Summer16_07Aug2017GH_V11_DATA', 
                '2016H' : 'Summer16_07Aug2017GH_V11_DATA', 
                '2016H' : 'Summer16_07Aug2017GH_V11_DATA', 
                '2017B' : 'Fall17_17Nov2017B_V32_DATA', 
                '2017C' : 'Fall17_17Nov2017C_V32_DATA', 
                '2017D' : 'Fall17_17Nov2017DE_V32_DATA', 
                '2017E' : 'Fall17_17Nov2017DE_V32_DATA', 
                '2017F' : 'Fall17_17Nov2017F_V32_DATA', 
                }   

jecTag = jecTagsMC[str(dataYear)] if isMC else jecTagsDATA[str(dataYear) + runPeriod]

jmeUncert = [x for x in jesUncert.split(",")]


print "JECTag =", bcolors.OKGREEN, jecTag,  bcolors.ENDC, \
    "jesUncertainties =", bcolors.OKGREEN, jmeUncert,  bcolors.ENDC, \
    "redoJec =", bcolors.OKGREEN, redojec,  bcolors.ENDC

#untar the zipped jec files when submitting crab jobs
if crab :
    jesDatadir = os.environ['CMSSW_BASE'] + "/src/PhysicsTools/NanoAODTools/data/jme/"
    jesInputFile = jesDatadir + jecTag + ".tar.gz"
    print "Using JEC files from:", jesInputFile
    subprocess.call(['tar', "-xzvf", jesInputFile, "-C", jesDatadir])

#jme corrections
if isMC:
    jmeCorrections=lambda : jetmetUncertaintiesProducer(era=str(dataYear), globalTag=jecTag, jesUncertainties=jmeUncert, redoJEC=redojec, saveJets=False)
else:
    jmeCorrections=lambda : jetRecalib(globalTag=jecTag)

################################################ MET
# MET dictionary 
doJERVar = True
doJESVar = True
doUnclustVar = True
metdict = {
    "pf"    : { "tag" : "MET",      "systs"  : [""] },
    "tk"    : { "tag" : "TkMET",    "systs"  : [""] },
    #"puppi" : { "tag" : "PuppiMET", "systs"  : [""] },
    }
if isMC:
    metdict["gen"] = {"tag" : "GenMET", "systs"  : [""]}
    if doJERVar:
        metdict["pf"]["systs"].extend( ["_nom", "_jerUp", "_jerDown"] )
    if doJESVar:
        metdict["pf"]["systs"].extend( ["_jesTotalUp", "_jesTotalDown"] )
    if doUnclustVar:
        metdict["pf"]["systs"].extend( ["_unclustEnUp", "_unclustEnDown"] )

################################################ PU
#pu reweight modules
puWeightProducer = puWeight_2016
if dataYear==2017:
    puWeightProducer = puWeight_2017

################################################ Muons
#Rochester correction for muons
muonScaleRes = muonScaleRes2016
if dataYear==2017:
    muonScaleRes = muonScaleRes2017

# muon dictionary
mudict = {
    "pf"     : { "tag" : "",             "systs"  : [""] },
    "roccor" : { "tag" : "_corrected",   "systs"  : [""] },
    }
if isMC:
    mudict["gen_bare"] = { "tag" : "_bare",  "systs" : [""] }
    # these exist only for 2017
    if dataYear==2017:
        mudict["roccor"]["systs"] = ["", "_sys_uncertUp",  "_sys_uncertDown"]    

################################################

##This is temporary for testing purpose
input_dir = "/gpfs/ddn/srm/cms/store/"
ifileMC = "mc/RunIISummer16NanoAODv3/DYJetsToLL_Pt-50To100_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v2/280000/26DE6A2F-9329-E911-8766-002590DE6E8A.root"
if dataYear==2017:
    ifileMC = "mc/RunIIFall17NanoAODv4/DYJetsToLL_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8/NANOAODSIM/PU2017_12Apr2018_Nano14Dec2018_102X_mc2017_realistic_v6-v1/20000/41874784-9F25-7C49-B4E3-6EECD93B77CA.root"    
ifileDATA = "data/Run2016D/DoubleEG/NANOAOD/Nano14Dec2018-v1/280000/481DA5C0-DF96-5640-B5D1-208F52CAC829.root"
if dataYear==2017:
    ifileDATA = "data/Run2017E/DoubleMuon/NANOAOD/31Mar2018-v1/710000/A452D873-4B6E-E811-BE23-FA163E60E3B4.root"

input_files = []
modules = []

if isMC:
    input_files.append( input_dir+ifileMC )
    modules = [puWeightProducer(), 
               preSelection(isMC=isMC, passall=passall, dataYear=dataYear), 
               lepSF(),
               jmeCorrections(),
               muonScaleRes(),
               recoZproducer(mudict=mudict, isMC=isMC),
               additionalVariables(isMC=isMC, mudict=mudict, metdict=metdict), 
               leptonSelectModule(), 
               CSAngleModule(), 
               genWproducerModule(),
               ]
else:
    input_files.append( input_dir+ifileDATA )
    modules = [preSelection(isMC=isMC, passall=passall, dataYear=dataYear), 
               jmeCorrections(),
               muonScaleRes(),
               recoZproducer(mudict=mudict, isMC=isMC),
               additionalVariables(isMC=isMC, mudict=mudict, metdict=metdict),
               ]

treecut = ("Entry$<" + str(maxEvents) if maxEvents > 0 else None)
p = PostProcessor(outputDir=".",  
                  inputFiles=(input_files if crab==0 else inputFiles()),
                  cut=treecut,      
                  modules=modules,
                  provenance=True,
                  outputbranchsel="keep_and_drop_"+("MC" if isMC else "Data")+".txt",
                  fwkJobReport=(False if crab==0 else True),
                  jsonInput=(None if crab==0 else runsAndLumis())
                  )
p.run()

print "DONE"
os.system("ls -lR")
