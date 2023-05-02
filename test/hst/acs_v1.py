"""Build-4 ACS hooks,  with modified for plug-in interface.

Apply to all ACS rmaps unless explicitly "un-hooked".

Dataset header preconditioning implemented as match-time operation.

Match fallbacks implemented as rmap-generation-time weaker matches,  single CRDS lookup.
"""
from .acs_common import *

def precondition_header_acs_biasfile_v1(rmap, header_in):
    """Mutate the incoming dataset header based upon hard coded rules
    and the header's contents.   This is an alternative to generating
    an equivalent and bulkier rmap.
    """
    header = dict(header_in)
    log.verbose("acs_biasfile_precondition_header:", log.format_parameter_list(header))
    exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
    if (exptime < SM4):
        #if "APERTURE" not in header or header["APERTURE"] == "UNDEFINED":
        log.verbose("Mapping pre-SM4 APERTURE to N/A")
        header["APERTURE"] = "N/A"
    try:
        numcols = int(float(header["NUMCOLS"]))
    except ValueError:
        log.verbose("acs_biasfile_selection: bad NUMCOLS.")
        # sys.exc_clear()
    else:
        header["NUMCOLS"] = utils.condition_value(str(numcols))
        # if pre-SM4 and NUMCOLS > HALF_CHIP
        exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
        if (exptime < SM4):
            if numcols > ACS_HALF_CHIP_COLS:
                if header["CCDAMP"] in ["A","D"]:
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp A or D " +
                                "to AD for NUMCOLS = " + header["NUMCOLS"])
                    header["CCDAMP"] = "AD"
                elif header["CCDAMP"] in ["B","C"]:
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp B or C " +
                                "to BC for NUMCOLS = " + header["NUMCOLS"])
                    header["CCDAMP"] = "BC"
    if header['DETECTOR'] == "WFC" and \
        header['XCORNER'] == "0.0" and header['YCORNER'] == "0.0":
        log.verbose("acs_biasfile_selection: precondition_header halving NUMROWS")
        try:
            numrows = int(float(header["NUMROWS"])) / 2
        except ValueError:
            log.verbose("acs_biasfile_selection: bad NUMROWS.")
            # sys.exc_clear()
        else:
            header["NUMROWS"] = utils.condition_value(str(numrows))
    return header     # XXXXXX RETURN NOW !!!!


# ===========================================================================

#   This section contains matching customizations.

# (('DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NUMCOLS', 'NUMROWS', 'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP'), ('DATE-OBS', 'TIME-OBS')),

"""
def _fallback_biasfile(header_in):
    header = _precondition_header_biasfile(header_in)
    log.verbose("No matching BIAS file found for",
               "NUMCOLS=" + repr(header['NUMCOLS']),
               "NUMROWS=" + repr(header['NUMROWS']),
               "LTV1=" + repr(header['LTV1']),
               "LTV2=" + repr(header['LTV2']))
    log.verbose("Trying full-frame default search")
    if header['DETECTOR'] == "WFC":
        header["NUMCOLS"] = "4144.0"
        header["NUMROWS"] = "2068.0"
        header["LTV1"] = "24.0"
        header["LTV2"] = "0.0"
    else:
        header["NUMCOLS"] = "1062.0"
        header["NUMROWS"] = "1044.0"
        header["LTV1"] = "19.0"
        if header['CCDAMP'] in ["C","D"]:
            header["LTV2"] = "0.0"
        else: # assuming HRC with CCDAMP = A or B
            header["LTV2"] = "20.0"
    return header

def fallback_header(rmap, header):
    return None
    if rmap.filekind == "biasfile":
        # log.info("x", end="",sep="")
        return _fallback_biasfile(header)
    else:
        None
"""

#  Originally this was code used to update the ACS BIASFILE rmap with a fallback case.

