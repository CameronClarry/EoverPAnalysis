#ifndef eoverpanalysis_EnergySumHelper_H
#define eoverpanalysis_EnergySumHelper_H

#include <map>
#include <xAODTracking/TrackParticleContainer.h>

namespace EnergySumHelper
{

// LAr barrel
//CALOSAMPLING(PreSamplerB, 1, 0) //  REMOVED
//CALOSAMPLING(EMB1,        1, 0) //  0
//CALOSAMPLING(EMB2,        1, 0) //  1
//CALOSAMPLING(EMB3,        1, 0) //  2

// LAr EM endcap
//CALOSAMPLING(PreSamplerE, 0, 1) //  REMOVED
//CALOSAMPLING(EME1,        0, 1) //  3
//CALOSAMPLING(EME2,        0, 1) //  4
//CALOSAMPLING(EME3,        0, 1) //  5

// Hadronic endcap
//CALOSAMPLING(HEC0,        0, 1) //  6
//CALOSAMPLING(HEC1,        0, 1) //  7
//CALOSAMPLING(HEC2,        0, 1) // 8
//CALOSAMPLING(HEC3,        0, 1) // 9

// Tile barrel
//CALOSAMPLING(TileBar0,    1, 0) // 10
//CALOSAMPLING(TileBar1,    1, 0) // 11
//CALOSAMPLING(TileBar2,    1, 0) // 12

// Tile gap (ITC & scint)
//CALOSAMPLING(TileGap1,    1, 0) // 13
//CALOSAMPLING(TileGap2,    1, 0) // 14
//CALOSAMPLING(TileGap3,    1, 0) // 15

// Tile extended barrel
//CALOSAMPLING(TileExt0,    1, 0) // 16
//CALOSAMPLING(TileExt1,    1, 0) // 17
//CALOSAMPLING(TileExt2,    1, 0) // 18

// Forward EM endcap
//CALOSAMPLING(FCAL0,       0, 1) // 19
//CALOSAMPLING(FCAL1,       0, 1) // 20
//CALOSAMPLING(FCAL2,       0, 1) // 21

// MiniFCAL
//CALOSAMPLING(MINIFCAL0,   0, 1) // 22
//CALOSAMPLING(MINIFCAL1,   0, 1) // 23
//CALOSAMPLING(MINIFCAL2,   0, 1) // 24
//CALOSAMPLING(MINIFCAL3,   0, 1) // 25


    const std::vector<std::string> layer = {
					    "EMB1", //0
					    "EMB2", //1
					    "EMB3", //2
					    "EME1", //3
					    "EME2", //4
					    "EME3", //5
					    "HEC0", //6
					    "HEC1", //7
					    "HEC2", //8
					    "HEC3", //9
					    "TileBar0", //10
					    "TileBar1", //11
					    "TileBar2", //12
					    "TileGap1", //13
					    "TileGap2", //14
					    "TileGap3", //15
					    "TileExt0", //16
					    "TileExt1", //17
					    "TileExt2" //18
                        }; //! array of all the calo layers
    
    const std::vector<std::string> layer_EM = {
					       "EMB1",
					       "EMB2",
					       "EMB3", 
					       "EME1",
					       "EME2",
					       "EME3"
                           };

    const std::vector<std::string> layer_HAD = {
                        "TileBar0",
						"TileBar1", 
						"TileBar2",
						"TileGap1",
						"TileGap2",
						"TileGap3",
						"TileExt0",
						"TileExt1",
						"TileExt2", 
						"HEC0",
						"HEC1",
						"HEC2",
						"HEC3"
                        }; //! array of HAD layers only

    const std::map<std::string, float> map_cutName_to_cutValue{
                                  {"025",0.025},
                                  {"050",0.050},
                                  {"075",0.075},
                                  {"100",0.100},
                                  {"125",0.125},
                                  {"150",0.150},
                                  {"175",0.175},
                                  {"200",0.200},
                                  {"225",0.225},
                                  {"250",0.250},
                                  {"275",0.275},
                                  {"300",0.300}
                                  };
               

    const std::map<std::string, unsigned int> layer_to_id = {
							      {"EMB1", 0},
							      {"EMB2", 1},
							      {"EMB3", 2},
							      {"EME1", 3},
							      {"EME2", 4}, 
							      {"EME3", 5},
							      {"HEC0", 6},
							      {"HEC1", 7},
							      {"HEC2", 8},
							      {"HEC3", 9},
							      {"TileBar0", 10},
							      {"TileBar1", 11},
							      {"TileBar2", 12},
							      {"TileGap1", 13},
							      {"TileGap2", 14},
							      {"TileGap3", 15},
							      {"TileExt0", 16},
							      {"TileExt1", 17},
							      {"TileExt2", 18}
                                  };

    const std::map<unsigned int, std::string> id_to_layer = { 
							      {1, "EMB1"},
							      {2, "EMB2"},
							      {3, "EMB3"},
							      {5, "EME1"},
							      {6, "EME2"},
							      {7, "EME3"},
							      {8, "HEC0"}, 
							      {9, "HEC1"}, 
							      {10, "HEC2"},
							      {11, "HEC3"},
							      {12, "TileBar0"},
							      {13, "TileBar1"},
							      {14, "TileBar2"},
							      {15, "TileGap1"},
							      {16, "TileGap2"},
							      {17, "TileGap3"},
							      {18, "TileExt0"}, 
							      {19, "TileExt1"}, 
							      {20, "TileExt2"}
                                  };

    extern std::map<unsigned int, float> getEnergySumInLayers(const xAOD::TrackParticle* trk, 
							      std::string variableToSum,
							      std::string radiusCut);
    
    extern std::map<std::string, float> getEnergySumInCalorimeterRegions(const xAOD::TrackParticle* trk,
									 std::string variableToSum, 
									 std::string radiusCut,
									 bool onlyPositiveEnergy = false);

    extern std::map<unsigned int, std::map<std::string, std::map<std::string, int > > > getNumberOfClustersInLayers(
                                     const xAOD::TrackParticle* trk,
                                     const std::map<std::string,float> map_cut_names_to_values);

    extern std::map<std::string, std::map< std::string, std::map<std::string, int> > > getNumberOfClustersInCaloriemterRegions(
                                     const xAOD::TrackParticle* trk,
                                     const std::map<std::string,float> map_cut_names_to_values);
}

#endif
