from histogram_manager import HistogramManager
import ROOT
from plotting_tools import *
from common_plots import *
from array import array
import os

MCKeys = ['PythiaJetJet', "SinglePion"]#,"SinglePion","PythiaJetJetHardScatter"]
DataKey = "LowMuData"
#, 'PythiaJetJetPionsReweighted'
#, 'SinglePion']

global_scope = []
ROOT.gROOT.SetBatch(ROOT.kFALSE)
#ROOT.gStyle.SetImageScaling(2.)

def CloseCanvas(canv):
    canv.Close()
    ROOT.gSystem.ProcessEvents()
    del canv

#filename = "event_npv2_reweighted.root"
filename = "pt_reweighted.root"
#filename = 

HM = HistogramManager(filename)
HM.listHistograms("*")

base_description = []
if "Count" in filename:
    base_description = []
if ("Pt" in filename or "pt" in filename) and "weight" in filename:
    base_description = ["P_{T} Reweighted"]
if "npv2" in filename and "weight" in filename:
    base_description = ["NPV Reweighted"]
channelLabels = {"SinglePion": "Single Pion", "PythiaJetJet" : "#splitline{Pythia8}{MinBias and Dijet}", DataKey: "2017 Low-<#mu> Data", "PythiaJetJetPionsReweighted":"Pythia8 MB+DJ Pions Only", "PythiaJetJetHardScatter":"Pythia8 MB+DJ Truth Matched", "PythiaJetJetTightIso": "#splitline{Pythia8}{MinBias and Dijet}", "LowMuDataTightIso":"2017 Low-<#mu> Data"}

plotting_directory = (filename.split("/")[-1]).replace(".root","") + "plots"

if not os.path.exists("Plots"):
    os.makedirs("Plots")
if not os.path.exists("Plots/" + plotting_directory):
    os.makedirs("Plots/" + plotting_directory)
plotting_directory = "Plots/" + plotting_directory

if "SinglePion" in MCKeys:
    plotting_directory += "_single_pion"

histogram_name_base = "EnergyBkgProfileVsMomentum__{}_Eta_{}"
histogram_name_base_up = "EnergyBkgUpProfileVsMomentum__{}_Eta_{}"
histogram_name_base_down = "EnergyBkgDownProfileVsMomentum__{}_Eta_{}"
selection = "MIPSelectionHadFracAbove70"
bins = range(0, 5)

#get the binning vectors
rf = ROOT.TFile(filename, "READ")

tree = rf.Get(selection + "BinningTree")
for el in tree:
    break

eta_bins_low = getattr(el, selection+"EtaBinsLow")
eta_bins_high = getattr(el, selection+"EtaBinsHigh")

from variables import cone_strings

for i in bins:
    break
    histogram_name = histogram_name_base.format(selection, i)
    histogram_name_up = histogram_name_base_up.format(selection, i)
    histogram_name_down = histogram_name_base_down.format(selection, i)
    hist = HM.getHistograms(histogram_name)
    hist_up = HM.getHistograms(histogram_name_up)
    hist_down = HM.getHistograms(histogram_name_down)

    for channel in ["LowMuData", "PythiaJetJet"]:
       #create a set of plots comparing the background subtraction methods
       to_plot= {}
       to_plot["nominal"] = hist[channel]
       to_plot["up"] = hist_up[channel]
       to_plot["down"] = hist_down[channel]
       these_MCKeys = ["up", "down"]
       these_DataKey = "nominal"
       to_plot = ProjectProfiles(to_plot)
       these_channelLabels = {"nominal":"Nominal", "up":"Outer Annulus", "down":"Inner Annulus"}
       description = base_description + ["MIP Selection"] + ["{:.1f} < |#eta| < {:.1f}".format(eta_bins_low[i], eta_bins_high[i])]
       DataVsMC1 = DrawDataVsMC(to_plot,\
                               these_channelLabels,\
                               MCKeys = these_MCKeys,\
                               DataKey = these_DataKey,\
                               ratio_min=0.9,\
                               ratio_max=1.1,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>_{BKG}",\
                               ratio_label = "Nom./Var.",\
                               extra_description = description)
       DataVsMC1[0].Draw()
       DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + "{}SystVar.png".format(channel))
       DataVsMC1[0].Close()

    hist_dict = {}
    base = "EOPProfileVsMomentum_{}_{}" +"__" + selection + "_Eta_"+str(i)
    nominal = "EOPProfileVsMomentum"  +"__" + selection + "_Eta_"+str(i)
    other_keys = []
    j = 0
    for low,high in zip(cone_strings[:-1], cone_strings[1:]):
        j += 1
        if j == 9:
            break
        histogram_name = base.format(low, high)
        key = "{}_{}".format(low,high)
        other_keys.append(key)
        hist_dict[key] = HM.getHistograms(histogram_name)

    hist_dict["nominal"] = HM.getHistograms(nominal)

    for channel in ["LowMuData", "PythiaJetJet"]:
        to_plot = {}
        for key in hist_dict:
            to_plot[key] = hist_dict[key][channel]
            these_MCKeys = other_keys
            these_DataKey = "nominal"
            these_channelLabels = {"nominal":"Nominal"}
            for key in these_MCKeys:
                low, high = key.split("_")
                low, high = int(low), int(high)
                low = float(low)/1000.0
                high = float(high)/1000.0
                these_channelLabels[key] = "["+str(low)+","+str(high)+"]"
        to_plot = ProjectProfiles(to_plot)
        DataVsMC1 = DrawDataVsMC(to_plot,\
                               these_channelLabels,\
                               MCKeys = these_MCKeys,\
                               DataKey = these_DataKey,\
                               ratio_min=0.0,\
                               ratio_max=1.0,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>",\
                               ratio_label = "Ann./Nom.",\
                               invert_ratio = True,\
                               skip_ratio = True,\
                               bigger_legend = True,\
                               skip_data = True,\
                               extra_description = description)
        DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + "{}Cones.png".format(channel))

    hist_dict = {}
    base = "EOPProfileVsMomentum_{}_{}_Area" +"__" + selection + "_Eta_"+str(i)
    nominal = "EOPProfileVsMomentum"  +"__" + selection + "_Eta_"+str(i)
    other_keys = []
    j = 0
    for low,high in zip(cone_strings[:-1], cone_strings[1:]):
        j += 1
        if j == 9:
            break
        histogram_name = base.format(low, high)
        key = "{}_{}".format(low,high)
        other_keys.append(key)
        hist_dict[key] = HM.getHistograms(histogram_name)

    hist_dict["nominal"] = HM.getHistograms(nominal)

    for channel in ["LowMuData", "PythiaJetJet"]:
        to_plot = {}
        for key in hist_dict:
            to_plot[key] = hist_dict[key][channel]
            these_MCKeys = other_keys
            these_DataKey = "nominal"
            these_channelLabels = {"nominal":"Nominal"}
            for key in these_MCKeys:
                low, high = key.split("_")
                low, high = int(low), int(high)
                low = float(low)/1000.0
                high = float(high)/1000.0
                these_channelLabels[key] = "["+str(low)+","+str(high)+"]"
        to_plot = ProjectProfiles(to_plot)
        DataVsMC1 = DrawDataVsMC(to_plot,\
                               these_channelLabels,\
                               MCKeys = these_MCKeys,\
                               DataKey = these_DataKey,\
                               ratio_min=0.0,\
                               ratio_max=1.0,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>/Area",\
                               ratio_label = "Ann./Nom.",\
                               invert_ratio = True,\
                               skip_ratio = True,\
                               bigger_legend = True,\
                               skip_data = True,\
                               extra_description = description)
        DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + "{}Cones.png".format(channel))

