"""This module defines limited facilities for extracting information from 
reference and datasets,  generally in the form of header dictionaries.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# =============================================================================

from crds.core  import utils, log

# =============================================================================

from crds.io.abstract import hijack_warnings, convert_to_eval_header, ensure_keys_defined
from crds.io.factory import file_factory, get_observatory, get_filetype, is_dataset
from crds.io.geis import is_geis, is_geis_data, is_geis_header, get_conjugate
from crds.io.fits import fits_open, fits_open_trapped, get_fits_header_union

# import asdf
# import yaml

# =============================================================================

def get_conditioned_header(filepath, needed_keys=(), original_name=None, observatory=None):
    """Return the complete conditioned header dictionary of a reference file,
    or optionally only the keys listed by `needed_keys`.

    `original_name`,  if specified,  is used to determine the type of the file
    and is not required to be readable,  whereas `filepath` must be readable
    and contain the desired header.
    """
    header = get_header(filepath, needed_keys, original_name, observatory=observatory)
    return utils.condition_header(header, needed_keys)

@hijack_warnings
def get_header(filepath, needed_keys=(), original_name=None, observatory=None):
    """Return the complete unconditioned header dictionary of a reference file.

    Hijack io.fits and data model warnings and map them to errors.

    Original name is used to determine file type for web upload temporary files which
    have no distinguishable extension.  Original name is browser-side name for file.
    """
    return get_free_header(filepath, needed_keys, original_name, observatory)

# A clearer name
get_unconditioned_header = get_header

@utils.cached
# @utils.gc_collected
def get_free_header(filepath, needed_keys=(), original_name=None, observatory=None):
    """Return the complete unconditioned header dictionary of a reference file.

    DOES NOT hijack warnings.

    Original name is used to determine file type for web upload temporary files
    which have no distinguishable extension.  Original name is browser-side
    name for file.

    get_free_header() is a cached function to prevent repeat file reads.  
    Although parameters are given default values,  for caching to work correctly
    even default parameters should be specified positionally.

    Since get_free_header() is cached,  loading file updates requires first
    clearing the function cache.
    """
    file_obj = file_factory(filepath, original_name, observatory)
    header = file_obj.get_header(needed_keys)
    log.verbose("Header of", repr(filepath), "=", log.PP(header), verbosity=90)
    return header

# ================================================================================================================

# @hijack_warnings
def getval(filepath, key, condition=True):
    """Return a single metadata value from `key` of file at `filepath`."""
    if condition:
        header = get_conditioned_header(filepath, (key,), None, None)
    else:
        header = get_unconditioned_header(filepath, (key,), None, None)
    return header[key]

@hijack_warnings
@utils.gc_collected
def setval(filepath, key, value):
    """Set metadata keyword `key` of `filepath` to `value`."""
    if key.upper().startswith(("META.","META_")):
        key = key.replace("META_", "META.")
    file_obj = file_factory(filepath)
    file_obj.setval(key, value)

# ================================================================================================================

def get_array_properties(filename, array_name, keytype="A"):
    """Return the dictionary defining basic properties of `array_name` of `filename`.
    
    Keytype == "A" for "array" means lightweight format only checks with no data included.
    Keytype == "D" for "data" means heavy data oriented checks with data arrays returned as well.
    """
    file_obj = file_factory(filename)
    props = file_obj.get_array_properties(array_name, keytype)
    return props

# ================================================================================================================

def test():
    """Run doctest on data_file module."""
    import doctest
    from crds import data_file
    return doctest.testmod(data_file)

if __name__ == "__main__":
    print(test())
