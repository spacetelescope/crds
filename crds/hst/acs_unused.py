"""This module defines UNUSED CRDS customizations for the HST ACS instrument.

This module switches emphasis from match-time preconditioning + fallback to
rmap generation + rmap update.   The theoretical advantage is that the resulting
rmap is not subject to any hidden interpretations or hooks at match time.  In 
practice,  the code is quite intricate and difficult to understand,  and the
resulting rmap is also complex.

INCOMPLETE:  rmap updating believed not to work due to unexploded match values
which would need to be exploded,  filtered,  and then re-clustered.  rmap generation
working as well as v2 hooks,  matching all but 6 of ~2000 unique test cases.
"""

from .acs_common import *

# ===========================================================================    

BIASFILE_PARKEYS = ('DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NAXIS1', 'NAXIS2', 
                    'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP')

def _rmap_update_headers_acs_biasfile_v1(rmap, header_in):
    """Given a reference file header specifying the applicable cases for a reference,  this generates
    a weaker match case which may apply when the primary match fails.  Called to update rmaps
    with "fallback cases" when a file is submitted to the CRDS web site and it updates the rmap,
    in addition to the primary match cases from the unaltered header_in.  
    """
    header_in = dict(header_in)
    
    header_in["EXPTIME"] = timestamp.reformat_date(header_in["DATE-OBS"] + " " + header_in["TIME-OBS"])
    
    header = fix_naxis2(header_in)
    
    # 1. Simulate CDBS header pre-conditioning by mutating rmap and primary match
    if matches(header, EXPTIME=("<=", SM4)):    
        # First case has hacked APERTURE and CCDAMP for pre-sm4
        yield fix_aperture_ccdamp_pre_sm4(header)
        
        # Second case simulates behavior of pre-sm4 references with post-sm4 EXPTIME by jamming USEAFTER to SM4
        # and omitting the pre-SM4 EXPTIME hacks.
        header_2 = dict(header)
        header_2["EXPTIME"] = SM4
        yield header_2
    else:  # Standard post-SM4 file is unmodified except for NAXIS2
        if header["APERTURE"].strip():
            yield header

def rmap_update_headers_acs_biasfile_v1(rmap, header_in):
    # 2. Simulate full frame fallback search
    
    header = dict(header_in)
    for variant in _rmap_update_headers_acs_biasfile_v1(rmap, header):

        if variant is None:
            continue
        
        yield variant
        show_header_mutations(header_in, variant)
        
        fallback = compute_fallback_header(variant)
        if fallback is not None:
            show_header_mutations(header_in, fallback)
            yield fallback

def fix_aperture_ccdamp_pre_sm4(header_in):
    header = dict(header_in)
    log.info("Mapping pre-SM4 APERTURE to *", header)
    header["APERTURE"] = "*"
#    elif header["APERTURE"].strip() == "":
#        header["APERTURE"] = "N/A"
#        log.warning("rmap_update_headers_acs_biasfile_v1:  Changing APERTURE=='' to 'N/A'.")

    # Here, the inverse of jamming dataset CCDAMP=A to AD is match references of AD and make sure
    # they also match datasets A|D.   Also,  files which matched on A|D|B|C no longer do once they're mapped to AD BC.
    if matches(header_in, CCDAMP="AD"):
        header["NAXIS1"] = ">" + str(ACS_HALF_CHIP_COLS)
        header["CCDAMP"] = "A|AD|D"
    elif matches(header_in, CCDAMP="A"):
        header["NAXIS1"] = "<=" + str(ACS_HALF_CHIP_COLS)
    elif matches(header_in, CCDAMP="D"):
        header["NAXIS1"] = "<=" + str(ACS_HALF_CHIP_COLS)
    elif matches(header_in, CCDAMP="BC"):
        header["NAXIS1"] = ">" + str(ACS_HALF_CHIP_COLS)
        header["CCDAMP"] = "B|BC|C"
    elif matches(header_in, CCDAMP="B"):
        header["NAXIS1"] = "<=" + str(ACS_HALF_CHIP_COLS)
    elif matches(header_in, CCDAMP="C"):
        header["NAXIS1"] = "<=" + str(ACS_HALF_CHIP_COLS)
    return header
    
def fix_naxis2(header):
    # CDBS was written from the dataset perspective,  so it halved dataset naxis2 to match reference naxis2
    # This code is adjusting the reference file perspective,  so it doubles reference naxis2 to match dataset naxis2
    # This change only applies to the first attempt.
    header_1 = dict(header)
    if matches(header_1, DETECTOR="WFC", XCORNER="0.0", YCORNER="0.0"):
        with log.warn_on_exception("rmap_update_headers_acs_biasfile_v1: bad NAXIS2"):
            naxis2 = int(float(header_1["NAXIS2"]))
            header_1["NAXIS2"] = naxis2*2
    return header_1

