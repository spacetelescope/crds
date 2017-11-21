'''
Created on Feb 15, 2017

@author: jmiller
'''
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

# from jwst import datamodels

from astropy.io import fits as pyfits

# ============================================================================

from crds.core import config, log, utils

from .abstract import hijack_warnings
from .fits import FitsFile
# ============================================================================

def sanitize_data_model_dict(flat_dict):
    """Given data model keyword dict `d`,  sanitize the keys and values to
    strings, upper case the keys,  and add fake keys for FITS keywords.
    """
    flat_dict = dict(flat_dict)

    # Reformat history paths so they sort correctly by using 0-filled sequence number.
    for key, val in sorted(flat_dict.items()):
        skey, sval = str(key).upper(), str(val)
        if skey.startswith("HISTORY") and skey.endswith("DESCRIPTION"):
            parts = skey.split(".")
            newkey = parts[0] + "%04d" % int(parts[1]) + parts[2]
            flat_dict[newkey] = flat_dict.pop(key)
        
    cleaned = {}
    history = []

    for key, val in sorted(flat_dict.items()):
        skey, sval = str(key).upper(), str(val)
        fits_magx = "EXTRA_FITS.PRIMARY.HEADER."
        if skey.startswith("HISTORY") and skey.endswith("DESCRIPTION"):
            history.append(sval)
            continue
        if skey.startswith(fits_magx):
            if key.endswith(".0"):
                skey = flat_dict[key].upper()
                sval = flat_dict[key[:-len(".0")] + ".1"]
        cleaned[skey] = sval
    if history:
        cleaned["HISTORY"] = "\n".join(history)
    # Hack for backward incompatible model naming change.
    if "META.INSTRUMENT.NAME" in cleaned:
        if "META.INSTRUMENT.TYPE" not in cleaned:
            cleaned["META.INSTRUMENT.TYPE"] = cleaned["META.INSTRUMENT.NAME"]
    return cleaned

# ================================================================================================================

class DataModelsFile(FitsFile):
    
    format = "JWSTDM"
    
    @hijack_warnings
    @utils.gc_collected
    def setval(self, key, value):
        """Set metadata `key` in file `filepath` to `value`."""
        ftype = config.filetype(self.filepath)
        if ftype == "fits":
            if key.upper().startswith(("META.","META_")):
                key = key.replace("META_", "META.")
                return self._setval(key, value)
            else:
                return pyfits.setval(self.filepath, key, value=value)
        elif ftype == "asdf":
            return self._setval(key, value)
        else:
            raise NotImplementedError("setval not supported for type " + repr(ftype))

    def _setval(self, key, value):
        """Set metadata `key` in file `filepath` to `value` using jwst datamodel."""
        from jwst import datamodels
        with datamodels.open(self.filepath) as d_model:
            d_model[key.lower()] = value
            d_model.save(self.filepath)
            
    # ----------------------------------------------------------------------------------------------

    def get_raw_header(self, needed_keys=(), **keys):
        """Get the header from `filepath` using the jwst data model."""
        flat_dict = self.get_data_model_flat_dict(needed_keys)
        header = sanitize_data_model_dict(flat_dict)
        return header
    
    def get_data_model_flat_dict(self, needed_keys=()):
        """Get the header from `filepath` using the jwst data model."""
        from jwst import datamodels
        with log.augment_exception("JWST Data Model (jwst.datamodels)"):
            with datamodels.open(self.filepath) as d_model:
                flat_dict = d_model.to_flat_dict(include_arrays=False)
        return flat_dict

'''
from jwst import datamodels
def dm_leak(filepath):
    """Memory leak demo/test/debug function."""
    # with log.augment_exception("JWST Data Model (jwst.datamodels)"):
    d_model = datamodels.open(filepath)
    flat_dict = d_model.to_flat_dict(include_arrays=False)
    d_model.close()
    del d_model
    return dict(flat_dict)
'''


