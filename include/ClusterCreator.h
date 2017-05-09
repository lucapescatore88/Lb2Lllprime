#ifndef CLUSTERCREATOR_H
#define CLUSTERCREATOR_H

//from std
#include <vector>

//from here
#include "Cluster.h"

typedef std::vector<Channel> Event;

class ClusterCreator{

    private:
        std::vector<Cluster*> clusters;

    public:
        ClusterCreator(){};
        ~ClusterCreator();

        std::vector<Cluster*> FindClustersInEventBoole(const Event& event,
            double neighbourThreshold, double seedThreshold, double sumThreshold,
            int maxClusterSize, bool debug, bool pacific);

        std::vector<Cluster*>FindClustersInEventBoole(
                const Event& event, std::vector<float> thresholds, 
                int maxClusterSize, bool debug, bool pacific);

        std::size_t getNumberOfClusters() const { return clusters.size(); }
        const std::vector<Cluster*> &getClusters() const { return clusters; }

};

#endif