histogram_name_base = "EnergyBigBkgProfileVsMomentum__{}_Eta_{}"
histogram_name_base_up = "EnergyBigBkgUpProfileVsMomentum__{}_Eta_{}"
histogram_name_base_down = "EnergyBigBkgDownProfileVsMomentum__{}_Eta_{}"
selection = "20TRTHitsNonZeroEnergy"
bins = range(0, 5)

#get the binning vectors
rf = ROOT.TFile(filename, "READ")

tree = rf.Get(selection + "BinningTree")
for el in tree:
    break

eta_bins_low = getattr(el, selection+"EtaBinsLow")
eta_bins_high = getattr(el, selection+"EtaBinsHigh")

for i in bins:
    break
    histogram_name = histogram_name_base.format(selection, i)
    histogram_name_up = histogram_name_base_up.format(selection, i)
    histogram_name_down = histogram_name_base_down.format(selection, i)
    hist = HM.getHistograms(histogram_name)
    hist_up = HM.getHistograms(histogram_name_up)
    hist_down = HM.getHistograms(histogram_name_down)

    for channel in ["LowMuDataTightIso", "PythiaJetJetTightIso"]:
       #create a set of plots comparing the background subtraction methods
       to_plot= {}
       to_plot["nominal"] = hist[channel]
       to_plot["up"] = hist_up[channel]
       to_plot["down"] = hist_down[channel]
       these_MCKeys = ["up", "down"]
       these_DataKey = "nominal"

       to_plot = ProjectProfiles(to_plot)

       these_channelLabels = {"nominal":"Nominal", "up":"Outer Annulus", "down":"Inner Annulus"}
       description = base_description + ["E_{TOTAL} != 0.0", "N_{TRT} >= 20", "Tight Isolation"] + ["{:.1f} < |#eta| < {:.1f}".format(eta_bins_low[i], eta_bins_high[i])]
       DataVsMC1 = DrawDataVsMC(to_plot,\
                               these_channelLabels,\
                               MCKeys = these_MCKeys,\
                               DataKey = these_DataKey,\
                               ratio_min=0.9,\
                               ratio_max=1.1,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>_{BKG}",\
                               ratio_label = "Nom./Var.",\
                               extra_description = description)
       DataVsMC1[0].Draw()
       DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + "{}SystVar.png".format(channel))
       DataVsMC1[0].Close()

    hist_dict = {}
    base = "EOPProfileVsMomentum_{}_{}" +"__" + selection + "_Eta_"+str(i)
    nominal = "EOPProfileVsMomentum"  +"__" + selection + "_Eta_"+str(i)
    other_keys = []
    j = 0
    for low,high in zip(cone_strings[:-1], cone_strings[1:]):
        j += 1
        if j == 9:
            break
        histogram_name = base.format(low, high)
        key = "{}_{}".format(low,high)
        other_keys.append(key)
        hist_dict[key] = HM.getHistograms(histogram_name)
    hist_dict["nominal"] = HM.getHistograms(nominal)

    for channel in ["LowMuDataTightIso", "PythiaJetJetTightIso"]:
        to_plot = {}
        to_plot = ProjectProfiles(to_plot)
        for key in hist_dict:
            to_plot[key] = hist_dict[key][channel]
            these_MCKeys = other_keys
            these_DataKey = "nominal"
            these_channelLabels = {"nominal":"Nominal"}
            for key in these_MCKeys:
                low, high = key.split("_")
                low, high = int(low), int(high)
                low = float(low)/1000.0
                high = float(high)/1000.0
                these_channelLabels[key] = "["+str(low)+","+str(high)+"]"
        DataVsMC1 = DrawDataVsMC(to_plot,\
                               these_channelLabels,\
                               MCKeys = these_MCKeys,\
                               DataKey = these_DataKey,\
                               ratio_min=0.0,\
                               ratio_max=1.0,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>",\
                               ratio_label = "Ann./Nom.",\
                               invert_ratio = True,\
                               skip_ratio = True,\
                               bigger_legend = True,\
                               skip_data = True,\
                               extra_description = description)
        DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + "{}Cones.png".format(channel))

    hist_dict = {}
    base = "EOPProfileVsMomentum_{}_{}_Area" +"__" + selection + "_Eta_"+str(i)
    nominal = "EOPProfileVsMomentum"  +"__" + selection + "_Eta_"+str(i)
    other_keys = []
    j = 0
    for low,high in zip(cone_strings[:-1], cone_strings[1:]):
        j += 1
        if j == 9:
            break
        histogram_name = base.format(low, high)
        key = "{}_{}".format(low,high)
        other_keys.append(key)
        hist_dict[key] = HM.getHistograms(histogram_name)
    hist_dict["nominal"] = HM.getHistograms(nominal)

    for channel in ["LowMuDataTightIso", "PythiaJetJetTightIso"]:
        to_plot = {}
        to_plot = ProjectProfiles(to_plot)
        for key in hist_dict:
            to_plot[key] = hist_dict[key][channel]
            these_MCKeys = other_keys
            these_DataKey = "nominal"
            these_channelLabels = {"nominal":"Nominal"}
            for key in these_MCKeys:
                low, high = key.split("_")
                low, high = int(low), int(high)
                low = float(low)/1000.0
                high = float(high)/1000.0
                these_channelLabels[key] = "["+str(low)+","+str(high)+"]"
        DataVsMC1 = DrawDataVsMC(to_plot,\
                               these_channelLabels,\
                               MCKeys = these_MCKeys,\
                               DataKey = these_DataKey,\
                               ratio_min=0.0,\
                               ratio_max=1.0,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>/Area",\
                               ratio_label = "Ann./Nom.",\
                               invert_ratio = True,\
                               skip_ratio = True,\
                               bigger_legend = True,\
                               skip_data = True,\
                               extra_description = description)
        DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + "{}Cones.png".format(channel))




