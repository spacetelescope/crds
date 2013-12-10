import string
import opusutil

class NoSuchInstrument(Exception):
  pass

class NoSuchReffile(Exception):
  pass

class InstReferenceFileDefs:
  """
=====================================================================
Class: InstReferenceFileDefs

Description:
------------
A master list of InstReferenceFiles objects.  The list is initially empty.
These objects define the reference files for a given instrument.

Members:
--------
._instruments     - the list of instrument objects

Methods:
--------
.append()         - add an InstReferenceFiles object to the master list
.find_instrument()- locate an InstReferenceFiles object in the master list by
                    instrument name
.dump()           - print the contents of the master list to stdout

History:
--------
10/01/02 xxxxx MSwam     first version
=====================================================================
  """
  # contains a list of Instruments
  #
  def __init__(self, instrument_name=""):
    #
    # the constructor
    self._instruments = []
    if (instrument_name):
      self.append(instrument_name)

  def append(self, instrument):
    self._instruments.append(instrument)

  def find_instrument(self, instrument_name):
    for i in self._instruments:
      if (instrument_name == i._name):
        return i
    raise NoSuchInstrument

  def dump(self):
    for i in self._instruments:
      i.dump()

class InstReferenceFiles:
  """
=====================================================================
Class: InstReferenceFiles

Description:
------------
A list of Reffile objects.  The list is initially empty.

Members:
--------
._name - name of the instrument
._missing_file - name to use for a ref file when it is missing (e.g.  N/A)
._reffiles - the list of Reffile objects
 
Methods:
--------
append() - add a Reffile object to the list
find_reffile() - locate a Reffile object in the list by reffile type
all_keywords() - returns the list of all keywords needed to compute
cdbs_keywords() - a list of only file_selection keywords for all ref files
set_missing_file() - sets the missing file value
reference files for an instrument
dump() - print the contents of the object to stdout

History:
--------
10/01/02 xxxxx MSwam     first version
10/15/04 51433 MSwam     add cdbs_keywords method
=====================================================================
  """
  # contains a list of Reffiles
  #
  def __init__(self, vname):
    self._name = vname
    # self._missing_file = " "  # default
    self._reffiles = []

  def append(self, reffile):
    self._reffiles.append(reffile)

  def set_missing_file(self, vmissing_file):
    # if the value = BLANK, set it to a single space
    if vmissing_file == "BLANK":
      self._missing_file= " "
    else:
      self._missing_file= vmissing_file

  def find_reffile(self, reffile_type):
    for i in self._reffiles:
      if (reffile_type == i._type):
        return i
    # not found by type, try by keyword
    for i in self._reffiles:
      if (reffile_type == i._keyword):
        return i
    raise NoSuchReffile

  # find all of the keywords used to determine this instrument's
  # reffiles, including reference file keywords, file selection
  # keywords and their restrictions, and general restrictions
  #
  def all_keywords(self):
    thelist = []
    for i in self._reffiles:
      i.all_keywords(thelist)
    return thelist

  # find all of the CDBS keywords used to determine this instrument's
  # reffiles, i.e. the file selection keywords but NO restrictions, 
  # since these are only for data sources
  #
  def cdbs_keywords(self):
    thelist = []
    for i in self._reffiles:
      i.cdbs_keywords(thelist)
    return thelist

  def dump(self):
    opusutil.PrintMsg("D",'inst:'+self._name)
    for i in self._reffiles:
      i.dump()

