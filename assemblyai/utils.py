import os


def get_dir_files(dir):
    """Return a list of filepaths for all files found in a directory."""
    files = []
    for (dirpath, dirnames, filenames) in os.walk(dir):
        for f in filenames:
            f = os.path.join(dirpath, f)
            files.append(f)
    return files
