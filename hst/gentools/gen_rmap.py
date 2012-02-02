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

import cdbs_db

from crds import (rmap, log, timestamp, utils, selectors)
from crds.compat import OrderedDict

import crds.hst.acs
import crds.hst.cos
import crds.hst.nicmos
import crds.hst.stis
import crds.hst.wfc3
import crds.hst.wfpc2

import crds.hst.parkeys as parkeys

# =======================================================================

def generate_all_rmaps(instrument):
    """Given an `instrument`, this function will generate a .rmap file
    for each filekind known for the instrument.
    """
    for kind in parkeys.get_filekinds(instrument):
        generate_rmap(instrument, kind)
    log.standard_status()

# =======================================================================

ROW_TABLES = {
   "nicmos"  : "nic_row",
}

FILE_TABLES = {
   "nicmos"  : "nic_file",
}

def generate_rmap(instrument, filekind):
    log.info("Processing", instrument, filekind)
    row_dicts = get_row_dicts(instrument, filekind)
    if not row_dicts:
        log.warning("No rows for",instrument,filekind)
        return
    kind_map = dicts_to_kind_map(instrument, filekind, row_dicts) 
    write_rmap("hst", instrument, filekind, kind_map)

def get_row_dicts(instrument, kind):
    db_parkeys = list(parkeys.get_db_parkeys(instrument, kind))
    reftype = parkeys.get_reftype(instrument, kind)
    row_table = ROW_TABLES.get(instrument, instrument + "_row")
    file_table = FILE_TABLES.get(instrument, instrument + "_file")
    columns = [ row_table + "." + key for key in db_parkeys + ["file_name", "comment"]]
    columns += [ file_table + "." + "useafter_date" ]
    tables = [row_table, file_table]
    sql = """select {columns} from {tables} where {row_table}.file_name={file_table}.file_name
and {row_table}.expansion_number={file_table}.expansion_number
and {file_table}.opus_load_date is not null
and {file_table}.archive_date is not null
and {file_table}.opus_flag = 'Y'
and {file_table}.reject_flag = 'N'
and {file_table}.reference_file_type = '{reference_file_type}'
""".format(columns = ", ".join(columns),
           tables = ", ".join(tables), 
           row_table = row_table,
           file_table = file_table,
           reference_file_type = reftype.upper())
    log.verbose("executing", sql)
    fits_parkeys = parkeys.get_fits_parkeys(instrument, kind)
    fields = list(db_parkeys) + ["file_name", "comment", "useafter_date"]
    try:
        generator = cdbs_db.get_reffile_ops().execute(sql)
    except:
        log.error("Database error")
        return
    row_dicts = []
    for row in generator:
        rowd = dict(zip(fields, row))
        for key, val in rowd.items():
            rowd[key] = utils.condition_value(val)
        rowd["file_name"] = rowd["file_name"].lower()
        row_dicts.append(rowd)
    return row_dicts    

def get_reference_dicts(instrument, filekind, reffile):
    return [ x for x in get_row_dicts(instrument, filekind) if x["file_name"] == reffile.lower()]

# =======================================================================

