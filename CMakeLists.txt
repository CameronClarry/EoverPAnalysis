################################################################################
# Package: EoverPAnalysis
################################################################################

# Declare the package name:
atlas_subdir( EoverPAnalysis )

# Find the needed external(s):
find_package( ROOT COMPONENTS Core RIO Hist Tree )
find_package( Eigen REQUIRED )

# build a dictionary for the library
atlas_add_root_dictionary ( EoverPAnalysisLib EoverPAnalysisDictSource
			    ROOT_HEADERS EoverPAnalysis/EoverPTreeAlgo.h EoverPAnalysis/TrackExtrapolationIsolationTool.h EoverPAnalysis/SecondariesTrees.h Root/LinkDef.h
                            EXTERNAL_PACKAGES ROOT
)

# build a shared library
atlas_add_library( EoverPAnalysisLib EoverPAnalysis/*.h Root/*.cxx ${EoverPAnalysisDictSource}
                   PUBLIC_HEADERS EoverPAnalysis
                   INCLUDE_DIRS ${ROOT_INCLUDE_DIRS} ${EIGEN_INCLUDE_DIRS}
                   LINK_LIBRARIES ${ROOT_LIBRARIES} 
                   xAODAnaHelpersLib 
)

# Install files from the package:
atlas_install_scripts( scripts/*.py )
atlas_install_data( data/* )
