# E/p analysis for run 2
# Lukas Adamek (lukas.adamek@cern.ch)

#from xAH_config import xAH_config
from xAODAnaHelpers import Config as xAH_config
c = xAH_config()

import shlex,argparse

# Parser for options passed through xAH_run.py --extraOptions="(...)"
parser = argparse.ArgumentParser("MLBJESJER")
parser.add_argument('--isData', action='store_true', default=False)
parser.add_argument('--isSingleParticle', action='store_true', default=False)
args = parser.parse_args(shlex.split(args.extra_options))

c.output("ANALYSIS")

# input containers
trks_unsorted = "InDetTrackParticles"
trks = "InDetTrackParticlesSorted"
trks_loose = trks + "Loose"
trks_tight = trks + "Tight"
trks_loose_isolated = trks_loose + "Isolated"
trks_tight_isolated = trks_tight + "Isolated"
trks_loose_isolated_vertex = trks_loose_isolated + "VertexAssociated"
trks_tight_isolated_vertex = trks_tight_isolated + "VertexAssociated"
radiusCuts = "025,050,075,100,125,150,175,200,225,250,275,300"

# Set up the Basic Event Selection for 2017 low-mu data
c.algorithm("BasicEventSelection", {"m_name": "BasicEventSelection",
                                 "m_applyGRLCut": args.isData,
                                 "m_doPUreweighting": False,
                                 "m_applyPrimaryVertexCut": True,
                                 "m_applyEventCleaningCut": True,
                                 "m_applyCoreFlagsCut": args.isData,
                                 "m_applyTriggerCut": args.isData,
                                 "m_GRLxml": "EoverPAnalysis/data17_13TeV.periodN_DetStatus-v98-pro21-16_Unknown_PHYS_StandardGRL_All_Good_25ns_ignore_GLOBAL_LOWMU.xml",
                                 "m_lumiCalcFileNames": "EoverPAnalysis/ilumicalc_histograms_HLT_mb_sptrk_341294_OflLumi-13TeV-010.root",
                                 "m_PRWFileNames": "EoverPAnalysis/ntup_prw_36102_JZ012.root",
                                 "m_triggerSelection": "HLT_mb_sptrk",
                                 "m_applyPrimaryVertexCut": (not args.isSingleParticle),
                                 "m_PVNTrack": 2,
                                 "m_useMetaData": False,
                                 "m_checkDuplicatesData": False,
                                 "m_checkDuplicatesMC": False
				 })


'''Sort the tracks by pt first'''
c.algorithm("TrackSorter", {"m_name" : "TrackSorting",\
                         "m_inTrackContainerName":trks_unsorted,\
                         "m_sort":"Pt",\
                         "m_sortedTrackContainerName" : trks,\
                         })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", {"m_name": "TrackEnergyDecoratorAlgoUno",
				  "m_energySumName":"TotalCalibHitEnergy",
                                  "m_inTrackContainerName": trks,
                                  "m_radiusCutCommaList":radiusCuts,
                                  "m_energyCalibCommaList":"ClusterEMActiveCalibHitEnergy,ClusterNonEMActiveCalibHitEnergy,ClusterEscapedActiveCalibHitEnergy,ClusterInvisibleActiveCalibHitEnergy,ClusterEMInactiveCalibHitEnergy,ClusterNonEMInactiveCalibHitEnergy,ClusterEscapedInactiveCalibHitEnergy,ClusterInvisibleInactiveCalibHitEnergy",
				  })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", { "m_name": "TrackEnergyDecoratorAlgoDos",
				   "m_energySumName":"TotalPhotonBackgroundCalibHitEnergy",
                                  "m_inTrackContainerName": trks,
				   "m_radiusCutCommaList":radiusCuts,
				   "m_energyCalibCommaList":"ClusterPhotonBackgroundEMActiveCalibHitEnergy,ClusterPhotonBackgroundNonEMActiveCalibHitEnergy,ClusterPhotonBackgroundEscapedActiveCalibHitEnergy,ClusterPhotonBackgroundInvisibleActiveCalibHitEnergy,ClusterPhotonBackgroundEMInactiveCalibHitEnergy,ClusterPhotonBackgroundNonEMInactiveCalibHitEnergy,ClusterPhotonBackgroundEscapedInactiveCalibHitEnergy,ClusterPhotonBackgroundInvisibleInactiveCalibHitEnergy",
				  })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", { "m_name": "TrackEnergyDecoratorAlgoTres",
				   "m_energySumName":"TotalHadronicBackgroundCalibHitEnergy",
				   "m_inTrackContainerName": trks,
				   "m_radiusCutCommaList":radiusCuts,
				   "m_energyCalibCommaList":"ClusterHadronicBackgroundEMActiveCalibHitEnergy,ClusterHadronicBackgroundNonEMActiveCalibHitEnergy,ClusterHadronicBackgroundEscapedActiveCalibHitEnergy,ClusterHadronicBackgroundInvisibleActiveCalibHitEnergy,ClusterHadronicBackgroundEMInactiveCalibHitEnergy,ClusterHadronicBackgroundNonEMInactiveCalibHitEnergy,ClusterHadronicBackgroundEscapedInactiveCalibHitEnergy,ClusterHadronicBackgroundInvisibleInactiveCalibHitEnergy",
				  })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", { "m_name": "TrackEnergyDecoratorAlgoQuaddro",
				   "m_energySumName":"CalibEMActiveEnergy",
				   "m_inTrackContainerName": trks,
				   "m_radiusCutCommaList":radiusCuts,
				   "m_energyCalibCommaList":"ClusterEMActiveCalibHitEnergy",\
				  })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", { "m_name": "TrackEnergyDecoratorAlgoCenqo",
				   "m_energySumName":"CalibEMInactiveEnergy",
				   "m_inTrackContainerName": trks,
				   "m_radiusCutCommaList":radiusCuts,
				   "m_energyCalibCommaList":"ClusterEMInactiveCalibHitEnergy",\
				  })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", { "m_name": "TrackEnergyDecoratorAlgoQuaddroAgain",
				   "m_energySumName":"CalibNonEMActiveEnergy",
				   "m_inTrackContainerName": trks,
				   "m_radiusCutCommaList":radiusCuts,
				   "m_energyCalibCommaList":"ClusterNonEMActiveCalibHitEnergy",\
				  })

