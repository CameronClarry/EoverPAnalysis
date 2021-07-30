import numpy as np
from array import array
from calculation import Calculation
import ROOT
import imp
import time
import os
import glob
import imp

def get_log_bins(minBin, maxBin, nBins):
    '''Get nBins logarithmically-evenly spaced bins ranging from minBin to maxBin'''
    bins = []
    base = (float(maxBin)/float(minBin)) ** (1.0/float(nBins))
    for i in range(0, nBins + 1):
        bins.append(minBin * (base) ** i)
    return bins

def get_bins(minBin, maxBin, nBins):
    '''Get nBins evenly spaced bins ranging from minBin to maxBin'''
    bins = []
    step = float(maxBin - minBin)/float(nBins)
    for i in range(0, nBins + 1):
        bins.append(minBin + (i*step))
    return bins

def get_p(Pt, eta):
    '''Given a value of pT and eta, return the momentum'''
    return Pt*np.cosh(eta)

def create_selection_function(template, branches, *args):
    '''
    Given a function template, and the branches that are needed to do the calculation in the function, create a calculation class instance and return it.
    '''
    if len(args) > 3:
        raise ValueError("Only up to three variables supported for the template function")
    if len(args) == 0:
        raise ValueError("You need to pass at least one argument")

    if len(args) == 1:
        function = lambda x, y=args[0]: template(x,y)
    if len(args) == 2:
        function = lambda x, y=args[0], z=args[1]: template(x,y,z)
    if len(args) == 3:
        function = lambda x, y=args[0], z=args[1], w=args[2]: template(x,y,z,w)

    function.__name__ = template.__name__ + "_".join([str(arg) for arg in args])
    selection_function = Calculation(function, branches)
    return selection_function

def create_inverse_selection_function(list_of_selections, name = None):
    '''
    Given a list of selections, create a selection that is the logical inverse of all of the selections
    '''
    #create the selection function
    branches = []
    for f in list_of_selections:
        for b in f.branches:
            if b not in branches:
                branches.append(b)

    #create the function that does the selection. Also, how slick is this! huh?
    sel_function = lambda trk, list_of_selections = list_of_selections: np.logical_not(np.logical_or.reduce([sel.eval(trk) for sel in list_of_selections]))

    if name == None:
        name = "_".join([s.name for s in list_of_selections])
    sel_function.__name__ = name

    #create the calculation
    sel_calculation = Calculation(sel_function, branches)

    return sel_calculation