class Reffile:
  """
=====================================================================
Class: Reffile

Description:
------------
A reference file object, including file and row selection information,
as well as restrictions.

Members:
--------
._type - the type of reference file (e.g. DRK for a dark file)
._keyword - the name of the header keyword for this ref file (e.g.  DARKFILE)
._format - the ref file format (IMAGE or TABLE)
._restrictions - a Selection object indicating any restrictions for
                 applying this reference file
._function - a special function for determining the best reference file
._required - flag set if this ref file is required, as in MUST be filled
._switch - name of calibration switch corresponding to this ref file
._file_selections - a list of Selection objects for file selection
                    restrictions
._row_selections - a list of Selection objects for row selection
                   restrictions

Methods:
--------
get_restriction_keywords() - appends to a list any keywords used in
                             restriction criteria for this ref file
set_restrictions() - saves a restriction criteria for this ref file
set_function() - saves a special selection function for this ref file
set_required() - sets the required flag for this ref file
set_switch() - sets the calibration switch name for this ref file
all_file_selection_keywords() - appends to a list any keywords used in 
                            file selection and file restriction
                            criteria for this ref file
only_file_selection_keywords() - appends to a list only those keywords
                            directly used for file selection (leaves out
                            any restriction keywords)
cdbs_keywords() - a list of keywords used to select a reference file 
dump() - print the contents of the object to stdout

History:
--------
10/01/02 xxxxx MSwam     first version
10/15/04 51433 MSwam     replace file_selection_keywords with all_*,only_*
=====================================================================
  """
  def __init__(self, vtype, vkeyword, vformat, vrestrictions="", vfunction=""):
    #
    # the constructor
    self._type = vtype          # e.g. DRK
    self._keyword = vkeyword    # e.g. DARKFILE
    self._format = vformat      # e.g. IMAGE
    self._restrictions = vrestrictions
    self._function = vfunction
    self._required = None
    self._switch = None
    #
    # lists of File and Row selection criteria are optional
    #
    self._file_selections = []  
    self._row_selections = []

  def set_restrictions(self, vrestrictions):
    self._restrictions = vrestrictions

  def set_function(self, vfunction):
    self._function = vfunction

  def set_required(self, vrequired):
    self._required= vrequired

  def set_switch(self, vswitch):
    self._switch= vswitch

  # find all of the keywords used to determine this
  # reffile, including file and switch keywords, file selection
  # keywords and their restrictions, and general restrictions
  #
  def all_keywords(self, thelist):
    thelist.append(self._keyword)
    if self._switch:
      thelist.append(self._switch)
    self.all_file_selection_keywords(thelist)
    self.get_restriction_keywords(self._restrictions, thelist)

  # find all of the CDBS keywords used to determine this
  # reffile, i.e. the file selection keywords only
  #
  def cdbs_keywords(self, thelist):
    self.only_file_selection_keywords(thelist)

  # appends field names used in a restriction clause to a list
  # by parsing the clause
  #
  def get_restriction_keywords(self, restrictions, thelist):
    # find all keyword names in the restriction clause
    startpos = 0
    while 1:
      startpos = string.find(restrictions, "keywords['", startpos)
      if (startpos < 0):
        break
      startpos += 10
      endpos = string.find(restrictions, "'", startpos)
      opusutil.PrintMsg("D","get_restriction_keywords: adding "+
                        restrictions[startpos:endpos])
      thelist.append(restrictions[startpos:endpos])
      startpos = endpos

  # appends field names used in reference file selection or reference
  # file restriction clauses to a list
  #
  def all_file_selection_keywords(self, thelist):
    for fs in self._file_selections:
      thelist.append(fs._field)
      self.get_restriction_keywords(fs._restrictions, thelist)

  # appends field names used in reference file selection only
  # to a list (leaves out restrictions)
  #
  def only_file_selection_keywords(self, thelist):
    for fs in self._file_selections:
      thelist.append(fs._field)

  def dump(self):
    opusutil.PrintMsg("D","====>"+self._type+" "+self._keyword+" "+self._format)
    if self._restrictions:
      opusutil.PrintMsg("D","restr:"+self._restrictions)
    if self._function:
      opusutil.PrintMsg("D","funct:"+self._function)
    if self._required:
      opusutil.PrintMsg("D","REQUIRED")
    if self._switch:
      opusutil.PrintMsg("D","switch:"+self._switch)
    for fs in self._file_selections:
      fs.dump("fs:")
    for rs in self._row_selections:
      rs.dump("rs:")

class Selection:
  """
=====================================================================
Class: Selection

Description:
------------
A selection object, including the keyword name and optional restriction

Members:
--------
._field - a keyword to select on
._restrictions - a restriction clause applying to this keyword

Methods:
--------
dump() - print the contents of the object to stdout

History:
--------
10/01/02 xxxxx MSwam     first version
=====================================================================
  """
  def __init__(self, vfield, vrestrictions=""):
    #
    # the constructor
    self._field = vfield
    #
    # Selections can contain optional restriction criteria
    self._restrictions = vrestrictions

  def dump(self, prefix):
    if (self._restrictions):
      opusutil.PrintMsg("D",prefix+" "+self._field+" restr:"+self._restrictions)
    else:
      opusutil.PrintMsg("D",prefix+" "+self._field)

#========================================================================
# TEST 
# % python instReferenceFileDefs.py
#========================================================================
if __name__ == "__main__":
  master = InstReferenceFileDefs()
  instrument = InstReferenceFiles("ACS")

  reffile = Reffile("FLS","FLSHFILE","IMAGE")
  reffile._file_selections.append(Selection("DETECTOR"))
  reffile._file_selections.append(Selection("CCDAMP"))
  instrument.append(reffile)

  reffile = Reffile("IDC","IDCTAB","TABLE")
  reffile._file_selections.append(Selection("DETECTOR"))
  instrument.append(reffile)

  reffile = Reffile("BIA","BIASFILE","IMAGE",
                    "(keyword['DETECTOR'] != 'SBC')",
                    "acs_bia_subarray")
  reffile._file_selections.append(Selection("DETECTOR"))
  reffile._file_selections.append(Selection("CCDAMP"))
  reffile._file_selections.append(Selection("CCDGAIN"))
  reffile._file_selections.append(Selection("NAXIS1"))
  reffile._file_selections.append(Selection("NAXIS2"))
  reffile._file_selections.append(Selection("LTV1"))
  reffile._file_selections.append(Selection("LTV2"))
  instrument.append(reffile)

  instReferenceFileDefs.append(instrument)

  instrument = instReferenceFileDefs.find_instrument("ACS")
  reffile = instrument.find_reffile("BIA")
  reffile.dump()

  all_keywords = instrument.all_keywords()
  opusutil.PrintMsg("I",'all keywords: '+str(all_keywords))
