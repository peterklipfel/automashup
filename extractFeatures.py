#!/usr/bin/env python
import sys
import echonest.remix.audio as audio
from pyechonest import config
config.CALL_TIMEOUT=30

# Usage:
#
#    extractFeatures.py <songs> 
#
# Given a directory, use Echo Nest to analyse each song in it.  Get back a
# feature matrix for each of bars, beats, sections, segments and tatums:
#
#  tatums:   sub-beat (usually 1/2)
#  beats:    as in quavers
#  bars:     4 beats
#  sections: chorus, verse etc
#  segments: ?
#
# Make a file (in curr directory) for each region type, and stuff in as csv

def writeFeaturesToFile( fn, songId, file, Q ):
    fmtStr = ',%.6f'
    for i,q in enumerate(Q):
        # file name
        file.write( '"%s"' % (fn) )
        # file id
        file.write( ',%s' % songId )
        # quantum number
        file.write( ',%s' % i )
        # confidence - sometimes missing... for sections?
        if q.confidence != None:
            file.write( fmtStr % q.confidence )
        else:
            file.write( ',' )
        # duration
        file.write( fmtStr % q.duration )
        # loudness
        file.write( fmtStr % q.mean_loudness() )
        # pitch (chroma), 12-elem vector
        file.write( ''.join([ fmtStr%x for x in q.mean_pitches()]) )
        # timbre
        file.write( ''.join([ fmtStr%x for x in q.mean_timbre()]) )
        file.write( '\n' )

regionTypes = [ 'bars', 'beats', 'sections', 'tatums' ]

ofileBase = 'songftrs'

# open the out files
files = []
for t in regionTypes:
    ofn = '%s_%s.csv' % (ofileBase,t)
    files.append( open( ofn, 'w' ) )

# Now, visit each of the song files
for fn in sys.argv[1:]:
    print 'Processing file %s...' % fn
    au = audio.LocalAudioFile(fn)
    # Write out the analysis data from each of the region types, for all regions
    id = str(au.analysis.identifier)
    #print 'nb bars = ', len(au.analysis.bars)
    writeFeaturesToFile( fn, id, files[regionTypes.index('bars')], au.analysis.bars )
    writeFeaturesToFile( fn, id, files[regionTypes.index('beats')], au.analysis.beats )
    writeFeaturesToFile( fn, id, files[regionTypes.index('sections')],au.analysis.sections )
    writeFeaturesToFile( fn, id, files[regionTypes.index('tatums')], au.analysis.tatums )

# close dem files
for f in files:
    f.close()
