"""Given an instrument this script will access the CDBS database reffile_ops
and generate an rmap file for each filekind associated with the
instrument as defined by reference_file_defs.xml.
"""
import sys
import os
import cProfile
import glob
import re
import pprint

from BeautifulSoup import BeautifulStoneSoup

import cdbs_db

from crds import (rmap, log, timestamp, utils, selectors)
from crds.compat import OrderedDict

import crds.hst.acs
import crds.hst.cos
import crds.hst.nicmos
import crds.hst.stis
import crds.hst.wfc3
import crds.hst.wfpc2

# =======================================================================

def ccontents(n): 
    """Return the lowercase stripped contents of a single values XML node"""
    return str(n.contents[0].strip().lower())

def process_reference_file_defs(instrument):
    """Given an `instrument` name, process the CDBS config file
    reference_file_defs.xml and return a dictionary mapping

    { filekind :  (reftype, parkeys) }

    where filekind is the name of a FITS header keyword which names
    a reference file,  reftype is the 3-or-so character suffix which
    reference filenames typically end with (xxx_<reftype>.fits),
    parkeys is a list of dataset header keywords used to select the
    reference file.
    """
    xml = BeautifulStoneSoup(open("../cdbs/cdbs_bestref/reference_file_defs.xml").read())
    rdefs = {}
    for node in xml.findAll("instrument"):
        instr = ccontents(node.instrument_name)
        if instr != instrument:
            continue
        for inode in node:
            if not hasattr(inode, "name"):
                continue
            if inode.name == "reffile":
                parkeys = []
                rtype = ccontents(inode.reffile_type)
                keyword = ccontents(inode.reffile_keyword)
                for rnode in inode:
                    if not hasattr(rnode, "name"):
                        continue
                    if rnode.name == "file_selection":
                        parkeys.append(ccontents(rnode.file_selection_field))
                rdefs[keyword] = (rtype, parkeys)
    return rdefs

def generate_all_rmaps(instrument):
    """Given an `instrument`, this function will generate a .rmap file
    for each filekind known for the instrument.
    """
    rdefs = process_reference_file_defs(instrument)
    for kind in sorted(rdefs):
        reftype, parkeys = rdefs[kind]
        generate_rmap(instrument, kind, reftype, parkeys)
    log.standard_status()

# =======================================================================

ROW_TABLES = {
   "nicmos"  : "nic_row",
}

FILE_TABLES = {
   "nicmos"  : "nic_file",
}

def generate_rmap(instrument, kind, reftype, parkeys):
    log.info("Processing", instrument, kind, parkeys)
    row_table = ROW_TABLES.get(instrument, instrument + "_row")
    file_table = FILE_TABLES.get(instrument, instrument + "_file")
    columns = [ row_table + "." + key for key in parkeys + ["file_name"]]
    columns += [ file_table + "." + "useafter_date" ]
    tables = [row_table, file_table]
    sql = "select %s from %s where %s.file_name=%s.file_name" % \
        (", ".join(columns), ", ".join(tables), row_table, file_table)
    print "executing", sql
    fields = parkeys + ["file_name", "useafter_date"]
    generator = cdbs_db.REFFILE_OPS.execute(sql)
    row_dicts = []
    for row in generator:
        rowd = dict(zip(fields, row))
        for key, val in rowd.items():
            rowd[key] = utils.condition_value(val)
        row_dicts.append(rowd)
    pprint.pprint(row_dicts)
    return

    map_contrib = dicts_to_kind_map(instr, kind, contrib) 
    kind_map = {}
    for key in map_contrib:
        if key not in kind_map:
                kind_map[key] = []
        for filemap in map_contrib[key]:
            if filemap not in kind_map[key]:
                kind_map[key].append(filemap)
    write_rmap("hst", instr, kind, kind_map)

# =======================================================================

