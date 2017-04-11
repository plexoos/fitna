#include "DataPool.h"


std::vector<Cluster> DataPool::find_clusters()
{
   std::vector<Cluster> clusters;

   while ( has_unclustered_data() )
   {
      // Create initial seed cluster
      Cluster cluster( make_seed_cluster() );

      grow_cluster(cluster);

      clusters.push_back(cluster);
   }

   return clusters;
}


/** Creates a cluster from a data point. */
Cluster DataPool::make_seed_cluster() const
{
   return Cluster();
}


int DataPool::grow_cluster(Cluster& cluster)
{
   grow_cluster(cluster);
}
