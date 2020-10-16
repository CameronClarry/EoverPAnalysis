import numpy as np
from array import array
import ROOT
import imp

try:
    imp.find_module('atlasplots')
    foundAtlasPlots = True
    print("Found atlas plots module. Setting atlas style")
except ImportError:
    foundAtlasPlots = False
    print("Didn't find atlas plots module. Did NOT set atlas style. Continuing")

try:
    imp.find_module('root_numpy')
    foundRootNumpy=True
    print("Found root_numpy")
except ImportError:
    foundRootNumpy=False
    print("Didn't find root_numpy module. Did NOT set atlas style. Continuing")

if foundRootNumpy:
    from root_numpy import fill_hist, fill_profile

if foundAtlasPlots:
    from atlasplots import atlas_style as astyle
    astyle.SetAtlasStyle()

global_scope = []
CANVAS_COUNTER = 1

DataColor = ROOT.kBlack
#ColorBlindFriendlyColours
COLOURS = {}
COLOURS["PythiaJetJet"] = ROOT.TColor.GetColor(0,73,73)
COLOURS["up"] = ROOT.TColor.GetColor(0,73,73)
COLOURS["PythiaJetJetTightIso"] = ROOT.TColor.GetColor(0,73,73)
COLOURS["PythiaJetJetPionsReweighted"] = ROOT.TColor.GetColor(146,73,0)
COLOURS["PythiaJetJetHardScatter"] = ROOT.TColor.GetColor(146,73,0)
COLOURS["PythiaJetJetHardScatterPion"] = ROOT.TColor.GetColor(146,73,0)
COLOURS["SinglePion"] = ROOT.TColor.GetColor(109,182,255)
COLOURS["SinglePionPos"] = ROOT.TColor.GetColor(146,73,0)
COLOURS["SinglePionNeg"] = ROOT.TColor.GetColor(109,182,255)
COLOURS["down"] = ROOT.TColor.GetColor(146,73,0)
CB_color_cycle = ['#ffffcc',\
'#ffeda0',\
'#fed976',\
'#feb24c',\
'#fd8d3c',\
'#fc4e2a',\
'#e31a1c',\
'#bd0026',\
'#800026']
from variables import cone_strings

for low, high, color in zip(cone_strings[:-1], cone_strings[1:], CB_color_cycle[::-1]):
     color = ROOT.TColor.GetColor(color)
     COLOURS["{}_{}".format(low, high)] = color

def GetBinsFromHistogram(hist, entriesPerBin):
    ''' Get bins with # of entries entriesPerBin inside of it'''
    bins = [] #a list of floats to store the bin edges of the new histograms
    bins.append(hist.GetBinLowEdge(1)) #append the bin edge of the lowest bin
    tracks = [] # list of the number of tracks in each bin
    runningCount = 0.0 #keep a running count of the number of tracks
    for binx in range(1,hist.GetNbinsX() + 1):
        runningCount += hist.GetBinContent(binx)
        if runningCount > entriesPerBin or binx == hist.GetNbinsX():
            bins.append(hist.GetBinLowEdge(binx) + hist.GetBinWidth(binx))
            tracks.append(runningCount)
            runningCount = 0.0

    return bins, tracks

def ATLASLabel(x, y, text=None, color=1, size = None):
    """Draw the ATLAS Label.
    Parameters
    ----------
    x : float
        x position in NDC coordinates
    y : float
        y position in NDC coordinates
    text : string, optional
        Text displayed next to label (the default is None)
    color : TColor, optional
        Text colour (the default is 1, i.e. black).
        See https://ROOT.cern.ch/doc/master/classTColor.html
    """
    l = ROOT.TLatex()
    l.SetNDC()
    l.SetTextColor(color)
    if size != None:
        l.SetTextSize(size)
    l.DrawLatex(x, y, r"#bf{#it{ATLAS}} " + text)


def toGlobalScope(obj):
    '''Keep TObjects alive at global scope'''
    global_scope.append(obj)

