from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
import argparse
import sys

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
parser.add_argument('-jesUncert', '--jesUncert',type=str, default="Total", help="")
parser.add_argument('-redojec', '--redojec',  type=int, default=0,      help="")
parser.add_argument('-runPeriod', '--runPeriod',  type=str, default="B", help="")
parser.add_argument('-run', '--run', type=str, default="submit", help="")
args = parser.parse_args()
tag = args.tag
isMC = args.isMC
dataYear = args.dataYear
jesUncert = args.jesUncert
redojec = args.redojec
runPeriod = args.runPeriod
run = args.run
samples = ('mc' if isMC else 'data')+'samples_'+str(dataYear)+'.txt'
print "tag =", bcolors.OKGREEN, tag, bcolors.ENDC, \
    ", isMC =", bcolors.OKGREEN, str(isMC), bcolors.ENDC, \
    ", dataYear =", bcolors.OKGREEN, str(dataYear), bcolors.ENDC, \
    " => running on sample file:", bcolors.OKGREEN, samples, bcolors.ENDC

config = Configuration()

config.section_("General")
config.General.requestName = 'TEST'
config.General.transferLogs=True
config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
config.JobType.inputFiles = ['../python/postprocessing/wmass/postproc.py','../scripts/haddnano.py','../python/postprocessing/wmass/keep_and_drop_MC.txt', '../python/postprocessing/wmass/keep_and_drop_Data.txt']
config.JobType.scriptArgs = ['crab=1', 'isMC='+('1' if isMC else '0'), 'dataYear='+str(dataYear), 'redojec='+str(redojec), 'runPeriod=B']
config.JobType.sendPythonFolder	 = True
config.section_("Data")
config.Data.inputDataset = 'TEST'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 5
#config.Data.totalUnits = 10
if not isMC:
    if dataYear==2016:
        config.Data.lumiMask = 'Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON.txt'
    elif  dataYear==2017:
        config.Data.lumiMask = 'Cert_294927-306462_13TeV_EOY2017ReReco_Collisions17_JSON.txt'
    else:
        config.Data.lumiMask = 'TEST'
    print "Using lumiMask", config.Data.lumiMask
config.Data.outLFNDirBase = '/store/user/%s/NanoAOD-%s' % (getUsernameFromSiteDB(), tag)
config.Data.publication = False
config.Data.outputDatasetTag = 'TEST'
config.section_("Site")
config.Site.storageSite = "T2_IT_Pisa"

if __name__ == '__main__':

    import os

    print 'Creating file '+'postcrab-'+tag+'.txt for crab submission '+tag
    fout = open('postcrab_'+samples.rstrip('.txt')+'_'+tag+'.txt', 'w') 

    if run in ['submit', 'dryrun']:
        print 'Cleaning the ../data/jme/ directory from unnecessary .txt files'
        backup_dir = '../../../../../JEC/'
        jec_dir = '../data/jme/'
        if not os.path.isdir(backup_dir):
            os.system('mkdir '+backup_dir)
        os.system('mv '+jec_dir+'Summer16*txt '+backup_dir)
        os.system('mv '+jec_dir+'Fall17*txt '+backup_dir)
        os.system('ls -tr '+jec_dir)
        os.system('du -h '+jec_dir)

    f = open(samples) 
    content = f.readlines()
    content = [x.strip() for x in content] 
    from CRABAPI.RawCommand import crabCommand

    n = 0
    for dataset in content :        
        if dataset[0]=='#':
            continue
        dataset_inputDataset = dataset.split(',')[0]
        dataset_unitsPerJob = int(dataset.split(',')[1])
        print 'inputDataset: '+dataset_inputDataset
        print 'unitsPerJob:  '+str(dataset_unitsPerJob)
        if isMC==0:
            pos = dataset.find('Run'+str(dataYear))
            runPeriod = dataset[pos+7:pos+8]
            ipos = -1
            for iar,ar in enumerate(config.JobType.scriptArgs):
                if 'runPeriod' in ar:
                    ipos = iar
                    print 'Argument %s (%s) will be set to %s' % (iar, ar, runPeriod)
                    break
            config.JobType.scriptArgs[iar] = 'runPeriod='+str(runPeriod)            
        print 'scriptArgs:  ',config.JobType.scriptArgs        
        config.Data.inputDataset = dataset_inputDataset
        config.Data.unitsPerJob = dataset_unitsPerJob
        config.General.requestName = dataset.split('/')[1]+'_'+tag+'_task_'+str(n)
        config.Data.outputDatasetTag = dataset.split('/')[2]
        print 'requestName:  '+config.General.requestName
        print 'output  ===> ', bcolors.OKBLUE , config.Data.outLFNDirBase+'/'+dataset.split('/')[1]+'/'+config.Data.outputDatasetTag+'/' , bcolors.ENDC
        if run=='submit':
            crabCommand('submit', config=config)
        elif run=='dryrun':
            crabCommand('submit', '--dryrun', config=config)
        elif run=='debug':            
            continue
        crablog = open('crab_'+config.General.requestName+'/crab.log', 'r').readlines()
        crabloglines = [x.strip() for x in crablog]
        username = getUsernameFromSiteDB()
        for crablogline in crabloglines:
            if 'Task name: ' in crablogline:
                pos = crablogline.find('%s' % username)
                taskid = crablogline[pos-14:pos-1]
                print 'Task name:   '+taskid
                break
        fout.write('/gpfs/ddn/srm/cms/'+config.Data.outLFNDirBase+'/'+dataset.split('/')[1]+'/'+config.Data.outputDatasetTag+'/'+taskid+'/''\n')
        n += 1
    fout.close()

    if run in ['submit', 'dryrun']:
        print 'Restore the '+jec_dir
        os.system('mv '+backup_dir+'Summer16*txt '+jec_dir)
        os.system('mv '+backup_dir+'Fall17*txt '+jec_dir)
    
