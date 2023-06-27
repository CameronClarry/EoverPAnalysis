// E/p analysis for run 2
// Lukas Adamek (lukas.adamek@cern.ch)

#include <EventLoop/Job.h>
#include <EventLoop/StatusCode.h>
#include <EventLoop/Worker.h>
#include <EventLoop/OutputStream.h>
#include "AthContainers/ConstDataVector.h"
#include "xAODEventInfo/EventInfo.h"
#include "xAODTruth/TruthParticle.h"
#include "xAODAnaHelpers/HelperFunctions.h"
#include <EoverPAnalysis/EoverPTreeAlgo.h>
//#include "AsgTools/MessageCheck.h"
#include "TMath.h"

#include "xAODTruth/TruthParticleContainer.h"
#include "xAODTruth/TruthParticle.h"
#include "AthLinks/ElementLink.h"
#include "AthContainers/AuxElement.h"
#include "EoverPAnalysis/EnergySumHelper.h"

// this is needed to distribute the algorithm to the workers
ClassImp(EoverPTreeAlgo)

  EoverPTreeAlgo :: EoverPTreeAlgo (std::string className) :
    Algorithm(className),
    // cutflows
    m_cutflowHist(nullptr),
    m_cutflowHistW(nullptr),
    m_trk_cutflowHist_1(nullptr),
    m_eventNumber(0),
    m_trkIndex(0),
    m_tree(nullptr)
{
  m_inTrackContainerName    = "";
  m_debug                   = false;
}

EL::StatusCode EoverPTreeAlgo :: setupJob (EL::Job& job)
{
  job.useXAOD();
  xAOD::Init("EoverPTreeAlgo").ignore();

  EL::OutputStream outForTree("tree");
  if(!job.outputHas("tree") ){ job.outputAdd ( outForTree ); }

  return EL::StatusCode::SUCCESS;
}

EL::StatusCode EoverPTreeAlgo :: histInitialize ()
{

  Info("histInitialize()", "%s", m_name.c_str() );
  ANA_CHECK(xAH::Algorithm::algInitialize());
  // needed here and not in initalize since this is called first
  if( m_inTrackContainerName.empty()){
    Error("configure()", "One or more required configuration values are empty");
    return EL::StatusCode::FAILURE;
  }

  if(m_useCutFlow) {
    TFile *file = wk()->getOutputFile ("cutflow");
    m_trk_cutflowHist_1  = (TH1D*)file->Get("cutflow_trks_1");
  }

  return EL::StatusCode::SUCCESS;
}

typedef ElementLink<xAOD::TruthParticleContainer> TruthLink_t;
static SG::AuxElement::Accessor<TruthLink_t> LINKTOTRUTH("truthParticleLink");
const xAOD::TruthParticle* EoverPTreeAlgo :: getTruthPtr(const xAOD::TrackParticle* trackParticle) {
  const xAOD::TruthParticle *result = nullptr;
  if ( LINKTOTRUTH.isAvailable(*trackParticle) ) {
    const TruthLink_t link = trackParticle->auxdata<TruthLink_t>("truthParticleLink");
    if ( link.isValid() ) {
      result = *link;
    }
  }
  return result;
}


EL::StatusCode EoverPTreeAlgo :: fileExecute () { return EL::StatusCode::SUCCESS; }
EL::StatusCode EoverPTreeAlgo :: changeInput (bool /*firstFile*/) { return EL::StatusCode::SUCCESS; }