def dicts_to_kind_map(instr, kind, row_dicts):
    """Given a list of dictionaries `row_dicts`, return an rmap
    dictionary mapping parkey bindings onto lists of date,file tuples.
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
                    # log.error("Overlap in match_tuple", 
                    #          repr(match_tuple), repr(mapping), repr(existing))
                    if "***" not in mapping.comment:
                        mapping = rmap.Filemap(
                            date=mapping.date, 
                            file=mapping.file, 
                            comment = "# *** " + mapping.comment[2:])
                else:
                    if not warned:
                        # log.warning("Duplicate", repr(mapping))
                        warned = True
                    continue
        kmap[match_tuple].append(mapping)

    kmap = instrument_specific_hacks(instr, kind, kmap)

    # kmap = unexplode_kmap(kmap)

    for val in kmap.values():
        val.sort()

    return kmap

# =======================================================================

def unexplode_kmap(kmap):
    useafters = {}
    for match_tuple, useafter_files in kmap.items():
        for use in useafter_files:
            use = rmap.Filemap(use.date, use.file, "")
            if use not in useafters:
                useafters[use] = []
            useafters[use].append(match_tuple)
    matches_view = {}
    for use, matches in useafters.items():
        cluster_key = tuple(sorted(matches))
        collapsed = collapse_cluster_key(cluster_key)
        for key in collapsed:
            if key not in matches_view:
                matches_view[key] = []
            matches_view[key].append(use)           
    return factor_out_overlaps(matches_view)

def collapse_cluster_key(key):
    parsets = []
    for i in range(len(key[0])):
        parset = set()
        for match in key:
            parset.add(match[i])
        parsets.append(parset)
    expanded = expand_parsets(parsets)
    if expanded == key:
        return [folded(parsets)]
    else:
        return key

def _expand_parsets(parsets):
    if not parsets:
        yield ()
    else:
        expanded = []
        for par in parsets[0]:
            for sub in expand_parsets(parsets[1:]):
                yield (par,) + sub

def expand_parsets(parsets):
    expanded = list(_expand_parsets(parsets))
    expanded.sort()
    return tuple(expanded)
       
def folded(parsets):
    combined = []
    for par in parsets:
        combined.append("|".join(sorted(par)))
    return tuple(combined)

def overlaps(match_t1, match_t2):
    for par1, par2 in zip(match_t1, match_t2):
        if "*" in [par1, par2]:
            continue
        if par1 == par2 or match_any(par1, par2) or match_any(par2, par1):
            continue
        return False
    return True

def match_any(par1, par2_all):
    matches = []
    for par2 in par2_all.split("|"):
        if re.match(fixre(par1), par2):
            matches.append(par2)
    return matches

def fixre(regex):
    return "|".join(["^" + par + "$" for par in regex.split("|")])

def factor_out_overlaps(kmap):
    for i, ikey in enumerate(kmap.keys()):
        for jkey in kmap.keys()[i+1:]:
            if ikey != jkey and overlaps(ikey, jkey):
                log.info("Overlap",repr(ikey),"<->", repr(jkey))
    return kmap

# =======================================================================

REFTYPE_FILTER = {
    ("wfc3", "biasfile") : crds.hst.wfc3.wfc3_biasfile_filter,
    # ("acs",  "pfltfile") : crds.hst.acs.acs_pfltfile_filter
}

HEADER_ADDITIONS = {}

def instrument_specific_hacks(instr, kind, kmap):
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

def get_match_tuple(row, instrument, filekind):
    """Format a row dictionary into a tuple of parkeys in the proper order.
    Apply parameter restrictions to reduce irrelevant match parameters to *.
    Return a tuple of match parameters.
    """
    db_parkeys = parkeys.get_db_parkeys(instrument, filekind)     # ordered
    restrictions = parkeys.get_parkey_restrictions(instrument, filekind)
    # Construct a raw parkey dictionary for this match tuple
    raw = {}
    for pkey in db_parkeys:
        raw[pkey] = row.get(pkey, "not present")
    # Mutate irrelevant parameters to *
    restricted = apply_restrictions(restrictions, raw, row)
    # Construct a simple match tuple (no names) in the right order.
    match = []
    for pkey in db_parkeys:
        match.append(restricted.get(pkey, "not present"))
    return tuple(match)

def apply_restrictions(restrictions, raw, row):
    """Apply CDBS parameter restrictions to a raw match tuple dictionary,
    mutating irrelevant parameters to "*".
    """
    # Define the value "header" in the restriction expressions in parkeys.dat 
    header = {}
    for key,value in raw.items():
        header[key.lower()] = value.lower()
    result = {}
    # Mutate irrelevant parameters to "*".
    for key, value in raw.items():
        if key in restrictions:
            if not eval(restrictions[key], {}, header):
                value = "*"
            log.info("restricting", row["file_name"], key, "of", header,"with",restrictions[key],"value =", value)
        result[key] = value
    return result

# =======================================================================

def get_mapping(row):
    """Given a table data row dictionary, return an rmap mapping tuple.
    """
    return rmap.Filemap(timestamp.format_date(timestamp.parse_date(
                row["useafter_date"])), row["file_name"], row["comment"])

# =======================================================================

def write_rmap(observatory, instrument, filekind, kind_map):
    """Constructs rmap's header and data out of the kind_map and
    outputs an rmap file
    """
    outname  = "./" + observatory + "_" + instrument + "_" + filekind + ".rmap"
    fitskeys = tuple([key.upper() for key in 
                    parkeys.get_fits_parkeys(instrument, filekind)])
    mapkeys  = ('DATE-OBS', 'TIME-OBS',)
    now = timestamp.now().split('.')[0]
    rmap_header = OrderedDict([
        ("name", outname[2:]),
        ("derived_from", "scraped " + now),
        ("mapping", "REFERENCE"),
        ("observatory", observatory.upper()),
        ("instrument", instrument.upper()),
        ("filekind", filekind.upper()),
        ("parkey", (fitskeys, mapkeys)),
        ("extra_keys", tuple([key.upper() for key in parkeys.get_extra_keys(instrument, filekind)])),
        ("relevance", parkeys.get_relevance(instrument, filekind)),
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
    if len(sys.argv) == 2:
        generate_all_rmaps(instrument=sys.argv[1])
    elif len(sys.argv) == 3:
        generate_rmap(instrument=sys.argv[1], filekind=sys.argv[2])
    else:
        sys.stderr.write("usage: %s <instrument> <filekind>\n" % sys.argv[0])
        sys.exit(-1)
