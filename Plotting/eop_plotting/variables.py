from calculation import Calculation, CalculationDataMC, WeightCalculation
import numpy as np
from math import pi

def TruthMomentum(trk):
    return trk["trk_truthP"] * 1000.0 #scale to GeV
calc_TruthMomentum = Calculation(TruthMomentum, ["trk_truthP"])

def TotalCalibHitEnergyEM(trk):
    return trk["trk_TotalPhotonBackgroundCalibHitEnergy_EM_200"] + trk["trk_TotalHadronicBackgroundCalibHitEnergy_EM_200"] + trk["trk_TotalCalibHitEnergy_EM_200"]

def TotalCalibHitEnergyHAD(trk):
    return trk["trk_TotalPhotonBackgroundCalibHitEnergy_HAD_200"] + trk["trk_TotalHadronicBackgroundCalibHitEnergy_HAD_200"] + trk["trk_TotalCalibHitEnergy_HAD_200"]

def TotalCalibHitEnergy(trk):
    return TotalCalibHitEnergyEM(trk) + TotalCalibHitEnergyHAD(trk)

CalibHitBranches = ["trk_TotalPhotonBackgroundCalibHitEnergy_EM_200", "trk_TotalHadronicBackgroundCalibHitEnergy_EM_200", "trk_TotalCalibHitEnergy_EM_200","trk_TotalPhotonBackgroundCalibHitEnergy_HAD_200", "trk_TotalHadronicBackgroundCalibHitEnergy_HAD_200", "trk_TotalCalibHitEnergy_HAD_200"]

def HasCalibHit(trk):
    return TotalCalibHitEnergy(trk) > 0.0
sel_HasCalibHit = Calculation(HasCalibHit, CalibHitBranches)

def HasEMCalibHit(trk):
    return TotalCalibHitEnergyEM(trk) > 0.0
sel_HasEMCalibHit = Calculation(HasCalibHit, CalibHitBranches)

def HasHADCalibHit(trk):
    return TotalCalibHitEnergyHAD(trk) > 0.0
sel_HasHADCalibHit = Calculation(HasHADCalibHit, CalibHitBranches)

def EOTotalEMCalibEnergy(trk):
    return (trk["trk_ClusterEMActiveCalibHitEnergy_EM_200"] + trk["trk_ClusterEMActiveCalibHitEnergy_HAD_200"])/trk["trk_p"]
calc_EOTotalEMCalibHitEnergy = Calculation(EOTotalEMCalibEnergy, ["trk_ClusterEMActiveCalibHitEnergy_EM_200", "trk_ClusterEMActiveCalibHitEnergy_HAD_200", "trk_p"])

def CalibHitFrac(trk):
    return (trk["trk_TotalCalibHitEnergy_EM_200"] + trk["trk_TotalCalibHitEnergy_HAD_200"]) / TotalCalibHitEnergy(trk)
calc_CalibHitFrac = Calculation(CalibHitFrac, CalibHitBranches)

def PhotonCalibHitFrac(trk):
    return (trk["trk_TotalPhotonBackgroundCalibHitEnergy_EM_200"] + trk["trk_TotalPhotonBackgroundCalibHitEnergy_HAD_200"]) / TotalCalibHitEnergy(trk)
calc_PhotonCalibHitFrac = Calculation(PhotonCalibHitFrac, CalibHitBranches)

def HadronCalibHitFrac(trk):
    return (trk["trk_TotalHadronicBackgroundCalibHitEnergy_EM_200"] + trk["trk_TotalHadronicBackgroundCalibHitEnergy_HAD_200"]) / TotalCalibHitEnergy(trk)
calc_HadronCalibHitFrac = Calculation(HadronCalibHitFrac, CalibHitBranches)

def EMCalibHitFrac(trk):
    return (trk["trk_TotalCalibHitEnergy_EM_200"]) / TotalCalibHitEnergyEM(trk)
calc_EMCalibHitFrac = Calculation(EMCalibHitFrac, CalibHitBranches)

def HADCalibHitFrac(trk):
    return (trk["trk_TotalCalibHitEnergy_HAD_200"]) / TotalCalibHitEnergyHAD(trk)
calc_HADCalibHitFrac = Calculation(HADCalibHitFrac, CalibHitBranches)