CreateCompositionPlot(HM, plotting_directory)
#MCKeys = ['PythiaJetJet', "SinglePion"]#,"SinglePion","PythiaJetJetHardScatter"]
#CreateZeroFractionPlotsFromSelection(HM, "NonZeroEnergy", "Inclusive", filename, base_description= base_description + [], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=MCKeys, DataKey="LowMuData")
#CreateZeroFractionPlotsFromSelection(HM, "20TRTHitsNonZeroEnergy", "20TRTHits", filename, base_description= base_description + ["N_{TRT} >= 20"], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=MCKeys, DataKey = "LowMuData")
#CreateZeroFractionPlotsFromSelection(HM, "NonZeroEnergy", "Inclusive", filename, base_description= base_description + ["Tight Isolation"], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=["PythiaJetJetTightIso"], DataKey="LowMuDataTightIso")
#CreateZeroFractionPlotsFromSelection(HM, "20TRTHitsNonZeroEnergy", "20TRTHits", filename, base_description= base_description + ["N_{TRT} >= 20", "Tight Isolation"], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=["PythiaJetJetTightIso"], DataKey = "LowMuDataTightIso")

#test the plot creation
#CreatePlotsFromSelection(HM,"Inclusive", filename, base_description = base_description, channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=MCKeys)
#CreatePlotsFromSelection(HM,"Inclusive", filename, base_description = base_description, channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=["PythiaJetJet"], DataKey  = "LowMuData")
#CreatePlotsFromSelection(HM,"Inclusive", filename, base_description = base_description + ["Tight Isolation"], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=["PythiaJetJetTightIso"], DataKey  = "LowMuDataTightIso")
TwentyTRTNonZero_description = base_description + ["E_{TOTAL} != 0.0", "N_{TRT} >= 20", "Tight Isolation"]
CreatePlotsFromSelection(HM,"20TRTHitsNonZeroEnergy", filename, base_description = TwentyTRTNonZero_description, channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=["PythiaJetJetTightIso", "SinglePion"], DataKey  = "LowMuDataTightIso")
#CreatePlotsFromSelection(HM,"20TRTHitsNonZeroEnergy", filename, base_description = base_description + ["N_{TRT} >= 20", "E_{TOTAL} != 0.0"], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=MCKeys)
CreatePlotsFromSelection(HM,"MIPSelectionHadFracAbove70", filename, base_description = base_description + ["MIP Selection"],channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=MCKeys)
#CreatePlotsFromSelection(HM,"MIPSelectionHadFracAbove70", filename, base_description = base_description + ["MIP Selection", "Tight Isolation"], channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=["PythiaJetJetTightIso"], DataKey  = "LowMuDataTightIso")
#CreatePlotsFromSelection(HM,"NonZeroEnergy", filename, base_description = base_description + ["E_{TOTAL} != 0.0"],doFit = True , fitfunction="convolution", channelLabels=channelLabels,plotting_directory=plotting_directory, MCKeys=MCKeys)
#CreatePlotsFromSelection(HM,"Inclusive", filename, base_description = base_description + [],doFit = True,fitfunction="convolution", channelLabels=channelLabels,plotting_directory=plotting_directory)

