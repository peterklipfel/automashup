#!/usr/bin/env python
import sys
import time
import echonest.remix.audio as audio

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

# Analyse songs on soundcloud to segment.
beats1 = audio_file1.analysis.beats
beats2 = audio_file2.analysis.beats

# Construct alternating segments result.
beats1.reverse()

# Write output file
audio.getpieces(audio_file1, beats1).encode( sys.argv[3] )

print "pingPong execution time: ", time.time() - start_time, " seconds"
