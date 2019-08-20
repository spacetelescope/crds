#========================================================================
#
# module: siname
#
# Routines for determining the science instrument name variations
# and abbreviations. Includes:
#
# WhichInstrument()
# add_IRAF_prefix()
# get_ref_data_prefix()
# get_cdbs_prefix()
#
# History
# -------
# 11/05/02 xxxxx MSwam    first version
# 10/23/03 49468 MSwam    activate COS,WFC3 in CDBS
# 10/22/12  Todd Miller   hacked into CRDS
#
#========================================================================
import re

# exceptions
class UnknownInstrument(Exception):
  pass

class UnknownIRAFPrefix(Exception):
  pass

class UnknownRefDataPrefix(Exception):
  pass

class UnsupportedCDBSInstrument(Exception):
  pass

class UnknownCDBSPrefix(Exception):
  pass

# global compiled regex for splitting filenames
filesplit = re.compile("[_\.]")

# post-SM2 instruments supported by CDBS
CDBS_supports = ("ACS","STIS","NICMOS","WFPC2","WFC3","COS")

def WhichInstrument(dataset):
   """
=======================================================================
Name: WhichInstrument

Description:
------------
Determines instrument name given a dataset name in IPPPSSOOT format by
looking at the first character of the dataset name.

Inputs:  dataset (I) - dataset name in IPPPSSOOT format
Returns: a capitalized instrument name (e.g. ACS)

Exceptions: UnknownInstrument is thrown if the instrument cannot be
            determined.
History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
   """
   try:
     return ID_CHAR_TO_INSTRUMENT[dataset[0].lower()]
   except:
     raise UnknownInstrument

ID_CHAR_TO_INSTRUMENT = {
  "j" : "ACS",
  "o": "STIS",
  "n": "NICMOS",
  "u": "WFPC2",
  "i": "WFC3",
  "l": "COS",
  "m" : "SYNPHOT",
  }

INSTRUMENT_TO_ID_CHAR = {
  val: key for (key, val) in ID_CHAR_TO_INSTRUMENT.items()
}

def instrument_to_id_char(instrument):
  """Given an instrument name (e.g. acs) return the corresponding CDBS
  instrument id character.
  """
  return INSTRUMENT_TO_ID_CHAR[instrument.upper()]

def add_IRAF_prefix(instrument_name):
    """
=======================================================================
Name: add_IRAF_prefix

Description:
------------
Determines IRAF prefix for a reference file name,
depending on instrument and reffile format.

Inputs:
-------
instrument_name - name of the instrument (e.g. ACS)

Returns:
--------
an iraf directory prefix (e.g. jref$ )

Exceptions: UnknownIRAFPrefix is thrown if the instrument cannot be
            determined.
History:
--------
10/01/02 xxxxx MSwam     Initial version
06/11/03 46981 MSwam     Don't use "tab" directories - all are "ref"
04/12/04 48141 MSwam     Add MULTI, SYNPHOT
=======================================================================
   """
    if (instrument_name == "ACS"):
      iraf_prefix = "jref$"
    elif (instrument_name == "STIS"):
      iraf_prefix = "oref$"
    elif (instrument_name == "NICMOS"):
      iraf_prefix = "nref$"
    elif (instrument_name == "WFPC2"):
      iraf_prefix = "uref$"
    elif (instrument_name == "WFC3"):
      iraf_prefix = "iref$"
    elif (instrument_name == "COS"):
      iraf_prefix = "lref$"
    elif (instrument_name == "MULTI"):
      iraf_prefix = "mtab$"
    elif (instrument_name == "SYNPHOT"):
      iraf_prefix = "ttab$"
    else:
      raise UnknownIRAFPrefix
    #
    return iraf_prefix

