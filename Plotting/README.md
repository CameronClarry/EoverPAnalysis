# EoverPPlotting

These macros ship jobs to condor for all of your plotting needs. The histograms are filled in the Fillingscript.py file.

## Setup
Create the environment needed for plotting. This package uses a python virtual environment (https://docs.python.org/3/tutorial/venv.html), in conjuction with an lcg virtual environment (https://ep-dep-sft.web.cern.ch/document/lcg-releases). You must be on a fresh login of lxplus (centos7) for everything to work. The setup will not work if an analysisbase release has be set up, for example. Running this package on any computing site with condor and cvmfs should (in principle) work. 

You must set the CMT config to match your operating system. "CMTCONFIG=x86_64-centos7-gcc8-opt" for centos7, and "CMTCONFIG=x86_64-slc6-gcc8-opt" for slc6
```
cd EoverPAnalysis/Plotting
git clone ssh://git@gitlab.cern.ch:7999/luadamek/lcg_virtualenv.git ./lcg_virtualenv
CMTCONFIG=x86_64-centos7-gcc8-opt ./lcg_virtualenv/create_lcg_virtualenv venv_EOPPlotting LCG_94python3
source venv_EOPPlotting/bin/activate
```

Install all of the dependencies. This package uses uproot (https://uproot.readthedocs.io/en/latest/), along with python bindings for XRootD (https://github.com/xrootd/xrootd).
First upgrade pip.
```
pip install --upgrade pip
```

Next install atlas-plots to help make the plots look good.
```
git clone https://github.com/joeycarter/atlas-plots.git
cd atlas-plots
pip install -e .
cd ..
```

Next install xrootd to run over the ntuples stored on atlas eos. Make sure to checkout a stable brance -- e.g. stable-5.0.x.
```
git clone https://github.com/xrootd/xrootd.git
cd xrootd/bindings/python/
git checkout stable-4.11.x
python setup_standalone.py install
cd ../../../
pip install uproot
```

Finish the setup by running the setup script
```
source ./setup.sh
```

Every few months, you will need to generate a grid proxy to access files on eos. You can do this with the following lines. This is required to access the files that are stored on eos.
```
voms-proxy-init --voms atlas --hours 10000
```

Here you can create a standalone installation of the JES_ResponseFitter that should work with pyroot.
```
git clone ssh://git@gitlab.cern.ch:7999/luadamek/JES_ResponseFitter.git
cd JES_ResponseFitter
mkdir build
cd build
cmake ../ && make
cd ${EOPPlottingDir}
```

## When logging back in
```
cd $TestArea/EoverPAnalysis/Plotting
source ./setup.sh
```

## Package Philosophy
A plotting job is defined in a script such as macros/fill_script.py, which must have a function called fill_histograms. fill_histograms takes a HistogramFiller instance, an output rootfile name, and fills histograms. Take a look inside of the script fill_scipt.py to get an idea of how this works. From a user's perspective, one does not have to worry about creating an instance of a "HistogramFiller" or defining the name of the output rootfile. The scripts responsible for shipping jobs to condor handle everything. 

All selections and variables to be plotted are defined as instances of the class "Caclulation". To define a new selection for tracks in a plot, you could write the following function:
```
from calculation import Calculation
def TightIso(trk):
    return trk["trk_nearest_dR_EM"] > 0.55
sel_TightIso = Calculation(TightIso, ["trk_nearest_dR_EM"])
```
The initialization of Calculation takes a function that calculates the selection (trk_nearest_dR_EM > 0.55), and a list of branches needed to perform the calculation (trk_nearest_dR_EM).

Similarly, one can create a function that calculates E/P
```
from calculation import Calculation
def EOP(trk):
    return (trk["trk_ClusterEnergy_EM_200"] + trk["trk_ClusterEnergy_HAD_200"])/trk["trk_p"]
branches = ["trk_ClusterEnergy_EM_200", "trk_ClusterEnergy_HAD_200", "trk_p"]
calc_EOP = Calculation(EOP, branches)
```

To fill an EOP histogram for all tracks passing the TightIso selection, define a histogram filling script like macros/fill_script_test.py .
```
def fill_histograms(hist_filler, outputRootFileName):
    outFile = ROOT.TFile(outputRootFileName, "RECREATE")

    #count the number of tracks in each channel
    histogram_name = "EOP"
    selections = [sel_TightIso]
    trkCountHist = hist_filler.book_histogram_fill(histogram_name,\
                                                         calc_EOP,\
                                                         selections = selections,\
                                                         bins = 100,\
                                                         range_low = -0.5,\
                                                         range_high = +3.5,\
                                                         xlabel ='E/P',\
                                                         ylabel = 'Number of Tracks')
    histograms = hist_filler.DumpHistograms()
    for histogram_name in histograms:
        write_histograms(histograms[histogram_name], outFile)

    outFile.Close()
```

The following lines would prepare a batch job for submission. This job would use 100 condor jobs, and run over a test set of files. The condor jobqueue corresponds to the --queue_flavour flag and can be set to espresso (20mins), longlunch (2hr), workday (8hr), etc. Notice that you have to define the "file flavour". These are defined in utils/utils.py and include a list of files separated by channels. Histograms will be filled for each channel independently by the histogram filling script. "test" includes channels for "PythiaJetJet", "LowMuData", and "SinglePions".
```
python macros/prepare_submission.py --tree_name LA_EoverP_InDetTrackParticlesSortedLooseIsolatedVertexAssociated_tree --n_jobs 100 --queue_flavour longlunch --file_flavour test --filling_script macros/fill_script.py --job_name test
```
You can change the argument passed to --filling_script to any filling script that you have written.

These lines will prepare a batch job for plotting from the identified hadron trees. 
```
python macros/prepare_submission.py --tree_name Tree_Ks --n_jobs 100 --queue_flavour longlunch --file_flavour identified --filling_script macros/fill_script_identified.py --job_name identified_ks
```


## Test one of the jobs locally
```
source condor/test/test_scripts/plot_local.sh 1 condor/test/Submission/test.pickle test
```

## Submit all of the batch jobs
```
condor_submit condor/test/test_scripts/condor_test.sub
```

## Upon job completion
An useful feature of hadd, is the ability to parallelize the h-addition of files. Call had with the flag -j ncores to use this feature.
```
hadd Plots_hadded.root Plots\*.root
```

## Create Reweighing histograms
The macro responsible for reweighing histograms can be found in the file ReweightingHistograms/CreateReweightingHistogram.py. There are a series of flags that you need to pass to the macro to create the reweighting.
```
python ReweightingHistograms/CreateReweightingHistogram.py >>args<<
```

## Apply Rewighing when filling histograms
In the filling script one could define a histogram as below. Note the definition of the selection and the variable that is being filled.
```
#count the number of events in each channel
histogram_name = "EventCount"
selections = [sel_Event]
trkCountHist = hist_filler.book_histogram_fill(histogram_name,\
calc_trkCount,\
selections = selections,\
bins = 1,\
range_low = -0.5,\
range_high = +0.5,\
xlabel ='Always 0',\
ylabel = 'Number Events')
```

One could then create a reweighting histogram, and add it as a weight to the histogram_filler. notice that the variable (calc_trkCount) and the selection are the same as when the reweighting was defined, as above. The Reweighting file contains a histogram of LowMuData divided by the same histogram for Pythia JetJet. This would allow the code to reweight the events when filling the histograms, so that the distribition in MC is forced to agree with data.
```
LowMuData_PythiaJetJet_Count_Reweight_file = ROOT.TFile(os.path.join(base_directory,"ReweightingHistograms/LowMuData_PythiaJetJet_Count_Reweight.root    "),"READ")
hist = LowMuData_PythiaJetJet_Count_Reweight_file.Get("LowMuData_PythiaJetJet_Count_Reweight")
hist_filler.weight_calculator.add_reweight_histogram("PythiaJetJet", [calc_trkCount], hist, selection = [sel_Event])
```


## Create TTrees to use for binning. These contain information about the total # of tracks and std deviation.
```
python BinningInformationTree/CreateBinningInformationTree.py -selname MIPSelectionHadFracAbove70 --file PTSpectrumReweighted.root --histogramName EOPDistribution --outputFile MIPSelectonHadFracAbove70Binning
python BinningInformationTree/CreateBinningInformationTree.py -selname 20TRTHitsNonZeroEnergy --file PTSpectrumReweighted.root --histogramName EOPDistribution --outputFile 20TRTHitsNonZeroEnergyBinning
```

## Draw histograms
```
git clone git@github.com:joeycarter/atlas-plots.git
cd atlas-plots
pip install -e . --user
cd ..
python
from CreatePlots import CreatePlots
CreatePlots("Outputs/Plots/Plots_hadded.root")
```
