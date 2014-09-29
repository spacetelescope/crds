"""This module defines limited facilities for reading and conditioning 
FITS and GEIS headers.

>>> is_geis("foo.r0h")
True
>>> is_geis("bar.fits")
False

>>> import cStringIO
>>> header = get_geis_header(cStringIO.StringIO(_GEIS_TEST_DATA))

>>> import pprint
>>> pprint.pprint(header)
{'ATODGAIN': '0.',
 'BITPIX': '16',
 'DATATYPE': 'INTEGER*2',
 'DESCRIP': 'STATIC MASK - INCLUDES CHARGE TRANSFER TRAPS',
 'FILETYPE': 'MSK',
 'FILTER1': '0',
 'FILTER2': '0',
 'FILTNAM1': '',
 'FILTNAM2': '',
 'GCOUNT': '4',
 'GROUPS': 'T',
 'HISTORY': ['This file was edited by Michael S. Wiggs, August 1995',
             '',
             'e2112084u.r0h was edited to include values of 256, which correspond'],
 'INSTRUME': 'WFPC2',
 'KSPOTS': 'OFF',
 'NAXIS': '1',
 'NAXIS1': '800',
 'PCOUNT': '38',
 'PDTYPE1': 'REAL*8',
 'PDTYPE2': 'REAL*8',
 'PEDIGREE': 'INFLIGHT 01/01/1994 - 15/05/1995',
 'PSIZE': '1760',
 'PSIZE1': '64',
 'PSIZE2': '64',
 'PTYPE1': 'CRVAL1',
 'PTYPE2': 'CRVAL2',
 'ROOTNAME': 'F8213081U',
 'SHUTTER': '',
 'SIMPLE': 'F',
 'UBAY3TMP': '0.',
 'UCH1CJTM': '0.',
 'UCH2CJTM': '0.',
 'UCH3CJTM': '0.',
 'UCH4CJTM': '0.'}
"""
import os.path
import re
import json

from crds import utils, log

from astropy.io import fits as pyfits

# =============================================================================

def get_filetype(name):
    """Identify file type based on filename,  not file contents.
    """
    if name.endswith(".fits"):
        return "fits"
    elif name.endswith(".finf"):
        return "finf"
    elif is_geis(name):
        return "geis"
    else:
        raise TypeError("Unknown file type for file named" + repr(name))

def is_dataset(name):
    """Returns True IFF `name` is plausible as a dataset.   Not a guarantee."""
    try:
        return isinstance(get_filetype(name), str)
    except Exception:
        return False

def get_observatory(filepath, original_name=None):
    """Return the observatory corresponding to `filepath`.  filepath
    may be a web temporary file with a garbage name.   Use 
    `original_name` to make inferences based on file extension, or
    filepath if original_name is None.
    """
    if original_name is None:
        original_name = filepath
    if "jwst" in original_name:
        return "jwst"
    if "hst" in original_name:
        return "hst"
    if original_name.endswith(".fits"):
        try:
            observatory = pyfits.getval(filepath, "TELESCOP")
        except Exception:
            observatory = "hst"
        return observatory.lower()
    elif original_name.endswith(".finf"):
        return "jwst"
    else:
        return "hst"

    
def getval(filepath, key, condition=True):
    """Return a single metadata value from `key` of file at `filepath`."""
    if condition:
        header = get_conditioned_header(filepath, needed_keys=[key])
    else:
        header = get_unconditioned_header(filepath, needed_keys=[key])
    return header[key]

def setval(filepath, key, value):
    """Set metadata `key` in file `filepath` to `value`."""
    ftype = get_filetype(filepath)
    if ftype == "fits":
        if key.upper().startswith("META."):
            return dm_setval(filepath, key, value)
        else:
            return pyfits.setval(filepath, key, value)
    elif ftype == "finf":
        return dm_setval(filepath, key, value)
    else:
        raise NotImplementedError("setval not supported for type " + repr(ftype))

@utils.capture_output 
def dm_setval(filepath, key, value):
    """Set metadata `key` in file `filepath` to `value` using jwst datamodel.
    """
    from jwst_lib import models
    with models.open(filepath) as dm:
        dm[key.lower()] = value
        dm.save(filepath)

def get_conditioned_header(filepath, needed_keys=(), original_name=None, observatory=None):
    """Return the complete conditioned header dictionary of a reference file,
    or optionally only the keys listed by `needed_keys`.
    
    `original_name`,  if specified,  is used to determine the type of the file
    and is not required to be readable,  whereas `filepath` must be readable
    and contain the desired header.
    """
    header = get_header(filepath, needed_keys, original_name, observatory=observatory)
    return utils.condition_header(header, needed_keys)