class HistogramFiller:
    '''
    Handle the filling of histograms.
    '''
    def __init__(self, trees, tree_name, weight_calculator, selection_string = "", partitions = None):
        self.channel_files = {}
        self.tree_name = tree_name
        self.partitions = partitions
        self.verbose = False
        self.all_selections = []
        self.all_variables =[]
        self.histogram_filling_functions = {}
        self.selection_string = selection_string
        self.object_counter = 0
        self.weight_calculator = weight_calculator
        self.selections_for_channels = {}
        self.trees = trees
        self.channels = list(trees.keys())
        self.subchannels = {} #dictionary of new_channel to dictionary of old_channel and selections

        for channel in self.trees:
            self.channel_files[channel] = []
            for f in self.trees[channel]:
                self.channel_files[channel].append(f)

    def apply_selection_for_channel(self, channel, selections):
        if channel not in self.selections_for_channels:
            self.selections_for_channels[channel] = selections
        else:
            self.selections_for_channels[channel] += selections
        for selection in selections:
            if selection.name not in [sel.name for sel in self.all_selections]:
                self.all_selections.append(selection)

    def create_subchannel_for_channel(self, subchannel, channel, selections):
        assert subchannel not in self.subchannels
        assert subchannel not in self.channels
        if channel not in self.channels:
            print("WARNING! Couldn't find the channel {} for subchannel {}".format(channel, subchannel))
            return
        self.subchannels[subchannel] = {}
        self.subchannels[subchannel]["original_channel"] = channel
        self.subchannels[subchannel]["selections"] = selections
        for selection in selections:
            if selection.name not in [sel.name for sel in self.all_selections]:
                self.all_selections.append(selection)
        self.channels.append(subchannel)
        self.channel_files[subchannel] = self.channel_files[channel]

    def get_data(self, channel, filename, variables, selections):
        '''
        Given a string channel, string filename, a list of calculation variables and a list of calculations selections, return a dictionary keys selection_dict, variable_dict and weights. selection_dict is a dictionary of key selection name to numpy array of bool. variable_dict is a dictionary of string variable name to numpy array variable. weights is a numpy array of floats
        '''
        print("\n"*2)
        print("Getting branches for channel {}".format(channel))
        branches = get_needed_branches(variables, selections)

        #get the parition of the ttree to be read
        partition = None
        if self.partitions == None:
            partition = (0, total_entries)
        else:
            partition = self.partitions[channel][filename]
            if self.verbose: print("Found a partition")

        tree = self.trees[channel][filename]

        print("Reading entries from {} until {}".format(partition[0], partition[1]))
        result = GetData(partition = partition, bare_branches = branches, channel = channel, filename = filename, tree = tree, treename = self.tree_name, variables=variables, weight_calculator = self.weight_calculator, selections = selections, selection_string = self.selection_string, verbose = self.verbose)

        #Get the selections, variables and weights
        selection_dict = result["selection_dict"]
        variable_dict = result["variable_dict"]
        weights = result["weights"]

        if channel in self.selections_for_channels:
            print("Applying selections for this channell")
            selections = self.selections_for_channels[channel]
            total_selection = np.ones(len(weights)) > 0.5
            for selection in selections:
                print("\t Applying {}, with {} events passing".format(selection.name, np.sum(1 * selection_dict[selection.name])))
                total_selection &= selection_dict[selection.name]
            weights = weights[total_selection]
            for key in selection_dict:
                selection_dict[key] = selection_dict[key][total_selection]
            for key in variable_dict:
                variable_dict[key] = variable_dict[key][total_selection]

        if self.verbose: print("The following selections have been evaluated ")
        for selection in selection_dict:
            print("Selection {} has {} tracks passing".format(selection, np.sum(1 * selection_dict[selection])))
        if self.verbose: print("The following variables have be evaluated ")
        for variable in variable_dict:
            if self.verbose: print(variable)

        return variable_dict, selection_dict, weights

    def fill_histograms(self, histogram_name, data, variable, selections = [], bins = 1, range_low = 0.000001, range_high=1. - 0.00001,  xlabel ="", ylabel = "", HistogramPerFile=False, useWeights = True):
        '''
        Get the histogram for variable after selections is applied.
        '''
        name_to_fill = variable.name
        variables = [variable]
        histogram_dictionary = {}
        for channel in self.channels:
            if (type(bins) == list):
                bins_array = array('d',bins)
                histogram_dictionary[channel] = ROOT.TH1D(histogram_name + channel, histogram_name + channel, len(bins_array)-1, bins_array)
            else:
                histogram_dictionary[channel] = ROOT.TH1D(histogram_name + channel, histogram_name + channel, bins, range_low + 0.0000001, range_high - 0.000001)
            histogram_dictionary[channel].GetXaxis().SetTitle(xlabel)
            histogram_dictionary[channel].GetYaxis().SetTitle(ylabel)
            histogram_dictionary[channel].Sumw2()

        for channel in self.channels:
            for filename in self.channel_files[channel]:
                variable_dict, selection_dict, weights = data[channel][filename]
                total_selection = np.ones(len(weights)) > 0.0
                for selection in selections:
                    total_selection &= selection_dict[selection.name]
                to_fill = variable_dict[name_to_fill][total_selection]
                to_weight = weights[total_selection]
                if self.verbose: print(len(to_fill))
                if self.verbose: print(len(to_weight))
                if self.verbose: print(to_fill)
                if self.verbose: print(to_weight)
                if self.verbose: print("Filling Variable " + variable.name)
                if useWeights:
                    fill_hist(histogram_dictionary[channel], to_fill, to_weight)
                else:
                    fill_hist(histogram_dictionary[channel], to_fill)
        return histogram_dictionary

    def fill_2d_histograms(self, histogram_name, data, variable_x, variable_y, selections = [], bins_x = 1, range_low_x = 0.000001, range_high_x=1. - 0.00001,  xlabel ="", bins_y=1, range_low_y=0.000001, range_high_y=1. - 0.00001, ylabel = "", zlabel="",):
        '''the 2-d histgram with variable_x and variable_y drawn'''
        name_to_fill_x = variable_x.name
        name_to_fill_y = variable_y.name
        variables = [variable_x, variable_y]
        histogram_dictionary = {}
        for channel in self.channels:
            if (type(bins_x) == list and type(bins_y) == list):
                bins_array_x = array('d',bins_x)
                bins_array_y = array('d',bins_y)
                histogram_dictionary[channel] = ROOT.TH2D(histogram_name + channel, histogram_name + channel, len(bins_array_x)-1, bins_array_x, len(bins_array_y)-1, bins_array_y)
            elif (type(bins_x) != list and type(bins_y) != list):
                histogram_dictionary[channel] = ROOT.TH2D(histogram_name + channel, histogram_name + channel, bins_x, range_low_x + 0.0000001, range_high_x - 0.000001, bins_y, range_low_y+0.0000001, range_high_y + 0.0000001)
            else:
                raise ValueError("both of the bins_x and bins_y variables need to be the same type. Both integers, or both lists")
            histogram_dictionary[channel].GetXaxis().SetTitle(xlabel)
            histogram_dictionary[channel].GetYaxis().SetTitle(ylabel)
            histogram_dictionary[channel].GetZaxis().SetTitle(zlabel)
            histogram_dictionary[channel].GetZaxis().SetTitleSize(0.035)
            histogram_dictionary[channel].GetZaxis().SetTitleOffset(1.35)
            histogram_dictionary[channel].Sumw2()

        for channel in self.channels:
            for filename in self.channel_files[channel]:
                variable_dict, selection_dict, weights = data[channel][filename]
                total_selection = np.ones(len(weights)) > 0.0
                for selection in selections:
                    total_selection &= selection_dict[selection.name]
                to_weight = weights[total_selection]
                n_sel = len(to_weight)
                to_fill = np.zeros((n_sel,2))
                to_fill[:,0] = variable_dict[name_to_fill_x][total_selection]
                to_fill[:,1] = variable_dict[name_to_fill_y][total_selection]
                if self.verbose: print(to_fill)
                if self.verbose: print(to_weight)
                if self.verbose: print("Filling Variable " + variable.name)
                fill_hist(histogram_dictionary[channel], to_fill, to_weight)
        return histogram_dictionary

    def fill_2d_tprofile_histograms(self, histogram_name, data, variable_x, variable_y, selections = [], bins_x = 1, range_low_x = 0.000001, range_high_x=1. - 0.00001,  xlabel ="", bins_y=1, range_low_y=0.000001, range_high_y=1. - 0.00001, ylabel = "", zlabel="",):
        '''the 2-d histgram with variable_x and variable_y drawn'''
        name_to_fill_x = variable_x.name
        name_to_fill_y = variable_y.name
        variables = [variable_x, variable_y]
        histogram_dictionary = {}
        for channel in self.channels:
            if (type(bins_x) == list and type(bins_y) == list):
                bins_array_x = array('d',bins_x)
                bins_array_y = array('d',bins_y)
                histogram_dictionary[channel] = ROOT.TProfile2D(histogram_name + channel, histogram_name + channel, len(bins_array_x)-1, bins_array_x, len(bins_array_y)-1, bins_array_y)
            elif (type(bins_x) != list and type(bins_y) != list):
                histogram_dictionary[channel] = ROOT.TProfile2D(histogram_name + channel, histogram_name + channel, bins_x, range_low_x + 0.0000001, range_high_x - 0.000001, bins_y, range_low_y+0.0000001, range_high_y + 0.0000001)
            else:
                raise ValueError("both of the bins_x and bins_y variables need to be the same type. Both integers, or both lists")
            histogram_dictionary[channel].GetXaxis().SetTitle(xlabel)
            histogram_dictionary[channel].GetYaxis().SetTitle(ylabel)
            histogram_dictionary[channel].GetZaxis().SetTitle(zlabel)
            histogram_dictionary[channel].GetZaxis().SetTitleSize(0.035)
            histogram_dictionary[channel].GetZaxis().SetTitleOffset(1.35)
            histogram_dictionary[channel].Sumw2()

        for channel in self.channels:
            for filename in self.channel_files[channel]:
                variable_dict, selection_dict, weights = data[channel][filename]
                total_selection = np.ones(len(weights)) > 0.0
                for selection in selections:
                    total_selection &= selection_dict[selection.name]
                to_weight = weights[total_selection]
                n_sel = len(to_weight)
                to_fill = np.zeros((n_sel,2))
                to_fill[:,0] = variable_dict[name_to_fill_x][total_selection]
                to_fill[:,1] = variable_dict[name_to_fill_y][total_selection]
                if self.verbose: print(to_fill)
                if self.verbose: print(to_weight)
                if self.verbose: print("Filling Variable " + variable.name)
                fill_profile(histogram_dictionary[channel], to_fill, to_weight)
        return histogram_dictionary

    def fill_tprofile_histograms(self, histogram_name, data, variable_x, variable_y, selections = [], bins = 1, range_low = 0.000001, range_high=1. - 0.00001,  xlabel ="", ylabel="",):
        '''Get a TProfile histogram with variable_y profiled against variable_x, after selections selections have been applied'''

        name_to_fill_x = variable_x.name
        name_to_fill_y = variable_y.name
        variables = [variable_x, variable_y]
        histogram_dictionary = {}
        for channel in self.channels:
            if (type(bins) == list):
                bins_array = array('d',bins)
                histogram_dictionary[channel] = ROOT.TProfile(histogram_name + channel, histogram_name + channel, len(bins_array)-1, bins_array)
            else:
                histogram_dictionary[channel] = ROOT.TProfile(histogram_name + channel, histogram_name + channel, bins, range_low + 0.0000001, range_high - 0.000001)
            histogram_dictionary[channel].Sumw2()

        for channel in self.channels:
            for filename in self.channel_files[channel]:
                variable_dict, selection_dict, weights = data[channel][filename]
                total_selection = np.ones(len(weights)) > 0.0
                for selection in selections:
                    total_selection &= selection_dict[selection.name]
                to_weight = weights[total_selection]
                n_sel = len(to_weight)
                to_fill = np.zeros((n_sel,2))
                to_fill[:,0] = variable_dict[name_to_fill_x][total_selection]
                to_fill[:,1] = variable_dict[name_to_fill_y][total_selection]
                if self.verbose: print(to_fill)
                if self.verbose: print(to_weight)
                if self.verbose: print("Filling Variable " + variable.name)
                if self.verbose: print("Filling Histogram")
                fill_profile(histogram_dictionary[channel], to_fill, to_weight)
                if self.verbose: print("Finished filling histogram")

            histogram_dictionary[channel].GetXaxis().SetTitle(xlabel)
            histogram_dictionary[channel].GetYaxis().SetTitle(ylabel)
        return histogram_dictionary

    def book_histogram_fill(self, histogram_name, variable, selections = [], bins = 1, range_low = 0.000001, range_high=1. - 0.00001,  xlabel ="", ylabel = "", HistogramPerFile=False, useWeights = True):
        if histogram_name not in self.histogram_filling_functions:
            self.histogram_filling_functions[histogram_name] = lambda data : self.fill_histograms(histogram_name, data, variable, selections = selections, bins = bins, range_low = range_low, range_high=range_high,  xlabel = xlabel, ylabel = ylabel, HistogramPerFile=HistogramPerFile, useWeights = useWeights)
        else:
            raise ValueError("histogram name already exists")
        for selection in selections:
            if selection.name not in [sel.name for sel in self.all_selections]:
                self.all_selections.append(selection)

        if variable.name not in [var.name for var in self.all_variables]:
            self.all_variables.append(variable)

    def book_2dhistogram_fill(self, histogram_name, variable_x, variable_y, selections = [], bins_x = 1, range_low_x = 0.000001, range_high_x=1. - 0.00001,  xlabel ="", bins_y=1, range_low_y=0.000001, range_high_y=1. - 0.00001, ylabel = "", zlabel=""):
        if histogram_name not in self.histogram_filling_functions:
            self.histogram_filling_functions[histogram_name] = lambda data : self.fill_2d_histograms(histogram_name, data, variable_x, variable_y, selections = selections, bins_x = bins_x, range_low_x =range_low_x, range_high_x=range_high_x,  xlabel =xlabel, bins_y=bins_y, range_low_y=range_low_y, range_high_y=range_high_y, ylabel = ylabel, zlabel=zlabel)
        else:
            raise ValueError("histogram name already exists")

        for selection in selections:
            if selection.name not in [sel.name for sel in self.all_selections]:
                self.all_selections.append(selection)

        if variable_x.name not in [var.name for var in self.all_variables]:
            self.all_variables.append(variable_x)

        if variable_y.name not in [var.name for var in self.all_variables]:
            self.all_variables.append(variable_y)

    def book_tprofile_fill(self, histogram_name,  variable_x, variable_y, selections = [], bins = 1, range_low = 0.000001, range_high=1. - 0.00001,  xlabel ="", ylabel = ""):
        if histogram_name not in self.histogram_filling_functions:
            self.histogram_filling_functions[histogram_name] = lambda data : self.fill_tprofile_histograms(histogram_name, data, variable_x, variable_y, selections = selections, bins = bins, range_low = range_low, range_high=range_high,  xlabel =xlabel, ylabel=ylabel)
        else:
            raise ValueError("histogram name already exists")

        for selection in selections:
            if selection.name not in [sel.name for sel in self.all_selections]:
                self.all_selections.append(selection)

        if variable_x.name not in [var.name for var in self.all_variables]:
            self.all_variables.append(variable_x)

        if variable_y.name not in [var.name for var in self.all_variables]:
            self.all_variables.append(variable_y)

    def DumpHistograms(self):
        data = {}
        for channel in self.channels:
            if channel not in self.subchannels:
                print("Dumping for channel {}".format(channel))
                data[channel] = {}
                for filename in self.channel_files[channel]:
                    data[channel][filename] = self.get_data(channel,filename, self.all_variables, self.all_selections)

        for subchannel in self.subchannels:
            print("Getting the data for subchannel {}".format(subchannel))
            origin_channel = self.subchannels[subchannel]["original_channel"]
            selections = self.subchannels[subchannel]["selections"]
            assert subchannel not in data
            data[subchannel] = {}
            for filename in data[origin_channel]:
                variable_dict, selection_dict, weights = data[origin_channel][filename]
                total_selection = np.ones(len(weights)) > 0.5
                for sel in selections:
                    total_selection &= selection_dict[sel.name]

                new_variable_dict = {}
                new_selection_dict = {}
                for key in variable_dict:
                    new_variable_dict[key] = variable_dict[key][total_selection]
                for key in selection_dict:
                    new_selection_dict[key] = selection_dict[key][total_selection]
                new_weights = weights[total_selection]
                data[subchannel][filename] = new_variable_dict, new_selection_dict, new_weights

        histograms = {}
        for histogram_name in self.histogram_filling_functions:
            histograms[histogram_name] = self.histogram_filling_functions[histogram_name](data)

        return histograms


