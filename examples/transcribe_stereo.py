"""
For stereo audio with two speakers on separate channels, you can leverage
enhanced accuracy and formatting by setting speak_count to 2.
"""

import assemblyai

aai = assemblyai.Client()

model = aai.transcribe('example.wav', speaker_count=2)
