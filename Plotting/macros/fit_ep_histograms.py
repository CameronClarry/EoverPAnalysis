import histogram_manager
import ROOT
import argparse

def get_binning(tf, selection):
    tree = tf.Get(selection + "BinningTree")
    for bins in tree:
        break

    eta_bins_low = getattr(bins, selection+"EtaBinsLow")
    eta_bins_high = getattr(bins, selection+"EtaBinsHigh")

    p_bins_low_for_eta_bin = []
    p_bins_high_for_eta_bin = []

    for i in range(0, eta_bins_low.size()):
        p_bins_low_for_eta_bin.append(getattr(bins, selection+"PBinsLow_Eta"+str(i)))
        p_bins_high_for_eta_bin.append(getattr(bins, selection+"PBinsHigh_Eta"+str(i)))
    return {"eta":(eta_bins_low, eta_bins_high), "momentum":(p_bins_low_for_eta_bin, p_bins_high_for_eta_bin)}

def get_histograms(tf, binnings, hist_manager, base_name = "EOPDistribution", selection = ""):
    histograms = {}
    eta_bins = binnings["eta"]
    p_bins = binnings["momentum"]
    for eta_count, (eta_low, eta_high, p_bins_low, p_bins_high) in enumerate(zip(eta_bins[0], eta_bins[1], p_bins[0], p_bins[1])):
        for p_count, (p_low, p_high) in enumerate(zip(p_bins_low, p_bins_high)):
            histogram_name = base_name + "_" + selection + "_Eta_" + str(eta_count) + "_Momentum_" + str(p_count)
            print("retrieving {}".format(histogram_name))
            histograms[histogram_name] ={}
            histograms[histogram_name]["histograms"] = hist_manager.getHistograms(histogram_name)
            histograms[histogram_name]["eta_bins"] = (eta_low, eta_high)
            histograms[histogram_name]["p_bins"] = (p_bins_low, p_bins_high)
            histograms[histogram_name]["p_count"] = p_count
            histograms[histogram_name]["eta_count"] = eta_count
    return histograms

def get_histogram_name(base_name, selection, eta_count, p_count):
    return base_name + "_" + selection + "_Eta_" + str(eta_count) + "_Momentum_" + str(p_count)

parser = argparse.ArgumentParser()
parser.add_argument("--root_file", dest="root_file", required=False, default="root_files/inclusive.root")
parser.add_argument("--selection", dest="selection", required=False, default="NonZeroEnergy")
parser.add_argument("--channels", dest="channels", required=False, default="PythiaJetJet,LowMuData")
args = parser.parse_args()
root_file = args.root_file
selection = args.selection
interesting_channels = args.channels.split(",")
base_name = "EOPDistribution"

nsigma = 1.1
fitter = ROOT.JES_BalanceFitter(nsigma)
hm = histogram_manager.HistogramManager(args.root_file)
tf = ROOT.TFile(args.root_file, "READ")
binnings = get_binning(tf, selection)
histograms = get_histograms(tf, binnings, hm, "EOPDistribution", selection = args.selection)

class FitResults():
    def __init__(self, eta_id, p_id, result=None, err=None,fit_canvas="", channel=None):
        self.eta_id = eta_id
        self.p_id = p_id
        self.result = result
        self.err=err
        self.channel=channel
        self.fit_canvas=fit_canvas

def sort_fit_results(results):
    pass

class FitResultSet():
    def __init__(self):
        self.results = []
    def add(self, result): self.results.append(result)

    @property
    def channels(self):
        return list(set([el.channel for el in self.results]))

    @property
    def eta_ids(self):
        return list(set([el.eta_id for el in self.results]))

    @property
    def p_ids(self):
        return list(set([el.p_id for el in self.results]))

    def get_results(self, channel=None,eta_id=None,p_id=None):
        assert channel in self.channels
        sel_channel = lambda x, channel = channel : channel != None and x.channel==channel
        sel_eta_id = lambda x, eta_id = eta_id : eta_id != None and x.eta_id==eta_id
        sel_p_id = lambda x, p_id = p_id : p_id != None and x.p_id==p_id
        to_return = [el for el in self.results if sel_channel(el) and sel_eta_id(el) and sel_p_id(el)]
        return to_return

tf.cd()
tree = tf.Get(selection + "BinningTree")
file_to_share = ROOT.TFile("histograms_for_fits_{}.root".format(args.selection), "RECREATE")
file_to_share.cd()
cloned = tree.CloneTree()
cloned.Write()