def get_header(filepath, needed_keys=(), original_name=None, observatory=None):
    """Return the complete unconditioned header dictionary of a reference file."""
    if original_name is None:
        original_name = os.path.basename(filepath)
    if is_geis(original_name):
        return get_geis_header(filepath, needed_keys)
    elif filepath.endswith(".json"):
        return get_json_header(filepath, needed_keys)
    elif filepath.endswith(".yaml"):
        return get_yaml_header(".yaml")
    else:
        if observatory is None:
            observatory = get_observatory(filepath, original_name)
        if observatory == "jwst":
            return get_data_model_header.suppressed(filepath, needed_keys)
        else:
            return get_fits_header_union(filepath, needed_keys)

# A clearer name
get_unconditioned_header = get_header

@utils.capture_output
def get_data_model_header(filepath, needed_keys=()):
    """Get the header from `filepath` using the jwst data model."""
    from jwst_lib import models
    with models.open(filepath) as dm:
        d = dm.to_flat_dict(include_arrays=False)
    d = sanitize_data_model_dict(d)
    header = reduce_header(filepath, d, needed_keys)
    return header

def get_json_header(filepath, needed_keys=()):
    """For now,  just treat the JSON as the header."""
    header = json.loads(open(filepath).read())
    return reduce_header(filepath, header, needed_keys)

def get_yaml_header(filepath, needed_keys=()):
    """For now,  just treat the YAML as the header."""
    import yaml
    header = yaml.loads(open(filepath).read())
    return reduce_header(filepath, header, needed_keys)

def reduce_header(filepath, old_header, needed_keys=()):
    """Limit `header` to `needed_keys`,  converting all keys to upper case
    and making note of any significant duplicates, and adding any missing
    `needed_keys` as UNDEFINED.
    
    To detect duplicates,  use an item list for `old_header`,  not a dict.
    """
    needed_keys = tuple(key.upper() for key in needed_keys)
    header = {}
    if isinstance(old_header, dict):
        old_header = old_header.items()
    for (key, value) in old_header:
        key = str(key.upper())
        value = str(value)
        if (not needed_keys) or key in needed_keys:
            if key in header and header[key] != value:
                log.verbose_warning("Duplicate key", repr(key), "in", repr(filepath),
                                    "using", repr(header[key]), "not", repr(value), verbosity=70)
                continue
            else:
                header[key] = value
                
    return ensure_keys_defined(header)

def ensure_keys_defined(header, needed_keys=(), define_as="UNDEFINED"):
    """Define any keywords from `needed_keys` which are missing in `header`,  or defined as 'UNDEFINED',
    as `default`.
    
    Normally this defines missing keys as UNDEFINED.
    
    It can be used to redefine UNDEFINED as something else,  like N/A.
    """
    header = dict(header)
    for key in needed_keys:
        if key not in header or header[key] == "UNDEFINED":
            header[key] = define_as
    return header

def sanitize_data_model_dict(d):
    """Given data model keyword dict `d`,  sanitize the keys and values to
    strings, upper case the keys,  and add fake keys for FITS keywords.
    """
    cleaned = {}
    for key, val in d.items():
        skey = str(key).upper()
        sval = str(val)
        fits_magx = "_EXTRA_FITS.PRIMARY."
        if key.upper().startswith(fits_magx):
            cleaned[skey[len(fits_magx):]] = sval
        cleaned[skey] = sval
    return cleaned

def get_fits_header(filepath, needed_keys=()):
    """Return `needed_keys` or all from FITS file `fname`s primary header."""
    primary_header = pyfits.getheader(filepath)
    return reduce_header(filepath, primary_header, needed_keys)

def get_fits_header_union(filepath, needed_keys=()):
    """Get the union of keywords from all header extensions of FITS
    file `fname`.  In the case of collisions, keep the first value
    found as extensions are loaded in numerical order.
    """
    union = []
    for hdu in pyfits.open(filepath):
        for card in hdu.header.cards:
            card.verify('fix')
            key, value = card.keyword, str(card.value)
            if not key:
                continue
            union.append((key, value))
    return reduce_header(filepath, union, needed_keys)


