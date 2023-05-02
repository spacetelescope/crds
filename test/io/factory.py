'''
This module defines top level functions for operating on files,  either related to
determining fundamental properties of a file (get_filetype, get_observatory) or
related to instantiating a specialized file handler object (file_factory) appropriate
for the given observatory and file format.
'''

import os

# ============================================================================

from astropy.io import fits as pyfits

# ============================================================================

# Defer these to avoid required heavy weight dependencies like "jwst" or "asdf"
# from crds.io import fits, json, yaml, geis, asdf, jwstdm

# ============================================================================

from crds.core import config, utils, constants

# ============================================================================

def file_factory(filepath, original_name=None, observatory=None):
    """Based on parameters,  construct a file object of the appropriate
    class.  Unspecified parameters determined from `filepath` as possible.

    Where possible file extension will be used to determine file type.

    filepath        must be a viable path to an existing reference
    original_name   may be a more informative basename if filepath is a temp file
    observatory     "hst" or "jwst",  biases JWST to use datamodels vs. fits
    """
    filetype = get_filetype(filepath, original_name)
    if filetype == "asdf":
        from crds.io import asdf
        file_class = asdf.AsdfFile
    elif filetype == "json":
        from crds.io import json
        file_class = json.JsonFile
    elif filetype == "yaml":
        from crds.io import yaml
        file_class = yaml.YamlFile
    elif filetype == "geis":
        from crds.io import geis
        file_class = geis.GeisFile
    elif filetype == "fits":
        from crds.io import fits
        file_class = fits.FitsFile
    else:
        raise RuntimeError("Unknown file type for " + repr(filepath) )
    if observatory is None:
        observatory = get_observatory(filepath, original_name) # slow?
    return file_class(filepath, original_name, observatory)

# ----------------------------------------------------------------------------------------------

@utils.gc_collected
def get_observatory(filepath, original_name=None):
    """Return the observatory corresponding to `filepath`.  filepath
    may be a web temporary file with a garbage name.   Use
    `original_name` to make inferences based on file extension, or
    filepath if original_name is None.
    """
    if original_name is None:
        original_name = filepath
    for observatory in constants.ALL_OBSERVATORIES:
        if original_name.startswith(observatory + "_"):
            return observatory
    observatory = "hst"
    if original_name.endswith(".fits"):
        try:
            observatory = pyfits.getval(filepath, keyword="TELESCOP")
        except KeyError:
            pass
    elif original_name.endswith(".asdf"):
        try:
            import asdf
            with asdf.open(filepath) as handle:
                observatory = handle["meta"]["telescope"]
        except KeyError:
            pass
    elif original_name.endswith((".yaml", ".json", ".text", ".txt")):
        return "jwst"
    return observatory.lower()

# ----------------------------------------------------------------------------------------------

def get_filetype(filepath, original_name=None):
    """Determine file type from `original_name` if possible, otherwise attempt to
    idenitfy based on file contents.
    """
    if original_name is None:
        original_name = os.path.basename(filepath)

    # Fast extension-based type determination
    filetype = config.filetype(original_name)
    if filetype != "unknown":
        return filetype

    with open(filepath, "rb") as handle:
        first_5 = str(handle.read(5).decode('utf-8'))
        if first_5 == "#ASDF":
            return "asdf"
        elif first_5 == "SIMPL":
            first_81 = first_5 + handle.read(76).decode('utf-8')
            if first_81[-1] == '\n':
                all_chars = first_81 + handle.read().decode('utf-8')
                lines = all_chars.splitlines()
                lengths = { len(line) for line in lines }
                if len(lengths) == 1 and 80 in lengths:
                    return 'geis'
                else:
                    return 'fits'
            else:
                return "fits"

    try:
        with open(filepath) as handle:
            import json
            json.load(handle)
            return "json"
    except Exception:
        pass

    try:
        with open(filepath) as handle:
            import yaml
            yaml.safe_load(handle)
            return "yaml"
    except Exception:
        pass

    return "unknown"

# ----------------------------------------------------------------------------------------------

def is_dataset(name):
    """Returns True IFF `name` is plausible as a dataset.   Not a guarantee."""
    return config.filetype(name) in ["fits", "asdf", "geis"]