fit_results = FitResultSet()
eta_bins = binnings["eta"]
p_bins = binnings["momentum"]
for eta_count, (eta_low, eta_high, p_bins_low, p_bins_high) in enumerate(zip(eta_bins[0], eta_bins[1], p_bins[0], p_bins[1])):
    for p_count, (p_low, p_high) in enumerate(zip(p_bins_low, p_bins_high)):
        histogram_name = get_histogram_name(base_name, selection, eta_count, p_count)
        canvas = ROOT.TCanvas(histogram_name, histogram_name)
        needed_for_fit = histograms[histogram_name]
        these_histograms = needed_for_fit["histograms"]
        eta_bins = needed_for_fit["eta_bins"]
        p_bins = needed_for_fit["p_bins"]
        p_count = needed_for_fit["p_count"]
        eta_count = needed_for_fit["eta_count"]
        for process in these_histograms:
            if process not in interesting_channels: continue
            to_fit = these_histograms[process]
            fitter.FitAndDraw(to_fit,0.0);
            canvas.Print("{}.eps".format(to_fit.GetName()))
            fit_result = FitResults(eta_count, p_count, result = fitter.GetMean(), err=fitter.GetMeanError(),fit_canvas="{}.eps".format(to_fit.GetName()), channel=process)
            fit_results.add(fit_result)
            file_to_share.cd()
            to_fit.Write()
            cloned = fitter.m_fitHisto.Clone(to_fit.GetName() + "_Fitted")
            cloned.Write()
            cloned = fitter.m_fit.Clone(to_fit.GetName() + "_FitGaussian")
            cloned.Write()

eta_bins = binnings["eta"]
p_bins = binnings["momentum"]
#create a histogram with the fit resutls:
from array import array
histograms_eta = {}
for eta_count, (eta_low, eta_high, p_bins_low, p_bins_high) in enumerate(zip(eta_bins[0], eta_bins[1], p_bins[0], p_bins[1])):
    histograms = {}
    for channel in fit_results.channels:
        if channel not in interesting_channels: continue
        fit_string = "EOPvsP_For_{}_InEtaBin_{}".format(channel, eta_count)
        histograms[channel] = ROOT.TH1D(fit_string, fit_string, len(p_bins_low), array("d", list(p_bins_low) + [p_bins_high[-1]]))
        for p_count, (p_low, p_high) in enumerate(zip(p_bins_low, p_bins_high)):
            result = fit_results.get_results(channel=channel, eta_id=eta_count, p_id = p_count)
            assert len(result) == 1
            histograms[channel].SetBinContent(p_count + 1, result[0].result)
            histograms[channel].SetBinError(p_count+1, result[0].err)
            histograms[channel].GetYaxis().SetTitle("<E/P>")
            histograms[channel].GetXaxis().SetTitle("P [GeV]")
        file_to_share.cd()
        histograms[channel].Write()
    histograms_eta[eta_count] = histograms
print(histograms_eta)


#MCKeys = ['PythiaJetJetHardScatterPion',"SinglePion"]
#DataKey = "LowMuData"
MCKeys = [el for el in interesting_channels if "Data" not in el]
DataKey = [el for el in interesting_channels if "Data" in el]
assert len(DataKey) == 1
DataKey = DataKey[0]
from plotting_tools import *
channelLabels = {"SinglePion": "Single Pion", "PythiaJetJet" : "#splitline{Pythia8}{MinBias and Dijet}", DataKey: "2017 Low-<#mu> Data", "PythiaJetJetPionsReweighted":"Pythia8 MB+DJ Pions Only", "PythiaJetJetHardScatter":"Pythia8 MB+DJ Truth Matched", "PythiaJetJetHardScatterPion":"Pythia8 MB+DJ Pions", "PythiaJetJetTightIso": "#splitline{Pythia8}{MinBias and Dijet}", "LowMuDataTightIso":"2017 Low-<#mu> Data#"}
channelLabels["SinglePionPos"] = "Pos. Single Pion"
channelLabels["SinglePionNeg"] = "Neg. Single Pion"
channelLabels = {key:value for (key, value) in channelLabels.items() if key in interesting_channels}

for eta_count, (eta_low, eta_high, p_bins_low, p_bins_high) in enumerate(zip(eta_bins[0], eta_bins[1], p_bins[0], p_bins[1])):
    to_plot = histograms_eta[eta_count]
    description = ["Non-Zero Energy"] + ["{} < |#eta| < {}".format(eta_low, eta_high)]
    DataVsMC1 = DrawDataVsMC(to_plot,\
                               channelLabels,\
                               MCKeys = MCKeys,\
                               DataKey = DataKey,\
                               ratio_min=0.9,\
                               ratio_max=1.1,\
                               doLogx=True,\
                               doLogy=False,\
                               xlabel="P [GeV]",\
                               ylabel="<E/p>",\
                               extra_description = description)
    DataVsMC1[0].Draw()
    DataVsMC1[0].Print(histogram_name + "_Spectrum_{}Plots.eps".format(eta_count))
    DataVsMC1[0].Close()

