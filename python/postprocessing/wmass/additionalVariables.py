import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import TLorentzVector
import math
from math import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

def evaluateMt(mu_pt, mu_phi, mu_mass, met_pt, met_phi) :
    muvec = TLorentzVector()
    muvec.SetPtEtaPhiM(mu_pt,0.0,mu_phi, mu_mass)
    metvec = TLorentzVector()
    metvec.SetPtEtaPhiM(met_pt,0.0,met_phi,0.0)
    hvec = -(muvec + metvec)
    mt, h_pt, h_phi  = hvec.M(), hvec.Pt(), hvec.Phi()
    met_par, met_per = metvec.Vect().Dot(muvec.Vect().Unit()), metvec.Vect().Cross(muvec.Vect().Unit()).Pz()
    return  (mt, h_pt, h_phi, met_par, met_per) 

class additionalVariables(Module):
    def __init__(self, isMC=True, mudict={}, metdict={}):
        self.mudict = mudict
        self.metdict = metdict
        self.isMC = isMC
        pass

    def beginJob(self):
        pass
    def endJob(self):
        pass
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        for key_mu,mu in self.mudict.items() :
            for ivar_mu,var_mu in enumerate(mu["systs"]):
                for key_met,met in self.metdict.items() :
                    for ivar_met,var_met in enumerate(met["systs"]):
                        # skip double-systematic variation
                        if (var_mu!="" and var_met!=""):
                            continue
                        # skip mixed reco-gen objects
                        if ("gen" in key_met and "gen" not in key_mu) or ("gen" in key_mu and "gen" not in key_met):
                            continue
                        title_label = "MET: "+met["tag"]+" (syst: "+var_met+"), Muon: "+mu["tag"]+" (syst: "+var_mu+")"
                        branch_label_mu = ("GenMuon" if "gen" in key_mu else "Muon")
                        branch_label_mu += "%s%s_%s%s" % (mu["tag"], var_mu, met["tag"], var_met)
                        self.out.branch("%s_mt" % branch_label_mu, "F", lenVar="nMuons", title="Mt, "+title_label)
                        self.out.branch("%s_h_pt"  % branch_label_mu, "F", lenVar="nMuons", title="H pt, "+title_label)
                        self.out.branch("%s_h_phi" % branch_label_mu, "F", lenVar="nMuons", title="H phi, "+title_label)
                        # these are MET-only variables, skip loop over muons
                        if mu["tag"]=="" and var_mu=="":
                            self.out.branch("%s_uPar" % branch_label_mu, "F", lenVar="nMuons", title="MET || mu, "+title_label)
                            self.out.branch("%s_uPer" % branch_label_mu, "F", lenVar="nMuons", title="MET T mu, "+title_label)
                        branch_label_Z  = ("GenZ" if "gen" in key_mu else "RecoZ")
                        branch_label_Z  += "%s%s_%s%s" % (mu["tag"], var_mu, met["tag"], var_met)
                        self.out.branch("%s_uPar" % branch_label_Z, "F")
                        self.out.branch("%s_uPer" % branch_label_Z, "F")
        pass

    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""

        #collections
        muons = Collection(event, "Muon")
        if self.isMC:
            genparticles = Collection(event, "GenPart")

        #final vectors
        Mt_vec         = [0.0]*len(muons)
        Recoil_pt_vec  = [0.0]*len(muons)
        Recoil_phi_vec = [0.0]*len(muons)
        met_par_vec    = [0.0]*len(muons)
        met_per_vec    = [0.0]*len(muons)

        for key_mu,mu in self.mudict.items() :
            for ivar_mu,var_mu in enumerate(mu["systs"]):
                for key_met,met in self.metdict.items() :
                    for ivar_met,var_met in enumerate(met["systs"]):
                        if (var_mu!="" and var_met!=""):
                            continue
                        if ("gen" in key_met and "gen" not in key_mu) or ("gen" in key_mu and "gen" not in key_met):
                            continue
                        branch_label_mu = ("GenMuon" if "gen" in key_mu else "Muon")
                        branch_label_mu += "%s%s_%s%s" % (mu["tag"], var_mu, met["tag"], var_met)
                        met_pt  = getattr(event,"%s_pt%s"  % (met["tag"], var_met))
                        met_phi = getattr(event,"%s_phi%s" % (met["tag"], var_met))
                        for imuon,muon in enumerate(muons) :
                            if "gen" not in key_mu:
                                if var_mu=="":
                                    mu_pt = getattr(muon, "pt"+mu["tag"])
                                else:
                                    if "Up" in var_mu:
                                        mu_pt = max(getattr(muon, "pt"+mu["tag"]) + getattr(muon, "pt"+var_mu.rstrip("Up")), 0.0)
                                    elif "Down" in var_mu:
                                        mu_pt = max(getattr(muon, "pt"+mu["tag"]) - getattr(muon, "pt"+var_mu.rstrip("Down")), 0.0)
                                muon_phi,muon_mass = muon.phi,muon.mass
                            else:
                                genIdx = muon.genPartIdx
                                if genIdx>=0 and genIdx<len(genparticles):
                                    genMu = genparticles[genIdx]
                                    mu_pt, muon_phi, muon_mass = genMu.pt, genMu.phi, genMu.mass
                                else:
                                    mu_pt, muon_phi, muon_mass = 0.,0.,0.
                            (mt,hpt,hphi,met_par,met_per) = evaluateMt( mu_pt, muon_phi, muon_mass, met_pt, met_phi)
                            Mt_vec[imuon] = mt
                            Recoil_pt_vec[imuon] = hpt
                            Recoil_phi_vec[imuon] = hphi
                            met_par_vec[imuon] = met_par
                            met_per_vec[imuon] = met_per
                        self.out.fillBranch("%s_mt" % branch_label_mu, Mt_vec)
                        self.out.fillBranch("%s_h_pt"  % branch_label_mu, Recoil_pt_vec)
                        self.out.fillBranch("%s_h_phi" % branch_label_mu, Recoil_phi_vec)
                        if mu["tag"]=="" and var_mu=="":
                            self.out.fillBranch("%s_uPar" % branch_label_mu, met_par_vec)
                            self.out.fillBranch("%s_uPer" % branch_label_mu, met_per_vec)
                        if event.Vtype in [2,3]:
                            branch_label_Z  = ("GenZ" if "gen" in key_mu else "RecoZ")
                            branch_label_Z  += "%s%s_%s%s" % (mu["tag"], var_mu, met["tag"], var_met)
                            Zpt = getattr(event, "%s%s%s_pt"  %  ("GenZ" if "gen" in key_mu else "RecoZ", mu["tag"], var_mu))
                            Zphi = getattr(event, "%s%s%s_phi"  %  ("GenZ" if "gen" in key_mu else "RecoZ", mu["tag"], var_mu))
                            Zmass = getattr(event, "%s%s%s_mass"  %  ("GenZ" if "gen" in key_mu else "RecoZ", mu["tag"], var_mu))
                            (Zmt, Zh_pt, Zh_phi, Zmet_par, Zmet_per) = evaluateMt( Zpt, Zphi, Zmass, met_pt, met_phi)
                            self.out.fillBranch("%s_uPar" % branch_label_Z, Zmet_par)
                            self.out.fillBranch("%s_uPer" % branch_label_Z, Zmet_per)

        return True

# define modules using the syntax 'name = lambda : constructor' to avoid having them loaded when not needed

addVarModule = lambda : additionalVariables()
