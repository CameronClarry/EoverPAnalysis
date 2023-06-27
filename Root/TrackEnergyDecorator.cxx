// E/p analysis for run 2
// Lukas Adamek (lukas.adamek@cern.ch)

#include <EventLoop/Job.h>
#include <EventLoop/StatusCode.h>
#include <EventLoop/Worker.h>
#include <EventLoop/OutputStream.h>
#include "xAODEventInfo/EventInfo.h"
#include "xAODAnaHelpers/HelperFunctions.h"
#include "EoverPAnalysis/TrackEnergyDecorator.h"
//#include "AsgTools/MessageCheck.h"
#include "TMath.h"
#include "AthLinks/ElementLink.h"
#include "AthContainers/AuxElement.h"

// this is needed to distribute the algorithm to the workers
ClassImp(TrackEnergyDecorator)

  TrackEnergyDecorator :: TrackEnergyDecorator (std::string className) :
    Algorithm(className)
    // cutflows
{
  m_inTrackContainerName    = "";
}

EL::StatusCode TrackEnergyDecorator :: setupJob (EL::Job& job)
{
  job.useXAOD();
  xAOD::Init("TrackEnergyDecorator").ignore();
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackEnergyDecorator :: histInitialize ()
{
  ANA_CHECK(xAH::Algorithm::algInitialize());
  if( m_inTrackContainerName.empty()){
    Error("configure()", "One or more required configuration values are empty");
    return EL::StatusCode::FAILURE;
  }
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackEnergyDecorator :: fileExecute () { return EL::StatusCode::SUCCESS; }
EL::StatusCode TrackEnergyDecorator :: changeInput (bool /*firstFile*/) { return EL::StatusCode::SUCCESS; }

EL::StatusCode TrackEnergyDecorator :: initialize ()
{
  std::string a;
  for(std::stringstream sst(m_energyCalibCommaList); getline(sst, a, ','); ) 
     m_energyCalibList.push_back(a);

  for(std::stringstream sst(m_radiusCutCommaList); getline(sst, a, ','); )
     m_radiusCutList.push_back(a);

  m_store = wk()->xaodStore();
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackEnergyDecorator :: execute ()
{
  const xAOD::TrackParticleContainer* trks(nullptr);
  ANA_CHECK( HelperFunctions::retrieve(trks, m_inTrackContainerName, m_event, m_store) );

  // loop over all tracks and create the new decorations
  for(auto trk: *trks){
    ANA_MSG_DEBUG("Beginning track loop");

    //create energy deposit decorations for different radii
    for (std::string radiusCut : m_radiusCutList){
        for (std::string calorimeterLayer : EnergySumHelper::layer){
            //create a name for the new decoration
            std::string decorName = "CALO_" + m_energySumName + "_" + calorimeterLayer + "_" + radiusCut;
            SG::AuxElement::Decorator< float > decor(decorName);
            float EnergySum = 0.0;
            for (std::string energyCalib : m_energyCalibList){
                //Sum the energy deposit for the track
                std::string toAccess = "CALO_" + energyCalib + "_" + calorimeterLayer + "_" + radiusCut;
                SG::AuxElement::ConstAccessor<float> accessor(toAccess);
                if (accessor.isAvailable(*trk)){
                    EnergySum += trk->auxdata<float>(toAccess);
                }
            }
            decor(*trk) = EnergySum;
        }
    }
  }
  return EL::StatusCode::SUCCESS;
}

EL::StatusCode TrackEnergyDecorator :: postExecute () { return EL::StatusCode::SUCCESS; }

EL::StatusCode TrackEnergyDecorator :: finalize () { 

  return EL::StatusCode::SUCCESS; 
}

EL::StatusCode TrackEnergyDecorator :: histFinalize ()
{
  ANA_CHECK(xAH::Algorithm::algFinalize());
  return EL::StatusCode::SUCCESS;
}

