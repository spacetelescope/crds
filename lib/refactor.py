"""This module defines functions for modifying rmaps in various ways,  generally
the transformations required to automate rmap maintenance on the CRDS website.
"""
import re
import cStringIO

KEY_RE = r"(\s*')(.*)('\s*:\s*')(.*)('\s*,.*)"

def replace_header_value(filename, key, new_value):
    # print "refactoring", repr(filename), ":", key, "=", repr(new_value)
    newfile = cStringIO.StringIO()
    openfile = open(filename)
    for line in openfile:
        m = re.match(KEY_RE, line)
        if m and m.group(2) == key:
            line = re.sub(KEY_RE, r"\1\2\3%s\5" % new_value, line)
        newfile.write(line)
    openfile.close()
    newfile.seek(0)
    open(filename, "w+").write(newfile.read())
    
