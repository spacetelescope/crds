"""This module extracts information about instruments, filekinds, filekind
relevance, parkeys, and parkey relevance out of the CDBS configuration file
reference_file_defs.xml.
"""
import pprint
import os.path
import re

from crds import (log, utils)

# =======================================================================

class Adjustment(object):
    """Describes mutations to parkeys and rows required by specific
    instrument reference filekinds.
    """
    def __init__(self, ignore=[], translate={}, extra=[]):
        self.ignore = ignore
        self.translate = translate
        self.extra = extra

    def adjust(self, parkeys):
        """Returned the reduced FITS and database versions of the parkeys list.
        Reduced FITS is missing ignored parkeys.  Database version includes
        parkey FITS to database field name translations.
        """
        fits, db = [], []
        parkeys = parkeys + self.extra
        for key in parkeys:
            if key not in self.ignore:
                fits.append(key)
            else:
                continue
            if key in self.translate:
                db.append(self.translate[key])
            else:
                db.append(key)
        return fits, db
          
ADJUSTMENTS = {
    "acs" : {
                "biasfile" : Adjustment(
                    ignore=["xcorner", "ycorner", "ccdchip"],
                    translate = { "numrows" : "naxis2", "numcols": "naxis1"}),
             },
    "wfpc2" : {
                "flatfile": Adjustment(
                    ignore=["imagetyp", "filtnam1", "filtnam2", "lrfwave"]
                    ),
               },
    "wfc3" : {
                "biasfile": Adjustment(
                    ignore=["subarray",],                 
                    ),
              },
    "cos" : {
                "spwcstab": Adjustment(
                    ignore=["exptype",],   # used in relevance, not matching, may be in db
                    extra=["exptype",],
                    ),
              },
}


NULL_ADJUSTMENT = Adjustment(ignore=[], translate={})

def get_adjustment(instrument, filekind):
    """Return the Adjustment object for `instrument` and `filekind`"""
    iadjust = ADJUSTMENTS.get(instrument, {})
    kadjust = iadjust.get(filekind, NULL_ADJUSTMENT)
    return kadjust

# =======================================================================

def ccontents(n): 
    """Return the lowercase stripped contents of a single values XML node"""
    return str(n.contents[0].strip().lower())

def process_reference_file_defs():
    """Process the CDBS config file reference_file_defs.xml and return a 
    dictionary mapping:  { insrtrument : { filekind :  (reftype, parkeys) } }
    where filekind is the name of a FITS header keyword which names a reference
    file, and parkeys is a list of dataset header keywords used to select the
    reference file.
    """
    from BeautifulSoup import BeautifulStoneSoup

    xml = BeautifulStoneSoup(
            open("cdbs/cdbs_bestref/reference_file_defs.xml").read())
    rdefs = {}
    for node in xml.findAll("instrument"):
        instr = ccontents(node.instrument_name)
        rdefs[instr] = {}
        for inode in node:
            if not hasattr(inode, "name"):
                continue
            if inode.name == "reffile":
                parkeys = []
                parkey_restrictions = {}
                relevant = "ALWAYS"
                reftype = ccontents(inode.reffile_type)
                filekind = ccontents(inode.reffile_keyword)
                for rnode in inode:
                    if not hasattr(rnode, "name"):
                        continue
                    if rnode.name == "file_selection":
                        parkey = ccontents(rnode.file_selection_field)
                        parkeys.append(parkey)
                        if rnode.file_selection_test is not None:
                            parkey_restrictions[parkey] = simplify_restriction(
                                ccontents(rnode.file_selection_test),
                                condition=True)
                    elif rnode.name == "restriction":
                        relevant = simplify_restriction(
                            ccontents(rnode.restriction_test),
                            condition=True)
                adjustment = get_adjustment(instr, filekind)
                fits_parkeys, db_parkeys = adjustment.adjust(parkeys)
                rdefs[instr][filekind] = dict(
                        reftype = reftype,
                        parkeys = tuple(fits_parkeys),
                        db_translations = adjustment.translate,
                        not_in_db = tuple(adjustment.ignore),
                        rmap_relevance = relevant,
                        parkey_relevance = parkey_restrictions,
                    )
    return rdefs

HERE = os.path.dirname(__file__) or "."
try:
    PARKEYS = eval(open(HERE + "/parkeys.dat").read())
except:
    PARKEYS = {}

FLOAT_RE = r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"

def _replace_syntax(match):
    return match.group(1) + match.group(2) + match.group(3)

