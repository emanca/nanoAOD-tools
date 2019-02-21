import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection 
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


def loose_muon_id(mu):
    return (abs(mu.eta)<2.4 and mu.pt>10 and abs(mu.dxy)<0.05 and abs(mu.dz)<0.2 and mu.isPFcand and mu.pfRelIso04_all< 0.30)
def medium_muon_id(mu):
    return (abs(mu.eta)<2.4 and mu.pt>20 and abs(mu.dxy)<0.05 and abs(mu.dz)<0.2 and mu.mediumId and mu.pfRelIso04_all<=0.10)
def medium_aiso_muon_id(mu):
    return (abs(mu.eta)<2.4 and mu.pt>20 and abs(mu.dxy)<0.05 and abs(mu.dz)<0.2 and mu.mediumId and mu.pfRelIso04_all >0.10 and mu.pfRelIso04_all<0.30)
def veto_electron_id(ele):
    etaSC = ele.eta + ele.deltaEtaSC
    if (abs(etaSC) <= 1.479):
        return (ele.pt>10 and abs(ele.dxy)<0.05 and abs(ele.dz)<0.1 and ele.cutBased>=1 and ele.pfRelIso03_all< 0.30)
    else:
        return (ele.pt>10 and abs(ele.dxy)<0.10 and abs(ele.dz)<0.2 and ele.cutBased>=1 and ele.pfRelIso03_all< 0.30)

class preSelection(Module):
    def __init__(self, isMC=True, passall=False, dataYear=2016):
        self.isMC = isMC
        self.passall = passall
        self.dataYear = str(dataYear)

        # baded on https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        # val = 2*(IS FOR DATA) + 1*(IS FOR MC)
        self.met_filters = {
            "2016": { "goodVertices" : 3,
                      "globalTightHalo2016Filter": 3,
                      "HBHENoiseFilter": 3,
                      "HBHENoiseIsoFilter" : 3,
                      "EcalDeadCellTriggerPrimitiveFilter": 3
                      },
            "2017": { "goodVertices": 3,
                      "globalTightHalo2016Filter": 3,
                      "HBHENoiseFilter": 3,
                      "HBHENoiseIsoFilter": 3,
                      "EcalDeadCellTriggerPrimitiveFilter": 3,
                      "BadPFMuonFilter": 3,
                      "BadChargedCandidateFilter": 3,
                      "eeBadScFilter" : 2,
                      #"ecalBadCalibFilter": 3, # needs to be rerun
                      },
            "2018": { "goodVertices": 3,
                      "globalTightHalo2016Filter": 3,
                      "HBHENoiseFilter": 3,
                      "HBHENoiseIsoFilter": 3,
                      "EcalDeadCellTriggerPrimitiveFilter": 3,
                      "BadPFMuonFilter" : 3,
                      "BadChargedCandidateFilter" : 3,
                      "eeBadScFilter" : 2,
                      #"ecalBadCalibFilter": 3,  # needs to be rerun 
                      },
            }
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Muon_HLT", "I", title="Event passes OR of HLT triggers")
        self.out.branch("Muon_idx1", "I", title="index of W-like muon / index of Z-like 1st muon")
        self.out.branch("Muon_idx2", "I", title="index of Z-like 2nd muon")
        self.out.branch("Vtype", "I", title="0:W-like; 1:Fake-like; 2:Z-like; 3:SS-dimuon")
        self.out.branch("MET_filters", "I", title="AND of all MET filters")
        self.out.branch("nVetoElectrons", "I", title="Number of veto electrons")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # Trigger bit
        if self.isMC==False:
            triggers_OR = ["IsoMu24", "IsoTkMu24"]
        else:
            triggers_OR = ["IsoMu24", "IsoTkMu24"]
        HLT_pass = False
        for hlt in triggers_OR:
            if not hasattr(event, "HLT_"+hlt): continue
            HLT_pass |= getattr(event, "HLT_"+hlt)
        self.out.fillBranch("Muon_HLT", int(HLT_pass))

        # MET filters
        met_filters_AND = True
        for key,val in self.met_filters[self.dataYear].items():
            met_filters_AND &=  (not (val & (1 << (1-int(self.isMC)) )) or getattr(event, "Flag_"+key))
        self.out.fillBranch("MET_filters", int(met_filters_AND))

        # Muon selection
        all_muons = Collection(event, "Muon")
        loose_muons       = [ [mu,imu] for imu,mu in enumerate(all_muons) if loose_muon_id(mu) ]
        medium_muons      = [ [mu,imu] for imu,mu in enumerate(all_muons) if medium_muon_id(mu)]
        medium_aiso_muons = [ [mu,imu] for imu,mu in enumerate(all_muons) if medium_aiso_muon_id(mu)]

        loose_muons.sort( key = lambda x: x[0].pt, reverse=True )
        medium_muons.sort(key = lambda x: x[0].pt, reverse=True )
        medium_aiso_muons.sort(key = lambda x: x[0].pt, reverse=True )

        # Electron selection
        all_electrons  = Collection(event, "Electron")    
        veto_electrons = [ [ele,iele] for iele,ele in enumerate(all_electrons) if veto_electron_id(ele) ]
        self.out.fillBranch("nVetoElectrons", len(veto_electrons))

        event_flag = -1        
        (idx1, idx2) = (-1, -1)
        # W-like event: 1 loose, 1 medium
        if len(medium_muons)==1 and len(loose_muons)==1:
            event_flag = 0
            (idx1, idx2) = (medium_muons[0][1], -1)
        # Fake-like event
        elif len(medium_muons)==0 and len(medium_aiso_muons)==1:
            event_flag = 1
            (idx1, idx2) = (medium_aiso_muons[0][1], -1)
        # Z-like event
        elif len(loose_muons)==2:
            (idx1, idx2) = (loose_muons[0][1], loose_muons[1][1])
            event_flag = 2 if (loose_muons[0][0].charge+loose_muons[1][0].charge)==0 else 3
        # anything else        
        else:   
            event_flag = -1

        self.out.fillBranch("Muon_idx1", idx1)
        self.out.fillBranch("Muon_idx2", idx2)
        self.out.fillBranch("Vtype", event_flag)

        if event_flag not in [0,1,2,3]: 
            return (False or self.passall)

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

preSelectionModule = lambda : preSelection() 
