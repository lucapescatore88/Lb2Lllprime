// $Id: FTClusterCreator.h 189046 2015-05-27 15:32:50Z cogneras $
#ifndef FTCLUSTERCREATOR_H 
#define FTCLUSTERCREATOR_H 1

// Include files
// from Gaudi
#include "GaudiAlg/GaudiHistoAlg.h"

// LHCbKernel
#include "Kernel/FTChannelID.h"

#include "Event/MCFTDigit.h"

//using namespace LHCb;

/** @class FTClusterCreator FTClusterCreator.h
 *  
 *
 *  @author Eric Cogneras
 *  @date   2012-04-06
 */
class FTClusterCreator : public GaudiHistoAlg {
public: 
  /// Standard constructor
  FTClusterCreator( const std::string& name, ISvcLocator* pSvcLocator );

  virtual ~FTClusterCreator( ); ///< Destructor

  virtual StatusCode initialize();    ///< Algorithm initialization
  virtual StatusCode execute   ();    ///< Algorithm execution
  virtual StatusCode finalize  ();    ///< Algorithm finalization

private:
  // Location
  std::string m_inputLocation;       ///< MCFTDigit input Container
  std::string m_outputLocation;      ///< FTCluster output Container

  unsigned int m_clusterMinWidth;   ///< Minimal Width for clusters
  unsigned int m_clusterMaxWidth;   ///< Maximal Width for clusters
  int m_adcThreshold;               ///< Minimal ADC value for cluster addition
  int m_clusterMinCharge;           ///< Minimal total ADC for clusters
  int m_clusterMinADCPeak;          ///< Minimal ADC for cluster peaks

  int m_fixClusterWidth;
  int m_fixClusterCharge;
  double m_fixFracPos;

  int m_removeITRegion;
  bool m_makeSpillPlots;
  float m_ITScale;

  //=== Sum for some average information
  int   m_nCluster;
  float m_sumCharge;
  int m_nberOfLostHitFromMap;
  int m_nberOfKeptHitFromMap;

};
#endif // FTCLUSTERCREATOR_H