def dicts_to_kind_map(instr, kind, parkeys, row_dicts):
    """Given a list of dictionaries `row_dicts`, return an rmap dictionary
    mapping parkey bindings onto lists of date,file tuples.  `instr`ument
    and file`kind` are used to choose parkeys from the KIND_KEYS map.
    KIND_KEYS defines which parkeys of all the columns in each row are used 
    in the rmap for a particular kind.   Strictly speaking,  a table column
    name is not a parkey but may only correspond to header keyword.
    """
    kmap = {}

    for row in row_dicts:
        match_tuple = get_match_tuple(row, instr, kind)
        if match_tuple is False:
            continue
        if match_tuple not in kmap:
            kmap[match_tuple] = list()
        mapping = get_mapping(row)
        warned = False
        for existing in kmap[match_tuple]:
            if mapping.date == existing.date:
                if mapping.file != existing.file:
                    log.error("Overlap in match_tuple", 
                              repr(match_tuple), repr(mapping))
                    if "***" not in mapping.comment:
                        mapping = rmap.Filemap(
                            date=mapping.date, 
                            file=mapping.file, 
                            comment = "# *** " + mapping.comment[2:])

                else:
                    if not warned:
                        log.warning("Duplicate", repr(mapping))
                        warned = True
                    continue
        kmap[match_tuple].append(mapping)

    kmap = expand_kmap(instr, kind, kmap)

    for val in kmap.values():
        val.sort()

    return kmap

# =======================================================================

REFTYPE_FILTER = {
    ("wfc3", "biasfile") : crds.hst.wfc3.wfc3_biasfile_filter,
    # ("acs",  "pfltfile") : crds.hst.acs.acs_pfltfile_filter
}

HEADER_ADDITIONS = {}

def expand_kmap(instr, kind, kmap):
    """Execute a (instr, filetype) specific filter to modify the kmap
    and return any required header additions for this case.

    Filters return a potentially modified kmap and a list of header
    dict items (because it is ordered).
    """
    if (instr, kind) not in REFTYPE_FILTER:
        return kmap
    else:
        kmap, header_additions = REFTYPE_FILTER[(instr, kind)](kmap)
        HEADER_ADDITIONS[(instr, kind)] = header_additions
    return kmap

# =======================================================================

def get_match_tuple(row, parkeys):
    lkey = []
    for pkey in parkeys:
        value = row.get(var, "not present")
        value = utils.condition_value(value)
        lkey.append(value)
    return tuple(lkey)


# =======================================================================

def get_mapping(row):
    """Given a table data row dictionary, return an rmap mapping tuple.
    """
    if COMMENTKEYS:
        comments = []
        for cvar in COMMENTKEYS:
            try:
                comments.append(row[cvar])
            except KeyError:
                pass
        comments_str = ", ".join(comments)
    else:
        comments_str = ""
    return rmap.Filemap(timestamp.format_date(timestamp.parse_date(
                row["use_after"])), dict_to_filename(row), comments_str)

# =======================================================================

def write_rmap(observatory, instrument, filekind, parkeys, kind_map):
    """Constructs rmap's header and data out of the kind_map and
    outputs an rmap file
    """
    outname  = "./" + observatory + "_" + instrument + "_" + filekind + ".rmap"
    fitskeys = tuple([key.upper() for key in parkeys])
    MAPKEYS  = ('DATE-OBS', 'TIME-OBS',)
    now = timestamp.now().split('.')[0]
    rmap_header = OrderedDict([
        ("name", outname[2:]),
        ("derived_from", "scraped " + now),
        ("mapping", "REFERENCE"),
        ("observatory", observatory.upper()),
        ("instrument", instrument.upper()),
        ("filekind", filekind.upper()),
        ("parkey", (fitskeys, mapkeys)),
        ("description", ("Initially generated on " + now)),
    ])

    # Execute filekind specific customizations on header    
    rmap_header.update(HEADER_ADDITIONS.get((instrument, filekind), {}))
    
    matching_selections = dict()
    for match_tuple in sorted(kind_map):
        filemaps = kind_map[match_tuple]
        useafter_selections = OrderedDict()
        for fmap in sorted(filemaps):
            if fmap.date in useafter_selections:
                existing_file = useafter_selections[fmap.date]
                if fmap.file != existing_file:
                    log.warning("Useafter date collision in", repr(instrument), 
                                repr(filekind), repr(match_tuple), "at", 
                                repr(fmap.date), repr(fmap.file), "replaces", 
                                repr(existing_file))
            useafter_selections[fmap.date] = fmap.file
        matching_selections[match_tuple] = selectors.UseAfterSelector(
                ("DATE-OBS", "TIME-OBS"), useafter_selections)
    rmap_selector = selectors.MatchingSelector(
        fitskeys[:-2], matching_selections)
    rmapping = rmap.ReferenceMapping(outname, rmap_header, rmap_selector)
    rmapping.write()

# ==========================================================================

def test():
    """Run the module doctests."""
    import doctest, gen_file_rmap
    return doctest.testmod(gen_file_rmap)

# ==========================================================================

if __name__ == "__main__":
    generate_all_rmaps(instrument=sys.argv[1])
