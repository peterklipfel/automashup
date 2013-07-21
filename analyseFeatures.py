#!/usr/bin/env python
import sys
import pickle
import cluster

# Usage:
#
#    analyseFeatures.py <list of mp3 files>
#
# So you've run extractFeatures.py on your library and that pickled up all the
# echo nest analysis results.  This program does clustering and then stores the
# cluster centres and cluster id per section.  Also, transition probabilities
# between clusters based on distance.  This gets put out to a pickle file that 
# can be ingested by the automashup infinite looper.

# in the end we want to store: analysis data (beats etc), then a cluster info
# for each region type
clinfoAll = []

for rtype in cluster.regionTypes:
    # Construct the matrix of features on which we are going to cluster for each
    # of the region types.
    # Perform clustering
    print 'Analysing ',rtype
    clinfoAll.append( cluster.ClusterInfo( rtype, sys.argv[1:] ) )

# Pickle all those results
f = open( 'clusterInfo.pkl', 'wb')
pickle.dump( clinfoAll, f )
f.close()

