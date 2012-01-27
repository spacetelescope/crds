"""This module extracts information about instruments, filekinds, filekind
relevance, and parkey relevance out of the CDBS configuration file
reference_file_defs.xml.
"""
import pprint
import os.path
import re

from BeautifulSoup import BeautifulStoneSoup

from crds import (log)

# =======================================================================

class Adjustment(object):
    """Describes mutations to parkeys and rows required by specific
    instrument reference filekinds.
    """
    def __init__(self, ignore=[], translate={}):
        self.ignore = ignore
        self.translate = translate
        
    def adjust(self, parkeys):
        """Returned the reduced FITS and database versions of the parkeys list.
        Reduced FITS is missing ignored parkeys.  Database version includes
        parkey FITS to database field name translations.
        """
        fits, db = [], []
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
                                ccontents(rnode.file_selection_test))
                    elif rnode.name == "restriction":
                        relevant = simplify_restriction(
                            ccontents(rnode.restriction_test))
                adjustment = get_adjustment(instr, filekind)
                fits_parkeys, db_parkeys = adjustment.adjust(parkeys)
                rdefs[instr][filekind] = \
                    (reftype, tuple(fits_parkeys), tuple(db_parkeys), relevant, 
                     parkey_restrictions)
    return rdefs

HERE = os.path.dirname(__file__)
try:
    PARKEYS = eval(open(HERE + "/parkeys.dat").read())
except:
    PARKEYS = {}

# (aSource._keywords['DETECTOR'][0] != 'SBC')

def replace_asource(match):
    return match.group(1) + "header" + match.group(2) + match.group(3)

def _simplify_restriction(restriction_text):
    return re.sub(r"(.*)asource._keywords\['(.*)'\]\[0\](.*)", 
                  r"\1\2\3",
                  restriction_text)

def simplify_restriction(restriction_text):
    """Transform file_selection_tests and restrictions to simple expressions of
    'header' values.
    """
    test = restriction_text
    for i in range(10):
        test = _simplify_restriction(test)
    val = test.replace("'", '"')
    if val[0] == "(" and val[-1] == ")":
        val = val[1:-1]
    return val

# note:  fits_parkeys and db_parkeys need to be in the same order.

def get_reftype(instrument, filekind):
    return PARKEYS[instrument][filekind][0]

def get_fits_parkeys(instrument, filekind):
    return PARKEYS[instrument][filekind][1]

def get_db_parkeys(instrument, filekind):
    return PARKEYS[instrument][filekind][2]

def get_relevance(instrument, filekind):
    return PARKEYS[instrument][filekind][3]

def get_parkey_restrictions(instrument, filekind):
    return PARKEYS[instrument][filekind][4]

def get_instruments():
    return sorted(PARKEYS.keys())

def get_filekinds(instrument):
    return sorted(PARKEYS[instrument].keys())

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
    
    log.write("Writing parkeys.dat")
    PARKEYS = process_reference_file_defs()
    open("parkeys.dat","w+").write(pprint.pformat(PARKEYS))
    
    log.write("Writing filekind_ext.dat")
    map = generate_filekinds_map()
    open("filekind_ext.dat","w+").write(pprint.pformat(map))

if __name__ == "__main__":
    main()