def Draw2DHistogramOnCanvas(TwoDHist, doLogx = False, doLogy = False, x_range = None, rebin=None, zlabel = None, y_range=None):
     '''Take a 2-D histogram and plot it on a canvas. Options for a logarithmic x and y axis are available.'''
     global CANVAS_COUNTER
     ROOT.gStyle.SetPalette(ROOT.kInvertedDarkBodyRadiator)
     canvas_name = TwoDHist.GetName() + "_" + str(CANVAS_COUNTER)
     CANVAS_COUNTER += 1
     canvas = ROOT.TCanvas(canvas_name, canvas_name, 1300, 800)
     canvas.SetRightMargin(0.25)
     TwoDHist.Draw("colz")
     #TwoDHist.GetZaxis().SetTitleSize(text_size)
     TwoDHist.GetZaxis().SetTitleOffset(3.5)
     TwoDHist.GetXaxis().SetTitleOffset(1.0)
     TwoDHist.GetZaxis().SetTitleOffset(0.8)
     TwoDHist.GetYaxis().SetTitleOffset(1.0)
     if x_range:
         TwoDHist.GetXaxis().SetRangeUser(x_range[0], x_range[1])
     if y_range:
         TwoDHist.GetYaxis().SetRangeUser(y_range[0], y_range[1])

     if doLogx:
         canvas.SetLogx()
     if doLogy:
         canvas.SetLogy()
     if rebin:
         TwoDHist.Rebin2D(rebin, rebin)
     if zlabel:
         TwoDHist.GetZaxis().SetTitle(zlabel)
     canvas.Draw()
     #TwoDHist.GetXaxis().SetRange(15, 300)
     canvas.Modified()
     canvas.Update()
     global_scope.append(canvas)
     return canvas

def DrawText(x, y, text, color=1, size=0.05):
    '''Draw text.

    Parameters
    ----------
    x : float
        x position in NDC coordinates
    y : float
        y position in NDC coordinates
    text : string, optional
        The text
    color : int, optional
        Text colour (the default is 1, i.e. black).
        See https://ROOT.cern.ch/doc/master/classTColor.html.
        If you know the hex code, rgb values, etc., use ``ROOT.TColor.GetColor()``
    size : float, optional
        Text size
        See https://ROOT.cern.ch/doc/master/classTLatex.html
    '''
    l = ROOT.TLatex()
    l.SetTextSize(size)
    l.SetNDC()
    l.SetTextColor(color)
    l.DrawLatex(x, y, text)

def handle_underflow_overflow(h):
    '''
    add the underflow and overflow (underflow = 0, overflow=nbins+1)
    '''
    # underflow
    underflow = h.GetBinContent(0)
    first_bin = h.GetBinContent(1)
    h.SetBinContent(1, first_bin+underflow)
    h.SetBinContent(0, 0) # remove underflow
    # underflow error
    underflow_error = h.GetBinError(0)
    first_bin_error = h.GetBinError(1)
    h.SetBinError(1, (underflow_error**2 + first_bin_error**2)**0.5)

    # overflow
    last_bin = h.GetNbinsX()
    last_bin_content = h.GetBinContent(last_bin)
    overflow = h.GetBinContent(last_bin+1)
    h.SetBinContent(last_bin, last_bin_content+overflow)
    h.SetBinContent(last_bin+1, 0) # remove overflow
    # overflow error
    last_bin_error = h.GetBinError(last_bin)
    overflow_error = h.GetBinError(last_bin+1)
    h.SetBinError(last_bin, (last_bin_error**2 + overflow_error**2)**0.5)

    return h

def cleanUpHistograms(h):
    '''Create a histogram with it's characteristics set to standard values.'''
    h.SetLineStyle(1)
    h.SetLineWidth(4)
    h.SetFillStyle(0)
    h.SetFillColor(0)
    h.SetMarkerSize(0)
    return h

def GetHistogramOfErrors(hist_dict):
    '''Given an input dictionary of histograms, return a dictionary of histograms with the bin content set to the error of the bin'''
    dict_keys = hist_dict.keys()

    for key in dict_keys:
        if key not in dict_keys:
            raise ValueError("The two dictionaries do not have the same keys")

    return_dict = {}
    for channel in dict_keys:
        Hist_clone = hist_dict[channel].Clone(hist_dict[channel].GetName() + "Errors")
        Hist_clone.GetXaxis().SetTitle(hist_dict[channel].GetXaxis().GetTitle())
        Hist_clone.GetYaxis().SetTitle(hist_dict[channel].GetYaxis().GetTitle())
        Hist_clone.Sumw2()
        for bin in range(0, Hist_clone.GetNbinsX() + 1):
            hist_clone.SetBinContent(bin, hist_dict[channel])
            hist_clone.SetBinError(bin, 0.0)

        return_dict[channel] = Hist_clone

    return return_dict

