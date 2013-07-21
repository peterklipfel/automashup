#!/usr/bin/env python
import sys
import pickle
import cluster
import numpy as np

# This is the demo script.
# Feed it a pre-computed pickle file from analyseFeatures.py.  Make sure
# you run both in the same directory, because the pickle file contains
# (relative) filenames.

# this loads a dict from rtype to clinfo
f = open(sys.argv[1],'rb');
clinfo = pickle.load(f)
f.close()

# Some technical issues:
#  - can't fit all songs into RAM
#  - loading takes a bit of time
# Here's an easy heuristic solution that should sound alright:
#  - set up a cache with some max nb songs to load in ram
#  - replace LRU
#  - every time it tries to change and can't because file isn't there, start
#    loading it.

nsame = 5
nrep  = 3

# The main tune is the 'sections' of the songs.  Randomly pick an initial
# cluster.
clSection = 0  # current section cluster
# current section, integer index
currSec = np.nonzero(clinfo['sections'].m_clusterIds==0)[0][0] 

while True:
    # single cluster loop:
    for i in range( nsame ):
        # single section loop
        for j in range( nrep ):
            print 'Playing cluster %d (of %d), section %d (of %d)' % \
                (clSection, clinfo['sections'].nbClusters(), currSec, \
                      clinfo['sections'].sizeOfCluster(clSection) )

        # todo: keep a history and don't go back too early?

        # pick a new section in this cluster
        currSec = clinfo['sections'].nextRegion( clSection, currSec )
    # pick a new cluster
    clSection = clinfo['sections'].nextCluster( clSection )
