"""
To receive transcript text without formatting or punctuation, set the option
format_text to False.
"""

import assemblyai

aai = assemblyai.Client()

model = aai.transcribe('example.wav', format_text=False)
