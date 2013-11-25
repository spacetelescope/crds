"""
================================================================================
History:

mm/dd/yy PR    Developer  Description
-------- ----- ---------- ------------------------------------------------------
05/18/06 55509 Sherbert   Add import traceback
07/15/10 57271 MSwam      remove db retry parameter
================================================================================
"""
import string
import os
import opusutil
import pyfits
import siname
import kwdbquery
import hst_archdbquery
import cdbsquery
import traceback

# exceptions
class MultipleARCHRows(Exception):
  pass

class NoFilesFound(Exception):
  pass

# special action is needed when updating GEIS keywords
GEIS_KEYWORDS = 0
FITS_KEYWORDS = 1

# output file extensions can be required or optional, input adds distinct
REQD = 0
OPTIONAL = 1
DISTINCT = 2

# indices for output extension list
NAME = 0
TYPE = 1

class Datasource:
  """
===========================================================================
Class: Datasource

Description:
------------
This class is a container class for the data sources
supported by the BESTREF task.  An source can have one or more
of one of these types:

FITSsources - input/output from/to a FITS disk file
DBsources - input from tables in the archive catalog/output to SQL file
CDBsources - input from tables in the REFFILE database/no output

Mixing of different types within a single inputsource is not
supported.

Members:
_inst - the instrument name
_sources - a list of source objects

History:
--------
10/01/02 xxxxx MSwam     first version
04/14/03 xxxxx MSwam     add CDBsources
===========================================================================
  """
  def __init__(self):
    self._sources = []

