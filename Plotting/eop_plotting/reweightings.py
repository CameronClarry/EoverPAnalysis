import os
import ROOT
from selections import sel_HardScatter, ParticlePDGID_ABS, ParticlePDGID, sel_TightIso, sel_Event
from selections import EtaBin, PBin, sel_SubleadingTrack, sel_Event, sel_hasHADExtrapolation, NTRTX
from eop_plotting.histogram_filling import HistogramFiller, get_p, get_bins, get_log_bins, create_selection_function, create_inverse_selection_function
from eop_plotting.eop_histograms import put_binning_vectors_in_file, create_eop_histograms
from eop_plotting.track_spectrum_plots import create_spectrum_plots

#create the functions that select tracks in the different eta bins
eta_bin_edges = [0.0, 0.2, 0.7, 1.3, 1.8, 2.5]
eta_bin_tuples = [(eta_bin_edges[i], eta_bin_edges[i+1]) for i in range(0, len(eta_bin_edges)-1)]
eta_bin_descriptions = ["eta_extrapol00_02", "eta_extrapol02_07", "eta_extrapol07_13", "eta_extrapol13_18", "eta_extapol18_25"]
eta_bin_branches = ["trk_etaEMB2","trk_etaEME2","trk_phiEMB2", "trk_phiEME2"]
eta_bin_selections = [create_selection_function(EtaBin, eta_bin_branches, eta_bin_tuple[0], eta_bin_tuple[1]) for eta_bin_tuple in eta_bin_tuples]
sel_Pion = create_selection_function(ParticlePDGID_ABS, ["trk_truthPdgId"], 211.0)
sel_PionPos = create_selection_function(ParticlePDGID, ["trk_truthPdgId"], 211.0)
sel_PionNeg = create_selection_function(ParticlePDGID, ["trk_truthPdgId"], -211.0)
sel_KaonPos = create_selection_function(ParticlePDGID, ["trk_truthPdgId"], 321.0)
sel_KaonNeg = create_selection_function(ParticlePDGID, ["trk_truthPdgId"], -321.0)
sel_ProtonPos = create_selection_function(ParticlePDGID, ["trk_truthPdgId"], 2212.0)
sel_ProtonNeg = create_selection_function(ParticlePDGID, ["trk_truthPdgId"], -2212.0)
sel_Other = create_inverse_selection_function([sel_PionPos, sel_PionNeg, sel_KaonPos, sel_KaonNeg, sel_ProtonPos, sel_ProtonNeg], name="sel_other")

pion_selections = [sel_Pion, sel_HardScatter]
pion_pos_selections = [sel_PionPos, sel_HardScatter]
pion_neg_selections = [sel_PionNeg, sel_HardScatter]
kaon_pos_selections = [sel_KaonPos, sel_HardScatter]
kaon_neg_selections = [sel_KaonNeg, sel_HardScatter]
proton_pos_selections = [sel_ProtonPos, sel_HardScatter]
proton_neg_selections = [sel_ProtonNeg, sel_HardScatter]
other_selections = [sel_Other, sel_HardScatter]
sel_Truth = [sel_HardScatter]
sel_TightIso = [sel_TightIso]

