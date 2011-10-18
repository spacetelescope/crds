"""This script processes the XML for the first tier of the CDBS HTML,  the
instrument index,  a map from file kinds to URLs of file mapping tables.  For
each file kind,  all URLs are retrieved and stored as raw HTML,  and the
corresponding simplified XML is also stored.   Files are named:

<instrument> _ <reftype> _ <url_number> . html
<instrument> _ <reftype> _ <url_number> . xml

All of the .xml files for a file kind can then be reduced to a single file mapping rmap.

Ignoring serial numbers,  the instrument index rmap can be named something like:

<instrument> . rmap

Ignoring reftype serial numbers,  the second tier map file names which make up the bulk of
the instrument index are implicit:

<instrument> _ <reftype> . rmap
"""

import sys
from cStringIO import StringIO
import argparse
from crds.compat import OrderedDict

from crds.hst.gentools import ezxml, scrape, tlist

from crds import log, rmap

# ==========================================================================================

from crds.hst import INSTRUMENTS

def get_instrument(fname):
    for instr in INSTRUMENTS:
        if instr in fname.lower():
            return instr
    raise RuntimeError("Can't determine instrument from filename: "+ repr(fname))

# ==========================================================================================

def get_filelist_xml(fname):
    """Iterates over the rows of the instrument index table in `fname`,  fetching each
    specified URL and dumping it as XML to a file list file.   Note that a single
    file kind (header keyword) can map onto multiple URLs which in turn can
    contain multiple tables of reference files;  this routine dumps each URL
    into it's own file.   This routine also writes out the top level instrument rmap
    which maps file kinds onto rmaps will will be generated later from the XML output here.
    The index is written here to include comments about the source XML tables.
    """
    instr = get_instrument(fname)
    for pars in tlist.xmlfile_tables_to_dicts(fname):
        converted = convert_pars(pars)
        keyword = converted["keyword"].lower()
        if "---" in keyword:
            log.warning("Skipping", repr(pars))
            continue
        print `keyword`, converted["comment"]
        urls = converted["urls"]
        for i, url in enumerate(urls):
            print i, "<--" , `url`
            sourcename = instr + "_" + keyword + "_" + str(i)
            scrape.dump_tables(url, sourcename)

def generate_context_rmap(fname):
    """Based on XML index file `fname`,  write out an imap.
    """
    instr = get_instrument(fname)
    source_url = scrape.get_url(open(fname).read())
    header = OrderedDict([
      ("mapping", "instrument"),
      ("observatory" , "HST"),
      ("instrument", instr.upper()),
      ('parkey', ('REFTYPE',)),
      ("source_url", source_url),      
    ])
    selector = {}
    for pars in tlist.xmlfile_tables_to_dicts(fname):
        converted = convert_pars(pars)
        keyword = converted["keyword"].lower()
        if "---" in keyword:
            log.warning("Skipping", repr(pars))
            continue
        eventually_generated_rmap = "hst_" + instr + "_" + keyword + ".rmap"
        selector[keyword] = (converted["ext"], eventually_generated_rmap)
    imap = rmap.Mapping("./"  + instr + ".imap", header, selector)
    imap.write()

def get_value_from_keys(d, keylist):
    for key in keylist:
        try:
            return d[key]
        except KeyError:
            pass
    raise KeyError(" ".join(keylist) + " not found.")

def convert_pars(pars):
    comment = get_value_from_keys(pars, [
        "reference_file_type", "pipeline_reference_files",
        "non-pipeline_reference_files"])
    comment = comment.split("<")[0]
    try:
        ext = pars["extension"].replace("/d","") # change GEIS h/d to simply h
    except:
        ext = pars["file_suffix"]
    keyword = pars["header_keyword"]
    urls = get_urls(get_value_from_keys(pars, ["camera", "detector", "mode"]))
    d = dict(locals())
    del d["pars"]
    return d

def get_urls(cstr):
    """Get urls returns a list of the hrefs of any top-level <a>'s in `cstr`.  cstr
    is a string of XML nominally containing one or more <a>'s from which the href's
    will be extracted.  cstr is well-formed with the possible exception of having multiple
    root elements.
    """
    x = ezxml.from_string("<doc>" + cstr + "</doc>")
    urls = []
    for c in x:
        if isinstance(c, (str, unicode)):
            continue
        if c.name == "a":
            urls.append(c["href"])
    return urls

# ==========================================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Generates context rmaps from index XML.')
    parser.add_argument('index_file', help='Filename of instrument index XML to convert.'),
    parser.add_argument('-r', '--generate-context-rmap', dest='generate_context',
                        action="store_const", default=False, const=True,
        help='Convert the index file into an instrument context rmap.')
    parser.add_argument('-s', '--scrape-file-mappings', dest='scrape_file_mappings',
                        action="store_const", default=False, const=True,
        help='Fetch the HTML URLs associated with each file kind in the index and convert to XML.')
    args = parser.parse_args()
    if args.generate_context:
        generate_context_rmap(args.index_file)

    if args.scrape_file_mappings:
        get_filelist_xml(args.index_file)

# ==========================================================================================

if __name__ == "__main__":
    main()