# Create new energy sum decorations for the tracks
c.algorithm("TrackEnergyDecorator", { "m_name": "TrackEnergyDecoratorAlgoCenqoHereWeGo",
				   "m_energySumName":"CalibNonEMInactiveEnergy",
				   "m_inTrackContainerName": trks,
				   "m_radiusCutCommaList":radiusCuts,
				   "m_energyCalibCommaList":"ClusterNonEMInactiveCalibHitEnergy",\
				  })

# Fill histograms with tracking details, passing only basic event selection
c.algorithm("TrackHistsAlgo", {"m_name": "Tracks_BasicEvtSel",
                            "m_inContainerName": trks,
                            "m_detailStr": "2D IPDetails HitCounts Chi2Details",
                            "m_msgLevel": "info"
			               })

# track selection algorithm
c.algorithm("InDetTrackSelectionToolAlgo", {"m_name": "Sel_" + trks_loose,
					 "m_inputTrackContainer": trks,
					 "m_minPt": 0.5,
					 "m_CutLevel": "Loose",
					 "m_outputTrackContainer": trks_loose,
					 "m_msgLevel": "info"
					 })


# Fill histograms with tracking details, after LoosePrimary selection
c.algorithm("TrackHistsAlgo", {"m_name": "TrackHist_" + trks_loose,
                            "m_inContainerName": trks_loose,
                            "m_detailStr": "2D IPDetails HitCounts Chi2Details",
                            "m_msgLevel": "info"
			                })

c.algorithm("TrackExtrapolationIsolationTool", {"m_name": "TrackIso_" + trks_loose,
					     "m_inputTrackContainer": trks_loose,
					     "m_outputTrackContainer": trks_loose_isolated,
					     "m_trkIsoDRmax": 0.4,
					     "m_msgLevel": "info"
					     })

# Fill histograms with tracking details, after LoosePrimary + Isolation selection
c.algorithm("TrackHistsAlgo", {"m_name": "TrackHist_" + trks_loose_isolated,
                            "m_inContainerName": trks_loose_isolated,
                            "m_detailStr": "2D IPDetails HitCounts Chi2Details",
                            "m_msgLevel": "info"
			               })

c.algorithm("InDetTrackSelectionToolAlgo", {"m_name": "Sel_" + trks_tight_isolated ,
					 "m_inputTrackContainer": trks_loose_isolated,
					 "m_outputTrackContainer": trks_tight_isolated,
					 "m_CutLevel": "TightPrimary",
					 "m_msgLevel": "info"
					 })

