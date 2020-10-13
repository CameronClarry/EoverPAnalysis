export EOPPlottingDir=${PWD}
export PYTHONPATH="${EOPPlottingDir}/utils:$PYTHONPATH"
export PYTHONPATH="${EOPPlottingDir}/eop_plotting:$PYTHONPATH"
export PYTHONPATH="${EOPPlottingDir}/macros:$PYTHONPATH"
export X509_USER_PROXY=${EOPPlottingDir}/grid_proxy
export PATH=/cvmfs/sft.cern.ch/lcg/external/texlive/2016/bin/x86_64-linux:$PATH
echo "READY TO GO!"
