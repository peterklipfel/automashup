#!/usr/bin/env python

# eg:
#   ./pingPong.py audio/illgates_sweatshop.mp3 audio/jayz_youngforever.mp3 test2.mp3
import sys
import time
import random
import echonest.remix.audio as audio

from pyechonest import config
config.CALL_TIMEOUT=30

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

audio_file1 = audio.LocalAudioFile(sys.argv[1])
audio_file2 = audio.LocalAudioFile(sys.argv[2])
#audio_file1 = audio.LocalAudioFile('../songs/02-far_too_loud-megaloud-alki.mp3')#sys.argv[1])
#audio_file2 = audio.LocalAudioFile('../songs/MordFustang-LickTheRainbow.mp3')#sys.argv[2])

# Analyse songs on soundcloud to segment.
beats1 = audio_file1.analysis.beats
beats2 = audio_file2.analysis.beats

# Swap so file 1 is the longest
if len(beats1) < len(beats2):
    beats1, beats2 = swap( beats1, beats2 )
    audio_file1, audio_file2 = swap( audio_file1, audio_file2 )

assert len(beats1) >= len(beats2)

# Construct alternating segments result. Don't use last beat in case same len
nb = len(beats2)

# make a list of audio segments
alist = []
i=0 # beat index

interesting_segments = []
for d in audio_file1.analysis.segments:
  if d.duration > 0.5:
    if len(audio_file1[ d ]) > 0 and len(audio_file2[ beats2[i]]) > 0:
      interesting_segments.append( audio_file1[ d ])

while i < nb:
    print 'Beat pair %d of %d' % (i,nb)
    # add next beat from song 1
    # alist.append( audio_file2[ beats2[i] ] )
    # add next beat from song 2
    # if audio_file2.analysis.bars[i].confidence > 0.15:
    #   minlen = min(audio_file1.data.shape[0], audio_file2.data.shape[0])
    #   # audiofile = audio_file2
    #   # audiofile.data = audiofile.data[:minlen,:] + audio_file1.data[:minlen,:]

    if random.randrange(100) < 70:
      alist.append( audio.mix(audio_file2[ beats2[i] ], interesting_segments[random.randrange(len(interesting_segments))] ) )
    else:
      alist.append(audio_file2[beats2[i]])

    # else:
      # alist.append( audio_file1[ beats1[i] ] )
    i += 1

# construct output waveform from these audiodata objects.
afout = audio.assemble( alist )

# Write output file
afout.encode( sys.argv[3] )

print "pingPong execution time: ", time.time() - start_time, " seconds"