#These are python JZW samples. I normalize to the number of generated events, the cross section and the filter efficiency
weight_dictionary = {\
"361020" : (1./(9999000.0)) * 78420000 * 0.9755, #xsection in nb
"361021" : (1./(3995000.0)) * 78420000 * 0.00067143, #xsection in nb
"361022" : (1./(1998000.0)) * 2433200 * 0.00033423, #xsection in nb
"428001" : 1.0,
"428002" : 1.0,
}

#prescale corrected luminosity:
lumi_prescaled = 5.25948 #nb ** (-1)
lumi_unprescaled = 147.717 * 1000.0 # nb ** (-1)

try:
    imp.find_module('root_numpy')
    foundRootNumpy=True
    print("Found root_numpy")
except ImportError:
    foundRootNumpy=False
    print("Didn't find root_numpy module. Did NOT set atlas style. Continuing")

if foundRootNumpy:
    from root_numpy import fill_hist, fill_profile
    from root_numpy import tree2array

import os
import psutil
process = psutil.Process(os.getpid())

def branchDresser(branches):
    '''this is a function that dresses branches with variable length arrays. See http://scikit-hep.org/root_numpy/reference/generated/root_numpy.tree2array.html for details. You need to define a maximum length and what filler variables to use. Fortunately, there are no vector branches in any EOP trees.'''
    return branches

