'''
Created on Feb 15, 2017

@author: jmiller
'''
import re

# ============================================================================

import contextlib
import uuid
import os
import io

from astropy.io import fits

import numpy as np

# ============================================================================

from crds.core import config, utils, log

from .abstract import AbstractFile, hijack_warnings

# ============================================================================

@hijack_warnings
def fits_open_trapped(filename, **keys):
    """Same as fits_open but with some astropy and JWST DM warnings hijacked by CRDS.
    This is predominantly an interface for crds.certify and nominally verifies
    checksums although technically they are driven by CRDS_FITS_VERIFY_CHECKSUM.
    """
    return fits_open(filename, **keys)

@contextlib.contextmanager
@utils.gc_collected
def fits_open(filename, **keys):
    """Return the results of io.fits.open() configured using CRDS environment
    settings, overridden by any conflicting keyword parameter values.
    Nominally used for updating bestrefs FITS headers.

    CRDS_FITS_VERIFY_CHECKSUM is used to enable/disable default checksum verification.
    CRDS_FITS_IGNORE_MISSING_END is used to enable/disable the missing FITS END check.
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

def get_fits_header_union(filepath, needed_keys=(), original_name=None, observatory=None, **keys):
    """Get the union of keywords from all header extensions of FITS
    file `fname`.  In the case of collisions, keep the first value
    found as extensions are loaded in numerical order.

    DOES NOT verify FITS checksums.
    """
    file_obj = FitsFile(filepath)
    header = file_obj.get_header(needed_keys, checksum=False)
    log.verbose("Header of", repr(filepath), "=", log.PP(header), verbosity=90)
    return header

# ============================================================================

class FitsFile(AbstractFile):

    format = "FITS"

    def get_info(self):
        """Capture the output from the fits info() function."""
        s = io.StringIO()
        fits.info(self.filepath, s)
        s.seek(0)
        info_string = "\n".join(s.read().splitlines()[1:])
        return info_string

    def _array_name_to_hdu_index(self, array_name):
        """Convert array names with extended notations into "index" values
        which can be used to select particular HDUs.

        The extended notations include specifying HDUs using an extension number
        pseudonym like this:

        # does next to nothing.
        >>> import os.path
        >>> path = os.path.abspath("tests/data/y951738kl_hv.fits")
        >>> fits_file = FitsFile(path)

         # doesn't require a real file or validate that it exists
        >>> fits_file._array_name_to_hdu_index("EXTENSION5")
        ('5', 5)

         # doesn't require a real file or validate that it exists
        >>> fits_file._array_name_to_hdu_index("EXT5")
        ('5', 5)

        or by name but referring to a particular "ver" like this:

        # info about file structure, real file required for this usecase
        finfo crds/tests/data/y951738kl_hv.fits
        -----------------------------------------------------
        Filename: crds/tests/data/y951738kl_hv.fits
        No.    Name      Ver    Type      Cards   Dimensions   Format
        0  PRIMARY       1 PrimaryHDU      22   ()
        1  FUVA          1 BinTableHDU     17   106R x 2C   [D, I]
        2  FUVB          1 BinTableHDU     17   127R x 2C   [D, I]

        # Actual test and expected results
        >>> fits_file._array_name_to_hdu_index("FUVB")
        ('FUVB', 2)

        """
        array_name = str(array_name)
        ext_match = re.match(r"(EXT(ENSION)?)?(\d+)", array_name)
        if ext_match:
            i = ext_match.group(3)
            return i, int(i)
        ver_match = re.match(r"(.*)__(\d+)", array_name)
        if ver_match:
            name, ver = ver_match.group(1), int(ver_match.group(2))
            return (name, ver), self._extension_number((name, ver))
        return array_name, self._extension_number(array_name)

    def _extension_number(self, index):
        """Converts an HDU `index` value returned by _array_name_to_hdu_index() or HD
        name (implicit ver 1) into a FITS HDU number.
        """
        with fits_open(self.filepath) as hdus:
            for i, hdu in enumerate(hdus):
                if isinstance(index, str):
                    if hdu.name == index:
                        return i
                elif isinstance(index, tuple):
                    if hdu.name == index[0] and hdu.ver == index[1]:
                        return i
                else:
                    raise ValueError(
                        "Unrecognized HDU index format: " + str(index))
            raise ValueError("Can't find HDU: " + str(index))

    def get_array(self, array_name):
        """Return the `name`d array data from `filepath`,  alternately indexed
        by `extension` number.
        """
        index = self._array_name_to_hdu_index(array_name)
        with fits_open(self.filepath) as hdus:
            return hdus[index[1]].data

    def get_raw_header(self, needed_keys=(), **keys):
        """Get the union of keywords from all header extensions of FITS
        file `fname`.  In the case of collisions, keep the first value
        found as extensions are loaded in numerical order.
        """
        union = []
        with fits_open(self.filepath, **keys) as hdulist:
            for hdu in hdulist:
                for card in hdu.header.cards:
                    card.verify('fix')
                    key, value = card.keyword, str(card.value)
                    if not key:
                        continue
                    union.append((key, value))
        return union

    def get_array_properties(self, array_name, keytype="A"):
        """Return a Struct defining the properties of the FITS array in extension named `array_name`."""
        with fits_open(self.filepath) as hdulist:
            try:
                array_name = self._array_name_to_hdu_index(array_name)
                hdu = hdulist[array_name[1]]
            except Exception:
                return 'UNDEFINED'
            generic_class = {
                "IMAGEHDU" : "IMAGE",
                "BINTABLEHDU" : "TABLE",
            }.get(hdu.__class__.__name__.upper(), "UNKNOWN")
            if generic_class in ["IMAGE","UNKNOWN"]:
                typespec = hdu.data.dtype.name
                column_names = None
            else: # TABLE
                dtype = hdu.data.dtype
                typespec = {name.upper():str(dtype.fields[name][0]) for name in dtype.names}
                column_names = [name.upper() for name in hdu.data.dtype.names]
            return utils.Struct(
                        SHAPE = hdu.data.shape,
                        KIND = generic_class,
                        DATA_TYPE = typespec,
                        COLUMN_NAMES = column_names,
                        NAME = array_name[0],
                        EXTENSION = array_name[1],
                        DATA = hdu.data if (keytype == "D") else None
                    )

    # ----------------------------------------------------------------------------------------------

    def getval(self, key):
        """FITS version of getval() with checksum=False added."""
        return super(FitsFile, self).getval(key, checksum=False)

    def setval(self, key, value):
        """FITS version of setval() method."""
        fits.setval(self.filepath, key, value=value)

    @hijack_warnings
    def add_checksum(self):
        """Add checksums to `filepath`."""
        output = "crds-" + str(uuid.uuid4()) + ".fits"
        with fits_open(self.filepath, do_not_scale_image_data=True) as hdus:
            for hdu in hdus:
                data = hdu.data if hdu.data is not None else np.array([])
                fits.append(output, data, hdu.header, checksum=True)
        os.remove(self.filepath)
        os.rename(output, self.filepath)

    @hijack_warnings
    def remove_checksum(self):
        """Remove checksums from `filepath`."""
        output = "crds-" + str(uuid.uuid4()) + ".fits"
        with fits_open(self.filepath, checksum=False, do_not_scale_image_data=True) as hdus:
            for hdu in hdus:
                hdu.header.pop("CHECKSUM",None)
                hdu.header.pop("DATASUM", None)
                data = hdu.data if hdu.data is not None else np.array([])
                fits.append(output, data, hdu.header, checksum=False)
        os.remove(self.filepath)
        os.rename(output, self.filepath)

    @hijack_warnings
    def verify_checksum(self):
        """Verify checksums in `filepath`."""
        with fits.open(self.filepath, do_not_scale_image_data=True, checksum=True) as hdus:
            for hdu in hdus:
                hdu.verify("warn")

    def get_asdf_standard_version(self):
        """
        Return the ASDF Standard version associated with this file as a string,
        or `None` if the file is neither an ASDF file nor contains an embedded
        ASDF file.
        """
        with fits.open(self.filepath) as hdus:
            asdf_hdu = next((hdu for hdu in hdus if hdu.name == "ASDF"), None)
            if asdf_hdu is None:
                return None
            else:
                import asdf
                buff = io.BytesIO(asdf_hdu.data)
                with asdf.open(buff) as handle:
                    return str(handle.version)

def test():
    from crds.io import fits
    import doctest
    return doctest.testmod(fits)

if __name__ == "__main__":
    print(test())
