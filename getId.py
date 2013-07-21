#!/usr/bin/env python

import sys
import echonest.remix.audio as audio

# getId.py <file.mp3>

audio_file = audio.LocalAudioFile(sys.argv[1])
print "Echo Nest processing ID = ", audio_file.analysis.identifier