EL::StatusCode EoverPTreeAlgo :: initialize ()
{
  std::string a;
  for(std::stringstream sst(m_energyCalibCommaList); getline(sst, a, ','); )  // that's all ! 
     m_energyCalibList.push_back(a);

  for(std::stringstream sst(m_radiusCutCommaList); getline(sst, a, ','); )  // that's all ! 
     m_radiusCutList.push_back(a);

  Info("initialize()", "EoverPTreeAlgo");
  Info("initialize()", m_inTrackContainerName.c_str());
  Info("initialize()", m_detailStr.c_str());

  Info("initialize()", "doing m_event = wk()->xaodEvent();");
  m_event = wk()->xaodEvent();
  Info("initialize()", "doing m_store = wk()->xaodStore();");
  m_store = wk()->xaodStore();

  Info("initialize()", "Registering Output Tree");
  // setup the tree output
  ANA_MSG_DEBUG("Registering Output Tree");
  TFile* treeFile = wk()->getOutputFile ("tree");
  Info("initialize()", "making directory");
  treeFile->mkdir(m_name.c_str());
  Info("initialize()", "changing directory");
  treeFile->cd(m_name.c_str());

  ANA_MSG_DEBUG("Tree Regiestered");
  std::string treeName = m_name+"_tree";
  if (m_tree == nullptr)
	Info("initialize()", "Creating ttree");
    m_tree = new TTree(treeName.c_str(),treeName.c_str());
  if (m_tree ==  nullptr) {
    Error("execute()","Failed to instantiate output tree!");
    return EL::StatusCode::FAILURE;
  }

  ANA_MSG_DEBUG("Adding a tree with name " + treeName);
  Info("initialize()", "listing directory");
  //treeFile->ls(m_name.c_str());

  ANA_MSG_DEBUG("Setting the directory of the tree");
  Info("initialize()", "Getting directory of file");
  TDirectory *dir = treeFile->GetDirectory(m_name.c_str());
  Info("initialize()", "Setting directory of tree");
  if (dir) m_tree->SetDirectory(dir);
  else ANA_MSG_ERROR("The output directory doesn't exist!");
      
  ANA_MSG_DEBUG("Adding the tree to the output");
  Info("initialize()", "Adding the tree to the output");
  wk()->addOutput( m_tree );

  ANA_MSG_DEBUG("Registering Tree Branches");
  Info("initialize()", "Registering tree branches");
  //m_tree->Branch("eventNumber",   &m_eventNumber,   "EventNumber/l"); I don't think we need this variable
  m_tree->Branch("trkIndex",      &m_trkIndex);
  m_tree->Branch("trk_etaID", &trk_etaID);
  m_tree->Branch("trk_phiID", &trk_phiID);
  m_tree->Branch("trk_pt", &trk_pt);
  m_tree->Branch("trk_d0", &trk_d0);
  m_tree->Branch("trk_nTRT", &trk_nTRT);
  m_tree->Branch("trk_nSCT", &trk_nSCT);
  m_tree->Branch("trk_charge", &trk_charge);
  m_tree->Branch("trk_z0sintheta", &trk_z0sintheta);
  m_tree->Branch("trk_z0sintheta_primary", &trk_z0sintheta_primary);
  m_tree->Branch("trk_p", &trk_p);
  m_tree->Branch("trk_p_err", &trk_p_err);
  m_tree->Branch("trk_nearest_dR_EM", &trk_nearest_dR_EM);
  m_tree->Branch("trk_nearest_dR_HAD", &trk_nearest_dR_HAD);
  m_tree->Branch("trkWeight", &trkWeight);
  m_tree->Branch("trk_NPV_2", &trk_NPV_2);
  m_tree->Branch("trk_NPV_4", &trk_NPV_4);
  m_tree->Branch("trk_hasTruthParticle", &trk_hasTruthParticle);
  m_tree->Branch("trk_truthPdgId", &trk_truthPdgId);
  m_tree->Branch("trk_truthEnergy", &trk_truthEnergy);
  m_tree->Branch("trk_truthP", &trk_truthP);
  m_tree->Branch("trk_truthProb", &trk_truthProb);
  m_tree->Branch("trk_actualmu", &trk_actualmu);
  m_tree->Branch("trk_averagemu", &trk_averagemu);
  m_tree->Branch("trk_corrected_averagemu", &trk_corrected_averagemu);

  for (std::string l: EnergySumHelper::layer){
      m_tree->Branch(("trk_eta" + l).c_str(), &(m_trk_extrapolEta[l]));
      m_tree->Branch(("trk_phi" + l).c_str(), &(m_trk_extrapolPhi[l]));
  }

  //All energy deposits in EM-Calorimeter and HAD-Calorimeter
  Info("initialize()", "Starting loop for making branches");
  for (std::string energyCalib : m_energyCalibList){
      for (std::string radiusCut : m_radiusCutList){
          Info("initialize()", "Inside loop of making branches for clusters/cuts");
          ANA_MSG_INFO("Made ttree branches for energy of clusters at scale " + energyCalib + " and cut " + radiusCut);
          std::string key_EM = "trk_" + energyCalib + "_EM_" + radiusCut;
          m_energyVariablesForTree[key_EM] = 0.0;
          std::string key_HAD = "trk_" + energyCalib + "_HAD_" + radiusCut;
          m_energyVariablesForTree[key_HAD] = 0.0;
          m_tree->Branch(("trk_" + energyCalib + "_EM_" + radiusCut).c_str(), &(m_energyVariablesForTree[key_EM]));
          m_tree->Branch(("trk_" + energyCalib + "_HAD_" + radiusCut).c_str(), &(m_energyVariablesForTree[key_HAD]));
      }
  }

  //Count the number of clusters at different radius cuts
  for (std::string radiusCut : m_radiusCutList){
      std::string key_EM = "trk_ncluters_EM_" + radiusCut;
      m_energyVariablesForTree[key_EM] = 0.0;
      std::string key_HAD = "trk_ncluters_HAD_" + radiusCut;
      m_energyVariablesForTree[key_HAD] = 0.0;

      std::string key_EM_EMLike = "trk_ncluters_EM_EMLike_" + radiusCut;
      m_energyVariablesForTree[key_EM_EMLike] = 0.0;
      std::string key_EM_HADLike = "trk_ncluters_EM_HADLike_" + radiusCut;
      m_energyVariablesForTree[key_EM_HADLike] = 0.0;

      std::string key_HAD_EMLike = "trk_ncluters_HAD_EMLike_" + radiusCut;
      m_energyVariablesForTree[key_HAD_EMLike] = 0.0;
      std::string key_HAD_HADLike = "trk_ncluters_HAD_HADLike_" + radiusCut;
      m_energyVariablesForTree[key_HAD_HADLike] = 0.0;

      m_tree->Branch(("trk_nclusters_EM_" + radiusCut).c_str(), &(m_clusterVariablesForTree[key_EM]));
      m_tree->Branch(("trk_nclusters_HAD_" + radiusCut).c_str(), &(m_clusterVariablesForTree[key_HAD]));

      m_tree->Branch(("trk_nclusters_EM_emlike_" + radiusCut).c_str(), &(m_clusterVariablesForTree[key_EM_EMLike]));
      m_tree->Branch(("trk_nclusters_HAD_emlike_" + radiusCut).c_str(), &(m_clusterVariablesForTree[key_HAD_EMLike]));

      m_tree->Branch(("trk_nclusters_EM_hadlike_" + radiusCut).c_str(), &(m_clusterVariablesForTree[key_EM_HADLike]));
      m_tree->Branch(("trk_nclusters_HAD_hadlike_" + radiusCut).c_str(), &(m_clusterVariablesForTree[key_HAD_HADLike]));
  }

  ANA_MSG_DEBUG("Getting the cuflows");
  if(m_useCutFlow) {
    TFile *file = wk()->getOutputFile ("cutflow");
    // retrieve the object cutflow
    m_trk_cutflowHist_1  = (TH1D*)file->Get("cutflow_trks_1");
  }

  const xAOD::EventInfo* eventInfo(nullptr);
  ANA_CHECK( HelperFunctions::retrieve(eventInfo, m_eventInfoContainerName, m_event, m_store));
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode EoverPTreeAlgo :: execute ()
{
  // retrieve event
  const xAOD::EventInfo* eventInfo(nullptr);
  ANA_CHECK( HelperFunctions::retrieve(eventInfo, m_eventInfoContainerName, m_event, m_store ));
  //  1.) the PU weight ("PileupWeight")
  //  2.) the corrected mu ("corrected_averageInteractionsPerCrossing")
  float eventWeight(1.);
  if( eventInfo->isAvailable< float >( "mcEventWeight" ) ) {
    eventWeight = eventInfo->auxdecor< float >( "mcEventWeight" );
    static SG::AuxElement::ConstAccessor< float > weight_pileup ("PileupWeight");
    if (weight_pileup.isAvailable(*eventInfo)){
        float pileupWeight(0.);
        pileupWeight = weight_pileup(*eventInfo);
        eventWeight *= pileupWeight;
    }
  }
  else {ANA_MSG_ERROR("No Event Weight Available");}

  m_eventNumber = -1;
  m_trkIndex = -1;

  const xAOD::VertexContainer *vtxs(nullptr);
  ANA_CHECK( HelperFunctions::retrieve(vtxs, "PrimaryVertices", m_event, m_store) );
  const xAOD::Vertex *pvx = HelperFunctions::getPrimaryVertex(vtxs, msg());

  const xAOD::TrackParticleContainer* trks(nullptr);
  ANA_CHECK( HelperFunctions::retrieve(trks, m_inTrackContainerName, m_event, m_store) );

  //"dRToNearestTrackInEM"
  SG::AuxElement::ConstAccessor< float > acc_dRToNearestTrackInEM("dRToNearestTrackInEM");
  SG::AuxElement::ConstAccessor< float > acc_dRToNearestTrackInHAD("dRToNearestTrackInHAD");

  // loop over all tracks only once
  for(auto trk: *trks){
    ANA_MSG_DEBUG("Beginning track loop");

    if (trk->auxdata<int>("CALO_extrapolation") == 0) continue;
    ANA_MSG_DEBUG("Track has CALO extrapolation");
    if (m_useCutFlow) m_trk_cutflowHist_1->Fill("Has calo extrapolation", 1.0);

    if (acc_dRToNearestTrackInEM.isAvailable(*trk)) trk_nearest_dR_EM = acc_dRToNearestTrackInEM(*trk);
    else {ANA_MSG_WARNING("Coulnd't find the decorator for the dR to the nearest track"); trk_nearest_dR_EM = -1.0;}

    if (acc_dRToNearestTrackInHAD.isAvailable(*trk)) trk_nearest_dR_HAD= acc_dRToNearestTrackInHAD(*trk);
    else {ANA_MSG_WARNING("Coulnd't find the decorator for the dR to the nearest track"); trk_nearest_dR_HAD = -1.0;}

    //get the track momentum from q/p
    trk_p = 0.0;
    if (fabs(trk->qOverP())>0.) trk_p = (1./fabs(trk->qOverP()))/1e3; 
    trk_charge = (trk->qOverP()>0.) ? 1 : -1;

    //This is the track pT
    trk_pt = trk->pt()/1e3;
    xAOD::ParametersCovMatrix_t cov;
    cov = trk->definingParametersCovMatrix();
    float trk_qoverp_err = 0.0;
    if (cov(4,4) > 0.0) trk_qoverp_err = TMath::Sqrt(cov(4,4)) * 1e3; // multiply by 1000 to convert to 1/GeV
    trk_p_err = 0.0;
    if (trk_qoverp_err > 0) trk_p_err = trk_p * trk_p * trk_qoverp_err; //use error propagation

    //Get the value of the eta and phi co-ordinates when extrapolated to the EMB/EME
    for (std::string l: EnergySumHelper::layer){
        m_trk_extrapolEta[l] = trk->auxdata<float>("CALO_trkEta_"+l);
        m_trk_extrapolPhi[l] = trk->auxdata<float>("CALO_trkPhi_"+l);
    }

    trk_d0 = trk->d0(); //This is the correct d0
    trk_z0sintheta = trk->z0() * TMath::Sin(trk->theta()); //This isn't the correct impact parameter w.r.t the primary vertex


    float dz;
    float trk_z0=trk->z0();
    float beamspot_z0=trk->vz();
    float theta=trk->theta();
    if (pvx != nullptr){ dz=fabs((trk_z0-(pvx->z())+beamspot_z0)*sin(theta));} // calculate dz
    else {dz = -999.0;}
    trk_z0sintheta_primary = dz;


    // coordinates of the track in the ID
    trk_etaID = trk->eta();
    trk_phiID = trk->phi();

    trkWeight = eventWeight;//The track weight is just the event weight

    //Sum all energy deposits in the EM calorimeter and the HAD caloriemter with different radius cuts
    for (std::string energyCalib : m_energyCalibList){
        for (std::string radiusCut : m_radiusCutList){
            std::string key_EM = "trk_" + energyCalib + "_EM_" + radiusCut;
            m_energyVariablesForTree[key_EM] = 0.0;
            std::string key_HAD = "trk_" + energyCalib + "_HAD_" + radiusCut;
            m_energyVariablesForTree[key_HAD] = 0.0;
            std::map<std::string, float> energySum = EnergySumHelper::getEnergySumInCalorimeterRegions(trk,energyCalib,radiusCut,false);
            m_energyVariablesForTree[key_HAD] = energySum["HAD"];
            m_energyVariablesForTree[key_EM] = energySum["EM"];
        }
    }

    //calorimeter region (EM or HAD) -> radius cut name (100, 200, etc) -> # number of clusters
    std::map<std::string, std::map< std::string, std::map<std::string, int> > > numberOfClusterMap;
    numberOfClusterMap = EnergySumHelper::getNumberOfClustersInCaloriemterRegions(trk, EnergySumHelper::map_cutName_to_cutValue);

    ///////////////////////////////////////Information about the # of clusters ////////////////////////////////////////////////////////////////
    //Count the number of clusters at different radius cuts
    for (std::string radiusCut : m_radiusCutList){
        std::string key_EM = "trk_ncluters_EM_" + radiusCut;
        std::string key_HAD = "trk_ncluters_HAD_" + radiusCut;

        std::string key_EM_EMLike = "trk_ncluters_EM_EMLike_" + radiusCut;
        std::string key_EM_HADLike = "trk_ncluters_EM_HADLike_" + radiusCut;

        std::string key_HAD_EMLike = "trk_ncluters_HAD_EMLike_" + radiusCut;
        std::string key_HAD_HADLike = "trk_ncluters_HAD_HADLike_" + radiusCut;

        m_clusterVariablesForTree[key_EM] = numberOfClusterMap["EM"][radiusCut]["NClusters"];
        m_clusterVariablesForTree[key_HAD] = numberOfClusterMap["HAD"][radiusCut]["NClusters"];
        m_clusterVariablesForTree[key_EM_EMLike] = numberOfClusterMap["EM"][radiusCut]["NClusters_EMLike"];
        m_clusterVariablesForTree[key_EM_HADLike] = numberOfClusterMap["EM"][radiusCut]["NClusters_HADLike"];
        m_clusterVariablesForTree[key_HAD_EMLike] = numberOfClusterMap["HAD"][radiusCut]["NClusters_EMLike"];
        m_clusterVariablesForTree[key_HAD_HADLike] = numberOfClusterMap["HAD"][radiusCut]["NClusters_HADLike"];
    }

    ///////////////////////////////////////TRUTH INFORMATION ////////////////////////////////////////////////////////////////
    //reset the truth information
    trk_truthPdgId = 0;
    trk_truthEnergy = -999.0;
    trk_truthP = -999.0;
    trk_truthProb = -1.0;
    trk_hasTruthParticle = 0;

    //Get the truth match probability of the track
    static SG::AuxElement::ConstAccessor< float > tmpAcc("truthMatchProbability"); //What is the name of the truth match probabily cut variable?
    if (tmpAcc.isAvailable(*trk)){
        const xAOD::TruthParticle* truthPart = getTruthPtr(trk);
        trk_truthProb = tmpAcc(*trk);
        //check if the track passes the truth match probaility cut
        if (!truthPart) {trk_hasTruthParticle = 0;} //there was a truth match, but the link is broken (or truth particle has energy < 100MeV!)
        else { 
            trk_hasTruthParticle = 1;
            trk_truthPdgId = truthPart->pdgId();
            trk_truthEnergy = truthPart->e()/1000.0;
            truthPartVec.SetPtEtaPhiE(truthPart->pt()/1000.0, truthPart->eta(), truthPart->phi(), truthPart->e()/1000.0);
            trk_truthP = truthPartVec.P()/1000.0;
        }
    }

    ///////////////////////////////////////TRT HITS ////////////////////////////////////////////////////////////////

    // set ttree variables
    m_eventNumber = eventInfo->eventNumber();
    if (!trk->summaryValue(trk_nTRT, xAOD::numberOfTRTHits))ANA_MSG_ERROR("TRT hits not filled");
    ANA_MSG_DEBUG(TString("The number of TRT hits was " + std::to_string (trk_nTRT)));

    if (!trk->summaryValue(trk_nSCT, xAOD::numberOfSCTHits))ANA_MSG_ERROR("SCT hits not filled");
    ANA_MSG_DEBUG(TString("The number of SCT hits was " + std::to_string (trk_nSCT)));

    ///////////////////////////////////////EVENT VARIABLES ////////////////////////////////////////////////////////////////

    trk_NPV_2 = HelperFunctions::countPrimaryVertices(vtxs, 2);
    trk_NPV_4 = HelperFunctions::countPrimaryVertices(vtxs, 4);
    trk_averagemu = -1;
    trk_actualmu = -1;
    trk_corrected_averagemu = -1;

    // get pileup
    if( eventInfo->isAvailable< float >( "actualInteractionsPerCrossing" ) ) {
      trk_actualmu = eventInfo->actualInteractionsPerCrossing();
    }
    if( eventInfo->isAvailable< float >( "corrected_averageInteractionsPerCrossing" ) && !eventInfo->eventType( xAOD::EventInfo::IS_SIMULATION )) 
      trk_corrected_averagemu = eventInfo->auxdata< float >( "corrected_averageInteractionsPerCrossing" );
    else if( eventInfo->isAvailable< float >( "averageInteractionsPerCrossing" ) )
      trk_averagemu = eventInfo->averageInteractionsPerCrossing();

    m_trkIndex += 1;
    ANA_MSG_DEBUG("Filling Tree");
    m_tree->Fill();
  } // END looping trk

  return EL::StatusCode::SUCCESS;
}

EL::StatusCode EoverPTreeAlgo :: postExecute () { return EL::StatusCode::SUCCESS; }

EL::StatusCode EoverPTreeAlgo :: finalize () { 

  return EL::StatusCode::SUCCESS; 
}

EL::StatusCode EoverPTreeAlgo :: histFinalize ()
{
  ANA_CHECK(xAH::Algorithm::algFinalize());
  return EL::StatusCode::SUCCESS;
}

