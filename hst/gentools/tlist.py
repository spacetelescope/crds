"""tlist is a fairly generic utility script which converts XML tables into a
list of dictionaries with one dictionary per table row.   The first row of each
table is assumed to be a header and its data or header items are scraped to become
the keys of the dictionaries.   Subsequent table rows are assumed to be data and
become the values of dictionaries.
"""
import sys
import argparse

import crds.hst.gentools.ezxml as ezxml

def process_table(t):
    tuples = []
    for element in t:
        if isinstance(element, (str, unicode)):
            continue
        if element.name == "tr":
            tuples.append(get_tuple(element))
    return tuples

def get_tuple(element):
    """Convert a table row into a tuple corresponding to its data items."""
    result = []
    for item in element:
        s = ""
        for piece in item:
            if not isinstance(piece, str) and piece.name == "a":
                piece = absolutize_url(piece)
            s += " " + clean_whitespace(str(piece))
        result.append(s.strip())
    return tuple(result)

def absolutize_url(anchor):
    """Convert relative href's into absolute URLs based on the global URL_ROOT."""
    global URL_ROOT
    href = anchor["href"]
    if not href.startswith("http://"):
        anchor["href"] = URL_ROOT + href
    return anchor

def clean_whitespace(s):
    """Remove line-breaks and change multi-space sequences to one space."""
    s = s.replace("\n", " ")
    s = " ".join(s.split())
    return s

def rationalize(keys):
    return [k.replace(" ","_").lower() for k in keys]

def tuples_to_dicts(tlist):
    keys = rationalize(tlist[0])
    dicts = []
    for row in tlist[1:]:
        dicts.append(dict(zip(keys,row)))
    return dicts

def dump_table(element):
    tuples = process_table(element)
    dicts = tuples_to_dicts(tuples)
    return dicts

URL_ROOT = ""

def xml_tables_to_dicts(s, table_numbers="all"):
    xml = ezxml.from_string(s)
    dicts = []
    table_no = 0
    for element in xml:
        if element.name == "url":
            global URL_ROOT
            URL_ROOT = element[0]
            if not URL_ROOT.endswith("/"):
                URL_ROOT += "/"
        elif element.name == "table":
            if (table_numbers == "all") or (table_no in table_numbers):
                dicts.extend(dump_table(element))
            table_no += 1
    return dicts

def xmlfile_tables_to_dicts(xmlname, table_numbers="all"):
    return xml_tables_to_dicts(open(xmlname).read(), table_numbers)

def process_tables(fname):
    print "["
    for d in xml_tables_to_dicts(open(fname).read()):
        print repr(d), ","
    print "]"

def dump_header_keys(fname, table_numbers="all"):
    dicts = xmlfile_tables_to_dicts(fname, table_numbers)
    headers = set()
    for d in dicts:
        header = tuple(sorted(d.keys()))
        if header not in headers:
            headers.add(header)
            print fname, "-->", repr(header)

# ==========================================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Process the specified tables from an XML file and re-emit them as Python dictionaries,  one table row per line.')
    parser.add_argument('files', help='Files to reformat as dictionaries', type=str, nargs="+")
    parser.add_argument('-t', '--table_numbers', dest='table_numbers', metavar='N', type=int, nargs='*',
        help='Which tables should be extracted,  numbered in order of appearance.  Specifying [] equivalent to "all".')
    args = parser.parse_args()
    for fname in args.files:
        dump_header_keys(fname, args.table_numbers or "all")

# ==========================================================================================

if __name__ == "__main__":
    main()