def rmap_update_headers_acs_biasfile_v1(rmap, header_in):
    header = _precondition_header_biasfile(header_in)

    if header_matches(header, dict(DETECTOR='WFC', NUMCOLS='4144.0', NUMROWS='2068.0', LTV1='24.0', LTV2='0.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    if header_matches(header, dict(DETECTOR='HRC', CCDAMP='C', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='0.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    if header_matches(header, dict(DETECTOR='HRC', CCDAMP='D', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='0.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    if header_matches(header, dict(DETECTOR='HRC', CCDAMP='C|D', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='0.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    if header_matches(header, dict(DETECTOR='HRC', CCDAMP='A', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='20.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    if header_matches(header, dict(DETECTOR='HRC', CCDAMP='B', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='20.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    if header_matches(header, dict(DETECTOR='HRC', CCDAMP='A|B', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='20.0')):
        return dont_care(header, ['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    return header

def header_matches(header, conditions):
    for var, val in conditions.items():
        if header[var] != val:
            return False
    return True

def dont_care(header, vars):
    header = dict(header)
    for var in vars:
        header[var] = "N/A"
    return header

# =============================================================================================

# This section contains rmap generation code.

header_additions = [   # dictionary items (ordered)
]

def acs_biasfile_filter(kmap):
    """APERTURE was added late as a matching parameter and so many existing references
    have an APERTURE value of '' in CDBS.   Where it's relevant,  it's actually defined.
    Here we change '' to * to make CRDS ignore it when it doesn't matter.   We also change
    APERTURE to * for any useafter date which precedes SM4 (possibly they define APERTURE).

    add_fallback_to_kmap() duplicates the correct filemaps to simulate the fallback header lookup.
    """
    replacement = "*"
    log.info("Hacking ACS biasfile  APERTURE macros.  Changing APERTURE='' to APERTURE='%s'" % replacement)
    start_files = total_files(kmap)
    for match, fmaps in kmap.items():
        new_key = na_key(match, replacement)
        if match[3] == '':
            if new_key not in kmap:
                kmap[new_key] = []
            kmap[new_key] = sorted(set(kmap[new_key] + fmaps))
            del kmap[match]
            for fmap in fmaps:
                log.info("Unconditionally mapping APERTURE '' to '%s' for" % replacement, fmap)
            continue
        remap_fmaps = []
        for fmap in fmaps[:]:
            if fmap.date < SM4:
                log.info("Remapping <SM4 APERTURE to '%s'" % replacement, repr(fmap))
                remap_fmaps.append(fmap)
                fmaps.remove(fmap)
        if remap_fmaps:
            if new_key not in kmap:
                kmap[new_key] = []
            kmap[new_key].extend(remap_fmaps)
            log.info("Moving", match, "to", new_key, "for files", total_files({None:remap_fmaps}))
            log.info("Remainder", match, "=", total_files({None:kmap[match]}))
            # log.info("New kmap for", repr(new_key), "is", repr(kmap[new_key]))
        if not fmaps and (new_key != match):
            del kmap[match]

    dropped_files = start_files - total_files(kmap)
    if dropped_files:  # bummer,  bug in my code...
        log.error("Dropped files:", sorted(dropped_files))

    kmap = add_fallback_to_kmap(kmap,
        matches=dict(DETECTOR='WFC', NUMCOLS='4144.0', NUMROWS='2068.0', LTV1='24.0', LTV2='0.0'),
        dont_care=['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    kmap = add_fallback_to_kmap(kmap,
        matches=dict(DETECTOR='HRC', CCDAMP='C', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='0.0'),
        dont_care=['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    kmap = add_fallback_to_kmap(kmap,
        matches=dict(DETECTOR='HRC', CCDAMP='D', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='0.0'),
        dont_care=['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    kmap = add_fallback_to_kmap(kmap,
        matches=dict(DETECTOR='HRC', CCDAMP='A', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='20.0'),
        dont_care=['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    kmap = add_fallback_to_kmap(kmap,
        matches=dict(DETECTOR='HRC', CCDAMP='B', NUMROWS='1044.0', NUMCOLS='1062.0', LTV1='19.0', LTV2='20.0'),
        dont_care=['NUMROWS','NUMCOLS','LTV1', 'LTV2'])

    return kmap, header_additions

#  An old example of hacking the kmap....
#     kmap[('UVIS', 'G280_AMPS', 1.5, 1.0, 1.0, 'G280-REF', 'T')] = \
#       [rmap.Filemap(date='1990-01-01 00:00:00', file='t6i1733ei_bia.fits',
#               comment='Placeholder file. All values set to zero.--------------------------, 12047, Jun 18 2009 05:36PM')]
#    return kmap, header_additions

def na_key(match, replacement='*'):
    """Replace APERTURE with N/A or *"""
    new = list(match)
    new[3] = replacement
    return tuple(new)

def total_files(kmap):
    total = set()
    for match, fmaps in kmap.items():
        total = total.union({fmap.file for fmap in fmaps})
    return total

def add_fallback_to_kmap(kmap, matches, dont_care,
    parkeys=('DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NUMCOLS', 'NUMROWS',
             'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP')):
    """Copy items in `kmap` whose keys match the parameters in `matches`,  setting
    the key-copy values named in `dont_care` to 'N/A'.   The copy with some 'N/A's is a fallback.
    `parkeys` names the items of each tuple key in `kmap`,  in order.
    """
    kmap = defaultdict(list, kmap.items())
    for key in kmap.keys():
        if key_matches(key, parkeys, matches):
            new_key = set_dont_care(key, parkeys, dont_care)
#            if new_key not in kmap:
#                kmap[new_key] = []
            kmap[new_key].extend(list(kmap[key]))
            kmap[new_key].sort()
            log.info("Creating fallback", repr(key), "-->", repr(new_key))
    return kmap

def key_matches(key, parkeys, matches):
    """Return True IFF `key` matches all the values in dict `matches`.
    Corresponding values in tuple `key` are named by values in `parkeys`.
    """
    for i, name in enumerate(parkeys):
        if name in matches:
            if utils.condition_value(matches[name]) != utils.condition_value(key[i]):
                log.verbose("Exiting on", repr(name),
                         utils.condition_value(matches[name]),
                         utils.condition_value(key[i]))
                return False
    log.verbose("Matching", repr(key))
    return True

def set_dont_care(key, parkeys, dont_care):
    """Set the values of `key` named in `dont_care` to 'N/A'."""
    key = list(key)
    for i, name in enumerate(parkeys):
        if name in dont_care:
            key[i] = 'N/A'
    return tuple(key)

# =============================================================================================