# Fill histograms with tracking details, after LoosePrimary + Isolation + tight primary selection
c.algorithm("TrackHistsAlgo", {"m_name": "TrackHist_" + trks_tight_isolated,
                            "m_inContainerName": trks_tight_isolated,
                            "m_detailStr": "2D IPDetails HitCounts Chi2Details",
                            "m_msgLevel": "info"
			               })

if not args.isSingleParticle:
    c.algorithm("TrackVertexAssociationToolAlgo", {"m_name":"LooseTrackVertexAssociationTool",
						 "m_inputTrackContainer": trks_loose_isolated,
						 "m_outputTrackContainer": trks_loose_isolated_vertex,
                         "m_workingPoint": "Old_Tight",
						 #"m_dzSinTheta_cut": 1.5,
						 #"m_d0_cut": 1.5,
						 "m_msgLevel": "info",
						 })
else:
    c.algorithm("TrackSorter", {"m_name" : "TrackSortingRenameOne",\
                         "m_inTrackContainerName":trks_loose_isolated,\
                         "m_sort":"Pt",\
                         "m_sortedTrackContainerName" : trks_loose_isolated_vertex,\
                         })

# Fill histograms with tracking details, after LoosePrimary + Isolation + vertex association cut
c.algorithm("TrackHistsAlgo", {"m_name": "TrackHist_" + trks_loose_isolated_vertex,
                            "m_inContainerName": trks_loose_isolated_vertex,
                            "m_detailStr": "2D IPDetails HitCounts Chi2Details",
                            "m_msgLevel": "info"
			               })

if not args.isSingleParticle:
    c.algorithm("TrackVertexAssociationToolAlgo", {"m_name":"TrackVertexAssociationTool",
						 "m_inputTrackContainer": trks_tight_isolated,
						 "m_outputTrackContainer": trks_tight_isolated_vertex,
                         "m_workingPoint": "Old_Tight",
						 #"m_dzSinTheta_cut": 1.5,
						 #"m_d0_cut": 1.5,
						 "m_msgLevel": "info",
						 })
else:
    c.algorithm("TrackSorter", {"m_name" : "TrackSortingRenameOne",\
                         "m_inTrackContainerName":trks_tight_isolated,\
                         "m_sort":"Pt",\
                         "m_sortedTrackContainerName" : trks_tight_isolated_vertex,\
                         })

# Fill histograms with tracking details, after LoosePrimary + Isolation + Tight Primary + vertex association cut
c.algorithm("TrackHistsAlgo", {"m_name": "TrackHist_" + trks_tight_isolated_vertex,
                            "m_inContainerName": trks_tight_isolated_vertex,
                            "m_detailStr": "2D IPDetails HitCounts Chi2Details",
                            "m_msgLevel": "info"
			               })

#### Make E/p ttree
for track_container in [trks_loose_isolated, trks_loose_isolated_vertex]:#, trks_tight_isolated, trks_tight_isolated_vertex]:
        # E/p histograms with LoosePrimary track selection
        c.algorithm("EoverPTreeAlgo", {"m_name": "LA_EoverP_" + track_container,
				    "m_inTrackContainerName": track_container,
				    "m_energyCalibCommaList": "ClusterEnergy,CellEnergy,LCWClusterEnergy,TotalCalibHitEnergy,TotalPhotonBackgroundCalibHitEnergy,TotalHadronicBackgroundCalibHitEnergy,CalibEMActiveEnergy,CalibEMInactiveEnergy,CalibNonEMActiveEnergy,CalibNonEMInactiveEnergy",
				    "m_radiusCutCommaList": radiusCuts,
				    "m_useCutFlow": True,
                    "m_msgLevel": "info"
				    })

if not args.isSingleParticle:
    for sv in ['Lambda','Ks','Phi']:
        c.algorithm("SecondariesTrees", {"m_name": "MLB_EoverP_" + sv,
                         "label": sv,
                         "isData": args.isData,
                         "MessageFrequency": 10000,
                         "VertexContainer" : sv+"Candidates",
                         "radiusCutCommaList": radiusCuts,
                         "energyCalibCommaList": "ClusterEnergy,CellEnergy,LCWClusterEnergy,TotalCalibHitEnergy,TotalPhotonBackgroundCalibHitEnergy,TotalHadronicBackgroundCalibHitEnergy,CalibEMActiveEnergy,CalibEMInactiveEnergy,CalibNonEMActiveEnergy,CalibNonEMInactiveEnergy",
                         "TrackContainer" : trks_loose
                         })
	
