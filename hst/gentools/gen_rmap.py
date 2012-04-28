"""Given an instrument this script will access the CDBS database
reffile_ops and generate an rmap file for each filekind associated
with the instrument as defined by reference_file_defs.xml.
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
import crds.hst.tpn as tpn

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
    row_dicts = get_row_dicts(instrument, filekind, condition=False)
    if not row_dicts:
        log.warning("No rows for",instrument,filekind)
        return
    kind_map = dicts_to_kind_map(instrument, filekind, row_dicts) 
    
    # kind_map = replace_full_sets_with_star(instrument, filekind, kind_map)
    
    write_rmap("hst", instrument, filekind, kind_map)

def get_row_dicts(instrument, kind, condition=True):
    """get_row_dicts() dumps the CDBS "row" table for `instrument` and
    file`kind`.  It is complicated because not all match parameters
    are in the database (hence extra_parkeys) and sometimes the
    database name for a key differs from the FITS name of a key.

    It returns a list of row dictionaries: [{parkey : value, ...}, ...]

    Always, "extra" parkeys are used in tests which precede or follow
    matching, but since they are not in the database by definition
    CDBS does not use them for matching.   For CRDS,  "extra" parkeys
    can once again be used in match relations but actual values for the
    extra keys must be added to the rmap through another mechanism such
    as an rmap customization filter.   By default,  extra parkeys are
    assigned the value "*" in all match tuples.
    """
    db_parkeys = list(parkeys.get_db_parkeys(instrument, kind))
    extra_parkeys = list(parkeys.get_extra_keys(instrument, kind))
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
    fields = list(db_parkeys) + \
        ["file_name", "comment", "useafter_date"] + \
        list(extra_parkeys)
    try:
        generator = cdbs_db.get_reffile_ops().execute(sql)
    except:
        log.error("Database error")
        return

    # Generate row dictionaries based on database values and N/A
    # for those extra parameters which are taken from the dataset
    # rather than the database and used for special processing 
    # instead of matching.
    row_dicts = []
    for row in generator:
        row = tuple(row) + (len(extra_parkeys) * ("N/A",))
        rowd = dict(zip(fields, row))
        for key, val in rowd.items():
            rowd[key] = utils.condition_value(val) if condition else val
        rowd["file_name"] = rowd["file_name"].lower()
        row_dicts.append(rowd)
    return row_dicts    

def get_reference_dicts(instrument, filekind, reffile):
    """Returns a list of the row dictionaries which apply to `reffile`."""
    return [ x for x in get_row_dicts(instrument, filekind, False) if x["file_name"] == reffile.lower()]

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

    kmap = unexplode_kmap(kmap)

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
        collapsed = roll_up_n_vars(cluster_key)
        for key in collapsed:
            if key not in matches_view:
                matches_view[key] = []
            matches_view[key].append(use)
    return matches_view           
    return factor_out_overlaps(matches_view)

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

def roll_up_n_vars(matches):
    original_matches = set(expand_all_ors(matches[:]))
    if not matches:
        return []
    for i in range(len(matches[0])):
        matches = roll_up_one_var(original_matches, matches)
    return matches

def roll_up_one_var(original_matches, matches):
    """Given a list of match tuples `matches`,  or-together any tuples which
    differ by only a single variable.
    """
    remainder = list(matches[:])
    rolled = []
    while remainder:
        match = remainder.pop()
        combined, remainder = _roll_up_one_var(original_matches, match, remainder)
        rolled.append(combined)
    return rolled

def _roll_up_one_var(original_matches, match, matches):
    remainder = matches[:]
    combined = match
    for match2 in matches:
        if differ_by_one(combined, match2):
            maybe = fold_one(combined, match2)
            if verify_completeness(maybe, original_matches):
                combined = maybe
                remainder.remove(match2)
    return combined, remainder

def verify_completeness(maybe, original_matches):
    for simple_match in expand_ors(maybe):
        if simple_match not in original_matches:
            return False
    return True

def expand_all_ors(matches):
    result = []
    for match in matches:
        result.extend(expand_ors(match))
    return result

def expand_ors(match):
    if not match:
        return [()]
    else:
        expanded = []
        nested_vals = expand_ors(match[1:])
        for val in str(match[0]).split("|"):
            for nested in nested_vals:
                expanded.append((val,) + nested)
        return expanded
                  
def differ_by_one(match1, match2):
    return len(set(match1) - set(match2)) == 1

def fold_one(match1, match2):
    """Combined two match tuples which differ in only a single variable."""
    folded = []
    for i in range(len(match1)):
        if match1[i] == match2[i]:
            folded.append(match1[i])
        else:
            set1 = set([x.strip() for x in str(match1[i]).split("|")])
            set2 = set([x.strip() for x in str(match2[i]).split("|")])
            combined = set1.union(set2)
            folded.append("|".join(sorted(combined)))
    return tuple(folded)

def factor_out_overlaps(kmap):
    """Overlapping match tuples of certain kinds result in ambiguous matches.
    Modify kmap to remove equal ranked overlaps.    Note that ambiguous matches 
    were initially considered an error but might be resolved by merging match 
    useafter sets.
    """
    for i, ikey in enumerate(kmap.keys()):
        for jkey in kmap.keys()[i+1:]:
            if ikey != jkey and overlaps(ikey, jkey):
                log.info("Overlap",repr(ikey),"<->", repr(jkey))
                
    # XXXXX TODO actually handle overlaps
                
    return kmap

def replace_full_sets_with_star(instrument, filekind, kmap):
    """Check each parameter of each match tuple to see if it contains the 
    or-ed set of all possible values.   If so,  replace it with '*'.
    """
    fitskeys = parkeys.get_fits_parkeys(instrument, filekind)
    tpnmap = { t.name.lower() : t for t in tpn.get_tpninfos(instrument, filekind) }
    for i, key in enumerate(fitskeys):
        try:
            keyset = set([utils.condition_value(x) for x in tpnmap[key].values])
        except KeyError:
            continue
        for match in kmap.keys():
            valset = set(match[i].split("|"))
            if keyset <= valset and len(keyset) > 1:
                log.write("Replacing", repr(match[i]), "with '*' in", repr(match))
                files = kmap.pop(match)
                match = list(match)
                match[i] = '*'
                match = tuple(match)
                kmap[match] = files
    return kmap

# =======================================================================

REFTYPE_FILTER = {
    ("wfc3", "biasfile") : crds.hst.wfc3.wfc3_biasfile_filter,
    ("wfpc2", "flatfile") : crds.hst.wfpc2.wfpc2_flatfile_filter,
    # ("acs",  "pfltfile") : crds.hst.acs.acs_pfltfile_filter
}

for instr in crds.hst.INSTRUMENTS:
    for filekind in crds.hst.FILEKINDS:
        try:
            REFTYPE_FILTER[(instr,filekind)] = utils.get_object(
                "crds.hst."+instr+"."+instr+"_"+filekind+"_filter")
            log.info("Found special case filter for",
                     repr(instr), repr(filekind))
        except:
            pass # log.error()

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
    Apply parameter restrictions to reduce irrelevant match parameters to N/A.
    Return a tuple of match parameters.
    """
    db_parkeys = parkeys.get_db_parkeys(instrument, filekind)     # ordered
    extra_parkeys = parkeys.get_extra_keys(instrument, filekind)     # ordered
    restricted = apply_restrictions(row, instrument, filekind)
    # Construct a simple match tuple (no names) in the right order.
    match = []
    for pkey in db_parkeys + extra_parkeys:
        match.append(restricted[pkey])
    return tuple(match)

