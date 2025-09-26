"""Precondition hooks are called after the parameters have already been reduced to required parkeys by minimize_header function. Therefore hooks are only useful for mutating the header *values* of required parkeys. By the time the hook is called, any header keys that are not part of the required parkey list have been excluded, and any req'd parkeys that were missing values have been set to "Undefined". This hook is being kept purely for documentation purposes - the L3-L2 conversions instead happen inside roman.locate.dataset_level_conversions()
"""
from crds.core import log
from astropy.time import Time 

def precondition_header_wfi_epsf_v1(rmap, header_in):
    """Preconditions Level 3 EPSF data model header time specification by replacing MJD Mean Time keyword with standard META.EXPOSURE.START_TIME used by Level 2 files."""
    header = dict(header_in)
    l2_key = 'ROMAN.META.EXPOSURE.START_TIME'
    dtstring = header.get(l2_key)
    if not dtstring:
        l3_keys = ['ROMAN.META.BASIC.TIME_FIRST_MJD', 'ROMAN.META.BASIC.TIME_MEAN_MJD', 'ROMAN.META.COADD_INFO.TIME_MEAN']
        mjd = header.get(l3_keys[0], header.get(l3_keys[1], header.get(l3_keys[2])))
        if mjd:
            dtstring = Time(mjd, format="mjd").isot
            header['ROMAN.META.EXPOSURE.START_TIME'] = dtstring
            log.verbose(f"Replaced MJD L3 header keyword with CRDS equivalent {l2_key}")
        else:
            log.error("No available Useafter (time-based) relevant keywords found in header")
        # Additional conversions
        l2_l3_conversions = {
            'ROMAN.META.INSTRUMENT.NAME': 'ROMAN.META.BASIC.INSTRUMENT',
            'ROMAN.META.INSTRUMENT.OPTICAL_ELEMENT': 'ROMAN.META.BASIC.OPTICAL_ELEMENT',
            'ROMAN.META.INSTRUMENT.DETECTOR': 'ROMAN.META.INSTRUMENT.DETECTOR' # force default to N/A
        }
        for k, v in l2_l3_conversions.items():
            if not header.get(k):
                header[k] = header.get(v, 'N/A')
        log.verbose(f"Preconditioned header: {header}")
    return header

def wfi_epsf_filter(rmap):
    """Adds precondition_header() hook to rmap header"""
    header_additions = {
        "hooks": {
            "precondition_header": "precondition_header_wfi_epsf_v1"
        }
    }
    return rmap, header_additions