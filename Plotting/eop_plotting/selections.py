from calculation import Calculation, CalculationDataMC
from variables import trkEtaPhiECAL
import numpy as np

def NoSelection(trk):
    return np.ones(len(trk)) > 0.0
branches = []
sel_NoSelection = Calculation(NoSelection, branches)

def TightIso(trk):
    return trk["trk_nearest_dR_EM"] > 0.55
sel_TightIso = Calculation(TightIso, ["trk_nearest_dR_EM"])

def HadIso(trk):
    return trk["trk_nearest_dR_HAD"] > 0.4
sel_HadIso = Calculation(HadIso, ["trk_nearest_dR_HAD"])

def pos(trk):
    return trk["trk_charge"] > 0
sel_pos_trk = Calculation(pos, ["trk_charge"])

def neg(trk):
    return np.logical_not(pos(trk))
sel_neg_trk = Calculation(neg, ["trk_charge"])

def pt_sevengev(trk):
    return trk["trk_p"] > 7.0
sel_pt_sevengev = Calculation(pt_sevengev, ["trk_p"])

def hasHADExtrapolation(trk):
    return (trk["trk_phiHEC1"] > -100) | (trk["trk_phiTileBar2"] > -100) | (trk["trk_phiTileExt1"] > -100)
branches =["trk_phiHEC1", "trk_phiTileBar2", "trk_phiTileExt1"]
sel_hasHADExtrapolation = Calculation(hasHADExtrapolation, branches)

#A selection for plotting event-based variables
def Event(trk):
    '''get only the variables associated with the first track in the event.
    This is so that we can reweight variables with an event, and not with individual tracks'''
    return (trk["trkIndex"] < 0.5) & (trk["trkIndex"] > -0.5)
branches = ["trkIndex"]
sel_Event = Calculation(Event, branches)

def SubleadingTrack(trk):
    '''get only the variables associated with the first track in the event.
    This is so that we can reweight variables with an event, and not with individual tracks'''
    return (trk["trkIndex"] < 1.5) & (trk["trkIndex"] > 0.5)
branches = ["trkIndex"]
sel_SubleadingTrack = Calculation(SubleadingTrack, branches)

#These are the definitions of the different types of track classifications according to tracking CP
def TruthLink(trk):
    return trk["trk_hasTruthParticle"] == 1

def TruthMatched(trk):
    return (trk["trk_truthProb"] > 0.5) 

def Fake(trk):
    return np.logical_not(TruthMatched(trk))
branches = ["trk_truthProb"]
sel_Fake = Calculation(Fake, branches)

def Pileup(trk):
    return TruthMatched(trk) & np.logical_not(TruthLink(trk))
branches = ["trk_truthProb", "trk_hasTruthParticle"]
sel_Pileup = Calculation(Pileup, branches)

def HardScatter(trk):
    return TruthMatched(trk) & TruthLink(trk)
branches = ["trk_truthProb", "trk_hasTruthParticle"]
sel_HardScatter = Calculation(HardScatter, branches)

def ParticlePDGID_ABS(trk, pdgID):

    return abs(np.abs(trk["trk_truthPdgId"]) - abs(pdgID)) < 0.1

def ParticlePDGID(trk, pdgID):
    return (np.abs(trk["trk_truthPdgId"] - pdgID)) < 0.1

#Define a significant hadron energy deposit with the amount of energy in the HAD calorimeter
def EHadBetween30And90OfMomentum(trk):
    '''At least 30 % of the track momentum and no more than 90 % of the track momentum was found the HAD calorimeter'''
    E_HAD_frac = trk["trk_ClusterEnergy_HAD_200"]/trk["trk_p"]
    return (E_HAD_frac > 0.3) & (E_HAD_frac < 0.9) #This selection only works for EM-scale
branches = ["trk_ClusterEnergy_HAD_200", "trk_p"]
sel_EHadBetween30And90OfMomentum = Calculation(EHadBetween30And90OfMomentum, branches)

def Lar1_1GeV(trk):
    return trk["trk_ClusterEnergy_EM_100"] < 1.1
branches = ["trk_ClusterEnergy_EM_100"]
sel_Lar1_1GeV = Calculation(Lar1_1GeV, branches)

def Z0SinThetaLess1_5(trk):
    return trk["trk_z0sintheta"] < 1.5
branches = ["trk_z0sintheta"]
sel_Z0SinThetaLess1_5 = Calculation(Z0SinThetaLess1_5, branches)

def d0Less1_5(trk):
    return trk["trk_d0"] < 1.5
branches = ["trk_d0"]
sel_d0Less1_5 = Calculation(d0Less1_5, branches)

