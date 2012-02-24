from crds import log, utils

# ===========================================================================    

ACS_HALF_CHIP_COLS = 2048         #used in custom bias selection algorithm

SM4 = "2009-05-14 00:00"  # date beyond which an exposure was
                          # taken in the SM4 configuration
                          # (day 2009.134 = May 14 2009,
                          #  after HST was captured by 
                          #  the shuttle during SM4, and
                          #  pre-SM4 exposures had ceased)

def _precondition_header_biasfile(header_in):
    """Mutate the incoming dataset header based upon hard coded rules
    and the header's contents.   This is an alternative to generating
    an equivalent and bulkier rmap.
    """
    header = dict(header_in)
    
    try:
        numcols = float(header["NUMCOLS"])
    except ValueError:
        log.verbose("acs_biasfile_selection: bad NUMCOLS.")
    else:
        # if pre-SM4 and NUMCOLS > HALF_CHIP
        exptime = utils.condition_value(
            header["DATE-OBS"] + " " + header["TIME-OBS"])
        if (exptime < SM4) and numcols > ACS_HALF_CHIP_COLS:
            if header["CCDAMP"] in ["A","D"]: 
                log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp A or D "+
                            "to AD for NUMCOLS = "+ header["NUMCOLS"])
                header["CCDAMP"] = "AD"
            elif header["CCDAMP"] in ["B","C"]:  
                log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp B or C "+
                            "to AD for NUMCOLS = "+ header["NUMCOLS"])
                header["CCDAMP"] = "BC"

    if header['DETECTOR'] == "WFC" and \
        header['XCORNER'] == "0.0" and header['YCORNER'] == "0.0":
        log.verbose("acs_biasfile_selection: precondition_header halving NUMROWS")
        try:
            numrows = float(HEADER["NUMROWS"]) / 2
        except ValueError:
            log.verbose("acs_biasfile_selection: bad NUMROWS.")
            sys.exc_clear()
        else:
            header["NUMROWS"] = utils.condition_value(str(numrows)) 

    return header

def precondition_header(rmap, header):
    if rmap.filekind == "biasfile":
        return _precondition_header_biasfile(header)
    else:
        return header
    
# ===========================================================================    


def _fallback_biasfile(header_in):
    header = dict(header_in)
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
    if rmap.filekind == "biasfile":
        # log.write("x", eol="",sep="")
        return _fallback_biasfile(header)
    else:
        None

