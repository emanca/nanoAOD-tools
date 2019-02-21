#!/usr/bin/env python
import commands
import time
import re
import os
import string
from os import listdir
from os.path import isfile, join
import sys
import argparse

from CRABClient.UserUtilities import config, getUsernameFromSiteDB

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
parser.add_argument('-tag', '--tag', type=str, default="TEST",      help="")
parser.add_argument('-isMC', '--isMC', type=int, default=1,      help="")
parser.add_argument('-dataYear', '--dataYear',type=int, default=2016, help="")
parser.add_argument('-run', '--run',type=str, default='batch', help="")
parser.add_argument('-pushback', '--pushback',type=int, default=0, help="")
args = parser.parse_args()
tag = args.tag
isMC = args.isMC
dataYear = args.dataYear
run = args.run
pushback = args.pushback
samples = ('mc' if isMC else 'data')+'samples_'+str(dataYear)+'.txt'

################################################################################

import subprocess

select_first_trial = True
n_max_files = 2

username = getUsernameFromSiteDB()
path = '/home/users/%s/wmass/CMSSW_10_2_9/src/PhysicsTools/NanoAODTools/crab/' % username
outdir_master = ("/gpfs/ddn/cms/user/%s/" % username)+"/NanoAOD-"+tag+"/"

print "Reading inputs from",  bcolors.OKGREEN, 'postcrab_'+samples.rstrip('.txt')+'_'+tag+'.txt'
if pushback:
    print "Pushing back to SRM area", bcolors.OKGREEN, "/gpfs/ddn/srm/cms/store/user/"+username,  bcolors.ENDC
else:
    print "Hadding to scratch area", bcolors.OKGREEN, outdir_master,  bcolors.ENDC

fin = open('postcrab_'+samples.rstrip('.txt')+'_'+tag+'.txt', 'r')
content = fin.readlines()
sample_dirs = [x.strip() for x in content]
for sample_dir in sample_dirs:    
    task_name = sample_dir.split('/')[-2]
    sample_name = sample_dir.split('/')[-4]
    ext = ''
    idx_ext = sample_dir.split('/')[-3].find('ext')    
    if idx_ext!=-1:
        ext = '_'+sample_dir.split('/')[-3][idx_ext:idx_ext+4]
    else:
        print "No extensions found in", sample_dir.split('/')[-3]
    job_name = task_name.replace('_', '')
    script_name = 'hn_'+task_name
    fout = open(script_name+'.sh','w')
    fout.write('#!/bin/bash\n\n')
    fout.write('cd '+path+'\n')
    fout.write('source /cvmfs/cms.cern.ch/cmsset_default.sh\n')
    fout.write('eval `scramv1 runtime -sh`\n')
    fout.write('\n')    
    pos = sample_dir.find("cms")
    sample_dir_from_cms = sample_dir[pos-1:] 
    if not os.path.isdir(outdir_master):
        mkoutdirmastercmd = "mkdir "+outdir_master
        print bcolors.OKBLUE, mkoutdirmastercmd, bcolors.ENDC
        fout.write(mkoutdirmastercmd+'\n')
        if run=='shell': os.system(mkoutdirmastercmd)
    outdir = ""
    if pushback:
        outdir = outdir_master+"/"+task_name+"/"
    else:
        outdir = outdir_master+"/"+sample_name+ext+"/"
    if not os.path.isdir(outdir):
        mkoutdircmd = "mkdir "+outdir
        print bcolors.OKBLUE, mkoutdircmd, bcolors.ENDC
        fout.write(mkoutdircmd+'\n')
        if run=='shell': os.system(mkoutdircmd)                
    crab_trials = os.listdir(sample_dir)
    for crab_trial in crab_trials:
        if select_first_trial and crab_trial!="0000":
            continue
        files = [sample_dir+"/"+crab_trial+"/"+x for x in os.listdir(sample_dir+'/'+crab_trial) if "tree_" in x]
    nfiles = len(files)
    haddargs = outdir+"tree.root "
    print "Found", bcolors.OKGREEN, "%s" % nfiles, bcolors.ENDC, "files"
    for nf,f in enumerate(files):
        if nf<n_max_files:
            haddargs += f+" "
    haddcmd = "python ../scripts/haddnano.py "+haddargs
    print bcolors.OKBLUE, haddcmd, bcolors.ENDC
    fout.write(haddcmd+'\n')
    if run=='shell': 
        os.system(haddcmd)
        if os.path.isfile(outdir+"tree.root"): print "File", bcolors.OKBLUE, outdir+"tree.root", bcolors.ENDC, "saved."
        else: print bcolors.FAIL, "File "+outdir+"tree.root NOT found.", bcolors.ENDC         
    if pushback:
        pushbackcmd = 'lcg-cp -b -U srmv2 -v file://'+outdir+'tree.root'+' \"srm://stormfe1.pi.infn.it:8444/srm/managerv2?SFN='+sample_dir_from_cms+'/tree.root'+'\"'
        print bcolors.OKBLUE, pushbackcmd, bcolors.ENDC
        if run=='shell':
            if os.path.isfile(outdir+"tree.root"):
                print "File:", bcolors.OKGREEN, outdir+"tree.root", bcolors.ENDC, "found. Move back to SRM"
                os.system('voms-proxy-init --voms cms')
                os.system(pushbackcmd)
                if os.path.isfile(sample_dir+"/tree.root"):
                    print "File:", bcolors.OKGREEN, sample_dir+"/tree.root", bcolors.ENDC, "is in SRM. Remove tmp files" 
                    rmcmd = "rm -r "+outdir
                    print bcolors.OKBLUE, rmcmd, bcolors.ENDC
                    os.system(rmcmd) 
                    fout.write(rmcmd+'\n')
                else:
                    print "File:", bcolors.FAIL, sample_dir+"/tree.root", "NOT found.", bcolors.ENDC
            else:
                print "File:", bcolors.FAIL, outdir+"tree.root", bcolors.ENDC, "NOT found."                
        elif run=='batch':
            fout.write('voms-proxy-init --voms cms\n')
            fout.write(pushbackcmd+'\n')
            rmcmd = "rm -r "+outdir
            print bcolors.OKBLUE, rmcmd, bcolors.ENDC
            fout.write(rmcmd+'\n')
    fout.close()
    if run=='batch': 
        os.system('chmod +x '+script_name+'.sh')
        submit_to_queue = 'bsub -q local -n 8 -J '+job_name+' -o '+path+'/'+script_name+'.stdout'+' -e '+path+'/'+script_name+'.stderr'+' -cwd `pwd` '+'./'+script_name+'.sh'
        print bcolors.OKBLUE, submit_to_queue, bcolors.ENDC
        os.system(submit_to_queue)
        time.sleep( 1.0 )
        print "@@@@@ END JOB @@@@@"        