def apply_restrictions(row, instrument, filekind):
    """Evaluate CDBS parameter restrictions in the context of a raw match 
    tuple dictionary,  mutating irrelevant parameters to "N/A".
    """
    restrictions = parkeys.get_parkey_restrictions(instrument, filekind)
    # Get a lowercase version of row for evaluating restriction expressions
    # Nominally this corresponds to the dataset header.
    header = {}
    for key,value in row.items():
        header[key.upper()] = value
    result = {}
    # Mutate irrelevant parameters to "N/A".
    for key, value in row.items():
        if key in restrictions:
            if not eval(restrictions[key], {}, header):
                value = "N/A"
            log.verbose("restricting", row["file_name"], key, "of", header, 
                     "with", restrictions[key], "value =", value)
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
    # CRDS matches against keys which come from both the CDBS database
    # and the dataset.  In both cases, FITS names are used in the rmap
    # while the database name was/is required to obtain the match
    # value.  At rmap generation time, the values of extra keys (non
    # database FITS) ware either hard coded to "*" or computed by a
    # reference specific generation filter.
    match_keys = tuple([key.upper() for key in 
                      parkeys.get_fits_parkeys(instrument, filekind) +
                      parkeys.get_extra_keys(instrument, filekind)
                      ])
    useafter_keys  = ('DATE-OBS', 'TIME-OBS',)
    now = str(timestamp.now())
    rmap_header = OrderedDict([
        ("name", outname[2:]),
        ("derived_from", "generated from CDBS database " + now),
        ("mapping", "REFERENCE"),
        ("observatory", observatory.upper()),
        ("instrument", instrument.upper()),
        ("filekind", filekind.upper()),
        ("parkey", (match_keys, useafter_keys)),
        # ("extra_keys", tuple([key.upper() for key in parkeys.get_extra_keys(instrument, filekind)])),
        ("relevance", parkeys.get_relevance(instrument, filekind)),
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
                useafter_keys, useafter_selections)
    rmap_selector = selectors.MatchingSelector(match_keys, matching_selections)
    rmapping = rmap.ReferenceMapping(outname, rmap_header, rmap_selector)
    rmapping.write()

# ==========================================================================

def test():
    """Run the module doctests."""
    import doctest, gen_file_rmap
    return doctest.testmod(gen_file_rmap)

# ==========================================================================

if __name__ == "__main__":
    if "--verbose" in sys.argv:
        log.set_verbose()
        sys.argv.remove("--verbose")
    if len(sys.argv) == 2:
        generate_all_rmaps(instrument=sys.argv[1])
    elif len(sys.argv) == 3:
        generate_rmap(instrument=sys.argv[1], filekind=sys.argv[2])
    else:
        sys.stderr.write("usage: %s <instrument> <filekind>\n" % sys.argv[0])
        sys.exit(-1)
