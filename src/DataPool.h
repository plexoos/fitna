#include <vector>

#include "Cluster.h"


class DataPool
{
public:

   /** Creates a temp copy of the data then recursively builds clusters. */
   std::vector<Cluster> find_clusters();
   bool has_unclustered_data() const { return false; }

private:

  Cluster make_seed_cluster() const;
  int grow_cluster(Cluster& cluster);
};
