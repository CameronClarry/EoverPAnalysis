# EoverPAnalysis

This package is based on the [xAODAnaHelpers (xAH)](https://github.com/UCATLAS/xAODAnaHelpers) RootCore package, thus I strongly recommend you check out the [xAH documentation first](https://xaodanahelpers.readthedocs.io/en/latest/).

For questions please contact: lukas.adamek[at]cern.ch, or joakim.olsson[at]cern.ch

Package created by Joakim Olsson
Ported to release 21 and modified by: Lukas Adamek (lukas.adamek[at]cern.ch)
Ported to release 22 and modified by: Cameron Clarry (cameron.clarry[at]cern.ch)

## Setup in Release 22

First setup the folders for running, building and the source files
```
setupATLAS -c centos7
mkdir myAnalysis; cd myAnalysis
mkdir source build run
cd source
```

Clone the packages that this analysis depends on. 
```
git clone https://github.com/CameronClarry/EoverPAnalysis.git
cp EoverPAnalysis/UpperCMakeLists.txt CMakeLists.txt
git clone http://github.com/UCATLAS/xAODAnaHelpers xAODAnaHelpers
cd xAODAnaHelpers && git checkout c6e4ebfa7a64a9330be836e23a93a26b3f7aae10 && cd ..
git clone https://github.com/CameronClarry/IDTrackSel.git
cd IDTrackSel && git checkout r22-updates && cd ..
asetup AnalysisBase,24.2.6,here
cd ../build
cmake ../source && make
```

## Running locally in Release 22

The Analysis configurations are located in the scripts folder, called xAH_EoverP.py. These scripts are responsible for booking/running EoverP xAH Algorithms to create ttrees for four different track selections, and store information about calorimeter energy deposits at the cell, EM, and LCW scale. To run a test job locally, try the following lines:
```
setupATLAS -c centos7
cd myAnalysis/source
asetup
cd ../
source build/x86_64-centos7-gcc11-opt/setup.sh
cd run
# For MC
xAH_run.py --files=>>DAOD_EOP_FILE<< --config=$TestArea/EoverPAnalysis/scripts/xAH_EoverP.py --submitDir=test_run --force --mode athena direct
# For data
xAH_run.py --extraOptions="--isData" --files=>>DAOD_EOP_FILE<< --config=$TestArea/EoverPAnalysis/scripts/xAH_EoverP.py --submitDir=test_run --force --mode athena direct
```
The file which contains the ttrees has the form ``test_run/hists-*.root``, depending on your input files.

## Submitting Grid Jobs in Release 22
Grid jobs are handled by a submission script located in $TestArea/EoverPAnalysis/scripts/. The grid job script takes four arguments as input: the submission directory, a txt file with all samples listed, a descriptor to label the output, and a configuration file. As an example, the following command will submit grid jobs to run over the 361022 jet jet MC sample.
```
setupATLAS -c centos7
lsetup panda
cd myAnalysis/source
asetup
cd ../
# Customize this for the production to be done
# Data
prun --bexec "ls;pwd;mkdir build;cd build;cmake ../source;make;cd ../" --exec "ls;pwd;source build/x86_64-centos7-gcc11-opt/setup.sh;echo %IN | tr ',' '\n' > files.txt;cat files.txt;xAH_run.py --extraOptions='--isData' --inputList --files=files.txt --config=source/EoverPAnalysis/scripts/xAH_EoverP.py --submitDir=grid-run --force --mode athena direct;cp grid-run/hist-files.root ./" --inDS <INPUT DATASET NAME> --output hist-files.root --outDS user.username.<OUTPUT DATASET NAME> --athenaTag=AnalysisBase,24.2.6 --excludeFile ./build/,./source/EoverPAnalysis/Plotting/,./run/
# Monte Carlo
prun --bexec "ls;pwd;mkdir build;cd build;cmake ../source;make;cd ../" --exec "ls;pwd;source build/x86_64-centos7-gcc11-opt/setup.sh;echo %IN | tr ',' '\n' > files.txt;cat files.txt;xAH_run.py --isMC --inputList --files=files.txt --config=source/EoverPAnalysis/scripts/xAH_EoverP.py --submitDir=grid-run --force --mode athena direct;cp grid-run/hist-files.root ./" --inDS <INPUT DATASET NAME> --output hist-files.root --outDS user.username.<OUTPUT DATASET NAME> --athenaTag=AnalysisBase,24.2.6 --excludeFile ./build/,./source/EoverPAnalysis/Plotting/,./run/
```

## Setup in Release 21

First setup the folders for running, building and the soruce files
```
mkdir myAnalysis; cd myAnalysis
mkdir source run build run/results
cd source
```

Clone the packages that this analysis depends on. 
```
git clone http://github.com/UCATLAS/xAODAnaHelpers xAODAnaHelpers
cd xAODAnaHelpers && git checkout aaf7fc3fde9819bcb5cc3737df0226e275110671 && cd ..
git clone http://github.com/luadamek/EoverPAnalysis
git clone https://github.com/mattleblanc/IDTrackSel.git
cd IDTrackSel && git checkout 13211645b1aa6c723d4f2c0b3492d5009dde8ee5 && cd ..
asetup AnalysisBase,21.2.84,here
cd ../build
cmake ../source && make
```

## Running locally in Release 21
The Analysis configurations are located in the scripts folder, called xAH_EoverP.py. These scripts are responsible for booking/running EoverP xAH Algorithms to create ttrees for four different track selections, and store information about calorimeter energy deposits at the cell, EM, and LCW scale. Files are located in  To run a test job locally, try the following lines:
```
cd ../build
source */setup.sh
cd ../run
mkdir results
xAH_run.py --files=>>DAOD_EOP_FILE<< --config=$TestArea/EoverPAnalysis/scripts/xAH_EoverP.py --submitDir=test_run --force direct
```

## Submitting Grid Jobs in Release 21
Grid jobs are handled by a submission script located in $TestArea/EoverPAnalysis/scripts/. The grid job script takes four arguments as input: the submission directory, a txt file with all samples listed, a descriptor to label the output, and a configuration file. As an example, the following command will submit grid jobs to run over the 361022 jet jet MC sample.
```
cd ../run
python ../source/EoverPAnalysis/scripts/submit_grid.py --user luadamek --tag EoverP --overwrite True --config ../source/EoverPAnalysis/scripts/xAH_EoverP.py --descriptor Jan7 --FileList ../source/EoverPAnalysis/filelists/mc16/mc16_JZ012.txt
```

## Plotting
Plotting macros can be found the root_numpy_plotting folder. See the README contained in that folder.

## Hadding together large root files. (Outdated. Not longer needed. The plotting code uses tchains).
A macro exists for hadding together root files that are too large (> ~ 100 Gb). To use the macro, do:
```
python hadd_bigfiles.py __outputfilename__ __directorywithfiles__
```
Do this on the /tmp/user/ directory of LxPlus nodes, and then move the large file to the final destination.
