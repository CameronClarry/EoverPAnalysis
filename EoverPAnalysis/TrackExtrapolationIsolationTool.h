// E/p analysis for run 2
// Joakim Olsson (joakim.olsson@cern.ch)

#ifndef TrackExtrapolationIsolationTool_TrackExtrapolationIsolationTool_H
#define TrackExtrapolationIsolationTool_TrackExtrapolationIsolationTool_H

#include "TTree.h"
#include "TH1.h"
#include "xAODTracking/VertexContainer.h"
#include "xAODTracking/TrackParticleContainer.h"
#include "xAODTruth/TruthParticle.h"

// algorithm wrapper
#include "xAODAnaHelpers/Algorithm.h"

class TrackExtrapolationIsolationTool : public xAH::Algorithm
{
  // put your configuration variables here as public variables.
  // that way they can be set directly from CINT and python.
  public:
    std::string m_outputTrackContainer;
    std::string m_inputTrackContainer;

    // save output tree of key variables
    double m_trkIsoDRmax = .4;
    //double m_trkIsoPfrac = 0.; Maybe in the future we could use a p-dependent isolation cut

    // turn on cutflows
    bool m_useCutFlow = false; 

  private:

    // cutflow
    TH1D* m_trk_cutflowHist_1; //!

    // list of calo layers
    const std::vector<std::string> m_layer = {"EMB1", "EMB2", "EMB3", "EME1", "EME2", "EME3", "HEC0", "HEC1", "HEC2", "HEC3", "TileBar0", "TileBar1", "TileBar2", "TileGap1", "TileGap2", "TileGap3", "TileExt0", "TileExt1", "TileExt2"}; //! array of all the calo layers
    const std::vector<std::string> m_layer_lar = {"EMB1", "EMB2", "EMB3", "EME1", "EME2", "EME3", "HEC0", "HEC1", "HEC2", "HEC3"}; //! array of lar layers only
    const std::vector<std::string> m_layer_tile = {"TileBar0", "TileBar1", "TileBar2", "TileGap1", "TileGap2", "TileGap3", "TileExt0", "TileExt1", "TileExt2"}; //! array of tile layers only

    float trk1_etaEMB2;
    float trk1_phiEMB2;

    float trk1_etaEME2;
    float trk1_phiEME2;

    float trk1_etaTileBar2;
    float trk1_phiTileBar2;

    float trk1_etaTileExt1;
    float trk1_phiTileExt1;

    float trk1_etaHEC1;
    float trk1_phiHEC1;

    float trk1_nearest_dR_HAD;
    float trk1_nearest_dR_EM;
    float trk1_secondNearest_dR_HAD;
    float trk1_secondNearest_dR_EM;

    TTree *m_tree; //!
    TFile *file; //!
    // variables that don't get filled at submission time should be
    // protected from being send from the submission node to the worker
    // node (done by the //!)
    public:
    // Tree *myTree; //!
    // TH1 *myHist; //!

    // tree for saving some key variables



    // this is a standard constructor
    TrackExtrapolationIsolationTool (std::string className = "TrackExtrapolationIsolationTool");

    // these are the functions inherited from Algorithm
    virtual EL::StatusCode setupJob (EL::Job& job);
    virtual EL::StatusCode fileExecute ();
    virtual EL::StatusCode histInitialize ();
    virtual EL::StatusCode changeInput (bool firstFile);
    virtual EL::StatusCode initialize ();
    virtual EL::StatusCode execute ();
    virtual EL::StatusCode postExecute ();
    virtual EL::StatusCode finalize ();
    virtual EL::StatusCode histFinalize ();
    double deltaR (double trk_eta, double trk_phi, double trk2_eta, double trk2_phi);
    std::vector<double> str2vec(std::string str);
    /// @cond
    // this is needed to distribute the algorithm to the workers
    ClassDef(TrackExtrapolationIsolationTool, 1);
    /// @endcond
};

#endif