def PhotonEMCalibHitFrac(trk):
    return (trk["trk_TotalPhotonBackgroundCalibHitEnergy_EM_200"] ) / TotalCalibHitEnergyEM(trk)
calc_PhotonEMCalibHitFrac = Calculation(PhotonEMCalibHitFrac, CalibHitBranches)

def PhotonHADCalibHitFrac(trk):
    return (trk["trk_TotalPhotonBackgroundCalibHitEnergy_HAD_200"] ) / TotalCalibHitEnergyHAD(trk)
calc_PhotonHADCalibHitFrac = Calculation(PhotonHADCalibHitFrac, CalibHitBranches)

def HadronCalibHitFrac(trk):
    return (trk["trk_TotalHadronicBackgroundCalibHitEnergy_EM_200"] + trk["trk_TotalHadronicBackgroundCalibHitEnergy_HAD_200"]) / TotalCalibHitEnergy(trk)
calc_HadronCalibHitFrac = Calculation(HadronCalibHitFrac, CalibHitBranches)

def HadronEMCalibHitFrac(trk):
    return (trk["trk_TotalHadronicBackgroundCalibHitEnergy_EM_200"] )/ TotalCalibHitEnergyEM(trk)
calc_HadronEMCalibHitFrac = Calculation(HadronEMCalibHitFrac, CalibHitBranches)

def HadronHADCalibHitFrac(trk):
    return (trk["trk_TotalHadronicBackgroundCalibHitEnergy_HAD_200"] )/ TotalCalibHitEnergyHAD(trk)
calc_HadronHADCalibHitFrac = Calculation(HadronHADCalibHitFrac, CalibHitBranches)

