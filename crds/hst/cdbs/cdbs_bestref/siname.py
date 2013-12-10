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
#
#========================================================================
import string
import opusutil
import instReferenceFileDefs
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
   if (string.lower(dataset[0]) == 'j'):
      return("ACS")
   elif (string.lower(dataset[0]) == 'o'):
      return("STIS")
   elif (string.lower(dataset[0]) == 'n'):
      return("NICMOS")
   elif (string.lower(dataset[0]) == 'u'):
      return("WFPC2")
   elif (string.lower(dataset[0]) == 'i'):
      return("WFC3")
   elif (string.lower(dataset[0]) == 'l'):
      return("COS")
   else:
      opusutil.PrintMsg("E",
                        "ERROR: unable to determine instrument for "+dataset)
      raise UnknownInstrument

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
      opusutil.PrintMsg("E","Unknown IRAF prefix for instrument "+
                        instrument_name)
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
      opusutil.PrintMsg("W","Unknown ref_data prefix for instrument "+
                        instrument_name)
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
    if (instrument_name == "ACS"):
      return "acs"
    elif (instrument_name == "STIS"):
      return "stis"
    elif (instrument_name == "NICMOS"):
      return "nic"
    elif (instrument_name == "WFPC2"):
      return "wfpc2"
    elif (instrument_name == "WFC3"):
      return "wfc3"
    elif (instrument_name == "COS"):
      return "cos"
    elif (instrument_name == "SYNPHOT" or instrument_name == "MULTI"):
      return "synphot"
    else:
      opusutil.PrintMsg("E","Unknown cdbs prefix for instrument "+ 
                        instrument_name)
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
   if (pos > 0 and 
       (string.lower(parts[pos]) == "syn" or
        string.lower(parts[pos]) == "th")):
      return("SYNPHOT")
   pos += 1
   if (pos > 0 and 
       (string.lower(parts[pos]) == "syn" or
        string.lower(parts[pos]) == "th")):
      return("SYNPHOT")

   # test the last character of the first piece
   if (string.lower(parts[0][-1:]) == 'j'):
      return("ACS")
   elif (string.lower(parts[0][-1:]) == 'o'):
      return("STIS")
   elif (string.lower(parts[0][-1:]) == 'n'):
      return("NICMOS")
   elif (string.lower(parts[0][-1:]) == 'u'):
      return("WFPC2")
   elif (string.lower(parts[0][-1:]) == 'i'):
      return("WFC3")
   elif (string.lower(parts[0][-1:]) == 'l'):
      return("COS")
   elif (string.lower(parts[0][-1:]) == 'm'):
      return("MULTI")
   else:
      opusutil.PrintMsg("E","Unable to determine instrument for "+
                         str(parts))
      raise UnknownInstrument

#========================================================================
# TEST 
# % python siname.py
#========================================================================
if __name__ == "__main__":
  print WhichInstrument("j8c103010")
  the_master = instReferenceFileDefs.InstReferenceFileDefs()
  instrument = instReferenceFileDefs.InstReferenceFiles("ACS")
  reffile = instReferenceFileDefs.Reffile("FLS","FLSHFILE","IMAGE")
  print add_IRAF_prefix("ACS")
  print get_ref_data_prefix("ACS")
  print get_cdbs_prefix("ACS")