#CreatePlotsFromSelection(HM,"20TRTHitsNonZeroEnergyHardScatter", filename, base_description = ["N_{TRT} >= 20", "E_{TOTAL} != 0.0"], doFit = True, channelLabels=channelLabels,plotting_directory=plotting_directory)
#CreatePlotsFromSelection(HM,"MIPSelectionHadFracAbove70HardScatter", filename, base_description = ["MIP Selection"],doFit=False, channelLabels=channelLabels,plotting_directory=plotting_directory)
#CreatePlotsFromSelection(HM,"NonZeroEnergyHardScatter", filename, base_description = ["E_{TOTAL} != 0.0"],doFit=False, channelLabels=channelLabels,plotting_directory=plotting_directory)
#CreatePlotsFromSelection(HM,"InclusiveHardScatter", filename, base_description = [],doFit=False, channelLabels=channelLabels,plotting_directory=plotting_directory)

#CreatePlotsFromSelection(HM,"20TRTHitsNonZeroEnergyHardScatterOnlyPion", filename, base_description = ["N_{TRT} >= 20", "E_{TOTAL} != 0.0"], doFit = True, channelLabels=channelLabels,plotting_directory=plotting_directory)
#CreatePlotsFromSelection(HM,"MIPSelectionHadFracAbove70HardScatterOnlyPion", filename, base_description = ["MIP Selection"],doFit=False, channelLabels=channelLabels,plotting_directory=plotting_directory)
#CreatePlotsFromSelection(HM,"NonZeroEnergyHardScatterOnlyPion", filename, base_description = ["E_{TOTAL} != 0.0"],doFit=False, channelLabels=channelLabels,plotting_directory=plotting_directory)
#CreatePlotsFromSelection(HM,"InclusiveHardScatterOnlyPion", filename, base_description = [],doFit=False, channelLabels=channelLabels,plotting_directory=plotting_directory)


