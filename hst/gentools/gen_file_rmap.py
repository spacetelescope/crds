"""Given an instrument and the path to it's CDBS XML table files,  this
script will generate an rmap file for each reftype associated with the
instrument.
"""
import sys
import os
import cProfile

import glob
import argparse
import re
import StringIO
import pprint as pp

import crds.hst.gentools.tlist as tlist
import crds.hst.gentools.ezxml as ezxml
import crds.hst.gentools.lookup as lookup
import crds.hst.gentools.keyval as keyval
import crds.hst.gentools.cdbs_parkeys as cdbs_parkeys
from   crds.hst.gentools.cdbs_parkeys import KIND_KEYS, MAPKEYS, COMMENTKEYS
import crds.hst.locate as locate

import crds.rmap as rmap
import crds.log as log
import crds.timestamp as timestamp
import crds.pysh as pysh
import crds.selectors as selectors
import crds.utils as utils
from crds.compat import OrderedDict

import crds.hst.acs
import crds.hst.cos
import crds.hst.stis
import crds.hst.wfc3

# =======================================================================

SELECT_TABLES = {
        "default" : "all",
        "stis" : {
            "default" : [0],
            "apdstab" : [1],
        }
}

def get_selected_tables(instr, kind):
    """Return a list of table numbers to extract.   Some instrument file kinds
    (STIS) have extraneous tables (.e.g. old references, layout, ...) which
    need to be ignored.
    """
    try:
        selected = SELECT_TABLES[instr][kind]
    except:
        try:
            selected = SELECT_TABLES[instr]["default"]
        except:
            selected = SELECT_TABLES["default"]
    return selected

# =======================================================================

def generate_all_rmaps(instrument, source_path):
    """Given an `instrument`,  this function will generate a .rmap file for
    each reftype known for the instrument.  The XML table sources for the rmap
    are found along path `source_path` and must be named:
        <instrument> _ <reftype> _ <serialno> .xml
    where serialno corresponds to the CDBS HTML URL from which the XML was scraped.
    """
    for kind in KIND_KEYS[instrument]:
        pattern = source_path + "/" + instrument + "_" + kind + "_*.xml"
        kind_files = sorted(glob.glob(pattern))
        if kind_files:
            generate_rmap(kind_files)
        else:
            log.warning("Skipping", repr(pattern))
    log.standard_status()

# =======================================================================

def generate_rmap(xml_files):
    """Given a set of ripped XML files for the same file kind,
    generate an rmap file describing the listed files.

    For the sake of simplicity and uniformity,  we require input filenames of
    the form:

    <instr>_<kind>_<serial>.xml

    where <instr> is .e.g. "acs" and <kind> should be one of the FITS header
    keywords used to locate reference files, lower-cased.   These filenames are
    emitted by convert_index.py.

    Serial corresponds to each of potentially multiple source URLs which define
    the mapping for a file kind, .i.e. the first URL is serial "0". Note that
    each URL may in turn define multiple tables of mappings.   All of the many
    URLs,  and all of their tables,  are transformed into a single rmap.   Each
    many-table URL is input here as a single file of XML.
    """
    kind_map = {}
    for name in xml_files:
        log.info("Processing", repr(name))
        # Note: instr and kind are always the same but are needed.  serial num is
        # mostly irrelevant.
        instr, kind, serial = os.path.basename(name).split(".")[0].split("_")
        xml = open(name).read()
        contrib = tlist.xml_tables_to_dicts(xml, get_selected_tables(instr, kind))
        contrib = [d for d in contrib if valid_dict(d)]
        if not contrib:
            log.warning("No mappings in", repr(name))
        map_contrib = dicts_to_kind_map(instr, kind, contrib) # lookup_keys : [ dict ]
        for key in map_contrib:
            if key not in kind_map:
                kind_map[key] = []
            for filemap in map_contrib[key]:
                if filemap not in kind_map[key]:
                    kind_map[key].append(filemap)
    write_rmap("hst", instr, kind, kind_map)

def valid_dict(d):
    return  True  # ("pedigree" not in d) or (d["pedigree"].strip().lower() != "dummy")

# =======================================================================

DICT_HACKS = {
    #   key_is    :   key_should_be  (more common parlance)
        "filter1" : "filter_1",
        "filter2" : "filter_2",
        "use_after_date" : "use_after"
}

def hack_dictionary(d):
    """Adjust for eccentricities in dictionary keys.   This is predominantly
    to avoid blindly bifurcating table columns because individual rows (dicts)
    have slightly different names for the same thing.   This naming oddness is
    brought about by collapsing multiple tables,  not all of which used the same
    column headers, into a single rmap.
    """
    for hack in DICT_HACKS:
        if hack in d:
            d[DICT_HACKS[hack]] = d.pop(hack)