def ProjectProfiles(hist_dict):
    '''Get the X Projection of a TProfile histogram. This is useful for dividing TProfile histograms later'''
    for channel in hist_dict:
        hist_dict[channel] = hist_dict[channel].ProjectionX()
    return hist_dict

def GetChannelName(hist_dict, hist):
    if len(hist_dict.keys()) < 2:
        raise ValueError("To figure out the channel name from the histogram dictionary, there needs to be more than one channel")

    other_channel_histogram = None
    keys = list(hist_dict.keys())
    for key in keys:
       if hist_dict[key].GetName() != hist.GetName():
           other_channel_histogram = hist_dict[key]

    hist1_name = hist.GetName()
    hist2_name = other_channel_histogram.GetName()
    first_difference = None

    for i, letter in enumerate(hist2_name):
        if letter != hist1_name[i]:
            first_difference = i
            break

    channel = hist1_name[first_difference:]
    return channel

def DrawDataVsMC(histogram_dict, LegendLabels = {}, MCKeys = [""], DataKey = "", doLogy = True, doLogx = False, ratio_min= 0.0, ratio_max = 2.0, extra_description = None, extra_desx = 0.40, extra_desy = 0.85, scale_factor = 1000, xTicksNumber = None, yTicksNumber = 505, rebin=None, ylabel = None, xAxis_range = None, xlabel=None,marker_size = None, ratio_label = None, invert_ratio = False, bigger_legend = False, skip_data = False, skip_ratio = False, skip_atlas_label=False, skip_legend=False, more_logx_labels=True):
    '''
    This function returns a canvas with a data and MC histogram drawn acoording to configurable settings.

    inputs
    -----------------------------------------------------------------------------------------------------
    histogram_dict: a dictionary of string channel name to TH1 or TProfile
    LegendLabels: a dictionary of string channel name to string description of channel to be used in the legend.
    MCKey: A string corresponding to the key for the MC histogram
    DataKey: a string correponding to the key for the data histogram
    doLogy: Bool. When true, the y axis is drawn with logarithmic scale
    doLogx: Bool. When true, the x axis is drawn with logarithmic scale
    ratio_min: the minimum value of the range of the y-axis in the data/MC ratio plot
    ratio_max: the maximum value of the range of the y-axis in the data/MC ratio plot
    extra_desction: list of strings corresponding to be drawn on the plot. These are used to describe what is being plotted.
    extra_desx: the x co-ordinate of the extra descriptions in NDC coordinates
    extra_desy: the y co-ordinate of the extra descriptions in NDC coordinates
    scale_dactor: the maximual value of the y-axis is set to scale_factor * (largest bin entry)
    xTicksNumber: change the number of ticks on the x-axis
    yTicksNumber: set the number of ticks on the y-axis
    -----------------------------------------------------------------------------------------------------
    '''
    text_size = 0.05
    if not skip_ratio:
        text_size *= 1.3

    global CANVAS_COUNTER #This is to make sure that no two canvases ever get the same name. Otherwise root complains...
    canvas_name = "Canvas" + "".join(MCKeys) + DataKey + str(CANVAS_COUNTER)
    CANVAS_COUNTER = CANVAS_COUNTER + 1
    canvas = ROOT.TCanvas(canvas_name, canvas_name, 1300, 800)
    canvas.cd()

    MCHists_keys = [(histogram_dict[MCKey], MCKey) for MCKey in MCKeys]
    MCHists = [MCHists_key[0] for MCHists_key in MCHists_keys]
    MCKeys = [MCHists_key[1] for MCHists_key in MCHists_keys]

    DataHist = histogram_dict[DataKey]

    if marker_size != None:
        DataHist.SetMarkerSize(marker_size)

    MCHists = [cleanUpHistograms(MCHist) for MCHist in MCHists]
    [MCHist.SetTickLength(0.06) for MCHist in MCHists]
    DataHist.SetTickLength(0.06)

    title_offset = 0.9

    if not skip_ratio:
       [MCHist.GetXaxis().SetLabelSize( float(MCHist.GetXaxis().GetLabelSize() * 1.2) ) for MCHist in MCHists]
       [MCHist.GetYaxis().SetLabelSize( float(MCHist.GetYaxis().GetLabelSize() * 1.2) ) for MCHist in MCHists]
       DataHist.GetYaxis().SetLabelSize( float(MCHists[0].GetYaxis().GetLabelSize() * 1.2) )
       DataHist.GetXaxis().SetLabelSize( float(MCHists[0].GetXaxis().GetLabelSize() * 1.2) )

       [MCHist.GetXaxis().SetTitleSize( float(MCHist.GetXaxis().GetTitleSize() * 1.7) ) for MCHist in MCHists]
       [MCHist.GetYaxis().SetTitleSize( float(MCHist.GetYaxis().GetTitleSize() * 1.7) ) for MCHist in MCHists]
       DataHist.GetYaxis().SetTitleSize( float(MCHists[0].GetYaxis().GetTitleSize() * 1.7) )
       DataHist.GetXaxis().SetTitleSize( float(MCHists[0].GetXaxis().GetTitleSize() * 1.7) )

       [MCHist.GetXaxis().SetTitleOffset( title_offset ) for MCHist in MCHists]
       [MCHist.GetYaxis().SetTitleOffset( title_offset ) for MCHist in MCHists]
       DataHist.GetYaxis().SetTitleOffset(title_offset)

    #title_offset = DataHist.GetYaxis().GetTitleOffset()
    #title_offset = MCHists[0].GetYaxis().GetTitleOffset()

    [MCHist.SetLineColor(COLOURS[MCKey]) for MCKey, MCHist in zip(MCKeys, MCHists)]
    if xlabel:
        [MCHist.GetXaxis().SetTitle(xlabel) for MCHist in MCHists]
    if ylabel:
        [MCHist.GetYaxis().SetTitle(ylabel) for MCHist in MCHists]
    DataHist.SetLineColor(DataColor)

    if rebin != None:
        [MCHist.Rebin(rebin) for MCHist in MCHists]
        DataHist.Rebin(rebin)

    if xAxis_range != None:
        #find the bin to use to set the range
        x_low = None
        x_high = None
        for MCHist in MCHists:
            for bin in range(0, MCHist.GetNbinsX() + 1):
                cent = MCHist.GetBinCenter(bin)
                if cent >= xAxis_range[0] and x_low == None:
                    x_low = bin
                elif cent > xAxis_range[1] and x_high == None:
                    x_high = bin -1

        [MCHist.GetXaxis().SetRange(x_low, x_high) for MCHist in MCHists]
        DataHist.GetXaxis().SetRange(x_low, x_high)

    if not bigger_legend:
        legend = ROOT.TLegend(0.58, 0.65, 0.94, 0.89)
    else:
        legend = ROOT.TLegend(0.58, 0.65, 0.94, 0.89)
        legend.SetNColumns(2)
    legend.SetTextSize(text_size)
    if skip_ratio:
        legend.SetTextSize(text_size * 0.7)
    legend.SetBorderSize(0)
    toGlobalScope(legend)

    if not skip_ratio:
        top_pad = ROOT.TPad("toppad" + str(CANVAS_COUNTER), "toppad" + str(CANVAS_COUNTER), 0, 0.3, 1, 1.0)
    else:
        top_pad = ROOT.TPad("toppad" + str(CANVAS_COUNTER), "toppad" + str(CANVAS_COUNTER), 0, 0.0, 1, 1.0)
    canvas.cd()
    top_pad.Draw()
    top_pad.cd()
    if not skip_ratio:
        top_pad.SetBottomMargin(0)
    else:
        top_pad.SetBottomMargin(0.2)

    filename = MCHists[0].GetTitle() + "histogram"

    if (type(extra_description) == list and len(extra_description) > 3):
        scale_factor *= 10.0

    maximum_bin = 0.0
    minimum_bin = 10000000000000000.0
    for MCHist in MCHists:
        for bin in range(1, MCHist.GetNbinsX() + 1):
            content = MCHist.GetBinContent(bin)
            if content > maximum_bin:
                maximum_bin = content
            if content < minimum_bin and content > 0.0:
                minimum_bin = content

        if not skip_data:
           for bin in range(1, DataHist.GetNbinsX() + 1):
               content = DataHist.GetBinContent(bin)
               if content > maximum_bin:
                   maximum_bin = content
               if content < minimum_bin and content > 0.0:
                   minimum_bin = content

    if doLogy:
        filename += "logy"

    if doLogy:
        if minimum_bin <= 0.0:
            minimum_bin = 1
        for MCHist in MCHists:
            MCHist.SetMaximum(maximum_bin * scale_factor)
            MCHist.SetMinimum(minimum_bin * 0.5)
        DataHist.SetMaximum(maximum_bin * scale_factor)
        DataHist.SetMinimum(minimum_bin * 0.5)

    else:
        for MCHist in MCHists:
            MCHist.SetMaximum(maximum_bin * 1.5)
            MCHist.SetMinimum(minimum_bin * 0.5)
        DataHist.SetMaximum(maximum_bin * 1.5)
        DataHist.SetMinimum(minimum_bin * 0.5)

    if ylabel:
        [MCHist.GetYaxis().SetTitle(ylabel) for MCHist in MCHists]


    MCHists[0].Draw("][ HIST E")
    MCHists[0].Draw("][ HIST SAME")
    for MCHist in MCHists[1:]:
        MCHist.Draw("SAME ][ HIST E")
        MCHist.Draw("SAME ][ HIST")
    if not skip_data:
        DataHist.Draw("SAME")

    hist_description = []
    for MCHist in MCHists:
        fit = MCHist.GetListOfFunctions().Last()
        if not fit:
            continue
        fit.SetLineColor(MCHist.GetLineColor())
        fit.Draw("SAME")
        chisq = fit.GetChisquare()
        ndf = fit.GetNDF()
        prob = fit.GetProb()
        string = "#chi^2/ndf = {:1.3f}/{}      Prob = {:1.3f}".format(chisq, ndf, prob)
        DrawText(0.60, 0.5, string, color = fit.GetLineColor(), size = text_size)

    fit = DataHist.GetListOfFunctions().Last()
    if fit:
       fit.Draw("SAME")
       fit.SetLineColor(DataHist.GetMarkerColor())
       chisq = fit.GetChisquare()
       ndf = fit.GetNDF()
       prob = fit.GetProb()
       string = "#chi^2/ndf = {:1.3f}/{}      Prob = {:1.3f}".format(chisq, ndf, prob)
       DrawText(0.6, 0.6, string, color = fit.GetLineColor(), size = text_size)

    #legend.SetTextSize(0.04)
    for MCHist, MCKey in zip(MCHists, MCKeys):
        legend.AddEntry(MCHist, LegendLabels[MCKey])
    legend.AddEntry(DataHist, LegendLabels[DataKey])
    if not skip_legend:
        legend.Draw()

    if skip_atlas_label:
        extra_desx -= 0.15

    if extra_description:
        if not type(extra_description) == list:
            DrawText(extra_desx, extra_desy, extra_description, size = text_size)
        else:
            top = extra_desy
            for descr in extra_description:
                DrawText(extra_desx, top, descr, size = text_size)
                if not skip_ratio:
                    top -= 0.10
                else:
                    top -= 0.07

    if doLogy:
        top_pad.SetLogy()
    if doLogx:
        top_pad.SetLogx()

    ROOT.gROOT.SetStyle("ATLAS")
    if foundAtlasPlots:
        x = 0.2
        y = 0.85
        if not skip_atlas_label:
            ATLASLabel(x, y, "Internal", size = text_size)
    top_pad.Modified()
    top_pad.Update()
    toGlobalScope(top_pad)

    canvas.cd()
    bottom_pad = ROOT.TPad("botpad" + str(CANVAS_COUNTER), "botpad" + str(CANVAS_COUNTER), 0, 0.01, 1, 0.3)
    if not skip_ratio:
       canvas.cd()
       if doLogx:
           bottom_pad.SetLogx()
       #bottom_pad.SetRightMargin(0.15)
       bottom_pad.Draw()
       bottom_pad.cd()
       toGlobalScope(bottom_pad)

       counter = 0
       for MCHist, MCKey in zip(MCHists, MCKeys):
           counter += 1
           if not invert_ratio:
               data_ratio = DataHist.Clone("data_histogram" + str(counter))
               data_ratio.Divide(MCHist)
           else:
               data_ratio = MCHist.Clone("data_histogram" + str(counter))
               data_ratio.Divide(DataHist)
           data_ratio = cleanUpHistograms(data_ratio)
           data_ratio.SetLineColor(COLOURS[MCKey])

           if doLogx and more_logx_labels:
               data_ratio.GetXaxis().SetMoreLogLabels(True)

           if counter == 1:
               data_ratio.Draw("][ HIST E")
               data_ratio.Draw("][ HIST SAME")
           else:
               data_ratio.Draw("][ HIST SAME E")
               data_ratio.Draw("][ HIST SAME")

           MCHist_label_size = MCHist.GetXaxis().GetLabelSize()
           MCHist_xtitle_size = MCHist.GetXaxis().GetTitleSize()
           MCHist_ytitle_size = MCHist.GetYaxis().GetTitleSize()
           variableLabel = MCHist.GetXaxis().GetTitle()

           data_ratio.GetYaxis().SetNdivisions(yTicksNumber)

           if ratio_label == None:
               data_ratio.GetYaxis().SetTitle("Data/MC")
           else:
               data_ratio.GetYaxis().SetTitle(ratio_label)

           scale_ratio = (top_pad.GetWh()*top_pad.GetAbsHNDC())/(bottom_pad.GetWh() * bottom_pad.GetAbsHNDC())
           data_ratio.GetXaxis().SetLabelSize(MCHist_label_size*(scale_ratio))
           data_ratio.GetYaxis().SetLabelSize(MCHist_label_size*(scale_ratio))
           data_ratio.GetXaxis().SetTitle(variableLabel)
           data_ratio.GetXaxis().SetTitleOffset(title_offset)
           data_ratio.SetMaximum(ratio_max - 0.0001)
           data_ratio.SetMinimum(ratio_min + 0.0001)
           data_ratio.GetXaxis().SetTitleSize(MCHist_xtitle_size*scale_ratio)
           data_ratio.GetYaxis().SetTitleSize(MCHist_ytitle_size*scale_ratio)
           data_ratio.GetYaxis().SetTitleOffset(title_offset/scale_ratio)
           data_ratio.SetMaximum(ratio_max - 0.0001)
           data_ratio.SetMinimum(ratio_min + 0.0001)

           if counter == 1:
               data_ratio.Draw("][ HIST E")
               data_ratio.Draw("][ HIST SAME")
           else:
               data_ratio.Draw("SAME ][ HIST E")
               data_ratio.Draw("SAME ][ HIST SAME")

           toGlobalScope(data_ratio)

           if xTicksNumber != None:
               data_ratio.GetXaxis().SetNdivisions(xTicksNumber)

       ##Draw a set of solid and dotted lines on the ratio plot to guide the reader's eyes
       straight_line = ROOT.TF1("line1", str(1.0) , -10e6, + 10e6)
       straight_line.SetLineWidth(2)
       straight_line.Draw("Same")
       toGlobalScope(straight_line)

       straight_line_up = ROOT.TF1("line2",  str(1.0 + (2.0 * (ratio_max - 1.0)/4)) , -10e6, + 10e6)
       straight_line_up.SetLineWidth(1)
       straight_line_up.SetLineStyle(1)
       straight_line_up.Draw("Same")
       toGlobalScope(straight_line_up)

       straight_line_up2 = ROOT.TF1("line3",  str(1.0 + (1.0 * (ratio_max - 1.0)/4)) , -10e6, + 10e6)
       straight_line_up2.SetLineWidth(1)
       straight_line_up2.SetLineStyle(3)
       straight_line_up2.Draw("Same")
       toGlobalScope(straight_line_up2)

       straight_line_up3 = ROOT.TF1("line4",  str(1.0 + (3.0 * (ratio_max - 1.0)/4)) , -10e6, + 10e6)
       straight_line_up3.SetLineWidth(1)
       straight_line_up3.SetLineStyle(3)
       straight_line_up3.Draw("Same")
       toGlobalScope(straight_line_up3)

       straight_line_down3 = ROOT.TF1("line5",  str(1.0 - (3.0 * (ratio_max - 1.0)/4)) , -10e6, + 10e6)
       straight_line_down3.SetLineWidth(1)
       straight_line_down3.SetLineStyle(3)
       straight_line_down3.Draw("Same")
       toGlobalScope(straight_line_down3)

       straight_line_down = ROOT.TF1("line6",  str(1.0 - (2.0 * (ratio_max - 1.0)/4)) , -10e6, + 10e6)
       straight_line_down.SetLineWidth(1)
       straight_line_down.SetLineStyle(1)
       straight_line_down.Draw("Same")
       toGlobalScope(straight_line_down)

       straight_line_down2 = ROOT.TF1("line7",  str(1.0 - (1.0 * (ratio_max - 1.0)/4)) , -10e6, + 10e6)
       straight_line_down2.SetLineWidth(1)
       straight_line_down2.SetLineStyle(3)
       straight_line_down2.Draw("Same")
       toGlobalScope(straight_line_down2)

       canvas.cd()
       bottom_pad.Modified()
       bottom_pad.Update()

       bottom_pad.Draw()
       bottom_pad.cd()
       bottom_pad.SetTopMargin(0)
       bottom_pad.SetBottomMargin(0.45)

       bottom_pad.Modified()
       bottom_pad.Update()

    top_pad.Modified()
    top_pad.Update()

    canvas.SetRightMargin(0.15);
    canvas.Modified()
    canvas.Update()

    return canvas, top_pad, bottom_pad