def HadFrac(trk):
    return (trk["trk_ClusterEnergy_HAD_200"]) / (trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"])
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200"]
calc_HadFrac = Calculation(HadFrac, branches)

def MomentumHadFrac(trk):
    return (trk["trk_ClusterEnergy_HAD_200"])/trk["trk_p"]
branches = ["trk_ClusterEnergy_HAD_200", "trk_p"]
calc_MomentumHadFrac = Calculation(MomentumHadFrac, branches)

def EnergyEMDR100(trk):
    return (trk["trk_ClusterEnergy_EM_100"])
branches = ["trk_ClusterEnergy_EM_100"]
calc_EnergyEMDR100 = Calculation(EnergyEMDR100, branches)

def nTRT(trk):
    return trk["trk_nTRT"]
branches = ["trk_nTRT"]
calc_nTRT = Calculation(nTRT, branches)

def trkCount(trk):
    return np.zeros(len(trk))
branches = []
calc_trkCount = Calculation(trkCount, branches)

def trkNClusters_template(trk, rad1, rad2):
    nclusters_EM = trk["trk_nclusters_EM_" + rad1] - trk["trk_nclusters_EM_" + rad2]
    nclusters_HAD = trk["trk_nclusters_HAD_" + rad1] - trk["trk_nclusters_HAD_" + rad2]
    return nclusters_EM + nclusters_HAD

def trkNClusters(trk):
    return trk["trk_nclusters_EM_200"] + trk["trk_nclusters_HAD_200"]
calc_trkNClusters = Calculation(trkNClusters, ["trk_nclusters_EM_200", "trk_nclusters_HAD_200"])

def trkNClusters_EM(trk):
    return trk["trk_nclusters_EM_200"]
calc_trkNClusters_EM = Calculation(trkNClusters_EM, ["trk_nclusters_EM_200"])

def trkNClusters_emlike(trk):
    return trk["trk_nclusters_EM_emlike_200"] + trk["trk_nclusters_HAD_emlike_200"]
calc_trkNClusters_emlike = Calculation(trkNClusters_emlike, ["trk_nclusters_EM_emlike_200","trk_nclusters_HAD_emlike_200"])

def trkNClusters_HAD(trk):
    return trk["trk_nclusters_HAD_200"]
calc_trkNClusters_HAD = Calculation(trkNClusters_HAD, ["trk_nclusters_HAD_200"])

def trkNClusters_hadlike(trk):
    return trk["trk_nclusters_EM_hadlike_200"] + trk["trk_nclusters_HAD_hadlike_200"]
calc_trkNClusters_hadlike = Calculation(trkNClusters_hadlike, ["trk_nclusters_EM_hadlike_200", "trk_nclusters_HAD_hadlike_200"])

def trkHADFraction(trk):
    return_value = np.zeros(len(trk))
    return_value = (trk["trk_ClusterEnergy_HAD_200"])/(trk["trk_ClusterEnergy_HAD_200"] + trk["trk_ClusterEnergy_EM_200"])
    return return_value
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200"]
calc_trkHADFraction = Calculation(trkHADFraction, branches)

def trkEMFraction(trk):
    return_value = np.zeros(len(trk))
    return_value = trk["trk_ClusterEnergy_EM_200"]/(trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"])
    return return_value
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200"]
calc_trkEMFraction = Calculation(trkEMFraction, branches)

def trkPt(trk):
    return trk["trk_pt"]
branches = ["trk_pt"]
calc_trkPt = Calculation(trkPt, branches)

def trkEtaID(trk):
    return trk["trk_etaID"]
branches = ["trk_etaID"]
calc_trkEta = Calculation(trkEtaID, branches)

def trkEtaID_ABS(trk):
    return np.abs(trk["trk_etaID"])
branches = ["trk_etaID"]
calc_trkEta_ABS = Calculation(trkEtaID_ABS, branches)

def trkEtaPhiECAL(trk):
    trk_etaEMB = trk["trk_etaEMB2"]
    trk_phiEMB = trk["trk_phiEMB2"]
    trk_etaEME = trk["trk_etaEME2"]
    trk_phiEME = trk["trk_phiEME2"]

    has_barrel_extrap = np.abs(trk_etaEMB) < 1000.0
    has_endcap_extrap = np.abs(trk_etaEME) < 1000.0

    has_both = has_barrel_extrap & has_endcap_extrap
    has_one = np.logical_not(has_both) & (has_endcap_extrap | has_barrel_extrap)

    #this will be the eta coordinates used to calculate the acceptance
    trk_eta = np.ones(len(trk)) * 99999999.0
    trk_phi = np.ones(len(trk)) * 99999999.0

    #if there is only one extrapolated coordinate, then it is easy
    trk_eta[has_one & has_barrel_extrap] = trk_etaEMB[has_one & has_barrel_extrap]
    trk_phi[has_one & has_barrel_extrap] = trk_phiEMB[has_one & has_barrel_extrap]
    trk_eta[has_one & has_endcap_extrap] = trk_etaEME[has_one & has_endcap_extrap]
    trk_phi[has_one & has_endcap_extrap] = trk_phiEME[has_one & has_endcap_extrap]

    #if there are two extrapolated coordinates, take the one in the barrel
    trk_eta[has_both] = trk_etaEMB[has_both]
    trk_phi[has_both] = trk_phiEMB[has_both]

    return trk_eta, trk_phi

def trkEtaECAL(trk):
    return trkEtaPhiECAL(trk)[0]
branches = ["trk_etaEMB2","trk_etaEME2", "trk_phiEMB2", "trk_phiEME2"]
calc_trkEtaECAL = Calculation(trkEtaECAL, branches)

def trkPhiECAL(trk):
    return trkEtaPhiECAL(trk)[1]
branches = ["trk_phiEMB2","trk_phiEME2", "trk_etaEMB2","trk_etaEME2"]
calc_trkPhiECAL = Calculation(trkPhiECAL, branches)

def trkNearestNeighbourEM2(trk):
    return trk["trk_nearest_dR_EM"]
branches = ["trk_nearest_dR_EM"]
calc_trkNearestNeighbourEM2 =  Calculation(trkNearestNeighbourEM2, branches)

def trkNPV2(trk):
    return trk["trk_NPV_2"]
branches = ["trk_NPV_2"]
calc_trkNPV2 = Calculation(trkNPV2, branches)

def trkNPV4(trk):
    return trk["trk_NPV_4"]
branches = ["trk_NPV_4"]
calc_trkNPV4 = Calculation(trkNPV4, branches)

def trkAverageMu(trk):
    return trk["trk_averagemu"]
branches = ["trk_averagemu"]
calc_trkAverageMu = Calculation(trkAverageMu, branches)

def trkP(trk):
    return trk["trk_p"]
branches = ["trk_p"]
calc_trkP = Calculation(trkP, branches)

def trkEtaID(trk):
    return trk["trk_etaID"]
branches = ["trk_etaID"]
calc_trkEtaID = Calculation(trkEtaID, branches)

def trkEtaEME2(trk):
    return trk["trk_etaEME2"]
branches = ["trk_etaEME2"]
calc_trkEtaEME2 = Calculation(trkEtaEME2, branches)

def trkEtaEMB2(trk):
    return trk["trk_etaEMB2"]
branches = ["trk_etaEMB2"]
calc_trkEtaEMB2 = Calculation(trkEtaEMB2, branches)

cone_strings = ["000","025", "050", "075", "100", "125", "150", "175", "200", "225", "250", "275", "300"]
def total_energy_annulus_template(trk, min_cone, max_cone):
    assert min_cone in cone_strings
    assert max_cone in cone_strings
    assert int(min_cone) < int(max_cone)

    if int(min_cone) < 24:
        lower_sum = np.zeros(len(trk))
    else:
        lower_sum = trk["trk_ClusterEnergy_EM_{}".format(min_cone)] + trk["trk_ClusterEnergy_HAD_{}".format(min_cone)]

    upper_sum = trk["trk_ClusterEnergy_EM_{}".format(max_cone)] + trk["trk_ClusterEnergy_HAD_{}".format(max_cone)]

    return upper_sum - lower_sum

def EnergyAnulus(trk):
    return trk["trk_ClusterEnergy_EM_200"] - trk["trk_ClusterEnergy_EM_100"]
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_EM_100"]
calc_EnergyAnulus = Calculation(EnergyAnulus, branches)

def EnergyAnulusUp(trk):
    return trk["trk_ClusterEnergy_EM_200"] - trk["trk_ClusterEnergy_EM_125"]
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_EM_125"]
calc_EnergyAnulusUp = Calculation(EnergyAnulusUp, branches)

def EnergyAnulusDown(trk):
    return trk["trk_ClusterEnergy_EM_175"] - trk["trk_ClusterEnergy_EM_100"]
branches = ["trk_ClusterEnergy_EM_175", "trk_ClusterEnergy_EM_100"]
calc_EnergyAnulusDown = Calculation(EnergyAnulusDown, branches)

def EOPBkg(trk):
    return (1./trk["trk_p"]) * ( (0.2**2)/( (0.2**2) - (0.1**2) )) * (EnergyAnulus(trk))
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_EM_100", "trk_p"]
calc_EOPBkg = Calculation(EOPBkg, branches)

def EOPBkgUp(trk):
    return (1./trk["trk_p"]) * ( (0.2**2)/( (0.2**2) - (0.125**2) )) * (EnergyAnulusUp(trk))
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_EM_125", "trk_p"]
calc_EOPBkgUp = Calculation(EOPBkgUp, branches)

def EOPBkgDown(trk):
    return (1./trk["trk_p"]) * ( (0.2**2)/( (0.175**2) - (0.1**2) )) * (EnergyAnulusDown(trk))
branches = ["trk_ClusterEnergy_EM_175", "trk_ClusterEnergy_EM_100", "trk_p"]
calc_EOPBkgDown = Calculation(EOPBkgDown, branches)

def EnergyBigAnulus(trk):
    return trk["trk_ClusterEnergy_EM_275"] - trk["trk_ClusterEnergy_EM_200"]
branches = ["trk_ClusterEnergy_EM_275", "trk_ClusterEnergy_EM_200"]
calc_EnergyBigAnulus = Calculation(EnergyBigAnulus, branches)

def EnergyBigAnulusUp(trk):
    return trk["trk_ClusterEnergy_EM_275"] - trk["trk_ClusterEnergy_EM_225"]
branches = ["trk_ClusterEnergy_EM_275", "trk_ClusterEnergy_EM_225"]
calc_EnergyBigAnulusUp = Calculation(EnergyBigAnulusUp, branches)

def EnergyBigAnulusDown(trk):
    return trk["trk_ClusterEnergy_EM_275"] - trk["trk_ClusterEnergy_EM_225"]
branches = ["trk_ClusterEnergy_EM_275", "trk_ClusterEnergy_EM_225"]
calc_EnergyBigAnulusDown = Calculation(EnergyBigAnulusDown, branches)

def EOPBigBkgUp(trk):
    return (1./trk["trk_p"]) * ( (0.2**2)/( (0.275**2) - (0.225**2) )) * (EnergyBigAnulusUp(trk))
branches = ["trk_ClusterEnergy_EM_275", "trk_ClusterEnergy_EM_225", "trk_p"]
calc_EOPBigBkgUp = Calculation(EOPBigBkgUp, branches)

def EOPBigBkgDown(trk):
    return (1./trk["trk_p"]) * ( (0.2**2)/( (0.25**2) - (0.2**2) )) * (EnergyBigAnulusDown(trk))
branches = ["trk_ClusterEnergy_EM_250", "trk_ClusterEnergy_EM_200", "trk_p"]
calc_EOPBigBkgDown = Calculation(EOPBigBkgDown, branches)

def EOPBigBkg(trk):
    return (1./trk["trk_p"]) * ( (0.2**2)/( (0.275**2) - (0.2**2) )) * (EnergyBigAnulus(trk))
branches = ["trk_ClusterEnergy_EM_275", "trk_ClusterEnergy_EM_200", "trk_p"]
calc_EOPBigBkg = Calculation(EOPBigBkg, branches)

def EOP(trk):
    return (trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"])/trk["trk_p"]
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200", "trk_p"]
calc_EOP = Calculation(EOP, branches)

def LCW_EOP(trk):
    return (trk["trk_LCWClusterEnergy_EM_200"] + trk["trk_LCWClusterEnergy_HAD_200"])/trk["trk_p"]
branches = ["trk_LCWClusterEnergy_EM_200", "trk_LCWClusterEnergy_HAD_200", "trk_p"]
calc_LCW_EOP = Calculation(LCW_EOP, branches)

def DPhi(trk):
    dphi = np.ones(len(trk)) * 100000000.0
    hasEMB2 = np.abs(trk["trk_phiEMB2"]) < 40
    hasEME2 = np.abs(trk["trk_phiEME2"]) < 40

    dphi[hasEME2] = np.abs(trk["trk_phiID"] - trk["trk_phiEME2"])[hasEME2]
    dphi[hasEMB2] = np.abs(trk["trk_phiID"] - trk["trk_phiEMB2"])[hasEMB2]
    greater_than_pi = dphi > pi

    dphi[greater_than_pi] = 2.0 * pi - dphi[greater_than_pi]
    return dphi
branches = ["trk_phiEMB2", "trk_phiEME2","trk_phiID"]
calc_trkDPhi = Calculation(DPhi, branches)

def DEta(trk):
    deta = np.ones(len(trk)) * 100000000.0
    hasEMB2 = np.abs(trk["trk_etaEMB2"]) < 40
    hasEME2 = np.abs(trk["trk_etaEME2"]) < 40

    deta[hasEME2] = np.abs(trk["trk_etaID"] - trk["trk_etaEME2"])[hasEME2]
    deta[hasEMB2] = np.abs(trk["trk_etaID"] - trk["trk_etaEMB2"])[hasEMB2]
    return deta
branches = ["trk_etaEMB2", "trk_etaEME2","trk_etaID"]
calc_trkDEta = Calculation(DEta, branches)

def transverse_energy(trk):
    return (trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"]) / np.cosh(trk["trk_etaID"])
branches = ["trk_etaID", "trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200"]
calc_transverse_energy = Calculation(transverse_energy, branches)

def transverse_energy_lcw(trk):
    return (trk["trk_LCWClusterEnergy_EM_200"] + trk["trk_LCWClusterEnergy_HAD_200"]) / np.cosh(trk["trk_etaID"])
branches = ["trk_etaID", "trk_LCWClusterEnergy_EM_200", "trk_LCWClusterEnergy_HAD_200"]
calc_transverse_energy_lcw = Calculation(transverse_energy_lcw, branches)

def weight(trk, isData):
    if not isData:
        return trk["trkWeight"]
    return np.ones(len(trk))
branches = ["trkWeight"]
calc_weight = WeightCalculation(weight, branches)