class FITSsources (Datasource):
  """
  """
  def __init__(self, needkeywords, dataset, indir):
    """
=====================================================================
Name: FITSsources.__init__

Description:
------------
Constructor defines an instrument-specific set of file input file
extensions that 
will be searched for as FITS files.  Some instruments require sets of
file extensions to be treated as different sources (with independent
reference file selection), so each set
results in another source added to the list of sources.
Most instruments will have only a single source in the list.
Some file extensions are required, while some are optional/distinct.
If a fileset has some distinct types, they MUST be listed before any
optional types.
Those file extensions marked distinct are used to conclusively identify a 
fileset.  If none of the distinct files for a set are present, then we don't 
have that type of set.  Missing optional or distinct extensions is not 
considered an error.

Inputs:
------------------
needkeywords (I) - list of keyword values needed from each input source
                   (this list will most likely contain duplicates)
dataset (I) - the rootname of the dataset whose files will be searched
indir (I) - directory in which FITS files will be found

History:
--------
10/01/02 xxxxx MSwam     first version
07/17/03 49117 MSwam     add tag as optional file for STIS
12/22/03 49468 MSwam     add COS extensions
05/03/07 56867 MSwam     replace COS "rawimage" with "raw"
08/09/07 55484 MSwam     nope, both rawimage and raw are valid
08/30/07 55484 MSwam     still needed more (rawimage_a and rawimage_b)
09/13/07 58629 MSwam     needed DISTINCT type added since COS can sometimes have
                           a AND b, but sometimes a OR b.
07/01/08 60176 Sherbert  COS file rename changes
=====================================================================
    """
    # call Superclass constructor
    #
    Datasource.__init__(self)
    self._inst = siname.WhichInstrument(dataset)
    #
    # define sets and file extensions to search for keywords
    if (self._inst == "ACS" or self._inst == "WFC3"):
      input_extensions = [["raw",REQD],["spt",REQD]]
      output_extensions = [["raw",REQD]]
      aSource = FITSInputsource(needkeywords, dataset, indir, 
                                input_extensions, output_extensions)
      self._sources.append(aSource)

    elif (self._inst == "STIS"):
      input_extensions = [["raw",REQD],["spt",REQD]]
      output_extensions = [["raw",REQD]]
      aSource = FITSInputsource(needkeywords, dataset, indir, 
                                input_extensions, output_extensions)
      self._sources.append(aSource)
      #
      input_extensions = [["wav",DISTINCT],["wsp",OPTIONAL]]
      output_extensions = [["wav",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      input_extensions = [["tag",DISTINCT],["spt",OPTIONAL]]
      output_extensions = [["tag",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)

    elif (self._inst == "WFPC2"):
      input_extensions = [["d0f",REQD]]
      output_extensions = [["d0f",REQD]]
      aSource = FITSInputsource(needkeywords, dataset, indir, 
                                input_extensions, output_extensions, 
                                GEIS_KEYWORDS)
      self._sources.append(aSource)

    elif (self._inst == "NICMOS"):
      input_extensions = [["rwb",DISTINCT],["spb",OPTIONAL]]
      output_extensions = [["rwb",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      input_extensions = [["raw",REQD],["spt",REQD]]
      output_extensions = [["raw",REQD]]
      aSource = FITSInputsource(needkeywords, dataset, indir, 
                                input_extensions, output_extensions)
      self._sources.append(aSource)
      #
      input_extensions = [["rwf",DISTINCT],["spf",OPTIONAL]]
      output_extensions = [["rwf",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
    elif (self._inst == "COS"):
      #
      # none of the sets are required, though one should exist
      # We will never calibrate a rawacq image, it would be better
      # to exit quickly - is there another place to do that?
      #
      found = 0
      input_extensions = [["rawacq",DISTINCT],["spt",OPTIONAL]]
      output_extensions = [["rawacq",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
        found = 1
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      input_extensions = [["rawtag",DISTINCT],["spt",OPTIONAL]]
      output_extensions = [["rawtag",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
        found = 1
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      input_extensions = [["rawaccum",DISTINCT],["spt",OPTIONAL]]
      output_extensions = [["rawaccum",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
        found = 1
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      input_extensions = [
        ["rawtag_a",DISTINCT],["rawtag_b",DISTINCT],["spt",OPTIONAL]]
      output_extensions = [["rawtag_a",OPTIONAL],["rawtag_b",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
        found = 1
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      input_extensions = [
        ["rawaccum_a",DISTINCT],["rawaccum_b",DISTINCT],["spt",OPTIONAL]]
      output_extensions = [["rawaccum_a",OPTIONAL],["rawaccum_b",OPTIONAL]]
      try:
        aSource = FITSInputsource(needkeywords, dataset, indir, 
                                  input_extensions, output_extensions)
        found = 1
      except NoFilesFound:
        pass
      else:
        # add source if files exist
        self._sources.append(aSource)
      #
      # one of the sets should have been found
      if not found:
        raise NoFilesFound

  def output(self, anInstrument):
    """
===========================================================================
Name: FITSsource.output

Description:
------------
This method updates the FITS headers of particular FITS files
(instrument-specific) with the keyword values of any changed keywords.

History:
--------
10/01/02 xxxxx MSwam     first version
===========================================================================
    """
    for aSource in self._sources:
      aSource.output(anInstrument)


class DBsources (Datasource):
  """
  """
  def __init__(self, needkeywords, dataset, kw_db, arch_db):
    """
=====================================================================
Name: DBsources.__init__

Description:
------------
Constructor for a database source object.

Inputs:
------------------
needkeywords (I) - list of keyword values needed from each input source
                   (this list will most likely contain duplicates)
dataset (I) - the rootname of the dataset whose files will be searched
kw_db (I) - open database object for the Keyword database
arch_db  (I) - open database object for the archive catalog database

History:
--------
10/01/02 xxxxx MSwam     first version
=====================================================================
    """
    # call Superclass constructor
    #
    Datasource.__init__(self)
    self._inst = siname.WhichInstrument(dataset)
    #
    aSource = DBInputsource(needkeywords, dataset, kw_db, arch_db)
    self._sources.append(aSource)

  def output(self, anInstrument, outfd, all=0):
    """
===========================================================================
Name: DBsource.output

Description:
------------
This method creates the update SQL for the archive catalog
(instrument-specific) with the keyword values of any changed keywords.

History:
--------
10/01/02 xxxxx MSwam     first version
02/25/05 51433 MSwam     add all argument
===========================================================================
    """
    for aSource in self._sources:
      aSource.output(anInstrument, outfd, all)


class CDBsources (Datasource):
  """
  """
  def __init__(self, needkeywords, dataset, cdbs_prefix, reffile_db):
    """
=====================================================================
Name: CDBsources.__init__

Description:
------------
Constructor for a REFFILE database source object.

Inputs:
------------------
needkeywords (I) - list of keyword values needed from each input source
                   (this list will most likely contain duplicates)
dataset (I) - list holding filename and expansion number of reference file
cdbs_prefix (I) - prefix for name of REFFILE db table (e.g. acs for acs_row)
reffile_db (I) - open database object for the REFFILE database

History:
--------
04/14/03 xxxxx MSwam     first version
=====================================================================
    """
    # call Superclass constructor
    #
    Datasource.__init__(self)
    #
    aSource = CDBSInputsource(needkeywords, dataset, cdbs_prefix, reffile_db)
    self._sources.append(aSource)

class Inputsource:
  """
===========================================================================
Class: Inputsource

Description:
------------
This class is a base class for the different kinds on inputsource
objects.  Currently two varieties are supported:

FITSInputsource - input from FITS header keywords
DBInputsource - input from archive catalog database tables

Members:
_dataset - name of dataset
_instrument - name of the instrument
_keywords - a dictionary of keyword value pairs for this source

History:
--------
10/01/02 xxxxx MSwam     first version
===========================================================================
  """
  def __init__(self, dataset):
    self._dataset = dataset
    self._keywords = {}

class FITSInputsource (Inputsource):
  """
  """
  def __init__(self, needkeywords, dataset, indir, input_extensions, 
               output_extensions, keyword_type=FITS_KEYWORDS):
    """
=====================================================================
Name: FITSInputsource.__init__

Description:
------------
The constructor for a FITSInputsource object attempts to open FITS files
for each file extension.  If an extension is required but not present,
an exception is raised.  Optional extensions can be missing.  Files can
also be flagged DISTINCT, which individually are optional, but one of
a set of DISTINCT files must be present to identify a fileset type. Once
opened, each FITS file is scanned for the needed keyword values.
The values are saved in a dictionary.
It is possible for all keyword values to be found without searching
every potential file extension.  Keyword values are first looked for
in the primary header, and then in the 1st image extension.  The first
value found is used.  Not finding a keyword in the FITS files is
acceptable, and generates no error (since headers for different
instrument modes can contain different sets of keywords).
If none of the file extensions specified can be found, an exception
is raised.

Inputs:
------------------
needkeywords (I) - list of keyword values needed from the input source
                   (this list will most likely contain duplicates)
dataset (I) - the rootname of the dataset whose files will be searched
indir (I) - directory in which FITS files will be found
input_extensions - a list of file extensions supplying input for this source
output_extensions - a list of file extensions to write output to
keyword_type - flag indicating if GEIS header keywords are used

Members:
---------
_indir
_input_extensions
_output_extensions
_keyword_type

Exceptions:
------------
IOError (from failed pyfits.open call)
NoFilesFound

History:
--------
10/01/02 xxxxx MSwam     first version
09/13/07 58629 MSwam     add DISTINCT file type (a special kind of OPTIONAL)
=====================================================================
    """
    # call Superclass constructor
    #
    Inputsource.__init__(self, dataset)
    self._inst = siname.WhichInstrument(dataset)
    self._indir = indir
    self._input_extensions = input_extensions
    self._output_extensions = output_extensions
    self._keyword_type = keyword_type

    # loop through file extensions while all keywords not found
    nfiles = 0
    #
    # we must find all REQD extensions or at least one DISTINCT extension
    #  to have a definitive identification
    #
    definitive = 0
    for ext in self._input_extensions:
      found = 1
      # open fits file
      filename = self._indir + os.sep + dataset+"_"+ext[NAME]+".fits"
      try:
        fd = pyfits.open(filename)
      except:
        # some file extensions are not required at all (OPTIONAL), while
        #   others are used to identify a DISTINCT fileset 
        #   (i.e. if one of the types marked DISTINCT is
        #   present, then the fileset has been identified)
        #
        if ext[TYPE] == OPTIONAL or ext[TYPE] == DISTINCT:
          opusutil.PrintMsg("D","FITSInputsource: missing optional/distinct "+
                                filename)
          #
          # if we have reached the OPTIONAL files and still have found none 
          # of the DISTINCT files then check no more since we don't have 
          #  this type of fileset
          #
          if ext[TYPE] == OPTIONAL and not definitive:
            break
          continue
        else:
          opusutil.PrintMsg("E","FITSInputsource: failed to open "+filename)
          raise
      #
      if ext[TYPE] == DISTINCT or ext[TYPE] == REQD:
        definitive = 1
      #
      # look for needed keywords in header
      nfiles = nfiles + 1
      for k in needkeywords:
        # verify keyword is NOT already filled
        if not self._keywords.has_key(k):
          #
          # keyword NOT already known, look it up in the primary header
          try:
            self._keywords[k] = [fd[0].header[k], 0]
          except KeyError:
            # not found, try the 1st image extension header
            try:
              self._keywords[k] = [fd[1].header[k], 0]
            except:
              # opusutil.PrintMsg("D","keyword "+k+" not in "+filename)
              found = 0
      del fd
      if found == 1:
        break
    if found == 0:
      # opusutil.PrintMsg("D","Unable to locate all keywords.")
      pass
    if not definitive or nfiles == 0:
      raise NoFilesFound

  def change_keyword_val(self, reff, new_value, default_value):
    """
===========================================================================
Name: FITSInputsource.change_keyword_val

Description:
------------
This method changes the value of a reference file keyword if the 
new value differs from the current value, and sets the "change" flag.
This flag is either 0 (no change) or 1 (changed), and is added as a
second element to every keyword value.

This routine will assign the proper IRAF directory prefix
to the filename, in order to get an accurate comparison to the
existing reference filename value.

Inputs:
-------
reff - Reffile object for a reference file
new_value - new value to assign to keyword
default_value - default value of keyword, if it is not filled

History:
--------
10/01/02 xxxxx MSwam     first version
05/28/09 62687 MSwam     replace None value with default_value
===========================================================================
    """
    if new_value == None:
      key_value = default_value
    #
    # add the IRAF directory prefix if not set to the default
    elif new_value != default_value:
      #
      # special cases: COMPTAB, GRAPHTAB map to $mtab prefix no
      # matter which instrument they appear in
      #
      if reff._keyword == "COMPTAB" or reff._keyword == "GRAPHTAB":
        key_value = ("mtab$" + 
                    string.lower(new_value) )
      else:
        key_value = (siname.add_IRAF_prefix(self._inst) +
                    string.lower(new_value) )
    else:
      key_value = default_value
    #
    # if the keyword exists and the value has changed, 
    # assign new value and set the change flag (=1)
    #
    if (self._keywords.has_key(reff._keyword) and  
        self._keywords[reff._keyword][0] != key_value):
      opusutil.PrintMsg("I", reff._keyword+" value changed: "+
                        self._keywords[reff._keyword][0]+ " => "+key_value)
      self._keywords[reff._keyword] = [key_value, 1]

  def output(self, anInstrument):
    """
===========================================================================
Name: FITSInputsource.output

Description:
------------
This method updates the FITS headers of particular FITS files
(instrument-specific) with the keyword values of any changed keywords.
Only keyword updates are performed.  If a FITS file is missing, but is
marked OPTIONAL, it is not considered an error.

Since not all keywords are present in all headers, even for a single
instrument, no error is generated if a keyword update fails because that
keyword is not part of the header.  Keyword inserts will NOT be
performed.

A special case exists when updating some GEIS reference file keywords, since
for these each reference file is actually specified by a pair of keywords.

Input:
------
anInstrument - instrument object defining the ref files for that instrument

History:
--------
10/01/02 xxxxx MSwam     first version
===========================================================================
    """
    # some instruments update multiple files
    #
    for extension in self._output_extensions:
      # open fits file
      opusutil.PrintMsg("D","output: extension = "+str(extension)+"|")
      filename = self._indir + os.sep + self._dataset+"_"+extension[NAME]+".fits"
      try:
        fd = pyfits.open(filename, "update")
      except IOError:
        if extension[TYPE] == OPTIONAL:
          # some extensions are NOT required; they can be missing
          continue
        else:
          opusutil.PrintMsg("E","output: failed to open "+filename)
          raise

      opusutil.PrintMsg("D","opened "+filename+" for update")

      #
      # loop through the reference file keywords
      for reff in anInstrument._reffiles:
        #
        # if keyword does not exist or change flag indicates
        # keyword value has not changed, skip it
        if (not self._keywords.has_key(reff._keyword) or
            self._keywords[reff._keyword][1] == 0):
          continue
        #
        # update keyword value
        try:
          opusutil.PrintMsg("D","output updating "+reff._keyword+" = "+
                            self._keywords[reff._keyword][0])
          fd[0].header[reff._keyword] = self._keywords[reff._keyword][0]
          if self._keyword_type == GEIS_KEYWORDS:
            # SPECIAL CASE: ($%*&% GEIS FILES!!)  The WFPC-2 keywords
            #   BIASFILE, DARKFILE, FLATFILE are actually pairs, requiring
            #   BIASDFIL, DARKDFIL, FLATDFIL as well.  The value for the DFIL
            #   is just the FILE value replacing ".r??" with ".b??".
            #
            if reff._keyword == "BIASFILE":
              fd[0].header['BIASDFIL'] = string.replace(
                                          self._keywords[reff._keyword][0],
                                          ".r", ".b")
            elif reff._keyword == "DARKFILE":
              fd[0].header['DARKDFIL'] = string.replace(
                                          self._keywords[reff._keyword][0],
                                          ".r", ".b")
            elif reff._keyword == "FLATFILE":
              fd[0].header['FLATDFIL'] = string.replace(
                                          self._keywords[reff._keyword][0],
                                          ".r", ".b")
        except KeyError: # ignore keywords that are not present in header
          pass
      fd.close()
      del fd


class DBInputsource (Inputsource):
  """
  """
  def __init__(self, needkeywords, dataset, kw_db, arch_db):
    """
=====================================================================
Name: DBInputsource.__init__

Description:
------------
This constructor locates the archive catalog location (tablename,
fieldname) where each needed keyword can be found, and saves these in a
dictionary.  Each archive catalog table in the dictionary is then queried 
to obtain the needed keyword values from that table , which are stored
in a different dictionary.  If keyword values cannot be found when using
the dataset name provided, the dataset name is interpreted as an
association, and the query is repeated using the first association
member as the dataset name (it is assumed that any fields needed for
reference file selection will have identical values across association
members).

Members:
---------
_dbsource (O) - the dictionary of archive catalog locations for keywords
_keywords (O) - the keyword/value pairs

Inputs:
------------------
needkeywords (I) - list of keyword values needed from the input source
                   (this list will most likely contain duplicates)
dataset (I) - the rootname of the dataset
kw_db (I) - an open Keyword Database connection object
arch_db (I)  - an open archive Database connection object

History:
--------
10/01/02 xxxxx MSwam     first version
09/20/06 56376 MSwam     tweak string find check for clarity
10/09/07 57618 Sherbert  kluge so that nsr_best_rnlcortb gets filled
04/15/09 62457 MSwam     fix bug affecting w3s_subarray check and special
                           handling for aperture field (sci_aper_1234)
=====================================================================
    """
    # call Superclass constructor
    #
    Inputsource.__init__(self, dataset)
    self._inst = siname.WhichInstrument(dataset)
    self._num_changed = 0

    #
    # set the index for reading the db query result
    use_row = 0
    #
    # find archive database location for needed keywords
    self._dbsource = {}
    for k in needkeywords:
      #
      # verify source is NOT already filled (since duplicates can exist)
      if not self._dbsource.has_key(k):
        #
        # keyword NOT already known, look up its source in the database
        try:
          ksource = kw_db.keyword_mapping(self._inst, k)
          #
          # adjust the keyword source for reference file, table,
          # and calibration switch  keywords
          # so that the "_best_" field is retrieved, instead of the original
          # field
          # 
          # REMOVE k[-8:] == "RNLCORTB" and change the following to use
          # the XML REFFILE_KEYWORD to figure this out.  See PR 58739.
          if (ksource[0][-8:] == "ref_data" and 
              (k[-3:] == "TAB" or k[-4:] == "FILE" or k[-4:] == "CORR"
               or k[-8:] == "RNLCORTB") ):
            self._dbsource[k] = (ksource[0], 
                                ksource[1][0:3] + "_best_" + ksource[1][4:])
            opusutil.PrintMsg("D",'using adjusted source '+str(self._dbsource[k]))
          else:
            self._dbsource[k] = ksource
            opusutil.PrintMsg("D",'using source '+str(self._dbsource[k]))
        except kwdbquery.NoMatchingKWDBField:
          #
          # not all fields (e.g. filename keywords like BIASFILE) will exist
          opusutil.PrintMsg("W","No keyword mapping for "+k)
    #
    # I HATE special cases!
    self.fix_acs_ccdchip()

    opusutil.PrintMsg("D",'self.dbsource='+str(self._dbsource))
    #
    # make a copy of the dbsource so members can be deleted
    dbsource = self._dbsource.copy()
    #
    # while dbsource items remain, form and execute DB queries to
    # obtain keyword values from archive tables
    while len(dbsource) > 0:
      #
      # start to form DB query for first table,field in dictionary
      allkeys = dbsource.keys()
      tablename = dbsource[allkeys[0]][0]
      fieldname = dbsource[allkeys[0]][1]
      prefix = fieldname[0:3]
      #
      # datetime conversion (Y.M.D H:M:S) for EXPSTART
      # (if it happens to be the first field)
      #
      if fieldname[4:] == "expstart":
        select = ("SELECT convert(char(12),"+fieldname+",102)+"+
                         "convert(char(12),"+fieldname+",108)" )
      else:
        select = "SELECT "+fieldname
      #
      # delete this dbsource entry so we only process it once
      del dbsource[allkeys[0]]
      #
      # add each dict entry using that same tablename (so we only
      #   have to query each table once)
      nfields = 1
      for akey in dbsource.keys():
        # don't know why this used to do a substring match (.find),
        # but it gave the wrong result for the wfc3_science.w3s_subarray field,
        # so it has been replaced with a straight equality check
        if (dbsource[akey][0] == tablename):
          #
          # found a table match, add it to the query
          fieldname = dbsource[akey][1]
          if fieldname[4:] == "expstart" or fieldname[4:] == "texpstrt":
            #
            # datetime conversion (Y.M.D H:M:S) for EXPSTART
            select = (select +", convert(char(12),"+
                                 dbsource[akey][1]+",102)+"+
                                "convert(char(12),"+
                                 dbsource[akey][1]+",108)" )
          else:
            select = select + "," + dbsource[akey][1]
          #
          # delete this dbsource table,field so we don't process it again
          del dbsource[akey]
          nfields = nfields + 1
      #
      # complete the query
      #
      # the normal case is to select on dataset name, but some
      # archive tables (e.g. acs_chip) don't have it, so verify
      # that the target table has it before using it, otherwise
      # try program_id, obset_id, and obsnum
      #
      try:
        kw_db.field_check(prefix+"_data_set_name")
        select = (select +" FROM "+ tablename +" WHERE "+ prefix +
                      "_data_set_name = '" +string.upper(dataset)+ "'")
      except kwdbquery.NoMatchingKWDBField:
        #
        # data_set_name field does not exist, try program_id
        # (fail if its missing as well)
        kw_db.field_check(prefix+"_program_id")
        select = (select +" FROM "+ tablename +" WHERE "+ 
                      prefix + "_program_id = '" +
                      string.upper(dataset[1:4]) + "' and " +
                      prefix + "_obset_id = '" +
                      string.upper(dataset[4:6]) + "' and " + 
                      prefix + "_obsnum = '" +
                      string.upper(dataset[6:8]) + "'")
      #
      # get results in a list of dictionaries
      result = [{}]
      arch_db.zombie_select(select, result)
      #
      # flag error if multiple rows found
      if len(result) > 1:
        # multiple rows found, this is an error if the table being
        # queried is NOT acs_chip (I HATE special cases!)
        #
        use_row = self.acs_chip_test(tablename, dataset, result)

      if len(result) == 0:
        opusutil.PrintMsg("D","No rows found in "+tablename)
        #
        # try to look for an asn member instead using the main asn product
        #
        dbrows = arch_db.get_top_asn(dataset[:-1]+"0")
        if len(dbrows) == 0:
          opusutil.PrintMsg("D","No parent ASN either.")
          continue
        #
        # now get the members for the product
        asn_members = arch_db.get_asn_members(dbrows, dataset)
        if len(asn_members) == 0:
          opusutil.PrintMsg("D","No asn members found.")
          continue
        #
        # replace the dataset name in the query text with the first
        # asn member and reissue the query
        if string.find(select, "_data_set_name") > -1:
          querytxt = string.replace(select,
                            "_data_set_name = '"+string.upper(dataset),
                            "_data_set_name = '"+string.upper(asn_members[0]))
        else: # must be a program_id query
          querytxt = string.replace(select,
                            "_program_id = '"+string.upper(dataset[1:4]),
                            "_program_id = '"+string.upper(asn_members[0][1:4]))
          querytxt = string.replace(querytxt,
                            "_obset_id = '"+string.upper(dataset[4:6]),
                            "_obset_id = '"+string.upper(asn_members[0][4:6]))
          querytxt = string.replace(querytxt,
                            "_obsnum = '"+string.upper(dataset[6:8]),
                            "_obsnum = '"+string.upper(asn_members[0][6:8]))
        #
        # get results in a list of dictionaries
        result = [{}]
        arch_db.zombie_select(querytxt, result)
        #
        if len(result) > 1:
          # multiple rows found, this is an error if the table being
          # queried is NOT acs_chip (I HATE special cases!)
          #
          use_row = self.acs_chip_test(tablename, dataset, result)

        if len(result) == 0:
          opusutil.PrintMsg("D","No rows found in "+tablename)
          continue
      #
      if (use_row+1) > len(result):
        use_row -= 1
        opusutil.PrintMsg("D","Result ("+str(result)+") doesn't contain row "+
                              str(use_row)+", using "+str(use_row)+" instead")
      #
      # save the keyword values (trim off the prefix and covert to upcase)
      # and a "changed" flag
      #
      for k in result[use_row].keys():
        opusutil.PrintMsg("D","saving "+str(k)+" = "+str(result[use_row][k]))
        if k == '': 
          # this is EXPSTART; conversion during query results is needed 
          # to set keyword name (it comes back empty in the query result)
          self._keywords['EXPSTART'] = [result[use_row][k], 0]
        else:
          # strip off _best_ if present
          if k[3:9] == "_best_":
            self._keywords[string.upper(k[9:])] = [result[use_row][k], 0]
            #
          elif k == 'sci_aper_1234':
            # except for...SPECIAL CASES (I HATE THOSE ! ! ! !)
            # wfc3 needs APERTURE, which comes from this DB field: sci_aper_1234
            #   so we CAN'T just trim the prefix to get the keyword name
            #   (aper_1234 is NOT a keyword name)   ARGH!
            #
            self._keywords['APERTURE'] = [result[use_row][k], 0]
          else:
            self._keywords[string.upper(k[4:])] = [result[use_row][k], 0]

  def change_keyword_val(self, reff, new_value, default_value):
    """
===========================================================================
Name: DBInputsource.change_keyword_val

Description:
------------
This method changes the value of a reference file keyword if the 
new value differs from the current value, and sets the "change" flag.
The change flag can be 0 (no change) or 1 (changed), and is added as a
second element to each keyword value.

Inputs:
-------
reff (I) - Reffile object for a reference file
new_value (I) - new value to assign to keyword
default_value (I) - not used (keeps calling args compatible between FITS
and DB versions)

Output: sets value and change indicator for a keyword 

History:
--------
10/01/02 xxxxx MSwam     first version
===========================================================================
    """
    # if the keyword exists and the value has changed, 
    # assign new value and set the change flag
    #
    if (self._keywords.has_key(reff._keyword) and  
        self._keywords[reff._keyword][0] != new_value):
      if self._keywords[reff._keyword][0] == None:
        # don't normally report changes from None in DB mode
        msg_level = "D"
      else:
        msg_level = "I"
      opusutil.PrintMsg(msg_level, reff._keyword+" value changed: "+
                        str(self._keywords[reff._keyword][0])+ 
                        " => "+new_value)
      self._keywords[reff._keyword] = [new_value, 1]
    #
    return

  def output(self, anInstrument, outfd, all=0):
    """
=====================================================================
Name: DBInputsource.output

Description:
------------
This method writes an SQL update statement for an instrument's
"_ref_data" table to a given output descriptor. It can write either
all keyword values or only any keyword values that have changed.

Inputs:
-------
anInstrument - an Instrument object holding the ref file objects
outfd - output file descriptor for SQL output file
all - flags when all values should be output, versus changes only

History:
--------
10/01/02 xxxxx MSwam     first version
02/25/05 51433 MSwam     add all argument
=====================================================================
    """
    self._num_changed = 0
    #
    # start the update statement
    querytxt = "UPDATE " + string.lower(anInstrument._name) + "_ref_data SET "
    pre = siname.get_ref_data_prefix(anInstrument._name)
    #
    # loop through the reference file keywords and update any
    # that have changed value
    for reff in anInstrument._reffiles:
      try:
        if self._keywords[reff._keyword][1] == 1:
          self._num_changed = self._num_changed + 1
        if all or self._keywords[reff._keyword][1] == 1:
          querytxt = (querytxt + pre + "_best_" + string.lower(reff._keyword) +
                      " = '" + self._keywords[reff._keyword][0] + "',")
      except KeyError:
        opusutil.PrintMsg("W","No such keyword: "+reff._keyword)
    #
    # if any ref file keywords changed value, or request is for all values,
    # write the update statement to the SQL output
    if all:
      # writing all values, pretty it up with newlines
      querytxt = querytxt.replace(",",",\n")
      querytxt = querytxt.replace("SET ","SET\n")
      querytxt = (querytxt[:-2] + "\nWHERE " + pre + "_data_set_name = '" +
                  string.upper(self._dataset) + "'")
      outfd.write(querytxt+"\n")
    #
    elif self._num_changed > 0:
      querytxt = (querytxt[:-1] + " WHERE " + pre + "_data_set_name = '" +
                  string.upper(self._dataset) + "'")
      outfd.write(querytxt+"\n")


  def fix_acs_ccdchip(self):
    """
===========================================================================
Name: DBInputsource.fix_acs_ccdchip

Description:
------------
This method is used for the SPECIAL CASE of the ACS "ccdchip" field.
This value can be found in the acs_ref_data table, but it is not always
accurate there.  The preferred location is the acs_chip table instead.
This routine forces the database source for the ccdchip field to be the
acs_chip table.

Input: self - the DBInputsource object

History:
--------
10/01/02 xxxxx MSwam     first version
===========================================================================
    """
    try:
      # replace the source of the ACS ccdchip keyword, if present
      if self._dbsource.has_key('CCDCHIP'):
        self._dbsource['CCDCHIP'] = ("acs_chip","acc_ccdchip")
    except:
      pass

  def acs_chip_test(self, tablename, dataset, result):
    """
===========================================================================
Name: DBInputsource.acs_chip_test

Description:
------------
This method is used for the SPECIAL CASE of the acs_chip database
table.  ACS WFC exposures have two entries in this table, one for each
chip.  The code picks chip2, if possible, otherwise an error occurs and
an exception is raised.

Inputs:
-------
tablename - name of archive database table being read from
dataset - name of the dataset being processed
result - query result from the archive database query

Output: indicates which resulting row from the db query to use (0 or 1)

Exceptions: MultipleARCHRows - raised if this is NOT an acs_chip entry
                               or if a single row cannot be picked

History:
--------
10/01/02 xxxxx MSwam     first version
===========================================================================
    """
    # multiple rows found, this is an error if the table being
    # queried is NOT acs_chip (I HATE special cases!)
    #
    if tablename != "acs_chip":
      opusutil.PrintMsg("E","Multiple "+dataset+" rows found in "+
                              tablename)
      raise MultipleARCHRows
    #
    # for acs_chip, use the "chip 2" row
    opusutil.PrintMsg("D","result="+str(result))
    try:
      if result[0]['acc_ccdchip'] == 2:
        use_row = 0
      elif result[1]['acc_ccdchip'] == 2:
        use_row = 1
      else:
        opusutil.PrintMsg("E","Unable to discern acs_chip row to use")
        raise MultipleARCHRows
    except:
      traceback.print_exc()
      opusutil.PrintMsg("E","Failure determining acs_chip row to use.")
      raise MultipleARCHRows
    #
    return use_row
          

class CDBSInputsource (Inputsource):
  """
  """
  def __init__(self, needkeywords, dataset, cdbs_prefix, reffile_db):
    """
=====================================================================
Name: CDBSInputsource.__init__

Description:
------------
This constructor reads the REFFILE database to obtain
needed keyword values, which are stored in a dictionary.

Members:
---------
_keywords (O) - the keyword/value pairs

Inputs:
------------------
needkeywords (I) - list of keyword values needed from the input source
                   (this list will most likely contain duplicates)
dataset (I) - list holding the name and expansion number of the reference file
cdbs_prefix (I) - REFFILE table prefix for the needed instrument
reffile_db (I) - an open REFFILE Database connection object

History:
--------
04/14/03 xxxxx MSwam     first version
=====================================================================
    """
    # call Superclass constructor
    #
    Inputsource.__init__(self, dataset[0])

    # reduce keyword list to unique keywords needed and build query
    self._dbsource = {}
    select = "SELECT DISTINCT "
    for k in needkeywords:
      #
      # leave out the ref file and switch keywords
      if k[-3:] == "TAB" or k[-4:] == "FILE" or k[-4:] == "CORR":
        # skip these
        continue

      # verify source is NOT already filled (since duplicates can exist)
      if not self._dbsource.has_key(k):
        # value doesn't matter, we're using the map to ensure uniqueness
        self._dbsource[k] = ''
        select = select + string.lower(k) + ','
    opusutil.PrintMsg("D",'self.dbsource='+str(self._dbsource))

    # if no fields are needed, return
    if len(self._dbsource) == 0:
      opusutil.PrintMsg("I","No keywords needed from REFFILE.")
      return

    #
    # trim extra comma and finish the query, if any fields were found
    select = (select[:-1] + " FROM " + cdbs_prefix + 
              "_row WHERE file_name = '" + dataset[0] + "' and " +
              "expansion_number = " + str(dataset[1]))
    #
    # get results in a list of dictionaries
    result = [{}]
    reffile_db.zombie_select(select, result)

    # save the keyword values (covert to upcase) and a "changed" flag (0)
    #
    opusutil.PrintMsg("D","result="+str(result))
    if len(result) > 0:
      for k in result[0].keys():
        opusutil.PrintMsg("D","saving "+str(k)+" = "+str(result[0][k]))
        self._keywords[string.upper(k)] = [result[0][k], 0]
    else:
      opusutil.PrintMsg("E","No result from REFFILE query.")

#========================================================================
# TEST 
# % python datasources.py
#========================================================================
if __name__ == "__main__":
  all_keywords = ['DETECTOR','CCDAMP','CCDGAIN','EXPSTART']
  dataset = "j8c103041"
  indir = os.getcwd()
  opusutil.PrintMsg("I","A FITS file open error is EXPECTED now.")
  try:
    fits_source = FITSsources(all_keywords, dataset, indir)
    opusutil.PrintMsg("I",'keywords='+str(fits_source._keywords))
  except IOError:
    pass
  #
  kw_db = kwdbquery.Kw_db(os.environ['KW_SERVER'], 
                          os.environ['KW_DB'])
  arch_db = hst_archdbquery.HST_Arch_db(os.environ['ARCH_SERVER'], 
                                os.environ['ARCH_DB'])
  db_source = DBsources(all_keywords, dataset, kw_db, arch_db)
  opusutil.PrintMsg("I",'keywords='+str(db_source._sources[0]._keywords))
  kw_db.close()
  arch_db.close()
  #
  dataset = ["N491401AO_PFL.FITS",1]
  all_keywords = ['DETECTOR','OBSTYPE','OPT_ELEM']
  cdbs_prefix = "stis"
  reffile_db = cdbsquery.Cdbs_db(os.environ['REFFILE_SERVER'], 
                              os.environ['REFFILE_DB'])
  cdb_source = CDBsources(all_keywords, dataset, cdbs_prefix, reffile_db)
  opusutil.PrintMsg("I",'keywords='+str(cdb_source._sources[0]._keywords))
  reffile_db.close()