def get_x_section_weight(filename):
    '''
    Search for the x-section weight for this file by searching for the dsid in the filename. Return the weight.
    '''
    if filename[-1] != "/": filename = filename.split("/")[-1]
    else: filename = filename.split("/")[-2]
    weight = None
    for dsid in weight_dictionary:
        if dsid in filename:
            weight = weight_dictionary[dsid]
    if weight == None:
        raise ValueError("Can't find the dataset id in the weight file")
    return weight

def getIsData(filename):
    '''
    Return true if the file is a data file. Otherwise, return false because the file is simulation.
    '''
    return ("Data" in filename.split("/")[-1] or "data" in filename.split("/")[-1] or "Data" in filename.split("/")[-2] or "data" in filename.split("/")[-2])

def GetData(partition = (0, 0), bare_branches = [], channel = "", filename = None, tree = None, treename = None, variables = [], weight_calculator = None, selections = [], selection_string = "",  verbose = False):
    '''
    A function for retrieving data

    partition -- a tuple of length 2. Retrieve tree entries from partition[0] until partition[1]
    bare_branches -- a list of all branches to be read. The branches will be dressed. See root_numpy.tree2array for more information
    channel -- a string for the channel that this file corresponds to. This is needed for the weight calculation, since channels may need reweighting.
    tree -- the name of the tree to read
    variables -- a list of all variables to calculate
    weight_calculator -- a instance of the Calculation class that calculates the weight for the event
    selections -- a list of all selections to calculate
    select_string -- a string used to select a subset of the entries in the tree. This uses the same syntax when selecting events using TTree draw:w
    verbose -- an option to have more printed output from the function.
    '''
    assert len(partition) == 2

    isData = getIsData(filename)
    for branch in weight_calculator.branches:
        if branch not in bare_branches:
            bare_branches.append(branch)
    branches = branchDresser(bare_branches)
    if verbose: print(branches)

    if verbose: print("Reading from file " + filename)

    data = None
    for i in range(1, 50):
        try:
            data = tree2array(tree, branches, selection_string, start = partition[0], stop = partition[1])
        except Exception as e:
            print("Catching a failed attempt to retrieve data error. Trying agagin in 5 seconds")
            print(e)
            time.sleep(5) #try again in 5 seconds
        else:
            break

    if data == None:
        raise ValueError("Could not retrieve the data.")

    if verbose: print("Got the data for parition " + str(partition))

    selection_dict = {}
    variable_dict = {}

    print("Evaluating weights")
    weights = weight_calculator.eval(data, isData, channel)

    if not isData:
        print("getting the xsection weight")
        xsec_weight = get_x_section_weight(filename)
        if verbose: print("X Section Weight Set To " + str(xsec_weight))
        weights = weights * xsec_weight * lumi_prescaled

    ##calculate everything we need in one go!
    for variable in variables:
        if verbose: print("calculating variables for " + variable.name)
        variable_dict[variable.name] = variable.eval(data)

    #selection_dict is a dictionary of numpy arrays that have dimension # of events
    #each entry in the numpy array tells you if the event passed the selection
    for selection in selections:
        if verbose: print("calculating selection " + selection.name)
        if not selection.name in selection_dict:
            selection_dict[selection.name] = selection.eval(data)

    #create the return diciontary, which contains all of the variables, selections and weights needed for calculations
    return_dict = {}
    return_dict["selection_dict"] = selection_dict
    return_dict["variable_dict"] = variable_dict
    return_dict["weights"] = weights
    f = tree.GetCurrentFile()
    tree.SetDirectory(0)
    f.Close()
    return return_dict

def get_needed_branches(variables, selections):
    '''given a list of variables and selections, get all of the branches that should be read from the tree'''
    branches = []

    for variable in variables:
        for branch in variable.branches:
            if branch not in branches:
                branches.append(branch)

    for selection in selections:
        for branch in selection.branches:
            if branch not in branches:
                branches.append(branch)

    return branches
