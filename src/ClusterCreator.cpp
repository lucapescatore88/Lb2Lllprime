#include "ClusterCreator.h"
#include "Cluster.h"

#include <iostream>
#include <vector>

ClusterCreator::~ClusterCreator()
{
    for(auto& clPtr : clusters)
    {
        delete clPtr;
    }
}

std::vector<Cluster*> ClusterCreator::FindClustersInEventBoole(const Event& event,
        std::vector<float> thresholds, int maxClusterSize,
        bool debug, bool pacific)
{

    if (thresholds.size()<3) 
    {
        //std::cout << "Using default thresholds" << std::endl;
        thresholds.clear();
        thresholds.push_back(1.5);
        thresholds.push_back(2.5);
        thresholds.push_back(4.5);
    }
    return FindClustersInEventBoole(event, 
            thresholds[0], thresholds[1], thresholds[2], 
            maxClusterSize, debug, pacific);
}

std::vector<Cluster*> ClusterCreator::FindClustersInEventBoole(const Event& event,
        double neighbourThreshold, double seedThreshold, double sumThreshold,
        int maxClusterSize, bool debug, bool pacific)
{
    if(pacific)
    {
        neighbourThreshold = 1;
        seedThreshold = 2;
        sumThreshold = 3;
    }
     
    std::vector<Cluster*> foundClusters;
    std::vector<Channel>::const_iterator lastStopDigitIter = event.begin(); // End digit of last cluster, to prevent overlap

    // Since Digit Container is sorted wrt channelID, clusters are defined searching for bumps of ADC Count
    std::vector<Channel>::const_iterator seedDigitIter = event.begin();

    while(seedDigitIter != event.end())
    {    
        // Loop over digits
        
        Channel seedDigit = *seedDigitIter; // The seed of the cluster

        //if (seedDigit.AdcValue > 0)
        //    std::cout << seedDigit.AdcValue << "   " <<  seedThreshold << std::endl;

        if(seedDigit.AdcValue >= seedThreshold)
        {
            // ADC above seed : start clusterin
            //  debug() << " ---> START NEW CLUSTER WITH SEED @ " << seedDigit->ChannelNumber << endmsg;

            std::vector<Channel>::const_iterator startDigitIter = seedDigitIter; // begin channel of cluster
            std::vector<Channel>::const_iterator stopDigitIter  = seedDigitIter; // end   channel of cluster

            // Test neighbours to define starting and ending channels of Cluster
            bool ContinueStartLoop = true;
            bool ContinueStopLoop  = true;

            while( ( (stopDigitIter-startDigitIter) < maxClusterSize ) && (ContinueStartLoop || ContinueStopLoop) ) 
            {
                // If cluster size =< maxClusterSize SiPM Channels

                // EXTEND TO THE RIGHT
                if(ContinueStopLoop && ((stopDigitIter+1) != event.end()) ) 
                {
                    // If the next digit exists: try to extend cluster to the 'right'

                    const Channel stopDigit = *(stopDigitIter+1); // The next digit

                    // Next digit should be in the same SiPM, the channel next door, and above neighbourThreshold
                    //std::cout << "neighbor " << stopDigit.AdcValue << "   " << neighbourThreshold << std::endl;

                    if((stopDigit.Uplink == seedDigit.Uplink)
                            && (stopDigit.ChannelNumber==((*stopDigitIter).ChannelNumber+1))
                            && (stopDigit.AdcValue >= neighbourThreshold)) 
                    {
                        // If ADC of next digit > the current seed digit, redefine the seed
                        if(stopDigit.AdcValue > seedDigit.AdcValue) 
                        {

                            seedDigitIter = stopDigitIter+1; // increment loop iterator
                            seedDigit = *seedDigitIter;      // increment seed channel
                            
                            // Set min and max channel of cluster to the new seed (i.e. reset the cluster finding)
                            startDigitIter = seedDigitIter;
                            stopDigitIter  = seedDigitIter;
                            ContinueStartLoop = true;

                        } 
                        else 
                        {
                            // If next digit ADC < current seed, but passes clustering requirements
                            stopDigitIter++; // extend cluster to the 'right'
                        }


                    } 
                    else 
                    {
                        // If next digit does not satisfy clustering requirements
                        ContinueStopLoop = false;
                    }

                } 
                else 
                {
                    // IF the next digit does not exist in the container (i.e. done with all clusterisation)
                    ContinueStopLoop = false;
                }


                // So far, we have extended the cluster to the 'right' as far as we could,
                // redefining the seed as we go (pulling our left-side 'tail' with us).
                // We now need to extend to the 'left' side.


                // EXTEND TO THE LEFT
                if(ContinueStartLoop && ((startDigitIter) != event.begin())) 
                {
                    // If the previous digit exists: try to extend cluster to the 'left'

                    const Channel startDigit = *(startDigitIter-1); // The 'previous' digit

                    // Previous digit should be in the same SiPM, the channel next door, above neighbourThreshold,
                    //  and also after the ending channel of the previous cluster
                    
                    if((startDigit.Uplink == seedDigit.Uplink)
                            &&(startDigit.ChannelNumber==((*startDigitIter).ChannelNumber-1))
                            && (startDigit.AdcValue >=neighbourThreshold)
                            &&((startDigitIter-1) > lastStopDigitIter)) {

                        // extend cluster to the 'left'
                        startDigitIter--;

                    } 
                    else 
                    {
                        // Previous channel does not satisfy clustering requirements
                        ContinueStartLoop = false;
                    }

                } 
                else 
                {
                    // There is no previous digit in the container
                    ContinueStartLoop = false;
                }

            }
            
            // MaxClusterSize has been reached, or iterator stop was set due to criteria
            // Cluster spans from startDigitIter to stopDigitIter

            // Check if cluster size < maxWidth. If not: choose highest ADC sum for cluster and shrink
            // This is possible because we check the size, then extend right, then extend left, and repeat.

            while((stopDigitIter - startDigitIter) >= maxClusterSize) 
            {    
                if(debug) std::cout << "Cluster size exceeded threshold" << std::endl;
                if((*stopDigitIter).AdcValue > (*startDigitIter).AdcValue) startDigitIter++;
                else stopDigitIter--;
            }

            lastStopDigitIter = stopDigitIter; // Update the 'previous cluster last channel'

            Cluster* currentCluster = new Cluster();
            for(std::vector<Channel>::const_iterator iterDigit = startDigitIter; iterDigit <(stopDigitIter+1); ++iterDigit) {
                currentCluster->AddChannel(iterDigit->Uplink, iterDigit->ChannelNumber, iterDigit->AdcValue);
            }
            
            // Before Cluster is recorded, check that total ADC > threshold and size > minSize

            //std::cout << "sum " << currentCluster->GetSumOfAdcValues() << "   " << sumThreshold << std::endl;
            if( ( currentCluster->GetSumOfAdcValues() >= sumThreshold) && ((stopDigitIter-startDigitIter+1) >= 1) )
            {

                // Define new cluster
                //  FTCluster::FTCluster( LHCb::FTChannelID &id, double fraction, int size, int charge )

                clusters.push_back(currentCluster);
                foundClusters.push_back(currentCluster);
                //std::cout << "Saved" << std::endl;

            } // End of Cluster satisfies charge / size requirements
            else delete currentCluster;

            // Set the loop iterator to the end digit, to continue looking for next cluster without overlap.
            // Will get +1 at end of loop.

            seedDigitIter = stopDigitIter;

        } // END of clustering ( if(seedDigit->adcCount() > m_adcThreshold) )

        // Prepare for next cluster
        ++seedDigitIter;

    } // END of loop over Digits

    return foundClusters;
}