def book_reweighting(hist_filler, reweighting_flavour):
    base_directory = os.getenv("EOPPlottingDir")
    if reweighting_flavour == "nominal":
      from variables import calc_trkNearestNeighbourEM2, calc_trkP, calc_EOP, calc_trkPt, calc_trkAverageMu, calc_trkEtaID, calc_trkEtaECAL, calc_trkNPV2, calc_trkCount, calc_trkNClusters, calc_trkNClusters_EM, calc_trkNClusters_HAD, calc_trkNClusters_emlike, calc_trkNClusters_hadlike, calc_TruthMomentum, calc_trkEta

      LowMuData_PythiaJetJet_Count_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuData_PythiaJetJet_Count_Reweight.root"),"READ")
      hist = LowMuData_PythiaJetJet_Count_Reweight_file.Get("LowMuData_PythiaJetJet_Count_Reweight")
      hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJet", [calc_trkCount], hist, selection = [sel_Event])

      LowMuData_PythiaJetJetHardScatter_Count_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuData_PythiaJetJetHardScatter_Count_Reweight.root"),"READ")
      hist = LowMuData_PythiaJetJetHardScatter_Count_Reweight_file.Get("LowMuData_PythiaJetJetHardScatter_Count_Reweight")
      hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetHardScatter", [calc_trkCount], hist, selection = [sel_Event])

      LowMuDataTightIso_PythiaJetJetTightIso_Count_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuDataTightIso_PythiaJetJetTightIso_Count_Reweight.root"),"READ")
      hist = LowMuDataTightIso_PythiaJetJetTightIso_Count_Reweight_file.Get("LowMuDataTightIso_PythiaJetJetTightIso_Count_Reweight")
      hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetTightIso", [calc_trkCount], hist, selection = [sel_Event])

      LowMuDataTightIso_PythiaJetJetHardScatterTightIso_Count_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuDataTightIso_PythiaJetJetHardScatterTightIso_Count_Reweight.root"),"READ")
      hist = LowMuDataTightIso_PythiaJetJetHardScatterTightIso_Count_Reweight_file.Get("LowMuDataTightIso_PythiaJetJetHardScatterTightIso_Count_Reweight")
      hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetHardScatterTightIso", [calc_trkCount], hist, selection = [sel_Event])

      #### do and NPV reweighting, too
      #LowMuData_PythiaJetJet_NPV2Hist_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuData_PythiaJetJet_NPV2Hist_Reweight.root"),"READ")
      #hist = LowMuData_PythiaJetJet_NPV2Hist_Reweight_file.Get("LowMuData_PythiaJetJet_NPV2Hist_Reweight")
      #hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJet", calc_trkNPV2, hist, selection = [sel_Event])

      #LowMuData_PythiaJetJetHardScatter_NPV2Hist_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuData_PythiaJetJetHardScatter_NPV2Hist_Reweight.root","READ")
      #hist = LowMuData_PythiaJetJetHardScatter_NPV2Hist_Reweight_file.Get("LowMuData_PythiaJetJetHardScatter_NPV2Hist_Reweight")
      #hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetHardScatter", calc_trkNPV2, hist, selection = [sel_Event])

      #LowMuDataTightIso_PythiaJetJetTightIso_NPV2Hist_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuDataTightIso_PythiaJetJetTightIso_NPV2Hist_Reweight.root"),"READ")
      #hist = LowMuDataTightIso_PythiaJetJetTightIso_NPV2Hist_Reweight_file.Get("LowMuDataTightIso_PythiaJetJetTightIso_NPV2Hist_Reweight")
      #hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetTightIso", calc_trkNPV2, hist, selection = [sel_Event])

      #LowMuDataTightIso_PythiaJetJetHardScatterTightIso_NPV2Hist_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuDataTightIso_PythiaJetJetHardScatterTightIso_NPV2Hist_Reweight.root"),"READ")
      #hist = LowMuDataTightIso_PythiaJetJetHardScatterTightIso_NPV2Hist_Reweight_file.Get("LowMuDataTightIso_PythiaJetJetHardScatterTightIso_NPV2Hist_Reweight")
      #hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetHardScatterTightIso", calc_trkNPV2, hist, selection = [sel_Event])


      #hist_filler.create_subchannel_for_channel("LowMuDataHadIso","LowMuData", [sel_HadIso]) #Tighter isolation requirement
      #hist_filler.create_subchannel_for_channel("PythiaJetJetHadIso","PythiaJetJet", [sel_HadIso]) #Tighter isolation requirement
      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterPionPos", "PythiaJetJetHardScatter", pion_pos_selections)
      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterPionNeg", "PythiaJetJetHardScatter", pion_neg_selections)

      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterKaonPos", "PythiaJetJetHardScatter", kaon_pos_selections)
      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterKaonNeg", "PythiaJetJetHardScatter", kaon_neg_selections)

      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterProtonPos", "PythiaJetJetHardScatter", proton_pos_selections)
      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterProtonNeg", "PythiaJetJetHardScatter", proton_neg_selections)

      hist_filler.create_subchannel_for_channel("PythiaJetJetHardScatterOther", "PythiaJetJetHardScatter", other_selections)


      for i, eta_bin_selection in enumerate(eta_bin_selections):
         spectrum_reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/PtSpectrumReweightLowMuDataOverPythiaJetJet_Eta"+str(i)+".root"),"READ")
         hist = spectrum_reweight_file.Get("PtSpectrumReweightLowMuDataOverPythiaJetJet_Eta"+str(i))
         hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJet", [calc_trkPt], hist, selection=[eta_bin_selection]) 

         spectrum_reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/PtSpectrumReweightLowMuDataTightIsoOverPythiaJetJetTightIso_Eta"+str(i)+".root"),"READ")
         hist = spectrum_reweight_file.Get("PtSpectrumReweightLowMuDataTightIsoOverPythiaJetJetTightIso_Eta"+str(i))
         hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetTightIso", [calc_trkPt], hist, selection=[eta_bin_selection]) 

         spectrum_reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/PtSpectrumReweightLowMuDataOverPythiaJetJetHardScatter_Eta"+str(i)+".root"),"READ")
         hist = spectrum_reweight_file.Get("PtSpectrumReweightLowMuDataOverPythiaJetJetHardScatter_Eta"+str(i))
         hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetHardScatter", [calc_trkPt], hist, selection=[eta_bin_selection]) 

         spectrum_reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/PtSpectrumReweightLowMuDataTightIsoOverPythiaJetJetHardScatterTightIso_Eta"+str(i)+".root"),"READ")
         hist = spectrum_reweight_file.Get("PtSpectrumReweightLowMuDataTightIsoOverPythiaJetJetHardScatterTightIso_Eta"+str(i))
         hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJetHardScatterTightIso", [calc_trkPt], hist, selection=[eta_bin_selection]) 

      spectrum_reweight_file = ROOT.TFile(os.path.join(base_directory, "ReweightingHistograms/TruthPSpectrumReweightPythiaJetJetHardScatterPionPosOverSinglePionPos.root"), "READ")
      hist = spectrum_reweight_file.Get("TruthPSpectrumReweightPythiaJetJetHardScatterPionPosOverSinglePionPos")
      hist_filler.weight_calculator.add_reweight_histogram("SinglePionPos", [calc_TruthMomentum, calc_trkEta], hist) 

      spectrum_reweight_file = ROOT.TFile(os.path.join(base_directory, "ReweightingHistograms/TruthPSpectrumReweightPythiaJetJetHardScatterPionNegOverSinglePionNeg.root"), "READ")
      hist = spectrum_reweight_file.Get("TruthPSpectrumReweightPythiaJetJetHardScatterPionNegOverSinglePionNeg")
      hist_filler.weight_calculator.add_reweight_histogram("SinglePionNeg", [calc_TruthMomentum, calc_trkEta], hist) 