def _replace_conditioned_float(match):
    unconditioned = match.group(2)
    number = utils.condition_value(unconditioned)
    return match.group(1) + repr(number) + match.group(4)

def _simplify_restriction(restriction_text):
    # simplify syntax
    # (aSource._keywords['DETECTOR'][0] != 'SBC')
    rval = re.sub(r"(.*)ASOURCE._KEYWORDS\['(.*)'\]\[0\](.*)", 
                  _replace_syntax,
                  restriction_text)
    rval = rval.upper()
    rval = rval.replace(" AND ", " and ")
    rval = rval.replace(" OR ", " or ")
    return rval

def _condition_numbers(restriction_text):
    # convert ints/floats to conditioned float strings
    rval = re.sub(r"(.*\s+)(" + FLOAT_RE + ")(.*)",
                  _replace_conditioned_float,
                  restriction_text)
    return rval

def simplify_restriction(restriction_text, condition):
    """Transform file_selection_tests and restrictions to simple expressions of
    'header' values.
    """
    test = restriction_text
    for i in range(10):
        test = _simplify_restriction(test)
    if condition:
        for i in range(10):
            test = _condition_numbers(test)
    val = test.replace("'", '"')
    return val

# =======================================================================

# note:  fits_parkeys and db_parkeys need to be in the same order.

# From another perspective,   I think fits_parkeys are the dataset version
# of a parameter,  and db_parkeys are the reference file version of a parameter
# which in general are the same...  except for ACS biasfile NUMROWS, NUMCOLS
# <-> BINAXIS1, BINAXIS2

def get_reftype(instrument, filekind):
    return PARKEYS[instrument][filekind]["reftype"]

def get_fits_parkeys(instrument, filekind):
    return PARKEYS[instrument][filekind]["parkeys"]

def get_db_parkeys(instrument, filekind):
    db_parkeys = []
    translations = PARKEYS[instrument][filekind]["db_translations"]
    for key in get_fits_parkeys(instrument, filekind):
        db_parkeys.append(translations.get(key, key))
    return tuple(db_parkeys)

def reference_keys_to_dataset_keys(instrument, filekind, header):
    """Given a header dictionary for a reference file,  map the header back to
    keys relevant to datasets.   So for ACS biasfile the reference says NAXIS1
    but the dataset says NUMCOLS.   This would convert { "NAXIS1": 1024 } to
    { "NUMCOLS" : 1024 }.
    
    In general,  rmap parkeys are matched against datset values and are defined
    as dataset header keywords.   For refactoring though,  what's initially
    available are reference file keywords...  which need to be mapped into the
    terms rmaps know:  dataset keywords.
    """
    inv_trans = utils.invert_dict(
        PARKEYS[instrument][filekind]["db_translations"])
    return { inv_trans.get(key.lower(), key).upper(): header[key] for key in header }

def get_rmap_relevance(instrument, filekind):
    return PARKEYS[instrument][filekind]["rmap_relevance"]

def get_parkey_relevance(instrument, filekind):
    return PARKEYS[instrument][filekind]["parkey_relevance"]

def get_instruments():
    return sorted(PARKEYS.keys())

def get_filekinds(instrument):
    return sorted(PARKEYS[instrument].keys())

def get_extra_keys(instrument, filekind):
    return PARKEYS[instrument][filekind]["not_in_db"]

def evaluate_parkey_relevance(instrument, filekind, rowdict):
    header = dict(rowdict)
    header2 = {key.upper(): utils.condition_value(val) for (key,val) in header.items()}
    relevance = get_parkey_relevance(instrument, filekind)
    for parkey, expr in relevance.items():
        try:
            if not eval(expr, header2, {}):
                log.verbose("parkey relevance", repr(expr), "mapping", 
                         parkey, "to N/A")
                header[parkey] = "N/A"
        except Exception, exc:
            log.verbose("ERROR parkey relevance", str(exc))
    return header

# =======================================================================

def generate_filekinds_map():
    map = {}
    for instrument in get_instruments():
        map[instrument] = {}
        for filekind in get_filekinds(instrument):
            map[instrument][filekind] = get_reftype(instrument, filekind)
    return map

# =======================================================================

def main():
    global PARKEYS
    
    log.info("Writing parkeys.dat")
    PARKEYS = process_reference_file_defs()
    open("parkeys.dat","w+").write(pprint.pformat(PARKEYS))
    
    log.info("Writing filekind_ext.dat")
    map = generate_filekinds_map()
    open("filekind_ext.dat","w+").write(pprint.pformat(map))

if __name__ == "__main__":
    main()
