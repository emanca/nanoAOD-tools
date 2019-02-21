import ROOT
import math
ROOT.PyConfig.IgnoreCommandLineOptions = True

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

def getWvariables(muon, neutrino):
    m = ROOT.TLorentzVector()
    n = ROOT.TLorentzVector()
    w = ROOT.TLorentzVector()
    m.SetPtEtaPhiM(muon.pt, muon.eta, muon.phi, muon.mass)
    n.SetPtEtaPhiM(neutrino.pt, neutrino.eta, neutrino.phi, 0.)
    w = m + n
    return w.Pt(), w.Rapidity(), w.Phi(), w.M()

class genWproducer(Module):
    def __init__(self):
        pass
    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("Wpt_bare", "F")
        self.out.branch("Wrap_bare", "F")
        self.out.branch("Wphi_bare", "F")
        self.out.branch("Wmass_bare", "F")
        self.out.branch("Wpt_preFSR", "F")
        self.out.branch("Wrap_preFSR", "F")
        self.out.branch("Wphi_preFSR", "F")
        self.out.branch("Wmass_preFSR", "F")
        self.out.branch("Wpt_dress", "F")
        self.out.branch("Wrap_dress", "F")
        self.out.branch("Wphi_dress", "F")
        self.out.branch("Wmass_dress", "F")

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        # reobtain the indices of the good muons and the neutrino
        if event.genVtype==0:
            genParticles = Collection(event, "GenPart")
            genDressedLeptons = Collection(event,"GenDressedLepton")
            bareMuonIdx = event.GenPart_bareMuonIdx
            NeutrinoIdx = event.GenPart_NeutrinoIdx
            preFSRMuonIdx = event.GenPart_preFSRMuonIdx
            dressMuonIdx = event.GenDressedLepton_dressMuonIdx
            if(bareMuonIdx>=0) :
                (Wpt_bare, Wrap_bare, Wphi_bare, Wmass_bare) = getWvariables(genParticles[bareMuonIdx], genParticles[NeutrinoIdx])
                self.out.fillBranch("Wpt_bare",Wpt_bare)
                self.out.fillBranch("Wrap_bare",Wrap_bare)
                self.out.fillBranch("Wphi_bare",Wphi_bare)
                self.out.fillBranch("Wmass_bare",Wmass_bare)
            if(preFSRMuonIdx>=0) :
                (Wpt_preFSR, Wrap_preFSR, Wphi_preFSR, Wmass_preFSR) = getWvariables(genParticles[preFSRMuonIdx], genParticles[NeutrinoIdx])
                self.out.fillBranch("Wpt_preFSR",Wpt_preFSR)
                self.out.fillBranch("Wrap_preFSR",Wrap_preFSR)
                self.out.fillBranch("Wphi_preFSR",Wphi_preFSR)
                self.out.fillBranch("Wmass_preFSR",Wmass_preFSR)
            if(dressMuonIdx>=0) :
                (Wpt_dress, Wrap_dress, Wphi_dress, Wmass_dress) = getWvariables(genDressedLeptons[dressMuonIdx], genParticles[NeutrinoIdx])
                self.out.fillBranch("Wpt_dress",Wpt_dress)
                self.out.fillBranch("Wrap_dress",Wrap_dress)
                self.out.fillBranch("Wphi_dress",Wphi_dress)
                self.out.fillBranch("Wmass_dress",Wmass_dress)

        return True


# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

genWproducerModule = lambda : genWproducer()