def ExtrapolAcceptanceCalculator(trk, min_cut, max_cut):
    trk_eta = np.abs(trkEtaPhiECAL(trk)[0]) #the absolute value of eta

    #check that both tracks are in the acceptance
    in_acceptance = (trk_eta < max_cut) & (trk_eta > min_cut)

    return in_acceptance

def NonZeroEnergy(trk):
    return (trk["trk_nclusters_EM_200"] + trk["trk_nclusters_HAD_200"]) > 0.5 #there was at least one cluster assocated with the track
branches = ["trk_nclusters_EM_200", "trk_nclusters_HAD_200"]
sel_NonZeroEnergy = Calculation(NonZeroEnergy, branches)

def ELessEqual0(trk):
    return (trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"]) <= 1e-6
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200"]
sel_ELessEqual0 = Calculation(ELessEqual0, branches)

def EHadFracAbove70(trk):
    return ((trk["trk_ClusterEnergy_HAD_200"]) / (trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"]) >= 0.7) & ((trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"]) > 0.0)
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200"]
sel_EHadFracAbove70 = Calculation(EHadFracAbove70, branches)

#A general function to pick different regions of the atlas detector based on track eta in the ID
def IDAcceptanceCalculator(trk, min_cut, max_cut):
    trk_etaID = np.abs(trk["trk_etaID"])
    upper_in_acceptance = trk_etaID < max_cut
    lower_in_acceptance = trk_etaID > min_cut
    return (upper_in_acceptance & lower_in_acceptance)

#You can do fancy things with lambda functions here
def EtaBin(trk, min_cut, max_cut):
    return ExtrapolAcceptanceCalculator(trk, min_cut, max_cut)

#### Here are the eta track selections ###
def ECAL_Eta00_06(trk):
    return EtaBin(trk, 0.0, 0.6)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta00_06 = Calculation(ECAL_Eta00_06, branches)

#### Here are the eta track selections ###
def ECAL_Eta00_02(trk):
    return EtaBin(trk, 0.0, 0.2)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta00_02 = Calculation(ECAL_Eta00_02, branches)

#### Here are the eta track selections ###
def ECAL_Eta02_04(trk):
    return EtaBin(trk, 0.2, 0.4)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta02_04 = Calculation(ECAL_Eta02_04, branches)

#### Here are the eta track selections ###
def ECAL_Eta04_06(trk):
    return EtaBin(trk, 0.4, 0.6)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta04_06 = Calculation(ECAL_Eta04_06, branches)

def ECAL_Eta06_11(trk):
    return EtaBin(trk, 0.6, 1.1)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta06_11 = Calculation(ECAL_Eta06_11, branches)

def ECAL_Eta11_14(trk):
    return EtaBin(trk, 1.1, 1.4)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta11_14 = Calculation(ECAL_Eta11_14, branches)

def ECAL_Eta14_15(trk):
    return EtaBin(trk, 1.4, 1.5)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta14_15 = Calculation(ECAL_Eta14_15, branches)

def ECAL_Eta15_18(trk):
    return EtaBin(trk, 1.5, 1.8)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta15_18 = Calculation(ECAL_Eta15_18, branches)

def ECAL_Eta18_23(trk):
    return EtaBin(trk, 1.8, 2.3)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta18_23 = Calculation(ECAL_Eta18_23, branches)

def ECAL_Eta19_23(trk):
    return EtaBin(trk, 1.9, 2.3)
branches = ["trk_etaEMB2"]
sel_ECAL_Eta19_23 = Calculation(ECAL_Eta19_23, branches)

def PBetween12_18(trk):
    return (1.2 < trk["trk_p"]) & (trk["trk_p"] < 1.8)
branches = ["trk_p"]
sel_PBetween12_18 = Calculation(PBetween12_18, branches)

def PBetween22_28(trk):
    return (2.2 < trk["trk_p"]) & (trk["trk_p"] < 2.8)
branches = ["trk_p"]
sel_PBetween22_28 = Calculation(PBetween22_28, branches)

def PBetween28_36(trk):
    return (2.8 < trk["trk_p"]) & (trk["trk_p"] < 3.6)
branches = ["trk_p"]
sel_PBetween28_36 = Calculation(PBetween28_36, branches)

def PBin(trk, min_cut, max_cut):
    return (trk["trk_p"] > min_cut) & (trk["trk_p"] <= max_cut)

def NTRTX(trk, nTRT_low, nTRT_high):
    return ((trk["trk_nTRT"] >= nTRT_low) & (trk["trk_nTRT"] < nTRT_high)) | (np.abs(trk["trk_etaID"]) > 2.0)

def NPVBin(trk, npv_low, npv_high):
    return (trk["trk_NPV2"] >= npv_low) & (trk["trk_NPV2"] < npv_high)
