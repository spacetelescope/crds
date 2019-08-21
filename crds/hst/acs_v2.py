"""Fixed September 2013 hooks for ACS (biasfile)

Replaced NUMROWS, NUMCOLS with NAXIS2, NAXIS1 everywhere.

Restored simple runtime fallback_header approach.

Added "hooks" to newly generated rmap headers provided acs_biasfile_filter is imported.

Simplified rmap generation process.
"""
import copy

from .acs_common import *

# ===========================================================================

def precondition_header_acs_biasfile_v2(rmap, header_in):
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
        naxis1 = int(float(header["NAXIS1"]))
    except ValueError:
        log.verbose("acs_biasfile_selection: bad NAXIS1.")
        # sys.exc_clear()
    else:
        header["NAXIS1"] = utils.condition_value(str(naxis1))
        # if pre-SM4 and NAXIS1 > HALF_CHIP
        exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
        if (exptime < SM4):
            if naxis1 > ACS_HALF_CHIP_COLS:
                if header["CCDAMP"] in ["A","D"]:
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp A or D " +
                                "to AD for NAXIS1 = " + header["NAXIS1"])
                    header["CCDAMP"] = "AD"
                elif header["CCDAMP"] in ["B","C"]:
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp B or C " +
                                "to BC for NAXIS1 = " + header["NAXIS1"])
                    header["CCDAMP"] = "BC"
    if header['DETECTOR'] == "WFC" and \
        header['XCORNER'] == "0.0" and header['YCORNER'] == "0.0":
        log.verbose("acs_biasfile_selection: precondition_header halving NAXIS2")
        try:
            naxis2 = int(float(header["NAXIS2"])) / 2
        except ValueError:
            log.verbose("acs_biasfile_selection: bad NAXIS2.")
            # sys.exc_clear()
        else:
            header["NAXIS2"] = utils.condition_value(str(naxis2))
    dump_mutations(header_in, header)
    return header

def dump_mutations(header1, header2):
    log.verbose("In header1 not header2:", set(dict(header1).items()) - set(dict(header2).items()))
    log.verbose("In header2 not header1:", set(dict(header2).items()) - set(dict(header1).items()))

# ===========================================================================

#   This section contains matching customizations.

BIASFILE_PARKEYS = ('DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NAXIS1', 'NAXIS2', 'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP')
# , ('DATE-OBS', 'TIME-OBS')),

def fallback_header_acs_biasfile_v2(rmap, header_in):
    """Mutates dataset header for 2nd try when primary match fails."""
    header = precondition_header_acs_biasfile_v2(rmap, header_in)
    log.verbose("No matching BIAS file found for",
               "NAXIS1=" + repr(header['NAXIS1']),
               "NAXIS2=" + repr(header['NAXIS2']),
               "LTV1=" + repr(header['LTV1']),
               "LTV2=" + repr(header['LTV2']))
    log.verbose("Trying full-frame default search")
    if header['DETECTOR'] == "WFC":
        header["NAXIS1"] = "4144.0"
        header["NAXIS2"] = "2068.0"
        header["LTV1"] = "24.0"
        header["LTV2"] = "0.0"
    else:
        header["NAXIS1"] = "1062.0"
        header["NAXIS2"] = "1044.0"
        header["LTV1"] = "19.0"
        if header['CCDAMP'] in ["C","D"]:
            header["LTV2"] = "0.0"
        else: # assuming HRC with CCDAMP = A or B
            header["LTV2"] = "20.0"
    return header

def acs_biasfile_filter(kmap_orig):
    """
    Post-SM4 APERTURE's of '' were all replaced and cannot match,  hence dropped at CRDS rmap generation time.
    """
    kmap = copy.deepcopy(kmap_orig)
    header_additions = {
        "hooks" : {
            "precondition_header" : "precondition_header_acs_biasfile_v2",
            "fallback_header" : "fallback_header_acs_biasfile_v2",
            },
        }
    for match in kmap_orig:
        header = dict(list(zip(BIASFILE_PARKEYS, match)))
        if header["APERTURE"] == "":
            for filemap in kmap_orig[match]:
                if filemap.date > SM4:
                    log.warning("Removing empty post-SM4 APERTURE for", repr(filemap))
                else:  # conceptually,  N/A.   To prevent conincidental stronger matches: *.
                    log.warning("Setting empty pre-SM4 APERTURE to 'N/A' for", repr(filemap))
                    new_match = match[0:3] + ("N/A",) + match[4:]
                    if new_match not in kmap:
                        kmap[new_match] = []
                    if filemap not in kmap[new_match]:
                        kmap[new_match].append(filemap)
                        kmap[new_match].sort()
                kmap[match].remove(filemap)
            if not kmap[match]:
                log.warning("Removing empty match", repr(match))
                del kmap[match]
    return kmap, header_additions

def acs_darkfile_filter(kmap_orig):
    """
    Post-SM4 APERTURE's of '' were all replaced and cannot match,  hence dropped at CRDS rmap generation time.
    """
    kmap = copy.deepcopy(kmap_orig)
    header_additions = {}
    for match in kmap_orig:
        header = dict(list(zip(BIASFILE_PARKEYS, match)))
        try:
            if float(header["CCDGAIN"]) == -999.0:
                log.warning("CCDGAIN=-999.0 Deleting match", match, "with", kmap[match])
                del kmap[match]
        except Exception:
            pass
    return kmap, header_additions
