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
        words = [x.strip() for x in line.split("=")]
        if len(words) < 2:
            continue
        key = words[0]
        if key == "HISTORY":
            continue
        
        if not words[1]:
            header[key] = ''
        elif words[1][0] == "'":
            value = words[1].split("'")[1].strip()
        else:
            value = words[1].split("/")[0].strip()
        header[key] = value
    return header