def DivideHistograms(hist_dict1, hist_dict2, efficiency_error=True):
    '''take the histograms from two dictionaries hist_dict1 and hist_dict2, and divide them by matching keys. Return a dictionary with each key corresponding to the divided histogram.'''
    dict1_keys = hist_dict1.keys()
    dict2_keys = hist_dict2.keys()

    for key in dict1_keys:
        if key not in dict2_keys:
            raise ValueError("The two dictionaries do not have the same keys")
    for key in dict2_keys:
        if key not in dict1_keys:
            raise ValueError("The two dictionaries do not have the same keys")

    return_dict = {}
    for channel in dict1_keys:
        Hist_clone1 = hist_dict1[channel].Clone(hist_dict1[channel].GetName() + "divided" + hist_dict2[channel].GetName())
        Hist_clone1.GetXaxis().SetTitle(hist_dict1[channel].GetXaxis().GetTitle())
        Hist_clone1.GetYaxis().SetTitle(hist_dict1[channel].GetYaxis().GetTitle())
        Hist_clone1.Divide(hist_dict2[channel])
        if efficiency_error:
            for i in range(0, Hist_clone1.GetNbinsX() + 1):
                eff = Hist_clone1.GetBinContent(i)
                N_o = hist_dict2[channel].GetBinContent(i)
                dP = hist_dict1[channel].GetBinError(i)
                dN = hist_dict2[channel].GetBinError(i)
                dF = ( (dN**2) - (dP**2))**0.5
                if N_o > 0:
                    term1 = ((1-eff)/N_o) * dP
                    term2 = (eff/N_o) * dF
                    err = ( ( (term1**2) + (term2**2) ) ** 0.5)
                    Hist_clone1.SetBinError(i, err)
                else:
                    Hist_clone1.SetBinError(i,0.0)
        return_dict[channel] = Hist_clone1

    return return_dict

