//from here
#include "Cluster.h"

//from std
#include <iostream>
#include <vector>

//void FindClustersInEventMax(std::vector<Cluster*>& Clusters
//                            const std::vector<Channel>& dataVector,
//                            const float neighbour_threshold,
//                            const float seed_threshold,
//                            const float sum_threshold,
//                            )
//{
//
//  Cluster* currentCluster = nullptr;
//
//  for(std::vector<Channel>::const_iterator chan = dataVector.begin(); chan != dataVector.end(); ++chan){
//    if( chan->AdcValue > neighbour_threshold){ //look for channels exceeding cluster threshold
//      if(!currentCluster){
//        currentCluster = new Cluster();
//        currentCluster->AddChannel(chan->ChannelNumber, chan->AdcValue);
//      }
//      else{
//        currentCluster->AddChannel(chan->ChannelNumber, chan->AdcValue);
//      }
//    }
//    if( chan->AdcValue <= neighbour_threshold && currentCluster){
//      if(currentCluster->GetMaximumAdcValue() > seed_threshold && currentCluster->GetSumOfAdcValues() > sum_threshold) Clusters.push_back(currentCluster);
//      currentCluster = nullptr;
//    }
//  }
//}


void FindClustersInEvent(std::vector<Cluster*>& clusterVector,
        const std::vector<Channel>& event,
        const double neighbourThreshold,
        const double seedThreshold,
        const double sumThreshold,
        const unsigned int maxClusterSize,
        bool debug){

    if(debug) std::cout << "Event has " << event.size() << " channels" << std::endl;

    bool possibleMultipleClusters = false;
    Cluster* currentCluster = nullptr;

    for(std::vector<Channel>::const_iterator chan = event.begin(); chan != event.end(); ++chan)
    {
        if(debug) std::cout << "Search at channel " << chan->ChannelNumber << " with adc value " << chan->AdcValue << std::endl;

        std::vector<Channel>::const_iterator storeCurrentChannel;
        if (chan->AdcValue > seedThreshold && currentCluster == nullptr) // Create a new cluster if there is none at the moment
        {
            currentCluster = new Cluster();
            possibleMultipleClusters = false;
            currentCluster->AddChannel(chan->Uplink, chan->ChannelNumber, chan->AdcValue);
            storeCurrentChannel = chan;

            if(chan != event.begin()) // Add all neighbours in backward direction
            {
                do{
                    --chan;
                    if(debug) std::cout << "Going down to channel " << chan->ChannelNumber << " with adc value " << chan->AdcValue << std::endl;
                    if(chan->AdcValue > neighbourThreshold) currentCluster->AddChannel(chan->Uplink, chan->ChannelNumber, chan->AdcValue);
                }while(chan->AdcValue > neighbourThreshold && chan != event.begin());
            }

            chan = storeCurrentChannel;
            if(chan != event.end()-1) // Add all neighbours in forward direction
            { 
                do{
                    ++chan;
                    if(debug) std::cout << "Going up to channel " << chan->ChannelNumber << " with adc value " << chan->AdcValue << std::endl;
                    if(chan->AdcValue > neighbourThreshold) currentCluster->AddChannel(chan->Uplink, chan->ChannelNumber, chan->AdcValue);
                    if(chan->AdcValue > seedThreshold && (chan-1)->AdcValue < seedThreshold) possibleMultipleClusters = true;
                }while(chan->AdcValue > neighbourThreshold && chan != event.end()-1);
            }
        }
        
        if(currentCluster == nullptr) continue;
        if(currentCluster->GetSumOfAdcValues() > sumThreshold)
        {
            if(debug) std::cout << "Storing cluster" << std::endl;
            
            // If cluster size is greater than max cluster size
            if(currentCluster->GetClusterSize() >= 2*maxClusterSize && possibleMultipleClusters){// try to split the clusters
                std::cout << "Cluster splitting needed!" << std::endl;
            }
            //      if(currentCluster->GetClusterSize() > maxClusterSize){//just reduce the cluster
            //        currentCluster->Resize(maxClusterSize);
            //       }
            
            clusterVector.push_back(currentCluster); //Store the cluster
        }

        currentCluster = nullptr; //Reset the pointer
    }
}




void FindClustersInEventBoole(std::vector<Cluster*>& clusterVector,
        const std::vector<Channel>& event,
        const double neighbourThreshold,
        const double seedThreshold,
        const double sumThreshold,
        const unsigned int maxClusterSize,
        bool debug)
{
    std::vector<Channel>::const_iterator lastStopDigitIter = event.begin(); // End digit of last cluster, to prevent overlap

    // Since Digit Container is sorted wrt channelID, clusters are defined searching for bumps of ADC Count
    std::vector<Channel>::const_iterator seedDigitIter = event.begin();

    while(seedDigitIter != event.end())
    {    
        // Loop over digits
        
        Channel seedDigit = *seedDigitIter; // The seed of the cluster

        if(seedDigit.AdcValue >= seedThreshold)
        {
            // ADC above seed : start clusterin
            //  debug() << " ---> START NEW CLUSTER WITH SEED @ " << seedDigit->ChannelNumber << endmsg;

            std::vector<Channel>::const_iterator startDigitIter = seedDigitIter; // begin channel of cluster
            std::vector<Channel>::const_iterator stopDigitIter  = seedDigitIter; // end   channel of cluster

            // vector of MCHits that contributed to the cluster
            //  std::vector<const LHCb::MCHit*> clusterHitDistribution;

            // total energy in the cluster from MC
            //      double totalEnergyFromMC = 0;

            // map of contributing MCParticles (MCHits) with their relative energy deposit
            //  std::map< const LHCb::MCParticle*, double> mcContributionMap;
            //  std::map< const LHCb::MCHit*, double> mcHitContributionMap;


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
                //  redefining the seed as we go (pulling our left-side 'tail' with us).
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
                if(debug) std::cout << "Cluster size exceeded threshold" << endmsg;
                if((*stopDigitIter).AdcValue > (*startDigitIter).AdcValue) startDigitIter++;
                else stopDigitIter--;
            }


            lastStopDigitIter = stopDigitIter; // Update the 'previous cluster last channel'


            Cluster* currentCluster = new Cluster();
            for(std::vector<Channel>::const_iterator iterDigit = startDigitIter; iterDigit <(stopDigitIter+1); ++iterDigit) {
                currentCluster->AddChannel(iterDigit->Uplink, iterDigit->ChannelNumber, iterDigit->AdcValue);
            }
            
            // Before Cluster is recorded, check that total ADC > threshold and size > minSize

            if( ( currentCluster->GetSumOfAdcValues() >= sumThreshold) && ((stopDigitIter-startDigitIter+1) >= 1) )
            {

                // Define new cluster
                //  FTCluster::FTCluster( LHCb::FTChannelID &id, double fraction, int size, int charge )

                clusterVector.push_back(currentCluster);


            } // End of Cluster satisfies charge / size requirements
            else delete currentCluster;

            // Set the loop iterator to the end digit, to continue looking for next cluster without overlap.
            // Will get +1 at end of loop.

            seedDigitIter = stopDigitIter;

        } // END of clustering ( if(seedDigit->adcCount() > m_adcThreshold) )

        // Prepare for next cluster
        ++seedDigitIter;

    } // END of loop over Digits
}




