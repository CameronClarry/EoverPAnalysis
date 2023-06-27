// E/p analysis for run 2
// Lukas Adamek (lukas.adamek@cern.ch)

#include <EventLoop/Job.h>
#include <EventLoop/StatusCode.h>
#include <EventLoop/Worker.h>
#include <EventLoop/OutputStream.h>
#include "xAODEventInfo/EventInfo.h"
#include "xAODAnaHelpers/HelperFunctions.h"
#include "EoverPAnalysis/TrackSorter.h"
//#include "AsgTools/MessageCheck.h"
#include "TMath.h"
#include "AthLinks/ElementLink.h"
#include "AthContainers/AuxElement.h"

// this is needed to distribute the algorithm to the workers
ClassImp(TrackSorter)

  TrackSorter :: TrackSorter (std::string className) :
    Algorithm(className)
    // cutflows
{
  m_inTrackContainerName    = "";
  m_sortedTrackContainerName = "";
}

EL::StatusCode TrackSorter :: setupJob (EL::Job& job)
{
  job.useXAOD();
  xAOD::Init("TrackSorter").ignore();
  ANA_CHECK(xAH::Algorithm::algInitialize());
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackSorter :: histInitialize ()
{

  if( m_inTrackContainerName.empty()){
    Error("configure()", "One or more required configuration values are empty");
    return EL::StatusCode::FAILURE;
  }
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackSorter :: fileExecute () { return EL::StatusCode::SUCCESS; }
EL::StatusCode TrackSorter :: changeInput (bool /*firstFile*/) { return EL::StatusCode::SUCCESS; }

EL::StatusCode TrackSorter :: initialize ()
{
  m_event = wk()->xaodEvent();
  m_store = wk()->xaodStore();
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackSorter :: execute ()
{
  const xAOD::TrackParticleContainer* trks(nullptr);
  ANA_CHECK( HelperFunctions::retrieve(trks, m_inTrackContainerName, m_event, m_store) );

  ConstDataVector<xAOD::TrackParticleContainer>* sortedTracks(nullptr);
  sortedTracks = new ConstDataVector<xAOD::TrackParticleContainer>(SG::VIEW_ELEMENTS);
  for (auto trk1: *trks){
     sortedTracks->push_back(trk1);
  }

  if (m_sort == "Pt") std::sort( sortedTracks->begin(), sortedTracks->end(), sort_pt );
  if (m_sort == "P") std::sort( sortedTracks->begin(), sortedTracks->end(), sort_p);

  m_store->record( sortedTracks, m_sortedTrackContainerName);

  return EL::StatusCode::SUCCESS;
}

bool TrackSorter::sort_p(const xAOD::TrackParticle_v1* A, const xAOD::TrackParticle_v1* B){
    float A_p = 1.0;
    float B_p = 1.0;
    if (fabs(A->qOverP())>0.) A_p = (1./fabs(A->qOverP()))/1e3; 
    else return -1;
    if (fabs(B->qOverP())>0.) B_p = (1./fabs(B->qOverP()))/1e3; 
    else return -1;
    return A_p > B_p;
}

bool TrackSorter::sort_pt(const xAOD::TrackParticle_v1* A, const xAOD::TrackParticle_v1* B){
    return A->pt() > B->pt();
}

EL::StatusCode TrackSorter :: postExecute () { return EL::StatusCode::SUCCESS; }

EL::StatusCode TrackSorter :: finalize () { 

  return EL::StatusCode::SUCCESS; 
}

EL::StatusCode TrackSorter :: histFinalize ()
{
  ANA_CHECK(xAH::Algorithm::algFinalize());
  return EL::StatusCode::SUCCESS;
}

