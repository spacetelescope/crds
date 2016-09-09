"""This module implements a get_data_level(reftype) function that returns the
first processing level at which the requested reftype is used.
"""
import json

import crds

def get_data_level(
    reftype, context=None, calibration_version=None, observatory="jwst", ignore_cache=False):
    """Based on `context` and `calibration_version` (nominally CAL_VER), return the
    minimum data level associated with reference type `reftype`.  Nominally
    this means fetching and interpreting the SYSTEM DATALVL reference file so
    utilizing this function requires operating in an environment with an
    up-to-date and accessible CRDS cache.
    """
    header = {
        "INSTRUMENT":"SYSTEM",
        "META.CALIBRATION_SOFTWARE_VERSION":calibration_version,
        }
    header.update(extras or {})
    bestrefs = crds.getreferences(
        header, reftypes=["datalvl"], observatory=observatory, ignore_cache=False)
    reference_path = bestrefs["datalvl"]
    type_to_level = get_type_to_level(reference_path)
    return type_to_level[reftype]

def get_type_to_level(refpath):
    """Given SYSTEM DATALVL reference file path `refpath`,  load it,
    and return the type_to_level mapping implied by the cal_levels field.
    """
    loaded = json.load(open(reference_path))
    return invert_cal_levels(loaded["cal_levels"])

def invert_cal_levels(cal_levels):
    """Invert and return the cal_levels mapping.
    
    >>> cal_levels = {
    ...    "2A": [ 
    ...        "dark",
    ...        "gain",
    ...        "ipc",
    ...    ],
    ...    "2B": [
    ...        "area",
    ...        "camera",
    ...        "collimator",
    ...    ],
    ...    "3": [
    ...        "distortion",
    ...        "drizpars",
    ...    ]
    ... }

    >>> inverted = invert_cal_levels(cal_levels)
    >>> sorted(inverted.items())
    [('area', '2B'), ('camera', '2B'), ('collimator', '2B'), ('dark', '2A'), ('distortion', '3'), ('drizpars', '3'), ('gain', '2A'), ('ipc', '2A')]

    >>> broken_levels = {
    ...    "1A" : [ "distortion"],
    ...    "2A" : [ "distortion"],
    ...    }
    >>> invert_cal_levels(broken_levels)
    Traceback (most recent call last):
    ...
    AssertionError: Invalid SYSTEM DATALVL reference.  type 'distortion' appears more than once.
    """
    type_to_level = dict()
    for level in cal_levels:
        for type in cal_levels[level]:
            assert type not in type_to_level, \
                "Invalid SYSTEM DATALVL reference.  type " + \
                repr(type) + " appears more than once."
            type_to_level[type] = level
    return type_to_level

def test():
    import doctest
    from crds import datalvl
    doctest.testmod(datalvl)

