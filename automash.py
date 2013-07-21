#!/usr/bin/env python
import sys
import pickle
import cluster
import numpy as np
import echonest.remix.audio as audio
from pyechonest import config
config.CALL_TIMEOUT=30
import threading
import os
import alsaaudio
import time

# This is the demo script.
# Feed it a pre-computed pickle file from analyseFeatures.py.  Make sure
# you run both in the same directory, because the pickle file contains
# (relative) filenames.

maxCacheSize = 15   # HM can we have in RAM at once
# This clock increments each time the cache is accessed
cacheTime = 0
# A dictionary from filename to CachedSong
songCache = {}

card = 'default'

# Open the device in playback mode.
out = alsaaudio.PCM(alsaaudio.PCM_PLAYBACK, card=card)

# Set attributes: Mono, 44100 Hz, 16 bit little endian frames
out.setchannels(2)
out.setrate(44100)
out.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# The period size controls the internal number of frames per period.
# The significance of this parameter is documented in the ALSA api.
out.setperiodsize(160)


class CachedSong:
    def __init__(self,fn):
        global cacheTime
        self.m_fn = fn
        self.m_birthTime = cacheTime
        print 'Song Cache: loading song %s...' % fn
        self.m_adata = audio.LocalAudioFile(fn)

class CacheSongThread(threading.Thread):
    def __init__(self,fn):
        self.m_fn = fn
        threading.Thread.__init__(self)
    def run (self):
        global songCache
        print '** Song fetch thread - begin **'
        newsong = CachedSong(self.m_fn)
        while len(songCache)>=maxCacheSize:
            # find oldest and remove
            ages = [cs.m_birthTime for cs in songCache.values()]
            minAge = np.min(ages)
            for k,v in songCache.iteritems():
                if v.m_birthTime == minAge:
                    # found it
                    del songCache[k]
                    break
        assert len(songCache) < maxCacheSize
        # can add our new one now
        songCache[self.m_fn] = newsong
        print '** Song fetch thread - end **'
        

def getSongFromCache( fn, loadBlocking=False ):
    # If the song is in the cache already - simple
    global cacheTime
    global songCache
    cacheTime += 1
    if fn in songCache:
        # simply return it
        return songCache[fn]
    else:
        if loadBlocking:
            # load this one, wait to finish, add and return it.
            assert len(songCache) < maxCacheSize
            newsong = CachedSong( fn )
            songCache[fn] = newsong
            return newsong
        else:
            # The song was not there so we return None.  But, start loading
            # the song in  a separate thread.
            # To stop a quick second call restarting a retrieve, store None
            # there fore now.
            songCache[fn] = None
            CacheSongThread(fn).start()
            return None
            

def playRegion( adata, rtype, rgnIdx ):
    # Get this region quantum
    q = cluster.getRegionsOfType( adata.analysis, rtype )[rgnIdx]
    # Don't know what to do right now.  Write to wav file and do a system call.
    aout = adata[ q ]
    aout.encode('/tmp/noplay.wav')
    os.system( 'aplay /tmp/noplay.wav' )

def playAudioData( adata ):
    filepath = "/tmp/noplay"+str(int(time.time()))+".wav"
    adata.encode(filepath)
    f = open(filepath)
    data = f.read(320)
    while data:
        out.write(data)
        data = f.read(320)
    # os.system( 'aplay /tmp/noplay.wav' )

def docheck( clsec, clSection, currSec ):
    assert clSection in range( clsec.nbClusters() ), 'clSection=%d out of range [0,%d)' % (clSection,clsec.nbClusters())
    assert currSec in range( clsec.nbRegions() ), 'currSec=%d out of range [0,%d)' % (currSec, clsec.nbRegions())