# =======================================================================

def explode_dictionary(d):
    """Given a dictionary `d` representing a CDBS table row,  if any of the fields
    contain magic values,  expand the row into multiple rows.  Return the corresponding
    list of dictionaries.

    Since in principle multiple parameters can be expanded this way,  and each
    variant of one parameter should be crossed with all the variants of the
    others, this is a potentially exponential expansion.

    >>> explode_dictionary({"foo":"1", "bar":"FR388N, FR423N AND FR462N"})
    [{'foo': '1', 'bar': 'FR388N'}, {'foo': '1', 'bar': 'FR423N'}, {'foo': '1', 'bar': 'FR462N'}]

    """
    return [x for x in _explode_dictionary_items(d.items())]

def explode_letters(value):
    return [x for x in value]

def explode_and(value):
    return value.split(" AND ")

def explode_comma(value):
    return value.split(", ")

EXPLODERS = {
        # ABCD really means all of these,  not any of these.
        # "^[ABCD]+$" : explode_letters,
        " AND " : explode_and,
        ", ": explode_comma,
}

NO_EXPLODE = COMMENTKEYS + MAPKEYS

def _explode_dictionary_items(items):
    if items == []:
        yield {}
    else:
        key, val = items[0]
        val = val.strip()
        for magic_re, exploder in EXPLODERS.items():
            if key not in NO_EXPLODE and re.search(magic_re, val):
                # log.write("Matched exploder", repr(magic_re))
                results = []
                for x in exploder(val):
                    results.extend(_explode_dictionary_items([(key, x.strip())]))
                # log.write("Exploding", repr(val), "-->", repr(results))
                break
        else:
            results = [{ key: val }]
        others = _explode_dictionary_items(items[1:])
        for o in others:
            for r in results:
                yield dict(o.items() + r.items())

# =======================================================================

def dicts_to_kind_map(instr, kind, dicts):
    """Given a list of dictionaries `dicts`, return an rmap dictionary
    mapping parkey bindings onto lists of date,file tuples.  `instr`ument
    and file `kind` are used to choose parkeys from the KIND_KEYS map.
    """
    kmap = {}

    exploded_dicts = []
    for d in dicts:
        exploded_dicts.extend(explode_dictionary(d))

    for d in exploded_dicts:
        hack_dictionary(d)
        key = get_key(d, instr, kind)
        if key is False:
            continue
        if key not in kmap:
            kmap[key] = list()
        mapping = get_mapping(d)
        warned = False
        for existing in kmap[key]:
            if mapping.date == existing.date:
                if mapping.file != existing.file:
                    log.error("Overlap in key", repr(key), repr(mapping))
                    if "***" not in mapping.comment:
                        mapping = rmap.Filemap(date=mapping.date, file=mapping.file, comment = "# *** " + mapping.comment[2:])

                else:
                    if not warned:
                        log.warning("Duplicate", repr(mapping))
                        warned = True
                    continue
        kmap[key].append(mapping)

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

def get_key(d, instr, kind):
    """Given a CDBS Table data row dictionary `d`, an `instrument`,  and a file
    `kind`,   return a tuple of dictionary values which have been selected as
    parkey values in KIND_KEYS.  If a parkey begins with '*' and `d` does
    not contain it (w/o the '*'),   the corresponding key element for `d` is also '*'.
    If a parkey begins with %,  the value is fetched first from the reference file,
    but will default to the value in `d` or '*' if not in `d`.
    If a required parkey is not present in `d`,  `d` is ignored with a warning.
    """
    parkeys = KIND_KEYS[instr][kind]
    lkey = []
    for pkey in parkeys:
        special, var, default = keyval.parse_parkey(pkey)
        if special == "*":  # optional and embedded keywords fail to *.
            value = d.get(var, default or "not present")
        elif special in ["%","!"]:
            value = get_parkey_from_reffile(d, instr, var)
            if value == "not present":
                value = d.get(var, default or "not present")
        else:
            try:   # Mandatory keywords must be there or fail.
                value = d[var]
            except KeyError:
                log.warning("Ignoring dict for: ", repr(var), ":", repr(d))
                return False  # Ew.
        if default is not None and value == "*":
            value = default
        value = utils.condition_value(value)
        lkey.append(value)
    return tuple(lkey)


