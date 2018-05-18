import assemblyai
import os


aai = assemblyai.Client()


def get_dir_files(dir):
    """Return a list of all files found in a directory."""
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        for f in filenames:
            f = os.path.join(dirpath, f)
            files.append(f)
    return files


files = get_dir_files('/home/chappy/Downloads/audio')

transcripts = []
for f in files:
    transcript = aai.transcribe(filename=f)
    transcripts.append(transcript)
