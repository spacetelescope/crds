'''
Created on Feb 15, 2017

@author: jmiller
'''
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

import contextlib
import ast

from astropy.io import fits

# ============================================================================

from crds.core import python23, config, utils, log, exceptions

from .abstract import AbstractFile, hijack_warnings

# ============================================================================

@contextlib.contextmanager
@utils.gc_collected
def fits_open(filename, **keys):
    """Return the results of io.fits.open() configured using CRDS environment settings,  overriden by
    any conflicting keyword parameter values.
    """
    keys = dict(keys)
    if "checksum" not in keys:
        keys["checksum"] = bool(config.FITS_VERIFY_CHECKSUM)
    if "ignore_missing_end" not in keys:
        keys["ignore_missing_end"] = bool(config.FITS_IGNORE_MISSING_END)
    handle = None
    try:
        handle = fits.open(filename, **keys)
        yield handle
    finally:
        if handle is not None:
            handle.close()

@hijack_warnings
def fits_open_trapped(filename, **keys):
    """Same as fits_open but with some astropy and JWST DM warnings hijacked by CRDS."""
    return fits_open(filename, **keys)

def get_fits_header_union(filepath, needed_keys=(), original_name=None, observatory=None):
    """Get the union of keywords from all header extensions of FITS
    file `fname`.  In the case of collisions, keep the first value
    found as extensions are loaded in numerical order.
    """
    file_obj = FitsFile(filepath)
    header = file_obj.get_header(needed_keys)
    log.verbose("Header of", repr(filepath), "=", log.PP(header), verbosity=90)
    return header

# ============================================================================

class FitsFile(AbstractFile):
    
    format = "FITS"

    def get_info(self):
        """Capture the output from the fits info() function."""
        s = python23.StringIO()
        fits.info(self.filepath, s)
        s.seek(0)
        info_string = "\n".join(s.read().splitlines()[1:])
        return info_string

    def get_array(self, array_name_or_ext):
        """Return the `name`d array data from `filepath`,  alternately indexed
        by `extension` number.
        """
        with fits_open(self.filepath) as hdus:
            return hdus[array_name_or_ext].data
            
    def get_raw_header(self, needed_keys=()):
        """Get the union of keywords from all header extensions of FITS
        file `fname`.  In the case of collisions, keep the first value
        found as extensions are loaded in numerical order.
        """
        union = []
        with fits_open(self.filepath) as hdulist:
            for hdu in hdulist:
                for card in hdu.header.cards:
                    card.verify('fix')
                    key, value = card.keyword, str(card.value)
                    if not key:
                        continue
                    union.append((key, value))
        return union

    def setval(self, key, value):
        fits.setval(self.filepath, key, value=value)

    def get_array_properties(self, array_name):
        """Return a Struct defining the properties of the FITS array in extension named `array_name`."""
        i, hdu = self._get_ith_named_hdu(array_name)
        summary = hdu._summary()  # XXX uses private _summary
        if len(summary) == 6:  # Image
            name, class_name, _header_len, shape, typespec, _unknown = summary
        else: # Table
            name, class_name, _header_len, shape, typespec = summary                    
        generic_class = {
            "IMAGEHDU" : "IMAGE",
            "BINTABLEHDU" : "TABLE", 
        }.get(class_name.upper(), "UNKNOWN")
        return utils.Struct( 
                    SHAPE = shape if generic_class == "IMAGE" else shape.replace(" ",""),
                    KIND = generic_class,
                    DATA_TYPE = typespec if generic_class == "IMAGE" else typespec.replace(" ","").replace(",",";"),
                    EXTENSION = i,
                )
    
    def _get_ith_named_hdu(self, array_name):
        """Return the extension numnber and HDU associated with `array_name`."""
        with fits_open(self.filepath) as hdulist:
            for (i, hdu) in enumerate(hdulist):
                if hdu.name == array_name:
                    return i, hdu
        raise exceptions.MissingArrayError("Array", repr(array_name), "not found in", repr(self.filepath))

