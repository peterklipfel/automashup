#!/usr/bin/env python
import sys
import time
import echonest.remix.audio as audio

def swap(a,b):
    return b,a

start_time = time.time()

# Usage:
#
#   pingPong.py <song1.mp3> <song2.mp3> <outfile.mp3>
#
assert len(sys.argv) == 4, "Incorrect usage.\n\tpingPong.py <song1.mp3> <song2.mp3> <outfile.mp3>"

# This test script takes two songs as input and creates one output song with
# alternating bars from the 2 songs.  Output written to mp3 file.

audio_file1 = audio.LocalAudioFile('../songs/02-far_too_loud-megaloud-alki.mp3')#sys.argv[1])
audio_file2 = audio.LocalAudioFile('../songs/MordFustang-LickTheRainbow.mp3')#sys.argv[2])

# Analyse songs on soundcloud to segment.
beats1 = audio_file1.analysis.beats
beats2 = audio_file2.analysis.beats

# Swap so file 1 is the longest
if len(beats1) < len(beats2):
    beats1, beats2 = swap( beats1, beats2 )
    audio_file1, audio_file2 = swap( audio_file1, audio_file2 )

assert len(beats1) >= len(beats2)

# Start output with first segment of beats1
#afout = audio_file1[ beats1[0] ]
#afout = audio.AudioData( shape=(audio_file1.data.shape[0]+audio_file2.data.shape[1],2), sampleRate=audio_file1.sampleRate, \
#                            numChannels=audio_file1.numChannels)

# Construct alternating segments result. Don't use last beat in case same len
nb = len(beats2)
# use this for quick result
#nb = 100

i = 1
# make a list of audio segments
alist = []
for b1,b2 in zip( beats1[:nb], beats2[:nb] ):
    print 'Beat pair %d of %d: %s, %s' % (i,nb, str(b1), str(b2))
    # add next beat from song 2
    alist.append( audio_file2[b2] )
    # add next beat from song 1
    alist.append( audio_file1[b1] )
    i += 1

# construct output waveform from these audiodata objects.
afout = audio.assemble( alist )

# Write output file
afout.encode( sys.argv[3] )

print "pingPong execution time: ", time.time() - start_time, " seconds"