def get_ref_data_prefix(instrument_name):
    """
=======================================================================
Name: get_ref_data_prefix

Description:
------------
Translate instrument name into archive database "*_ref_data" prefix.
This is the 3-character prefix that is part of every field name in the
"*_ref_data" table.  For example, in stis_ref_data all fields are
prefixed with "ssr".

Inputs:
-------
instrument_name - name of the instrument (e.g. ACS)

Returns:
--------
an archive database "*_ref_data" prefix (e.g. for stis = ssr)

Exceptions: UnknownRefDataPrefix is thrown if the instrument cannot be
            determined.
History:
--------
10/01/02 xxxxx MSwam     Initial version
01/31/05 51433 MSwam     Change message to warning, since MULTI processing
                         results in a message for SM4 SIs
11/01/07 56836 Sherbert  Add WF3 and COS now that tables exist
=======================================================================
   """
    if (instrument_name == "ACS"):
      return "acr"
    elif (instrument_name == "STIS"):
      return "ssr"
    elif (instrument_name == "NICMOS"):
      return "nsr"
    elif (instrument_name == "WFPC2"):
      return "w2r"
    elif (instrument_name == "COS"):
      return "csr"
    elif (instrument_name == "WFC3"):
      return "w3r"
    else:
      raise UnknownRefDataPrefix

def supported_by_CDBS(instrument_name):
  """
=======================================================================
Name: supported_by_CDBS

Description:
------------
Throws an exception if the specified instrument is not yet supported
by CDBS.  The global string "CDBS_supports" contains the list of
instruments supported by CDBS.

Inputs:
-------
instrument_name - name of the instrument (e.g. ACS)

Exceptions: UnsupportedCDBSInstrument is raised if the instrument is
            not yet supported.
History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
  """
  if not instrument_name in CDBS_supports:
    raise UnsupportedCDBSInstrument

def get_cdbs_prefix(instrument_name):
    """
=======================================================================
Name: get_cdbs_prefix

Description:
------------
Translate instrument name into CDBS database file and row table prefix.
Each HST instrument has two tables in CDBS, one for file-level info
(*_file) and one for row-level info (*_row).  Each has a prefix
indicating the instrument name (e.g. acs_row).

Inputs:
-------
instrument_name - name of the instrument (e.g. ACS)

Returns:
--------
the CDBS *_file and *_row table prefix for the instrument (e.g. acs)

Exceptions: UnknownCDBSPrefix is thrown if the instrument cannot be
            determined.
History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
   """
    if instrument_name in CDBS_supports:
      return instrument_name.lower()
    elif (instrument_name == "SYNPHOT" or instrument_name == "MULTI"):
      return "synphot"
    else:
      raise UnknownCDBSPrefix

def WhichCDBSInstrument(reffilename):
   """
=======================================================================
Name: WhichCDBSInstrument

Description:
------------
Determines instrument name given a reference file name in CDBS format by
looking at the last character of the name, before the first
underscore.

Inputs:  reffilename (I) - dataset name in CDBS format
Returns: a capitalized instrument name (e.g. ACS)

NOTE: The reffilename can be the full FITS filename, or just the
      part of the filename included in the catalog entry.

Exceptions: UnknownInstrument is thrown if the instrument cannot be
            determined.
History:
--------
10/01/02 xxxxx MSwam     Initial version
05/03/05 51433 MSwam     Tweak syn test to work for catalog entries too
05/14/08 59478 MSwam     Add th (thermal) synphot type as well
=======================================================================
   """
   # split the filename into pieces on field delimiters
   parts = re.split(filesplit,reffilename)

   # first test for a synphot or thermal file (check the last two pieces)
   pos = len(parts) - 2
   if pos > 0 and parts[pos].lower() in ["syn", "th"]:
      return "SYNPHOT"
   pos += 1
   if pos > 0 and parts[pos].lower() in ["syn", "th"]:
      return "SYNPHOT"
   try:
     return ID_CHAR_TO_INSTRUMENT[parts[0][-1:].lower()]
   except:
      raise UnknownInstrument