if True:
        histogramName = "TwoDTrackPtVsEtaHistogram_HasExtrapolation"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC = Draw2DHistogramOnCanvas(hist["PythiaJetJet"], doLogx = False, doLogy = True)
        DataVsMC.Print(plotting_directory + "/PythiaJetJet" + histogramName + ".png")
        DataVsMC.Close()

        histogramName = "lowPTLess07_TwoDHistTrkEtavsDEtaInnerToExtrapolEM2"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC = Draw2DHistogramOnCanvas(hist["PythiaJetJet"], doLogx = False, doLogy = False, y_range=(0.01, 0.4))
        DataVsMC.Print(plotting_directory + "/PythiaJetJet" + histogramName + ".png")
        DataVsMC.Close()

        histogramName = "TrkEtaPhiEMCal_MomentumBetween3And4GeV_Denomenator"
        hist = HM.getHistograms(histogramName)
        DataVsMC = Draw2DHistogramOnCanvas(hist["PythiaJetJet"], doLogx = False, doLogy = False, x_range = (-1.0, +1.0), zlabel = "N(E!=0)")
        DataVsMC.Print(plotting_directory + "/PythiaJetJet" + histogramName + ".png")
        DataVsMC.Draw()
        DataVsMC.Close()
        DataVsMC = Draw2DHistogramOnCanvas(hist[DataKey], doLogx = False, doLogy = False, x_range = (-1.0, +1.0), zlabel = "N(E!=0)")
        DataVsMC.Print(plotting_directory + "/LowMuData" + histogramName + ".png")
        DataVsMC.Draw()
        DataVsMC.Close()
        hist_den = hist

        histogramName = "TrkEtaPhiEMCal_MomentumBetween3And4GeV_Numerator"
        hist = HM.getHistograms(histogramName)
        DataVsMC = Draw2DHistogramOnCanvas(hist["PythiaJetJet"], doLogx = False, doLogy = False, x_range = (-1.0, +1.0), zlabel = "N(E!=0)")
        DataVsMC.Print(plotting_directory + "/PythiaJetJet" + histogramName + ".png")
        DataVsMC.Draw()
        DataVsMC.Close()
        DataVsMC = Draw2DHistogramOnCanvas(hist[DataKey], doLogx = False, doLogy = False, x_range = (-1.0, +1.0), zlabel = "N(E!=0)")
        DataVsMC.Print(plotting_directory + "/LowMuData" + histogramName + ".png")
        DataVsMC.Draw()
        DataVsMC.Close()
        hist_num = hist

        ratio = DivideHistograms(hist_num, hist_den)
        DataVsMC = Draw2DHistogramOnCanvas(ratio["PythiaJetJet"], doLogx = False, doLogy = False, x_range = (-1.0, +1.0), zlabel = "N(E!=0)/N(Inclusive)")
        DataVsMC.Draw()
        DataVsMC.Print(plotting_directory + "/PythiaJetJet" + "TrkEtaPhiEMCal_MomentumBetween3And4GeV_ZeroFraction" + ".png")
        DataVsMC.Close()

        DataVsMC = Draw2DHistogramOnCanvas(ratio[DataKey], doLogx = False, doLogy = False, x_range = (-1.0, +1.0), zlabel = "N(E!=0)/N(Inclusive)")
        DataVsMC.Draw()
        DataVsMC.Print(plotting_directory + "/LowMuData" + "TrkEtaPhiEMCal_MomentumBetween3And4GeV_ZeroFraction" + ".png")
        DataVsMC.Close()

        histogramName = "trkAverageMu"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC1 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey= DataKey,\
                                ratio_min=0.6,\
                                ratio_max=1.4,\
                                extra_description = description)
        DataVsMC1[0].Draw()
        DataVsMC1[0].Print(plotting_directory + "/" + histogramName + ".png")
        DataVsMC1[0].Close()

        histogramName = "LeadingPtTrkHist"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC1 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                ratio_min=0.6,\
                                ratio_max=1.4,\
                                doLogx=True,\
                                xlabel="Leading Track P_{T} [GeV]",\
                                ylabel="Number of Events",\
                                extra_description = description)
        DataVsMC1[0].Draw()
        DataVsMC1[0].Print(plotting_directory + "/" + histogramName + ".png")
        DataVsMC1[0].Close()

        histogramName = "SubleadingPtTrkHist"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC1 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                ratio_min=0.0,\
                                ratio_max=2.0,\
                                doLogx=True,\
                                xlabel="Subleading Track P_{T} [GeV]",\
                                ylabel="Number of Events",\
                                extra_description = description)
        DataVsMC1[0].Draw()
        DataVsMC1[0].Print(plotting_directory + "/" + histogramName + ".png")
        DataVsMC1[0].Close()


        histogramName = "trkNPV2"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC3 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                extra_description = description)
        DataVsMC3[0].Draw()
        DataVsMC3[0].Print(plotting_directory + "/" + histogramName + ".png")
        DataVsMC3[0].Close()

        histogramName =  "eventNPV2Hist"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC5 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                ratio_min=0.2,\
                                ratio_max=1.8,\
                                extra_description = description)
        DataVsMC5[0].Draw()
        DataVsMC5[0].Print(plotting_directory + "/" + histogramName + ".png")

        histogramName =  "eventAverageMu"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC6 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                ratio_min=0.2,\
                                ratio_max=1.8,\
                                extra_description = description)
        DataVsMC6[0].Draw()
        DataVsMC6[0].Print(plotting_directory + "/" + histogramName + ".png")

        histogramName =  "InclusiveEOP"
        hist = HM.getHistograms(histogramName)
        description = base_description + ["Inclusive Selection"]
        DataVsMC7 = DrawDataVsMC(hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                extra_description = description)
        DataVsMC7[0].Draw()
        DataVsMC7[0].Print(plotting_directory + "/" + histogramName + ".png")


        for extraString in ["", "HasExtrapolation"]:
            histogramName = "trkPtHist" + extraString
            hist = HM.getHistograms(histogramName)
            description = base_description + ["Inclusive Selection"]
            DataVsMC4 = DrawDataVsMC(hist,\
                                    channelLabels,\
                                    MCKeys = MCKeys,\
                                    DataKey=DataKey,\
                                    doLogx = True,\
                                    doLogy = True,\
                                    ratio_min = 0.0,\
                                    ratio_max = 2.0,\
                                    extra_description = description)
            DataVsMC4[0].Draw()
            DataVsMC4[0].Print(plotting_directory + "/" + histogramName + ".png")



        histogramName_num =  "InclusiveZeroFractionVsPNumerator"
        hist_num = HM.getHistograms(histogramName_num)

        histogramName_den = "InclusiveZeroFractionVsPDenomenator"
        hist_den = HM.getHistograms(histogramName_den)
        ratio_hist = DivideHistograms(hist_num, hist_den)

        description = base_description + ["Inclusive Selection"]
        DataVsMC9 = DrawDataVsMC(ratio_hist,\
                                channelLabels,\
                                MCKeys = MCKeys,\
                                DataKey=DataKey,\
                                doLogx=True,
                                doLogy=False,
                                ratio_min = 0.8,\
                                ratio_max = 1.2,\
                                extra_description = description)
        DataVsMC9[0].Draw()
        DataVsMC9[0].Print(plotting_directory + "/" + histogramName_num.replace("Numerator", "") + ".png")

        for histogramName in ["EtaLess08_TwoDHistTrkPvsPhiInnerToExtrapolEM2", "TwoDHistTrkPvsPhiInnerToExtrapolEM2"]:

            description = base_description + ["|#eta_{ID}|<0.8"]
            hist = HM.getHistograms(histogramName)
            DataVsMC10 = Draw2DHistogramOnCanvas(hist["PythiaJetJet"], doLogx = False, doLogy = True, x_range=(0.0, 1.5))
            DataVsMC10.Draw()
            DataVsMC10.Print(plotting_directory + "/" + histogramName.replace("Numerator", "") + "PythiaJetJet" + ".png")

            description = base_description + ["|#eta_{ID}|<0.8"]
            hist = HM.getHistograms(histogramName)
            DataVsMC10 = Draw2DHistogramOnCanvas(hist[DataKey], doLogx = False, doLogy = True, x_range=(0.0,1.5))
            DataVsMC10.Draw()
            DataVsMC10.Print(plotting_directory + "/" + histogramName.replace("Numerator", "") + DataKey + ".png")


        description = base_description + ["0.0<|#eta_{ID}|<0.4", "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "MIP Selection"]
        histogramName = "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70_InBin_0_4"
        histograms = HM.getHistograms(histogramName)

        MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
        MCCanvas.Draw()
        MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

        DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
        DataCanvas.Draw()
        DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

        description = base_description + ["0.4<|#eta_{ID}|<0.8", "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "MIP Selection"]
        histogramName = "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70_InBin_4_8"
        histograms = HM.getHistograms(histogramName)

        MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
        MCCanvas.Draw()
        MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

        DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
        DataCanvas.Draw()
        DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

        description = base_description + ["0.8<|#eta_{ID}|<1.2", "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "MIP Selection"]
        histogramName = "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70_InBin_8_12"
        histograms = HM.getHistograms(histogramName)

        MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
        MCCanvas.Draw()
        MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

        DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
        DataCanvas.Draw()
        DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

        description = base_description + ["1.2<|#eta_{ID}|<1.6", "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "MIP Selection"]
        histogramName = "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70_InBin_12_16"
        histograms = HM.getHistograms(histogramName)

        MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
        MCCanvas.Draw()
        MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

        DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
        DataCanvas.Draw()
        DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

        description = base_description + ["1.6<|#eta_{ID}|<2.0", "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "MIP Selection"]
        histogramName = "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70_InBin_16_20"
        histograms = HM.getHistograms(histogramName)

        MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
        MCCanvas.Draw()
        MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

        DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
        DataCanvas.Draw()
        DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

        description = base_description + ["2.0<|#eta_{ID}|<2.4", "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "MIP Selection"]
        histogramName = "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70_InBin_20_24"
        histograms = HM.getHistograms(histogramName)

        MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
        MCCanvas.Draw()
        MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

        DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
        DataCanvas.Draw()
        DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

        #histogramNames = ["TrkMultiplicityVsP_MIPSelection_HadFracAbove70_InBin_0_4" , "TrkMultiplicityVsP_MIPSelection_HadFracAbove70_InBin_12_16", "TrkMultiplicityVsP_MIPSelection_HadFracAbove70_InBin_16_20", "TrkMultiplicityVsP_MIPSelection_HadFracAbove70_InBin_20_24", "TrkMultiplicityVsP_MIPSelection_HadFracAbove70_InBin_4_8", "TrkMultiplicityVsP_MIPSelection_HadFracAbove70_InBin_8_12"]
        #
        eta_descriptors = ["0.0<|#eta_{ID}|<0.4", "0.4<|#eta_{ID}|<0.8", "0.8<|#eta_{ID}|<1.2", "1.2<|#eta_{ID}|<1.6", "1.6<|#eta_{ID}|<2.0", "2.0<|#eta_{ID}|<2.4"]
        #
        #for histogramName, descriptor in zip(histogramNames, eta_descriptors):
        #    description = base_description + [descriptor, "#frac{E_{HAD}}{E_{TOTAL}} > 0.7", "E^{dR<0.1}_{EM} < 1.1 GeV"]
        #    histograms = HM.getHistograms(histogramName)
        #
        #    for key in histograms:
        #        histograms[key].Rebin(20)
        #
        #    DataVSMC10 = DrawDataVsMC(histograms,\
        #                          channelLabels,\
        #                          MCKeys = MCKeys,\
        #                          DataKey = DataKey,\
        #                          doLogx = True,\
        #                          doLogy = False,
        #                          ratio_min = 0.6,\
        #                          ratio_max = 1.4,\
        #                          extra_description = description)
        #    DataVSMC10.Draw()
        #    DataVSMC10.Print(plotting_directory + "/" + histogramName + ".png")
        eta_ranges = [(0.0, 0.4), (0.4, 0.8), (0.8, 1.2), (1.2, 1.6), (1.6, 2.0), (2.0, 2.4)]
        profileNames = ["EOPProfileVsMomentum", "EOPProfileVsMomentum_MIPSelection_HadBetween30And90OfMomentum", "EOPProfileVsMomentum_MIPSelection_HadFracAbove70", "EOPProfileVsMomentum_NonZeroE"]
        bkgProfileNames = ["EnergyBkgProfileVsMomentum", "EnergyBkgProfileVsMomentum_MIPSelection_HadBetween30And90OfMomentum", "EnergyBkgProfileVsMomentum_MIPSelection_HadFracAbove70", "EnergyBkgProfileVsMomentum_NonZeroE"]
        TwoDHistNames = ["2DHist_EOPVsMomentum", "2DHist_EOPVsMomentum_MIPSelection_HadBetween30And90OfMomentum", "2DHist_EOPVsMomentum_MIPSelection_HadFracAbove70", "2DHist_EOPVsMomentum_NonZeroE"]
        #bkgTwoDHistNames = ["2DHist_EOPBkgVsMomentum", "2DHist_EOPBkgVsMomentum_MIPSelection_HadBetween30And90OfMomentum", "2DHist_EOPBkgVsMomentum_MIPSelection_HadFracAbove70", "2DHist_EOPBkgVsMomentum_NonZeroE"]
        plotDescriptors = [ [], ["0.3 P < E_{HAD} < 0.9 P", "E^{dR<0.1}_{EM} < 1.1 GeV", "N_{TRT} >= 20"], ["E_{HAD}/E_{TOTAL} > 0.7", "E^{dR<0.1}_{EM} < 1.1 GeV", "N_{TRT} >= 20"], ["E_{TOTAL} != 0.0"]]

        for eta_range, eta_descriptor in zip(eta_ranges, eta_descriptors):
            histogramName = "TrkMultiplicityVsP_NonZeroE" + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
            hist_NonZero = HM.getHistograms(histogramName, rebin = 100)
            histogramName = "TrkMultiplicityVsP" + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
            hist_Inclusive = HM.getHistograms(histogramName, rebin = 100)
            histogramName = "TrkMultiplicityVsP_MIPSelection_HadFracAbove70" + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1])) 
            hist_HadFracAbove70 = HM.getHistograms(histogramName, rebin = 100)

            frac_MIP_of_NonZero = DivideHistograms(hist_HadFracAbove70, hist_NonZero)
            frac_MIP_of_Inclusive = DivideHistograms(hist_HadFracAbove70, hist_Inclusive)

            DataVSMC10 = DrawDataVsMC(frac_MIP_of_NonZero,\
                                  channelLabels,\
                                  MCKeys = MCKeys,\
                                  DataKey = DataKey,\
                                  doLogx = True,\
                                  doLogy = False,
                                  ratio_min = 0.2,\
                                  ratio_max = 1.8,\
                                  ylabel="N(MIP)/N(E!=0)",\
                                  extra_description = base_description  + [eta_descriptor])
            DataVSMC10[0].Draw()
            DataVSMC10[0].Print(plotting_directory + "/" + "FracNonZero_MIP_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1])) + ".png")
            DataVSMC10[0].Close()

            DataVSMC10 = DrawDataVsMC(frac_MIP_of_Inclusive,\
                                  channelLabels,\
                                  MCKeys = MCKeys,\
                                  DataKey = DataKey,\
                                  doLogx = True,\
                                  doLogy = False,
                                  ratio_min = 0.6,\
                                  ratio_max = 1.4,\
                                  ylabel="N(MIP)/N(Inclusive)",\
                                  extra_description = base_description +  [eta_descriptor])
            DataVSMC10[0].Draw()
            DataVSMC10[0].Print(plotting_directory + "/" + "FracInclusive_MIP_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1])) + ".png")
            DataVSMC10[0].Close()




            for bkgProfileName, profileName, TwoDHistName, plotDescriptor in zip(bkgProfileNames, profileNames, TwoDHistNames, plotDescriptors):
                description = ["P_{T} Reweighted", eta_descriptor] + plotDescriptor

                histogramName = profileName + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
                histograms = HM.getHistograms(histogramName)
                histograms = ProjectProfiles(histograms)
                histogram_num = histograms
                DataVSMC10 = DrawDataVsMC(histograms,\
                                      channelLabels,\
                                      MCKeys = MCKeys,\
                                      DataKey = DataKey,\
                                      doLogx = True,\
                                      doLogy = False,
                                      ratio_min = 0.5,\
                                      ratio_max = 1.5,\
                                      extra_description = description)
                DataVSMC10[0].Draw()
                DataVSMC10[0].Print(plotting_directory + "/" + histogramName + ".png")
                DataVSMC10[0].Close()

                histogramName = bkgProfileName + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
                histograms = HM.getHistograms(histogramName)
                histograms = ProjectProfiles(histograms)
                histogram_den = histograms
                DataVSMC10 = DrawDataVsMC(histograms,\
                                      channelLabels,\
                                      MCKeys = MCKeys,\
                                      DataKey = DataKey,\
                                      doLogx = True,\
                                      doLogy = False,
                                      ratio_min = 0.5,\
                                      ratio_max = 1.5,\
                                      extra_description = description)
                DataVSMC10[0].Draw()
                DataVSMC10[0].Print(plotting_directory + "/" + histogramName + ".png")
                DataVSMC10[0].Close()

                EOPCorrHistograms = SubtractHistograms(histogram_num, histogram_den)
                histogramName = "EOPCorrHistogram_" + bkgProfileName + "_"  + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
                DataVSMC10 = DrawDataVsMC(EOPCorrHistograms,\
                                      channelLabels,\
                                      MCKeys = MCKeys,\
                                      DataKey = DataKey,\
                                      doLogx = True,\
                                      doLogy = False,\
                                      ylabel = "<E/p>_{Corr}",\
                                      ratio_min = 0.95,\
                                      ratio_max = 1.05,\
                                      extra_description = description)
                DataVSMC10[0].Draw()
                DataVSMC10[0].Print(plotting_directory + "/" + histogramName + ".png")
                DataVSMC10[0].Close()

                histogramName = TwoDHistName + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
                histograms = HM.getHistograms(histogramName)

                DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
                DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

                MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
                MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

            histogram_name =  "TrkMultiplicityVsP_NonZeroE_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
            histograms = HM.getHistograms(histogram_name)
            DataVsMC = DrawDataVsMC(histograms,\
                                    channelLabels,\
                                    MCKeys = MCKeys,\
                                    DataKey=DataKey,\
                                    ratio_min=0.6,\
                                    ratio_max=1.4,\
                                    rebin=100,\
                                    extra_description = ["P_{T} Reweighted", "E_{Total} != 0.0", eta_descriptor])
            DataVsMC[0].Draw()
            DataVsMC[0].Print(plotting_directory + "/" + histogram_name + ".png")
            DataVsMC[0].Close()
        #plot the average energy in the anulus
        profileNames = ["EnergyAnulusProfileVsMomentum_MIPSelection_HadBetween30And90OfMomentum", "EnergyAnulusProfileVsMomentum_MIPSelection_HadFracAbove70"]
        TwoDHistNames = ["2DHist_EnergyAnulusVsMomentum_MIPSelection_HadBetween30And90OfMomentum", "2DHist_EnergyAnulusVsMomentum_MIPSelection_HadFracAbove70"]
        profileDescriptors = [ ["0.3 P < E_{HAD} < 0.9 P", "E^{dR<0.1}_{EM} < 1.1 GeV", "N_{TRT} >= 20"], ["E_{HAD}/E_{TOTAL} > 0.7", "E^{dR<0.1}_{EM} < 1.1 GeV", "N_{TRT} >= 20"], ["E_{TOTAL} != 0.0"] ]

        for eta_range, eta_descriptor in zip(eta_ranges, eta_descriptors):
            eta = eta_range[1]
            p_bins_max = 15.05
            p_bins_min = getP(0.5, eta)
            nBins = 20
            p_bins = getLogBins(p_bins_min, p_bins_max, nBins)
            for profileName, TwoDHistName, profileDescriptor in zip(profileNames, TwoDHistNames,  profileDescriptors):
                description = ["P_{T} Reweighted", eta_descriptor] + profileDescriptor

                histogramName = profileName + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
                histograms = HM.getHistograms(histogramName)
                histograms = ProjectProfiles(histograms)
                DataVSMC10 = DrawDataVsMC(histograms,\
                                      channelLabels,\
                                      MCKeys = MCKeys,\
                                      DataKey = DataKey,\
                                      doLogx = True,\
                                      doLogy = False,
                                      ratio_min = 0.4,\
                                      ratio_max = 1.6,\
                                      extra_description = description)
                DataVSMC10[0].Draw()
                DataVSMC10[0].Print(plotting_directory + "/" + histogramName + ".png")
                DataVSMC10[0].Close()

                histogramName = TwoDHistName + "_InBin_" + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1]))
                histograms = HM.getHistograms(histogramName)
                DataCanvas = Draw2DHistogramOnCanvas(histograms[DataKey], doLogx = True, doLogy = False)
                DataCanvas.Print(plotting_directory + "/" + histogramName + "LowMuData.png")

                MCCanvas = Draw2DHistogramOnCanvas(histograms["PythiaJetJet"], doLogx = True, doLogy = False)
                MCCanvas.Print(plotting_directory + "/" + histogramName + "PythiaJetJet.png")

                p_ranges = [ (p_bins[i], p_bins[i+1])  for i in range(0, len(p_bins)-1) ]
                for p_range in p_ranges:
                    histogramNames = ["trkEMDR100", "MomentumHadFrac", "HadFrac", "trkTRTHits"]
                    p_high_str = "{:.2f}".format(p_range[1])
                    p_low_str= "{:.2f}".format(p_range[0])
                    for selection_type in ["_NonZeroE_20TRT_InEtaBin_", "_NonZeroE_InEtaBin_", "_MIPSelection_HadFracAbove70_InEtaBin_"]:
                        if "_NonZeroE_20TRT_InEtaBin_" == selection_type:
                            extra_stuff = ["E_{TOTAL} != 0", "N_{TRT Hits} >= 20"]
                        elif "_MIPSelection_HadFracAbove70_InEtaBin_" == selection_type:
                            extra_stuff = ["MIP Seleciton"]
                        else:
                            extra_stuff = ["E_{TOTAL} !=0"]
                        for histogramName in histogramNames:
                            if selection_type == "_MIPSelection_HadFracAbove70_":
                                break
                            histogramName = histogramName + selection_type + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1])) + "_InPBin_" + str(int(100*p_range[0])) + "_" + str(int(100*p_range[1]))
                            histograms = HM.getHistograms(histogramName)
                            DataVSMC = DrawDataVsMC(histograms,\
                                           channelLabels,\
                                           MCKeys = MCKeys,\
                                           DataKey = DataKey,\
                                           doLogx = False,\
                                           doLogy = False,
                                           ratio_min = 0.4,\
                                           ratio_max = 1.6,\
                                           extra_description = ["P_{T} Reweighted", eta_descriptor, p_low_str + " < |P/GeV| < " + p_high_str] + extra_stuff)
                            DataVSMC[0].Draw()
                            DataVSMC[0].Print(plotting_directory + "/" + histogramName + ".png")
                            DataVSMC[0].Close()

                        for histogramName in ["NClusters","NClusters_EM","NClusters_HAD","NClusters_emlike","NClusters_hadlike"]:
                            histogram_name = histogramName + selection_type + str(int(10*eta_range[0])) + "_" + str(int(10*eta_range[1])) + "_InPBin_" +  str(int(100*p_range[0])) + "_" + str(int(100*p_range[1]))
                            hist = HM.getHistograms(histogram_name)
                            DataVsMC1 = DrawDataVsMC(hist,\
                                                    channelLabels,\
                                                    MCKeys = MCKeys,\
                                                    DataKey=DataKey,\
                                                    extra_description =  ["P_{T} Reweighted", eta_descriptor, p_low_str + " < |P/GeV| < " + p_high_str] + extra_stuff)
                            DataVsMC1[0].Draw()
                            DataVsMC1[0].Print(plotting_directory + "/" + histogram_name + ".png")
                            DataVsMC1[0].Close()
                        ROOT.gSystem.ProcessEvents()

raw_input()
