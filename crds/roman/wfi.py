"""The epsf reftype will be used for both Level 2 (ImageModel, RampModel) and Level 3 (MosaicModel) data. For level 2, the keyword for the time specification is META.EXPOSURE.START_TIME. For Level 3 the keyword is META.BASIC.TIME_MEAN_MJD.

There is no apparent way in the rmaps themselves to equivalence two different source keywords to the same parkey matching parameter. Assuming there is not, a different method will need to be used.

An option is to use the "precondition_header" feature. This allows arbitrary modifications of the input header prior to any selections. At this point, if META.EXPOSURE.START_TIME does not exist and META.BASIC.TIME_MEAN_MJD does, META.EXPOSURE.START_TIME can be created and assigned the value of META.BASIC.TIME_MEAN_MJD.
"""
from crds.core import log
from astropy.time import Time 

def precondition_header_wfi_epsf_v1(rmap, header_in):
    """Preconditions Level 3 EPSF data model header time specification by replacing MJD Mean Time keyword with standard META.EXPOSURE.START_TIME used by Level 2 files."""
    header = dict(header_in)
    l2_key = 'ROMAN.META.EXPOSURE.START_TIME'
    l3_keys = ['ROMAN.META.BASIC.TIME_FIRST_MJD', 'ROMAN.META.BASIC.TIME_MEAN_MJD', 'ROMAN.META.COADD_INFO.TIME_MEAN']
    dtstring = header.get(l2_key)
    if not dtstring:
        mjd = header.get(l3_keys[0], header.get(l3_keys[1], header.get(l3_keys[2])))
        if mjd:
            dtstring = Time(mjd, format="mjd").isot
            header['ROMAN.META.EXPOSURE.START_TIME'] = dtstring
            log.verbose(f"Replaced MJD L3 header keyword with CRDS equivalent {l2_key}")
        else:
            log.error("No available Useafter (time-based) relevant keywords found in header")
    instr_params = header.get('ROMAN.META.INSTRUMENT')
    if not instr_params:
        instr_params = dict(name=header.get('ROMAN.META.BASIC.INSTRUMENT'), detector='WFI02', optical_element=header.get('ROMAN.META.BASIC.OPTICAL_ELEMENT'))
        header['ROMAN.META.INSTRUMENT'] = instr_params
    return header

def wfi_epsf_filter(rmap):
    """Adds precondition_header() hook to rmap header"""
    header_additions = {
        "hooks": {
            "precondition_header": "precondition_header_wfi_epsf_v1"
        }
    }
    return rmap, header_additions