def compute_fallback_header(header_in):
    # The inverse of jamming the dataset header with canned matching values is
    # jamming the reference header with N/A's for those variables.   Thus,  when
    # a dataset header appears with any value,   it is matched against N/A, and
    # works the same as if it had been jammed to a value matching the reference.
    # Since N/A is weighted lower than a true match,  it acts as a fall-back if a
    # real match is also present.
    header = dict(header_in)
    if matches(header, DETECTOR='WFC', NAXIS1='4144.0', NAXIS2='2068.0', LTV1='24.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='C', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='D', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='A', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='20.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='B', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='20.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    else:
        header = None
    return header


def matches(header, **keys):
    """Nominally check each element of **keys for equality with the same key in `header`.
    
    If a value in **keys is a tuple, it should be of the form (operator_str, value) and the
    expression will be evaluated with respect to `header`.
    """
    header = { key:utils.condition_value(val) for (key,val) in header.items() }
    for var, val in keys.items():
        if isinstance(val, tuple):
            op, val = val
        else:
            op = "=="
        val = utils.condition_value(val)
        if not evaluate(var + op + repr(val), header, var):
            return False
    return True

def evaluate(expr, header, var):
    """eval `expr` with respect to `var` in `header`."""
    rval = eval(expr, {}, header)  # hard coded expr
    log.info("evaluate:", repr(expr), "-->", rval, expr.replace(var, repr(header[var])))
    return rval

def dont_care(header, vars):
    """Set vars in header to N/A."""
    header = dict(header)
    for var in vars:
        header[var] = "N/A"
    return header

def show_header_mutations(header_in, header):
    """Print out keys which changed between header_in and header."""
    for key in header:
        if key in header_in:
            if header[key] != header_in[key]:
                log.info("mutating", repr(key), header_in[key], "-->", header[key])
        else:
            log.info("mutating", repr(key), "added as", header[key])
    for key in header_in:
        if key not in header:
            log.info("mutating", repr(key), "deleted as", header_in[key])

# =============================================================================================

# This section contains RMAP GENERATION code. It is unversioned, plugging into hst_gentools/gen_rmap.py and
# running only at rmap generation time during system bootstrap.  

def acs_biasfile_filter(kmap):
    """This is a plug-in for branches/hst_gentools/gen_rmap.py which mutates a "kmap" to produce
    a modified .rmap file when the .rmap is generated from the CDBS database.

    kmap is of the form 
    
        { match_tuple : [ Filemap, ... ] } 

    where Filemap is a named tuple containing reference_name, useafter, and comment.

    Returns  

         (modified_kmap,  header_additions)

    where header_additions is of the form

         [ (header_key, header_value), ... ]

    i.e. a list of .rmap header dictionary items.

    APERTURE was added late as a matching parameter and so many existing references
    have an APERTURE value of '' in CDBS.   Where it's relevant,  it's actually defined.
    Here we change '' to * to make CRDS ignore it when it doesn't matter.   We also change 
    APERTURE to * for any useafter date which precedes SM4 (possibly they define APERTURE).
    
    add_fallback_to_kmap() duplicates the correct filemaps to simulate the fallback header lookup.
    """
    start_files = total_files(kmap)
    
    kmap2 = defaultdict(set)
    for match, fmaps in kmap.items():
        header = dict(zip(BIASFILE_PARKEYS, match))
        for f in fmaps:
            header["DATE-OBS"], header["TIME-OBS"] = f.date.split()
            for alt in rmap_update_headers_acs_biasfile_v1(None, header):
                if alt is None:
                    continue
                if not alt["APERTURE"].strip():
                    log.warning("Dropping APERTURE='' for", repr(alt))
                    continue
                new_match = tuple(alt[key] for key in BIASFILE_PARKEYS)
                for flat_match in explode(new_match):
                    f2 = rmap.Filemap(alt["EXPTIME"], f.file, f.comment)
                    kmap2[flat_match].add(f2)

    kmap2 = { match:sorted(kmap2[match]) for match in kmap2 }
    
    log.verbose("Final ACS BIASFILE kmap:\n", log.PP(kmap2))
                                           
    header_additions = [
        ("hooks",  {
            "precondition_header" : "none",     # unplug original hook from now on
            "fallback_header" : "none",   # unplug original hook from now on
            "rmap_update_headers" : "rmap_update_headers_acs_biasfile_v1",
        }),
    ]

    dropped_files = start_files - total_files(kmap2)
    if dropped_files:  # bummer,  bug in my code...
        log.error("Dropped files:", sorted(dropped_files))

    return kmap2, header_additions

# =============================================================================================

def total_files(kmap):
    total = set()
    for match, fmaps in kmap.items():
        total = total.union(set([fmap.file for fmap in fmaps]))
    return total


def _explode(match):
    if not match:
        yield ()
    else:
        if isinstance(match[0], str):
            for part in match[0].split("|"):
                for remainder in _explode(match[1:]):
                    yield (utils.condition_value(part),) + remainder
        else:
            for remainder in _explode(match[1:]):
                yield (utils.condition_value(match[0]),) + remainder

def explode(match):
    return list(_explode(match))

