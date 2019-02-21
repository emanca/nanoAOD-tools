import os
import copy

# corrected = Rochester
muon = '_corrected'

# nom = MET w/ jet smearing
met = '_nom'

selections = {

    'W' : {
        'mc' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Muon_idx1]>25. && ' % muon) \
                #('Muon%s_MET%s_mt[Muon_idx1]>40.' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',            
            'weight' : 'TMath::Abs(LHEWeight_originalXWGTUP)/LHEWeight_originalXWGTUP*' \
                'puWeight*' \
                'Muon_effSF[Muon_idx1]',
            },
        'data' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Muon_idx1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Muon_idx1]>40. ' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },

    'Fake' : {
        'mc' : {
            'cut': 'Vtype==1 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Muon_idx1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Muon_idx1]<40. ' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : 'TMath::Abs(LHEWeight_originalXWGTUP)/LHEWeight_originalXWGTUP*' \
                'puWeight*' \
                'Muon_effSF[Muon_idx1]',
            },
        'data' : {
            'cut': 'Vtype==0 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Muon_idx1]>25. && ' % muon_pt) \
                #('Muon%s_MET%s_mt[Muon_idx1]<40.' % (muon, met)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },

    'Z' : {
        'mc' : {
            'cut': 'Vtype==2 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Muon_idx1]>25. && Muon_pt%s[Muon_idx2]>20.' % (muon_pt, muon_pt)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : 'TMath::Abs(LHEWeight_originalXWGTUP)/LHEWeight_originalXWGTUP*' \
                'puWeight*' \
                'Muon_effSF[Muon_idx1]*Muon_effSF[Muon_idx2]',
            },
        'data' : {
            'cut': 'Vtype==2 && ' \
                #'Muon_HLT && ' \
                #('Muon_pt%s[Muon_idx1]>25. && Muon_pt%s[Muon_idx2]>20.' % (muon_pt, muon_pt)) \
                #'MET_filters==1 && ' \
                #'nVetoElectrons==0 && ', \
                '1',
            'weight' : '',
            },
        },
    }

selections['Wplus'] = copy.deepcopy(selections['W'])
selections['Wminus'] = copy.deepcopy(selections['W'])
selections['Wplus']['mc']['cut']  += ' && Muon_charge[Muon_idx1]>0'
selections['Wminus']['mc']['cut'] += ' && Muon_charge[Muon_idx1]<0'

selections['Fakeplus'] = copy.deepcopy(selections['Fake'])
selections['Fakeminus'] = copy.deepcopy(selections['Fake'])
selections['Fakeplus']['mc']['cut']  += ' && Muon_charge[Muon_idx1]>0'
selections['Fakeminus']['mc']['cut'] += ' && Muon_charge[Muon_idx1]<0'

variables =  {
    'W' : [('Muon%s_pt[Muon_idx1]' % muon), 
                ('Muon%s_eta[Muon_idx1]' % muon), 
                ('Muon%s_phi[Muon_idx1]' % muon), 
                ('Muon%s_pfRelIso04_all[Muon_idx1]' % muon), 
                ('Muon%s_dxy[Muon_idx1]' % muon), 
                ('Muon%s_dz[Muon_idx1]' % muon), 
                ('Muon%s_MET%s_mt[Muon_idx1]' % (muon, met)),
                ('Muon%s_MET%s_h_pt[Muon_idx1]' % (muon, met)),
                ('GenMuon_bare_GenMET_mt[Muon_idx1]'),
                ('GenMuon_bare_GenMET_h_pt[Muon_idx1]'),
                ('MET%s_pt' % met),
                ('Muon_MET%s_uPar' % met),  
                ('Muon_MET%s_uPer' % met),  
                ('PV_npvsGood'),
                ],
    'Z' : [('Muon%s_pt[Muon_idx1]' % muon), 
                ('Muon%s_eta[Muon_idx1]' % muon), 
                ('Muon%s_phi[Muon_idx1]' % muon), 
                ('Muon%s_pfRelIso04_all[Muon_idx1]' % muon), 
                ('Muon%s_dxy[Muon_idx1]' % muon), 
                ('Muon%s_dz[Muon_idx1]' % muon), 
                ('Muon%s_pt[Muon_idx2]' % muon), 
                ('Muon%s_eta[Muon_idx2]' % muon), 
                ('Muon%s_phi[Muon_idx2]' % muon), 
                ('Muon%s_pfRelIso04_all[Muon_idx2]' % muon), 
                ('Muon%s_dxy[Muon_idx2]' % muon), 
                ('Muon%s_dz[Muon_idx2]' % muon),
                ('RecoZ%s_mass' % muon),
                ('RecoZ%s_y' % muon),
                ('RecoZ%s_pt' % muon),
                ('RecoZ%s_CStheta' % muon),
                ('RecoZ%s_CSphi' % muon),
                ('GenZ%s_mass' % muon),
                ('GenZ%s_y' % muon),
                ('GenZ%s_pt' % muon),
                ('GenZ%s_CStheta' % muon),
                ('GenZ%s_CSphi' % muon),
                ('RecoZ%s_MET%s_uPar' % (muon, met)),  
                ('RecoZ%s_MET%s_uPer' % (muon, met)),  
                ('PV_npvsGood'),
                ],
}
variables['Fake'] = copy.deepcopy(variables['W'])