def addBarsToAudio( clInfo, sectionSongData, sectionParentQnt, indexBars ):
    # The strategy for bars logic is:
    #  + if it comes in empty, initialise it.
    #  + pick some number of bars (eg 2, or random small) to use as a pool
    #  + cycle through them including the first bar of of the next section.
    #    So you reset on the second bar of each section.
    #  + to reset, change clusters with some prob, and randomly pick bars from
    #    the cluster.

    # secAData is section audio data
    # for each bar in this section:
    unmixedBars = []
    print '\taddBarsToAudio: section has %d children:' % len(sectionParentQnt.children())
    for i, barDestQnt in enumerate(sectionParentQnt.children()):
        # first, potentially update our pool bars
        # add the bar after the selected one
        if indexBars == None or i==1:
            # move along.  list of cluster idx, bar idx's
            barSongs = [None,None,None,None]
            if indexBars == None:
                indexBars = [None,None,None,None,None]
            while None in barSongs:
                # advance the cluster
                newIndexBars = [clInfo['bars'].nextCluster( indexBars[0] ), None, None, None, None ]
                for j in range(1,len(indexBars)):
                    # for each pool...
                    if j==2 or j==4:
                        newIndexBars[j] = min(newIndexBars[j-1]+1,clInfo['bars'].nbRegions()-1) # continuity!
                    else:
                        newIndexBars[j] = clInfo['bars'].nextRegion(newIndexBars[0],\
                                                                        indexBars[j] )
                    # try loading the data
                    barSongs[j-1] = getSongFromCache( clInfo['bars'].getFilenameOfRegion(\
                            newIndexBars[j] ) )
            # update the var
            indexBars = newIndexBars
        # assertion: these bars cannot give no data
        # use this info to get the bars we want, alternate.
        npool = len(indexBars)-1
        poolIdx = i%npool
        fnSrc = clInfo['bars'].getFilenameOfRegion( indexBars[1+poolIdx] )
        barSong = getSongFromCache( fnSrc )
        assert barSong != None
        barSong = barSong.m_adata
        barSrcIdxIntoSong = clInfo['bars'].getSongRegionIdx( indexBars[1+poolIdx] )
        barSrcQnt = barSong.analysis.bars[ barSrcIdxIntoSong ]
        barSrcAData = barSong[ barSrcQnt ]
        #   mix the bar into the section
        unmixedBars.append( barSrcAData )
        print '\t\ti=',i,', indexBars=', indexBars
    # return the result
    return ( audio.assemble( unmixedBars ), indexBars )

# this loads a dict from rtype to clInfo
f = open(sys.argv[1],'rb')
clInfo = pickle.load(f)
f.close()
# makes code briefer
clsec = clInfo['sections']

# Some technical issues:
#  - can't fit all songs into RAM
#  - loading takes a bit of time
# Here's an easy heuristic solution that should sound alright:
#  - set up a cache with some max nb songs to load in ram
#  - replace LRU
#  - every time it tries to change and can't because file isn't there, start
#    loading it.

nsame = 2
nrep  = 1

print 'INITIALIZING...'
# The main tune is the 'sections' of the songs.  Randomly pick an initial
# cluster.

# current section cluster
clSection = clsec.nextCluster( None )
# current section, integer index into ALL regions of this type
currSec = clsec.nextRegion( clSection, None )
getSongFromCache( clsec.getFilenameOfRegion(currSec), True )

# This is the cluster/bar index for bars
indexBars = None

# keep doing this check every time these vars change, for consistency.
docheck( clsec, clSection, currSec )

# Don't play for this many iterations, to warm it up.
warmUpCounter = np.round(maxCacheSize/2)

while True:
    # single cluster loop:
    for i in range( nsame ):
        # single section loop
        for j in range( nrep ):
            print 'Playing cluster %d (of %d), section %d (of %d)' % \
                (clSection, clsec.nbClusters(), currSec, \
                      clsec.sizeOfCluster(clSection) )

            currFn = clsec.getFilenameOfRegion(currSec)
            csong = getSongFromCache(currFn)
            # must be in the cache
            assert csong != None
            if warmUpCounter > 0:
                warmUpCounter -= 1
                if warmUpCounter == 0:
                    print 'MASHING...'
            else:
                rgnIdx = clsec.getSongRegionIdx(currSec) # an int
                allSectionsForSong = cluster.getRegionsOfType( \
                    csong.m_adata.analysis, 'sections' ) # array of quanta
                (secAData, indexBars) = addBarsToAudio( \
                    clInfo, csong.m_adata, allSectionsForSong[rgnIdx], \
                        indexBars )
                #secAData = addBeatsToAudio( clInfo, csong.m_adata, \
                #                                allSectionsForSong[rgnIdx] )
                playAudioData( secAData )
        # todo: keep a history and don't go back too early?
        # todo: pick same key?

        # pick a new section in this cluster
        currSecCand = clsec.nextRegion( clSection, currSec )
        if getSongFromCache(clsec.getFilenameOfRegion(currSecCand)) != None:
            # The song is there, we can move to this region.  Otherwise
            # we've prompted it to load, but don't go there right now.
            currSec = currSecCand
            docheck( clsec, clSection, currSec )

    # pick a new cluster
    clSectionCand = clsec.nextCluster( clSection )
    currSecCand = clsec.nextRegion( clSectionCand, None )
    if getSongFromCache(clsec.getFilenameOfRegion(currSecCand)) != None:
        # The song is there, we can move to this cluster.  Otherwise
        # we've prompted it to load, but don't go there right now.
        clSection = clSectionCand
        currSec = currSecCand
        docheck( clsec, clSection, currSec )