def SubtractHistograms(hist_dict1, hist_dict2):
    '''take the histograms from two dictionaries hist_dict1 and hist_dict2, and divide them by matching keys. Return a dictionary with each key corresponding to the divided histogram.'''
    dict1_keys = hist_dict1.keys()
    dict2_keys = hist_dict2.keys()

    for key in dict1_keys:
        if key not in dict2_keys:
            raise ValueError("The two dictionaries do not have the same keys")
    for key in dict2_keys:
        if key not in dict1_keys:
            raise ValueError("The two dictionaries do not have the same keys")

    return_dict = {}
    for channel in dict1_keys:
        Hist_clone1 = hist_dict1[channel].Clone(hist_dict1[channel].GetName() + "subtracted" + hist_dict2[channel].GetName())
        Hist_clone1.GetXaxis().SetTitle(hist_dict1[channel].GetXaxis().GetTitle())
        Hist_clone1.GetYaxis().SetTitle(hist_dict1[channel].GetYaxis().GetTitle())
        Hist_clone1.Add(hist_dict2[channel], -1.0)
        return_dict[channel] = Hist_clone1

    return return_dict

def DivideTwoChannels(hist_dict, channel_numerator, channel_denomenator, new_zlabel = "", z_low = 0.0, z_high = 2.0):
    '''Given a dictionary string channel to TH1D or TProfile histogram, divide the histogram with key channel_numerator by the histogram with key channel denomenator'''
    hist_numerator = hist_dict[channel_numerator]
    hist_denomenator = hist_dict[channel_denomenator]

    Hist_clone = hist_numerator.Clone(hist_dict[channel_numerator].GetName() + "divided" + hist_dict[channel_numerator].GetName())

    Hist_clone.Divide(hist_denomenator)

    Hist_clone.SetMaximum(z_high)
    Hist_clone.SetMinimum(z_low)
    Hist_clone.GetXaxis().SetTitle(new_zlabel)

    return Hist_clone