_GEIS_TEST_DATA = """
SIMPLE  =                    F /
                                                                              
BITPIX  =                   16 /                                                
DATATYPE= 'INTEGER*2'          /                                                
NAXIS   =                    1 /                                                
NAXIS1  =                  800 /                                                
GROUPS  =                    T /                                                
GCOUNT  =                    4 /                                                
PCOUNT  =                   38 /
PSIZE   =                 1760 /                                                
PTYPE1  = 'CRVAL1  '           /right ascension of reference pixel              
PDTYPE1 = 'REAL*8  '           /                                                
PSIZE1  =                   64 /                                                
PTYPE2  = 'CRVAL2  '           /declination of reference pixel                  
PDTYPE2 = 'REAL*8  '           /                                                
PSIZE2  =                   64 /                                                
                                                                                
                               / GROUP PARAMETERS: OSS                          
                                                                                
                                                                                
                               / GROUP PARAMETERS: PODPS                        
                                                                                                                                                                
INSTRUME= 'WFPC2   '           / instrument in use                              
ROOTNAME= 'F8213081U'          / rootname of the observation set                
FILETYPE= 'MSK     '           / shp, ext, edq, sdq, sci                        
                                                                                
                               / SCIENCE INSTRUMENT CONFIGURATION               
                                                                                
FILTNAM1= '        '           / first filter name                              
FILTNAM2= '        '           / second filter name                             
FILTER1 =                    0 / first filter number (0-48)                     
FILTER2 =                    0 / second filter number (0-48)                    
                                                                                
UCH1CJTM=                   0. / TEC cold junction #1 temperature (Celcius)     
UCH2CJTM=                   0. / TEC cold junction #2 temperature (Celcius)     
UCH3CJTM=                   0. / TEC cold junction #3 temperature (Celcius)     
UCH4CJTM=                   0. / TEC cold junction #4 temperature (Celcius)     
UBAY3TMP=                   0. / Bay 3 A1 temperature (Celcius)                 
KSPOTS  = 'OFF     '           / Status of Kelsall spot lamps: ON, OFF          
SHUTTER = '        '           / Shutter in place during preflash or IFLAT (A,B)
ATODGAIN=                   0. /                                                
                                                                                
                               / RSDP CONTROL KEYWORDS                          
                                                                                
PEDIGREE= 'INFLIGHT 01/01/1994 - 15/05/1995'                                    
DESCRIP = 'STATIC MASK - INCLUDES CHARGE TRANSFER TRAPS'                        
HISTORY This file was edited by Michael S. Wiggs, August 1995                   
HISTORY                                                                         
HISTORY e2112084u.r0h was edited to include values of 256, which correspond     
END                                                                             
"""

def is_geis(name):
    """Return True IFF `name` identifies a GEIS header file."""
    name = os.path.basename(name)
    return bool(re.match(r"r[0-9](h|d)", name[-3:]))

def is_geis_data(name):
    """Return True IFF `name` identifies a GEIS data file."""
    name = os.path.basename(name)
    return bool(re.match(r"r[0-9]d", name[-3:]))

def is_geis_header(name):
    """Return True IFF `name` identifies a GEIS data file."""
    name = os.path.basename(name)
    return bool(re.match(r"r[0-9]h", name[-3:]))

def get_geis_header(name, needed_keys=()):
    """Return the `needed_keys` from GEIS file at `name`."""

    if isinstance(name, basestring):
        if name.endswith("d"):
            name = name[:-1] + "h"
        lines = open(name)
    else:  # assume file-like object
        lines = name

    header = {}
    history = []

    for line in lines:

        # Drop comment
        if len(line) >= 32 and line[31] == "/":
            line = line[:31]
            
        if line.startswith("HISTORY"):
            history.append(line[len("HISTORY"):].strip())
            continue

        words = [x.strip() for x in line.split("=")]

        if len(words) < 2:
            continue
        
        key = words[0]
        
        # Skip over unneeded keys            
        if needed_keys and key not in needed_keys:
            continue
        
        # Recombine value / comment portion
        value = "=".join(words[1:])

        # Remove quotes from strings        
        value = value.strip()
        if value and value[0] == "'" and value[-1] == "'":
            value = value[1:-1].strip()

        # Assign value,  supporting list of values for HISTORY
        header[key] = value
        
    if not needed_keys or "HISTORY" in needed_keys:
        header["HISTORY"] = history
    
    return header

def get_conjugate(reference):
    """Return any file associated with `reference`,  nominally GEIS data from header,
    e.g.  'something.r3h' --> 'something.r3d'
    If there is no file associated with reference,  return None.
    """
    if is_geis_data(reference):
        return reference[:-1] + "h"
    elif is_geis_header(reference):
        return reference[:-1] + "d"
    return None

def test():
    """Run doctest on data_file module."""
    import doctest
    from . import data_file
    return doctest.testmod(data_file)

if __name__ == "__main__":
    print test()

