import os.path
import re

def is_geis_header(name):
    name = os.path.basename(name)
    return bool(re.match(r"\w+\.r\dh", name))

def get_header(name):
    assert is_geis_header(name), \
           "File " + repr(name) + " is not a geis filename."
    header = {}
    for line in open(name):
        words = line.split()
        if len(words) < 3:
            continue
        if words[1] != "=":
            continue
        key = words[0]
        if key == "HISTORY":
            continue
        value = words[2]
        header[key] = value
    return header