def get_parkey_from_reffile(d, instr, var):
    """Attempt to resolve undefined lookup keys for a reference file by looking
    at the file's FITS header.
    """
    ref_filename = dict_to_filename(d)
    try:
        ref_path = locate.locate_server_reference(ref_filename)
    except KeyError, e:
        log.error("Can't find reference file", repr(ref_filename))
        return "%no reference%"
    
    fits_var = cdbs_parkeys.to_fitskey(instr, var)

    try:
        header = lookup.get_header_union(ref_path)
        value = header[fits_var]
    except KeyError:
        # log.warning("Can't find", repr(var), "mapped to FITS", repr(fits_var), "in", repr(ref_path))
        value = "not present"
    except IOError, e:
        log.warning("Error reading",repr(ref_path),"trying to get",repr(var), str(e))
        value = "%reference error%"
    return value

# =======================================================================

def get_mapping(d):
    """Given a table data row dictionary, return an rmap mapping tuple.
    """
    if COMMENTKEYS:
        comments = []
        for cvar in COMMENTKEYS:
            try:
                comments.append(d[cvar])
            except KeyError:
                pass
        comments_str = ", ".join(comments)
    else:
        comments_str = ""
    return rmap.Filemap(timestamp.format_date(timestamp.parse_date(d["use_after"])), dict_to_filename(d), comments_str)

def dict_to_filename(d):
    """Given the XHTML <a> corresponding to the 'file' field,  ignore the href and
    just return the name which appear as the contents.
    """
    anchor = d["file"]
    fname = ezxml.from_string(anchor)[0]
    if isinstance(fname, (str, unicode)):
        return fname.strip()
    else:   # wfpc2 holy crap!:   <ecm09460u href="hspace"> ecm09460u </ecm09460u>
        return fname[0].strip()

# =======================================================================

def parkeys_to_fitskeys(instrument, all_parkeys):
    fits_keys = []
    required = []
    for key in all_parkeys:
        special, var, default = keyval.parse_parkey(key)
        fvar = cdbs_parkeys.to_fitskey(instrument, var)
        if special in ["*","%"]:   # optional
            special = "*"
        else:                      # required
            special = ""
        combined_fvar = keyval.compose_parkey(special, fvar, None)
        fits_keys.append(combined_fvar)
    if "*" in fits_keys:
        log.error("Incomplete FITS keys for", repr(outname),  "parkeys =", repr(all_parkeys), "fitskeys = ", repr(fits_keys))
    return tuple(fits_keys)

def write_rmap(observatory, instrument, reftype, kind_map):
    """Constructs rmap's header and data out of the kind_map and
    outputs an rmap file
    """
    parkeys = KIND_KEYS[instrument][reftype]
    fitskeys = parkeys_to_fitskeys(instrument, parkeys)
    mapkeys = parkeys_to_fitskeys(instrument, MAPKEYS[:-1])
    rmap_header = OrderedDict([
        ("mapping", "reference"),
        ("observatory", observatory.upper()),
        ("instrument", instrument.upper()),
        ("reftype", reftype.upper()),
        ("parkey", (fitskeys, mapkeys))
    ])

    # Execute reftype specific customizations on header    
    rmap_header.update(HEADER_ADDITIONS.get((instrument, reftype), {}))
    
    matching_selections = dict()
    for key in sorted(kind_map):
        mappings = kind_map[key]
        useafter_selections = OrderedDict()
        for m in sorted(mappings):
            if m.date in useafter_selections:
                existing_file = useafter_selections[m.date]
                if m.file != existing_file:
                    log.warning("Useafter date collision in", repr(instrument), repr(reftype), repr(key),"at",repr(m.date),
                                repr(m.file), "replaces", repr(existing_file))
            useafter_selections[m.date] = m.file
        matching_selections[key] = selectors.UseAfterSelector(("DATE-OBS", "TIME-OBS"), useafter_selections)
    rmap_selector = selectors.MatchingSelector(fitskeys[:-2], matching_selections)
    outname = observatory + "_" + instrument + "_" + reftype + ".rmap"
    r = rmap.ReferenceMapping(outname, rmap_header, rmap_selector)
    r.write()

# ==========================================================================================

def test():
    import doctest, gen_file_rmap
    return doctest.testmod(gen_file_rmap)

# ==========================================================================================

def main():
    generate_all_rmaps(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    SAVE = "--save" in sys.argv
    if SAVE:
        sys.argv.remove("--save")
    lookup.load_header_cache()
    if "--profile" in sys.argv:
        sys.argv.remove("--profile")
        cProfile.run("main()")
    else:
        if "--verbose" in sys.argv:
            sys.argv.remove("--verbose")
            log.set_verbose(True)
        main()
    if SAVE:
        lookup.save_header_cache()
