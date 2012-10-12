# python modules used
import string
import os
import time
import traceback

# local modules used
import instReferenceFileDefs
import opusutil
import siname
import datasources
import hst_archdbquery
import kwdbquery
import base_db

# exceptions raised
#
class FailedTimeConversion(Exception):
  pass

class ZeroRowsFound(Exception):
  # No matching rows from CDBS query
  pass

class MissingRequiredFile(Exception):
  # Required reference file could not be found
  pass

class MultipleRefFileTypes(Exception):
  pass

ACS_HALF_CHIP_COLS = 2048         #used in custom bias selection algorithm
SM4_YYYYDDDHHMMSS  = '2009.134:12:00:00'  # date beyond which an exposure was
                                          # taken in the SM4 configuration
                                          # (day 2009.134 = May 14 2009,
                                          #  after HST was captured by 
                                          #  the shuttle during SM4, and
                                          #  pre-SM4 exposures had ceased)

# the query templates (constants)
#05/27/09 62687 MSwam     add max() to filename select to ensure latest match
query_template_1 = (
       "SELECT max(SI_file_1.file_name) "+
       "FROM SI_file SI_file_1, SI_row SI_row_1 "+
       "WHERE SI_file_1.useafter_date = "+
           "(SELECT max(SI_file_2.useafter_date) "+
           "FROM SI_file SI_file_2, SI_row SI_row_2 "+
               "WHERE SI_file_2.reference_file_type = 'REFFILETYPE' "+
               "and SI_file_2.useafter_date <= 'EXPOSURE_START' "+
               "and SI_file_2.reject_flag = 'N' "+
               "and SI_file_2.opus_flag = 'Y' "+
               "and SI_file_2.archive_date is not null "+
               "and SI_file_2.opus_load_date is not null "+
               "and SI_file_2.file_name =SI_row_2.file_name "+
               "and SI_file_2.expansion_number = SI_row_2.expansion_number ")

query_template_2 = (
           ") and SI_file_1.reference_file_type = 'REFFILETYPE' "+
       "and SI_file_1.reject_flag = 'N' "+
       "and SI_file_1.opus_flag = 'Y' "+
       "and SI_file_1.archive_date is not null "+
       "and SI_file_1.opus_load_date is not null "+
       "and SI_file_1.file_name =SI_row_1.file_name "+
       "and SI_file_1.expansion_number = SI_row_1.expansion_number ")

class Cdbs_db(base_db.Base_db):
  """
=======================================================================
Class: Cdbs_db

Description:
------------
This class provides access to relations in the CDBS database.
It inherits common function from the base_db.Base_db class.

Methods:
--------

History:
--------
10/01/02 xxxxx MSwam     Initial version
06/30/10 64432 MSwam     Use single quotes for SQLServer
=======================================================================
  """
  def __init__(self, server, dbname):
    #
    # call Superclass constructor
    base_db.Base_db.__init__(self, server, dbname)

  """
=======================================================================
Name: find_exposure_start

Description:
------------
This function converts a specific keyword value into a formatted exposure
start time.  It uses the TEXPSTRT, EXPSTART or PSTRTIME, whichever is
present.  The input format of each of these keyword
values is assumed, and the result output format is like
mm/dd/yy HH:MM:SS.  

It also computes whether the exposure start keyword
value indicates if the exposure occurred after SM4, and returns a flag
indicating True/False to that condition.

Inputs:
----------
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.

Returns: a formatted (mm/dd/yy HH:MM:SS) exposure start time
         a boolean flag indicating True if the exposure start is after SM4

Note: Can throw a FailedTimeConversion exception if neither time keyword
      exists, or if the input keyword format is not as expected.

History:
--------
10/01/02 xxxxx MSwam     Initial version
10/11/04 51865 MSwam     Add blank to strptime format to eat trailing whitespace
07/23/08 60086 MSwam     New Python seems to want strptime switched back
09/04/08 59821 MSwam     Argh.  Ops found at least one strptime that
                           still needed the "gobbling space".
04/14/09 62419 Sherbert  New approach to the space problem.
03/15/11 67806 MSwam     Add beyond_SM4 return value flag
=======================================================================
  """
  def find_exposure_start(self, aSource):
    # fill the exposure start time, after converting keyword value
    # to datetime format from source format
    beyond_SM4 = True    # default
    try:
      if aSource._keywords.has_key('TEXPSTRT'):
       #timetuple = time.strptime(aSource._keywords['TEXPSTRT'][0],
       #                        "%Y.%m.%d %H:%M:%S")
        timetuple = time.strptime(aSource._keywords['TEXPSTRT'][0].rstrip(),
                                "%Y.%m.%d %H:%M:%S")
      elif aSource._keywords.has_key('EXPSTART'):
       #timetuple = time.strptime(aSource._keywords['EXPSTART'][0],
       #                        "%Y.%m.%d %H:%M:%S ")
        timetuple = time.strptime(aSource._keywords['EXPSTART'][0].rstrip(),
                                "%Y.%m.%d %H:%M:%S")
      #
      # these are used in FITS input mode
      elif (aSource._keywords.has_key('PSTRTIME') and
            aSource._keywords['PSTRTIME'][0] != ' '):
        opusutil.PrintMsg("D","Trying PSTRTIME for exposure start:"+
                          aSource._keywords['PSTRTIME'][0]+'|')
        # its there, use it and convert it
       #temptuple = time.strptime(aSource._keywords['PSTRTIME'][0],
       #                        "%Y.%j:%H:%M:%S")
        temptuple = time.strptime(aSource._keywords['PSTRTIME'][0].rstrip(),
                                "%Y.%j:%H:%M:%S")
        # convert DOY to month and day
        parts = string.split(aSource._keywords['PSTRTIME'][0],":")
        moparts = string.split(parts[0],".")
        if int(moparts[0]) % 4 == 0:
          modays = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        else:
          modays = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
        monum = 0
        doy = int(moparts[1])
        while doy > modays[monum]:
          doy = doy - modays[monum]
          monum = monum + 1
        # adjust month to 1-relative value
        month = monum + 1
        day = doy
        timetuple = (temptuple[0],month,day,temptuple[3],temptuple[4],
                     temptuple[5],temptuple[6],temptuple[7],temptuple[8])
      elif (aSource._keywords.has_key('TVSTART') and 
            aSource._keywords['TVSTART'][0] != ' '):
        # thermal vac keyword for COS/WFC3 testing
        opusutil.PrintMsg("D","Trying TVSTART for exposure start:"+
                          aSource._keywords['TVSTART'][0]+'|')
        timetuple = time.strptime(aSource._keywords['TVSTART'][0],
                                  "%Y-%m-%dT%H:%M:%S")
      elif (aSource._keywords.has_key('DATE-OBS') and 
            aSource._keywords['DATE-OBS'][0] != ' ' and
            aSource._keywords.has_key('TIME-OBS') and 
            aSource._keywords['TIME-OBS'][0] != ' ') :
        opusutil.PrintMsg("D","Trying DATE-OBS,TIME-OBS for exposure start.")
        timetuple = time.strptime(aSource._keywords['DATE-OBS'][0]+' '+
                                  aSource._keywords['TIME-OBS'][0],
                                  "%Y-%m-%d %H:%M:%S")
      else:
        opusutil.PrintMsg("E","Failed to find any exposure start keys")
        raise FailedTimeConversion
      #
      exposure_start = time.strftime("%m/%d/%Y %H:%M:%S",timetuple)
      #
      # determine if exposure start is post SM4
      exposure_start_compare = time.strftime("%Y.%j:%H:%M:%S",timetuple)
      if (exposure_start_compare > SM4_YYYYDDDHHMMSS): beyond_SM4 = True
      else:                                            beyond_SM4 = False

    except:
      traceback.print_exc()
      opusutil.PrintMsg("E","Failed time conversion for exposure start.")
      raise FailedTimeConversion
    #
    return exposure_start, beyond_SM4

  """
=======================================================================
Name: find_reffile

Description:
------------
This function composes a database query against the CDBS database to
find an applicable reference file for a given instrument mode.
The instrument mode information is passed in the "keywords" dictionary.
The reference file information is passed in "thereffile" object.
An open database object is passed in for running the query.

Templates are used as starting points for the query.  Values specific to
the instrument and reffile being computed are changed in the template
and saved in a string, which is passed on as the database query to
execute.

Inputs:
----------
instrument_name (I) - name of the instrument being processed
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.

Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)
History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
  """
  def find_reffile(self, instrument_name, thereffile, aSource):
    # get the CDBS table prefix for this instrument
    cdbs_prefix = siname.get_cdbs_prefix(instrument_name)

    # begin to build up a query by
    # replacing the template1 fields with the actual values
    querytxt = string.replace(query_template_1,"REFFILETYPE",
                              thereffile._type)
    querytxt = string.replace(querytxt,"SI",
                              cdbs_prefix)

    # fill the exposure start time, after converting the keyword value
    # to datetime format from source format and ignore the extra return value
    exposure_start, dontcare = self.find_exposure_start(aSource)
    querytxt = string.replace(querytxt,"EXPOSURE_START", exposure_start)                         
    # add the file selection fields (row_2)
    querytxt = querytxt + self.add_file_selection_fields(cdbs_prefix, "2", 
                                                    thereffile, aSource)

    # replace the template2 fields with the actual values
    temptxt = string.replace(query_template_2,"REFFILETYPE",
                              thereffile._type)
    temptxt = string.replace(temptxt,"SI",
                              cdbs_prefix)
    querytxt = querytxt + temptxt

    # add the file selection fields again (row_1)
    querytxt = querytxt + self.add_file_selection_fields(cdbs_prefix, "1", 
                                                    thereffile, aSource)

    # replace any None values with null in query
    querytxt = string.replace(querytxt,"None","null")

    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    if len(result) == 0 or result[0][0] == None:
      #
      # no matching CDBS record found
      opusutil.PrintMsg("D","Zero matching rows found.")
      raise ZeroRowsFound, querytxt
    #
    # return the first filename found
    return result[0][0]

  """
=======================================================================
Name: add_file_selection_fields

Description:
------------
Composes the file selection criteria for a CDBS query of a reference
file.  Adds a clause for each file selection field that passes any (optional) 
restriction condition.

Inputs:
----------
cdbs_prefix (I) - the prefix of the CDBS relation being queried
querynum (I) - a number used to indicate which query match is used
thereffile (I) - a reference file object
aSource (I) - an input source object

Returns:
--------
a string containing the file selection clauses for the query

History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
  """
  def add_file_selection_fields(self, cdbs_prefix, querynum, thereffile, 
                                aSource):
    querytxt = ""

    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        if (not eval(k._restrictions)):
          opusutil.PrintMsg("D","file selection restriction NOT met: "+
                            k._restrictions)
          continue
      #
      # apply the file selection field
      # (first as a string, but if that fails, as a number converted to string
      #  since numbers don't get quoted, and strings do)
      opusutil.PrintMsg("D","adding file selection "+k._field)
      try:
        querytxt = (querytxt + "and " + cdbs_prefix + "_row_" + querynum + 
                 "." + string.lower(k._field) + " = '" + 
                 aSource._keywords[k._field][0] + "' ")
      except TypeError:
        querytxt = (querytxt + "and " + cdbs_prefix + "_row_" + querynum + 
                 "." + string.lower(k._field) + " = " + 
                 str(aSource._keywords[k._field][0]) + " ")
    return querytxt

  """
=======================================================================
Name: multi_tab

Description:
------------
This function composes a database query against the CDBS database to
find an applicable SYNPHOT (COMPTAB or GRAPHTAB) reference file.
The reference file information is passed in "thereffile" object.
An open database object is passed in for running the query.

A template is used as the starting point for the query.  Values specific to
the query are changed in the template
and saved in a string, which is passed on as the database query to
execute.

Inputs:
----------
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters

Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)
History:
--------
10/01/02 xxxxx MSwam     Initial version
05/27/09 62687 MSwam     add max() to filename select to ensure latest match
=======================================================================
  """
  def multi_tab(self, thereffile):
    # the query template
    query_template = (
       "SELECT max(synphot_file_1.file_name) FROM synphot_file synphot_file_1 "+
       "WHERE synphot_file_1.general_availability_date = "+
       "(SELECT max(synphot_file_2.general_availability_date) "+
       "     from synphot_file synphot_file_2 "+
           "  where synphot_file_2.reference_file_type = 'REFFILEKEYWORD' "+
           "  and synphot_file_2.reject_flag = 'N' "+
           "  and synphot_file_2.opus_flag = 'Y' "+
           "  and synphot_file_2.archive_date is not null and "+
           "synphot_file_2.opus_load_date is not null "+
       ") "+
       "and synphot_file_1.reference_file_type = 'REFFILEKEYWORD' "+
       "and synphot_file_1.reject_flag = 'N' "+
       "and synphot_file_1.opus_flag = 'Y' "+
       "and synphot_file_1.archive_date is not null and "+
       "synphot_file_1.opus_load_date is not null " )
    #
    # replace the template1 fields with the actual values
    querytxt = string.replace(query_template,"REFFILEKEYWORD",
                              thereffile._keyword)
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    if len(result) == 0 or result[0][0] == None:
      #
      # no matching CDBS record found
      opusutil.PrintMsg("D","Zero matching rows found. ")
      raise ZeroRowsFound, querytxt
    #
    # return the first filename found
    return result[0][0]

  """
=======================================================================
Name: add_bias file_selection

Description:
------------
Composes the file selection criteria for a CDBS query of the ACS
BIAS reference file.  Adds a clause for each file selection field that passes 
any (optional) restriction condition.

Inputs:
----------
querynum (I) - a number used to indicate which query match is used
thereffile (I) - a reference file object
aSource (I) - an input source object

Returns:
--------
a string containing the file selection clauses for the query

History:
--------
10/01/02 xxxxx MSwam     Initial version
09/21/06 56495 MSwam     add amp conversions for single-amp multi-chip reads
03/15/11 67806 MSwam     only do amp conversion for pre-SM4 data
03/29/11 67806 MSwam     change in algorithm from ACS team 
09/05/12 72156 MSwam     add APERTURE selection field for post-SM4 cases

=======================================================================
  """
  def acs_bias_file_selection(self, querynum, thereffile, aSource, beyond_SM4):
    querytxt = ""
    #
    # add the file selection fields
    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        opusutil.PrintMsg("D",'found a file select restricted: '+
                               k._restrictions)
        if (not eval(k._restrictions)):
          opusutil.PrintMsg("D","File_selection on "+k._field+
                                " restricted away")
          continue
      #
      # skip these (not used in selection, only for special tests)
      if (k._field == 'XCORNER' or k._field == 'YCORNER' or
          k._field == 'CCDCHIP'):
          continue
      #
      # skip APERTURE prior to SM4, otherwise use it (PR 72156)
      if (k._field == 'APERTURE' and not beyond_SM4):
          continue
      #
      # special cases
      elif k._field == 'NUMROWS':
        querytxt = querytxt + "and acs_row_"+querynum+ ".naxis2 = OBS_NAXIS2 "
        continue
      elif k._field == 'NUMCOLS':
        querytxt = querytxt + "and acs_row_"+querynum+ ".naxis1 = OBS_NAXIS1 "
        continue
      elif k._field == 'LTV1':
        querytxt = querytxt + "and acs_row_"+querynum+ ".ltv1 = OBS_LTV1 "
        continue
      elif k._field == 'LTV2':
        querytxt = querytxt + "and acs_row_"+querynum+ ".ltv2 = OBS_LTV2 "
        continue
      # only apply this case for exposures before SM4
      elif k._field == 'CCDAMP' and not beyond_SM4:
        #
        # convert amp A or D reads to AD if size is more than half a chip
        if ((aSource._keywords["CCDAMP"][0] == "A" or
             aSource._keywords["CCDAMP"][0] == "D") and
            aSource._keywords["NUMCOLS"][0] > ACS_HALF_CHIP_COLS):
            opusutil.PrintMsg("I","acs_bias_file_selection: exposure is pre-SM4, converting amp A or D "+
                                  "to AD for NUMCOLS = "+
                                  str(aSource._keywords["NUMCOLS"][0]))
            aSource._keywords["CCDAMP"][0] = "AD"
        #
        # convert amp B reads to BC if size is more than half a chip
        elif ((aSource._keywords["CCDAMP"][0] == "B" or
               aSource._keywords["CCDAMP"][0] == "C") and
              aSource._keywords["NUMCOLS"][0] > ACS_HALF_CHIP_COLS):
            opusutil.PrintMsg("I","acs_bias_file_selection: exposure is pre-SM4, converting amp B or C"+
                                  "to BC for NUMCOLS = "+
                                  str(aSource._keywords["NUMCOLS"][0]))
            aSource._keywords["CCDAMP"][0] = "BC"
      #
      # apply the file selection field
      # (first as a string, but if that fails, as a number converted to string,
      #  since numbers are not quoted but string are)
      try:
        querytxt = (querytxt + "and acs_row_"+querynum+"." +
                 string.lower(k._field) + " = '" + 
                 aSource._keywords[k._field][0] + "' ")
      except TypeError:
        querytxt = (querytxt + "and acs_row_"+querynum+"." +
                 string.lower(k._field) + " = " + 
                 str(aSource._keywords[k._field][0]) + " ")
    #
    return querytxt


  """
=======================================================================
Name: wfpc2_flat_file_selection

Description:
------------
Composes the file selection criteria for a CDBS query of the WFPC2 FLAT
reference file.  Adds a clause for each file selection field that passes 
any (optional) restriction condition.  Special code is needed because
some of the WFPC2 FLAT keywords are not used as actual file selection
fields but ARE used in special tests to set up the selection call
(these are SKIPPED in this routine).

Inputs:
----------
querynum (I) - a number used to indicate which query match is used
thereffile (I) - a reference file object
aSource (I) - an input source object

Returns:
--------
a string containing the file selection clauses for the query

History:
--------
07/08/09 xxxxx MSwam     first version
=======================================================================
  """
  def wfpc2_flat_file_selection(self, querynum, thereffile, aSource):

    querytxt = ""
    #
    # add the file selection fields
    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        opusutil.PrintMsg("D",'found a file select restricted: '+
                               k._restrictions)
        if (not eval(k._restrictions)):
          opusutil.PrintMsg("D","File_selection on "+k._field+
                                " restricted away")
          continue
      #
      # skip these (not used in selection, only elsewhere for special tests)
      if (k._field == 'IMAGETYP' or
          k._field == 'FILTNAM1' or
          k._field == 'FILTNAM2' or
          k._field == 'LRFWAVE') :
          continue
      #
      # apply the file selection field
      # (first as a string, but if that fails, as a number converted to string,
      #  since numbers are not quoted but string are)
      try:
        querytxt = (querytxt + "and wfpc2_row_"+querynum+"." +
                 string.lower(k._field) + " = '" + 
                 aSource._keywords[k._field][0] + "' ")
      except TypeError:
        querytxt = (querytxt + "and wfpc2_row_"+querynum+"." +
                 string.lower(k._field) + " = " + 
                 str(aSource._keywords[k._field][0]) + " ")
    #
    return querytxt


  """
=======================================================================
Name: wfpc2_flatfile_custom

Description:
------------
This customized function composes a database query against the CDBS 
database to find an applicable WFPC2 FLAT reference file.   A special
query is needed because the LRFWAVE keyword value can trigger a set of
hard-coded file selections, and if not, the two filter values can occur in
either order.

Arguments:
----------
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.
Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)

History:
--------
07/08/09 63053 MSwam     Initial version
=======================================================================
  """
  def wfpc2_flatfile_custom(self, thereffile, aSource):
    # the query templates
    # (no need to define these outside, like those for the generic case, since
    #  this routine is only called once per dataset)
    query_template_a = (
       "SELECT max(wfpc2_file_1.file_name) "+
       "FROM wfpc2_file wfpc2_file_1, wfpc2_row wfpc2_row_1 "+
       "WHERE wfpc2_file_1.useafter_date = "+
           "(SELECT max(wfpc2_file_2.useafter_date) "+
           "FROM wfpc2_file wfpc2_file_2, wfpc2_row wfpc2_row_2 "+
               "WHERE wfpc2_file_2.reference_file_type = 'FLT' "+
               "and wfpc2_file_2.useafter_date <= 'EXPOSURE_START' "+
               "and wfpc2_file_2.reject_flag = 'N' "+
               "and wfpc2_file_2.opus_flag = 'Y' "+
               "and wfpc2_file_2.archive_date is not null "+
               "and wfpc2_file_2.opus_load_date is not null "+
               "and wfpc2_file_2.file_name =wfpc2_row_2.file_name "+
               "and wfpc2_file_2.expansion_number = wfpc2_row_2.expansion_number ")
    #
    query_template_b = (
           ") and wfpc2_file_1.reference_file_type = 'FLT' "+
       "and wfpc2_file_1.reject_flag = 'N' "+
       "and wfpc2_file_1.opus_flag = 'Y' "+
       "and wfpc2_file_1.archive_date is not null "+
       "and wfpc2_file_1.opus_load_date is not null "+
       "and wfpc2_file_1.file_name =wfpc2_row_1.file_name "+
       "and wfpc2_file_1.expansion_number = wfpc2_row_1.expansion_number ")

    querytxt = query_template_a

    # fill the exposure start time, after converting keyword value
    # to datetime format from source format
    #
    exposure_start, dontcare = self.find_exposure_start(aSource)
    querytxt = string.replace(querytxt,"EXPOSURE_START", exposure_start)

    # add the file selection fields (row_2)
    querytxt = querytxt + self.wfpc2_flat_file_selection("2", thereffile, 
                                                        aSource)
    # add second template
    querytxt = querytxt + query_template_b
    
    # add the file selection fields again (row_1)
    querytxt = querytxt + self.wfpc2_flat_file_selection("1", thereffile, 
                                                        aSource)
    
    # replace any None values with null
    query1 = string.replace(querytxt, "None", "null")                         

    # get results in a list of lists
    result = [[]]
    self.zombie_select(query1, result)
    if len(result) == 0 or result[0][0] == None:
      #
      # no matching CDBS record found
      opusutil.PrintMsg("E","No matching FLAT found.")
      raise ZeroRowsFound, query1
    #
    # return the first filename found
    return result[0][0]

  """
=======================================================================
Name: wfpc2_flatfile

Description:
------------
This special-purpose function handles the WFPC2 FLATFILE.
In addition to handling the possibility that the WFPC2 filters can occur in 
"normal" or "reversed" order, this routine also include special handling
for linear ramp filters (LRF), which get their flat selected based
on the LRFWAVE keyword.  In fact, because the LRFWAVE selection only
affects a small subset of data, and because it was added during the
final stages of WFPC-2 closeout processing, it was NOT added to 
CDBS, and the names of the actual FLATs applied in these special cases
WILL BE HARD-CODED HERE.

The filter-ordering case is handled by making
a normal lookup first, and if that works then nothing else special
is done.  If it fails, then the order of the filter values is switched
and the query is tried again.  This is needed because the WFPC-2 filter order
is irrelevant for taking and collecting the science data, but is relevant in
the CDBS FLATs that have been delivered.  The delivered FLATS should have
supported the filters in either order, through an expansion, but that was
not done and there are too many of them now to reasonably expect the
entire set to be redelivered to CDBS.

Arguments:
----------
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.
Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)

History:
--------
03/37/03 46981 MSwam     another special case
07/08/09 63053 MSwam     add LRFWAVE handling
08/19/09 63351 MSwam     fix non-existing filter1 or filter2 case
=======================================================================
  """
  def wfpc2_flatfile(self, thereffile, aSource):
    try:
      # SPECIAL HARD-CODED LRFWAVE HANDLING CASE FIRST:
      #
      # If a linear ramp filter is being used, then the flat field
      # filename is HARD-CODED in the block below, and the normal
      # CDBS file selection algorithm is not used, since the LRFWAVE
      # value is not known to CDBS.
      #
      #print("filtnam1="+str(aSource._keywords['FILTNAM1']))
      #print("filtnam2="+str(aSource._keywords['FILTNAM2']))
      if (aSource._keywords['IMAGETYP'][0] == "EXT" and
          ((aSource._keywords['FILTNAM1'] != [None,0] and 
            aSource._keywords['FILTNAM1'][0][0:2] == "FR") or
           (aSource._keywords['FILTNAM2'] != [None,0] and 
            aSource._keywords['FILTNAM2'][0][0:2] == "FR") )):

         opusutil.PrintMsg("I","FLATFILE selection will be based on LRFWAVE value = "+str(aSource._keywords['LRFWAVE'][0]))
         lrfwave = float(aSource._keywords['LRFWAVE'][0])

         # THIS COULD be read from an external file, which would give
         # Ops the chance to override it, if it ever needs changes, but we
         # hear it will not be changed.
         #
         if lrfwave > 3000 and lrfwave <= 4200:
            filename = "M3C10045U.R4H"
         elif lrfwave > 4200 and lrfwave <= 5800:
            filename = "M3C1004FU.R4H"
         elif lrfwave > 5800 and lrfwave <= 7600:
            filename = "M3C1004NU.R4H"
         elif lrfwave > 7600 and lrfwave <= 10000:
            filename = "M3C10052U.R4H"
         else:
            opusutil.PrintMsg("E","FLATFILE selection FAILED for LRFWAVE value = "+aSource._keywords['LRFWAVE'][0])
            filename = " "
         return filename

      # reaching here means this is NOT a LRFWAVE case, 
      #   so use the normal CDBS file selection method first
      #
      filename = self.wfpc2_flatfile_custom(thereffile, aSource)

    except ZeroRowsFound, querytxt:
      # normal query didn't work, try flipping the filters
      tmp = aSource._keywords['FILTER1'][0]
      aSource._keywords['FILTER1'][0] = aSource._keywords['FILTER2'][0]
      aSource._keywords['FILTER2'][0] = tmp
      opusutil.PrintMsg("D","FLATFILE not found for default filter order; now trying them reversed")
      filename = self.wfpc2_flatfile_custom(thereffile, aSource)
    #
    return filename

  """
=======================================================================
Name: acs_biasfile

Description:
------------
This special-purpose function composes a database query against the CDBS 
database to find an applicable ACS BIAS reference file.   A special
query is needed because a search is first made using the image
dimensions of the exposure, which can indicate a sub-array.  If a
corresponding BIAS file does not exist for those dimensions, then a 
second search is made for the default full-frame BIAS file.

Arguments:
----------
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.
Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)

History:
--------
10/01/02 xxxxx MSwam     Initial version
05/27/09 62687 MSwam     add max() to filename select to ensure latest match
03/15/11 67806 MSwam     add beyond_SM4 to acs_bias_file_selection call
=======================================================================
  """
  def acs_biasfile(self, thereffile, aSource):
    # the query templates
    # (no need to define these outside, like those for the generic case, since
    #  this routine is only called once per dataset)
    query_template_a = (
       "SELECT max(acs_file_1.file_name) "+
       "FROM acs_file acs_file_1, acs_row acs_row_1 "+
       "WHERE acs_file_1.useafter_date = "+
           "(SELECT max(acs_file_2.useafter_date) "+
           "FROM acs_file acs_file_2, acs_row acs_row_2 "+
               "WHERE acs_file_2.reference_file_type = 'BIA' "+
               "and acs_file_2.useafter_date <= 'EXPOSURE_START' "+
               "and acs_file_2.reject_flag = 'N' "+
               "and acs_file_2.opus_flag = 'Y' "+
               "and acs_file_2.archive_date is not null "+
               "and acs_file_2.opus_load_date is not null "+
               "and acs_file_2.file_name =acs_row_2.file_name "+
               "and acs_file_2.expansion_number = acs_row_2.expansion_number ")
    #
    query_template_b = (
           ") and acs_file_1.reference_file_type = 'BIA' "+
       "and acs_file_1.reject_flag = 'N' "+
       "and acs_file_1.opus_flag = 'Y' "+
       "and acs_file_1.archive_date is not null "+
       "and acs_file_1.opus_load_date is not null "+
       "and acs_file_1.file_name =acs_row_1.file_name "+
       "and acs_file_1.expansion_number = acs_row_1.expansion_number ")

    querytxt = query_template_a

    # fill the exposure start time, after converting keyword value
    # to datetime format from source format
    #
    exposure_start, beyond_SM4 = self.find_exposure_start(aSource)
    querytxt = string.replace(querytxt,"EXPOSURE_START", exposure_start)                         
    # adjust naxis2 for WFC full-array images
    try:
      obs_naxis2 = aSource._keywords['NUMROWS'][0]
      if (aSource._keywords['DETECTOR'][0] == "WFC" and
          aSource._keywords['XCORNER'][0] == 0 and
          aSource._keywords['YCORNER'][0] == 0) :
        #
        # image is half of the specific size (2 chips)
        obs_naxis2 = obs_naxis2 / 2
    except KeyError:
      # missing key parameters
      opusutil.PrintMsg("E","Key parameters missing for acs_biasfile")
      raise ZeroRowsFound, "missing one of NUMROWS, DETECTOR, XCORNER, YCORNER"

    # add the file selection fields (row_2)
    querytxt = querytxt + self.acs_bias_file_selection("2", thereffile, aSource,
                                                       beyond_SM4)

    # add second template
    querytxt = querytxt + query_template_b
    
    # add the file selection fields again (row_1)
    querytxt = querytxt + self.acs_bias_file_selection("1", thereffile, aSource,
                                                       beyond_SM4)
    
    # replace the place-holders in the query with the real selection values
    query1 = string.replace(querytxt,"OBS_NAXIS1", 
                                       str(aSource._keywords['NUMCOLS'][0]))
    query1 = string.replace(query1,"OBS_NAXIS2", str(obs_naxis2))
    query1 = string.replace(query1,"OBS_LTV1",
                                       str(aSource._keywords['LTV1'][0]))
    query1 = string.replace(query1,"OBS_LTV2",
                                       str(aSource._keywords['LTV2'][0]))

    # replace any None values with null
    query1 = string.replace(query1, "None", "null")                         

    # get results in a list of lists
    result = [[]]
    self.zombie_select(query1, result)
    if len(result) == 0 or result[0][0] == None:
      #
      # no matching CDBS record found for inital search, try full-frame search
      opusutil.PrintMsg("D","No matching BIAS file found for "+
                            "naxis1="+str(aSource._keywords['NUMCOLS'][0])+
                            " naxis2="+str(obs_naxis2)+
                            " ltv1="+str(aSource._keywords['LTV1'][0])+
                            " ltv2="+str(aSource._keywords['LTV2'][0]))
      opusutil.PrintMsg("D","Trying full-frame default search")
      #
      # replace the place-holders with full-frame selection values
      if aSource._keywords['DETECTOR'][0] == "WFC":
        obs_naxis1 = "4144"
        obs_naxis2 = "2068"
        obs_ltv1 = "24.0"
        obs_ltv2 = "0.0"
      else:
        obs_naxis1 = "1062"
        obs_naxis2 = "1044"
        obs_ltv1 = "19.0"
        if (aSource._keywords['CCDAMP'][0] == "C" or
            aSource._keywords['CCDAMP'][0] == "D"):
          obs_ltv2 = "0.0"
        else: # assuming HRC with CCDAMP = A or B
          obs_ltv2 = "20.0"
      query2 = string.replace(querytxt,"OBS_NAXIS1", obs_naxis1)
      query2 = string.replace(query2,"OBS_NAXIS2", obs_naxis2)
      query2 = string.replace(query2,"OBS_LTV1", obs_ltv1)
      query2 = string.replace(query2,"OBS_LTV2", obs_ltv2)
      #
      # get results in a list of lists
      result = [[]]
      self.zombie_select(query2, result)
      if len(result) == 0 or result[0][0] == None:
        #
        # no matching CDBS record found
        opusutil.PrintMsg("E","No full-frame default BIAS found either.")
        raise ZeroRowsFound, query2
    #
    # return the first filename found
    return result[0][0]

  """
=======================================================================
Name: nicmos_saadfile

Description:
------------
This special-purpose function handles the NICMOS SAADFILE.
A normal lookup is made first to find a qualifying SAA Dark reference
file according to the mode/useafter parameters.
After that a check of the TARGNAME value is performed to verify that
the science exposure is an SAA dark (if not, the reference file name
is set to N/A, since this file type only applies to SAA dark exposures).

This special query is needed because the only way to distinguish an SAA
dark exposure is by TARGNAME and that is not one of the mode parameters
in the CDBS database.

Arguments:
----------
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.
Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)

History:
--------
09/21/06 56376 MSwam     first version
=======================================================================
  """
  def nicmos_saadfile(self, thereffile, aSource):
    filename = self.find_reffile("NICMOS", thereffile, aSource)
    try:
      if aSource._keywords['TARGNAME'][0] != "POST-SAA-DARK":
        opusutil.PrintMsg("D","nicmos_saadfile: targname not a post-saa-dark:"+
                      str(aSource._keywords['TARGNAME'])+", so saadfile=N/A")
        return "N/A"
    except KeyError:
      opusutil.PrintMsg("I","nicmos_saadfile: TARGNAME keyword not found.")
      opusutil.PrintMsg("I","nicmos_saadfile: SAADFILE will be filled by CDBS .")
      return None
    #
    return filename


  """
=======================================================================
Name: missing_reffile

Description:
------------
This function uses the reference file information and possibly
some keyword values to decide if the failure to find a value for this
particular reference file is an error, or OK.

The .required flag is checked, and if not set things are OK.
However if the file is required, then if the calibration switch is OMIT then 
things are OK.  In either OK case, the provided default value is 
returned as the reference file name.  If things are not OK, an error
message is printed using the text provided, and an exception is
raised.

Arguments:
----------
reff (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.
message (I) - a string holding the message that will be printed if the
                 missing reference file is considered an error
default_value (I) - the default name for the missing reference file
                    (e.g. N/A, " ", etc.)
Returns:
--------
filename - default name of the reference file, since none was found

History:
--------
10/01/02 xxxxx MSwam     Initial version
07/09/04 51057 MSwam     Handle NO as "required" value (as well as empty)
=======================================================================
  """
  def missing_reffile(self, reff, aSource, message, default_value):
    opusutil.PrintMsg("D","required="+str(reff._required))
    if (not reff._required) or reff._required == "NO":
      #
      # this is not a required file, no problem
      opusutil.PrintMsg("D",str(reff._keyword)+" NOT required")
      opusutil.PrintMsg("D",str(message))
      return default_value
  
    # the reference file IS required; see if there is a corresponding
    # calibration switch and its value is OMIT
    #
    if (reff._switch and aSource._keywords.has_key(reff._switch) and
        aSource._keywords[reff._switch][0] == "OMIT"):
      #
      # the file is not required since the switch is OMIT, no problem
      opusutil.PrintMsg("W",reff._switch+" = OMIT, "+reff._keyword+ 
                            " NOT required")
      return default_value
  
    # the reference file should have been found, print the error message
    # and raise an exception
    #
    opusutil.PrintMsg("E","Missing "+str(reff._keyword))
    opusutil.PrintMsg("E",str(message))
    raise MissingRequiredFile

  """
=======================================================================
Name: get_new_cal_files

Description:
------------
This function composes database queries against the CDBS database to
read the entries in the new_cal_files table and verify they are
ready for processing.  It returns a list of new_cal_files entries 
THAT ALSO have a non-null opus_load_date field in their
SI_file table.

An open database object is passed in for running the query.

Returns:
--------
newfiles - list of filenames and expansion numbers for the new ref files
           that are ready for processing (have non-NULL opus_load_date)

History:
--------
10/01/02 xxxxx MSwam     Initial version
07/27/11 68982 MSwam     replace !=NULL with IS NOT NULL
=======================================================================
  """
  def get_new_cal_files(self):
    # first get the candidate entries from new_cal_files
    querytxt = "SELECT file_name, expansion_number from new_cal_files"
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    #
    # for each candidate, delete it from the list if its opus_load_date
    # field is not yet filled
    loopcount = len(result)
    opusutil.PrintMsg("D","loopcount="+str(loopcount))
    i = 0
    while i < loopcount:
      opusutil.PrintMsg("D","i="+str(i))
      #
      # identify CDBS "instrument" (can include SYNPHOT and MULTI)
      cdbs_inst = siname.WhichCDBSInstrument(result[i][0])
      cdbs_prefix = siname.get_cdbs_prefix(cdbs_inst)
      #
      # build the db query
      querytxt = ("SELECT COUNT(*) FROM "+cdbs_prefix+"_file WHERE "+
                  "file_name = '"+result[i][0]+"' and opus_load_date is not NULL")
      #
      # get count in a list of lists
      count = [[]]
      self.zombie_select(querytxt, count)
      if count[0][0] <= 0:
        opusutil.PrintMsg("I","new_cal_files: "+result[i][0]+",expansion="+
                          str(result[i][1])+" not OPUS-ready.")
        # remove it from the candidate list,
        # shrink the loop limit and leave loop count unadjusted to process
        # the next entry 
        del result[i]
        loopcount = loopcount - 1
      else:
        i = i + 1
    #
    # return the entries found
    return result

  """
=======================================================================
Name: get_ref_file_type

Description:
------------
This function composes a database query against the CDBS database to
determine the reference file type for a given reference file.

The instrument name is used to determine which CDBS relation needs
querying.

An open database object is passed in for running the query.

Inputs:
----------
inst (I)       - the CDBS "instrument" name
reffilename (I) - name of the reference file

Returns:
--------
ref_file_type - the type of reference file that reffilename is

History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
  """
  def get_ref_file_type(self, inst, reffilename):
    querytxt = ("SELECT DISTINCT reference_file_type FROM "+
                siname.get_cdbs_prefix(inst)+
                "_file WHERE file_name = '"+string.upper(reffilename)+"'")
    
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    #
    # more than one entry is an error
    if len(result) > 1:
      raise MultipleRefFileTypes
    #
    # return the entry found
    return result[0]

  """
=======================================================================
Name: wfc3_bias file_selection

Description:
------------
Composes the file selection criteria for a CDBS query of the WFC3
BIAS reference file.  Adds a clause for each file selection field that passes 
any (optional) restriction condition.  Special code is needed because
some of the WFC3 BIAS keywords are not used as actual file selection
fields but ARE used in special tests to set up the selection call
(these are SKIPPED in this routine).

Inputs:
----------
querynum (I) - a number used to indicate which query match is used
thereffile (I) - a reference file object
aSource (I) - an input source object

Returns:
--------
a string containing the file selection clauses for the query

History:
--------
03/03/09 62083 MSwam     first version
=======================================================================
  """
  def wfc3_bias_file_selection(self, querynum, thereffile, aSource):

    querytxt = ""
    #
    # add the file selection fields
    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        opusutil.PrintMsg("D",'found a file select restricted: '+
                               k._restrictions)
        if (not eval(k._restrictions)):
          opusutil.PrintMsg("D","File_selection on "+k._field+
                                " restricted away")
          continue
      #
      # skip these (not used in selection, only elsewhere for special tests)
      if (k._field == 'SUBARRAY'):
          continue
      #
      # special case: APERTURE is NOT a selection field for custom subarrays
      #                        but IS for every other mode
      #
      if (k._field == 'APERTURE' and 
          aSource._keywords["SUBARRAY"] == "T" and
          aSource._keywords["APERTURE"].find("SUB") == -1):

          # this is a custom subarray, so do NOT use APERTURE for file select
          continue
      #
      # apply the file selection field
      # (first as a string, but if that fails, as a number converted to string,
      #  since numbers are not quoted but string are)
      try:
        querytxt = (querytxt + "and wfc3_row_"+querynum+"." +
                 string.lower(k._field) + " = '" + 
                 aSource._keywords[k._field][0] + "' ")
      except TypeError:
        querytxt = (querytxt + "and wfc3_row_"+querynum+"." +
                 string.lower(k._field) + " = " + 
                 str(aSource._keywords[k._field][0]) + " ")
    #
    return querytxt

  """
=======================================================================
Name: wfc3_biasfile

Description:
------------
This special-purpose function composes a database query against the CDBS 
database to find an applicable WFC3 BIAS reference file.   A special
query is needed because the APERTURE keyword must be added as a 
search field for MOST exposure modes, with the exception of custom-sized
(available, but unsupported) subarrays, and detecting these custom
subarrays can't be done in the standard reference file selection rules.

Arguments:
----------
thereffile (I) - a Reffile object containing information about the reference
                 file and its selection parameters
aSource (I)   - Input source object containing a dictionary of 
                 keyword name/value pairs.  These form the
                 inputsource for the database query parameters.
Returns:
--------
reference_filename - name of the first reference file found by the DB query
                     (normally only one is found)

History:
--------
03/02/09 62083 MSwam     Initial version
05/27/09 62687 MSwam     add max() to filename select to ensure latest match
=======================================================================
  """
  def wfc3_biasfile(self, thereffile, aSource):
    # the query templates
    # (no need to define these outside, like those for the generic case, since
    #  this routine is only called once per dataset)
    query_template_a = (
       "SELECT max(wfc3_file_1.file_name) "+
       "FROM wfc3_file wfc3_file_1, wfc3_row wfc3_row_1 "+
       "WHERE wfc3_file_1.useafter_date = "+
           "(SELECT max(wfc3_file_2.useafter_date) "+
           "FROM wfc3_file wfc3_file_2, wfc3_row wfc3_row_2 "+
               "WHERE wfc3_file_2.reference_file_type = 'BIA' "+
               "and wfc3_file_2.useafter_date <= 'EXPOSURE_START' "+
               "and wfc3_file_2.reject_flag = 'N' "+
               "and wfc3_file_2.opus_flag = 'Y' "+
               "and wfc3_file_2.archive_date is not null "+
               "and wfc3_file_2.opus_load_date is not null "+
               "and wfc3_file_2.file_name =wfc3_row_2.file_name "+
               "and wfc3_file_2.expansion_number = wfc3_row_2.expansion_number ")
    #
    query_template_b = (
           ") and wfc3_file_1.reference_file_type = 'BIA' "+
       "and wfc3_file_1.reject_flag = 'N' "+
       "and wfc3_file_1.opus_flag = 'Y' "+
       "and wfc3_file_1.archive_date is not null "+
       "and wfc3_file_1.opus_load_date is not null "+
       "and wfc3_file_1.file_name =wfc3_row_1.file_name "+
       "and wfc3_file_1.expansion_number = wfc3_row_1.expansion_number ")

    querytxt = query_template_a

    # fill the exposure start time, after converting keyword value
    # to datetime format from source format
    #
    exposure_start, dontcare = self.find_exposure_start(aSource)
    querytxt = string.replace(querytxt,"EXPOSURE_START", exposure_start)

    # add the file selection fields (row_2)
    querytxt = querytxt + self.wfc3_bias_file_selection("2", thereffile, 
                                                        aSource)
    # add second template
    querytxt = querytxt + query_template_b
    
    # add the file selection fields again (row_1)
    querytxt = querytxt + self.wfc3_bias_file_selection("1", thereffile, 
                                                        aSource)
    
    # replace any None values with null
    query1 = string.replace(querytxt, "None", "null")                         

    # get results in a list of lists
    result = [[]]
    self.zombie_select(query1, result)
    if len(result) == 0 or result[0][0] == None:
      #
      # no matching CDBS record found
      opusutil.PrintMsg("E","No matching BIAS found.")
      raise ZeroRowsFound, query1
    #
    # return the first filename found
    return result[0][0]

  """
=======================================================================
Name: cdbs_report

Description:
------------
This function creates a report for cdbs installation.  It looks for a
delivery number in multiple instrument tables.  When found, will create
a list of results with the delivery number.  The results will be passed
to a formatting method and printed.

Arguments:
----------
delivery_number - Integer describing the delivery number to be looked up

Returns:
--------
Result set? - Two dimensional array of rows from the results
Print?      - Format and print these rows

History:
--------
08/12/10 PR ????? RBelt Initial Revision
========================================================================
  """

  def cdbs_report(self,delivery_number):
    file_dict = {'hrs_file': 'HRS',
                 'foc_file': 'FOC',
                 'wfpc2_file': 'WFPC2',
                 'fos_file': 'FOS',
                 'nic_file': 'NIC',
                 'stis_file': 'STIS',
                 'acs_file': 'ACS',
                 'wfc3_file': 'WFC3',
                 'cos_file': 'COS',
                 'synphot_file': 'SYNPHOT'
                }
    active_file = ""
    for file in file_dict.keys():
      result = [[]]
      query = "select file_name from "+file+" where delivery_number="+delivery_number
      result = self.zombie_select(query,result)
      if(result):
        active_file = file
        print "Found results in instrument "+file
        break

    result=[[]]

    query = ("select file_name,opus_load_date,archive_date,reference_file_type,useafter_date from "+
             active_file+" where delivery_number="+delivery_number+" and expansion_number<2")
    result = self.zombie_select(query,result)
    row = self.format_cdbs_report(file_dict[active_file],result)
    print row
#    return result

  """

History:
--------
08/12/10 PR ????? RBelt Initial Revision
=========================================================================
  """

  def format_cdbs_report(self,inst,result):
    instrument     = 13
    ref_file_type  = 15
    file_name      = 21
    useafter_date  = 21
    archive_date   = 21
    opus_load_date = 13

    formatted_row = "Instrument  Reference  File Name                    Useafter Date              Archive Date             Opus Load Date\n"
    formatted_row += "                  File Type\n"
    formatted_row += "---------------  ---------------  -----------------------------      -------------------------------  -----------------------------   -----------------------------\n"
    for row in result:
      formatted_row += str(inst)
      for i in range(0,instrument-len(str(inst))):
        formatted_row += " "
      formatted_row += str(row[3])
      for i in range(0,ref_file_type-len(str(row[3]))):
        formatted_row += " "
      formatted_row += str(row[0])
      for i in range(0,file_name-len(str(row[0]))):
        formatted_row += " "
      formatted_row += str(row[4])
      for i in range(0,useafter_date-len(str(row[4]))):
        formatted_row += " "
      formatted_row += str(row[2])
      for i in range(0,archive_date-len(str(row[2]))):
        formatted_row += " "
      formatted_row += str(row[1])
      formatted_row +="\n"

    return formatted_row

#========================================================================
# TEST 
# % python cdbsquery.py
#
# 07/15/10 57271 MSwam     remove db retry parameter
#========================================================================
if __name__ == "__main__":
  opusutil.PrintMsg("I","Starting...")
  the_master = instReferenceFileDefs.InstReferenceFileDefs()
  instrument = instReferenceFileDefs.InstReferenceFiles("ACS")
  reffile = instReferenceFileDefs.Reffile("FLS","FLSHFILE","IMAGE")
  reffile._file_selections.append(instReferenceFileDefs.Selection("DETECTOR"))
  reffile._file_selections.append(instReferenceFileDefs.Selection("CCDAMP"))
  instrument.append(reffile)
  the_master.append(instrument)

  instrument = the_master.find_instrument("ACS")
  search_type = "FLS"
  reff = instrument.find_reffile(search_type)
  reff.dump()

  kw_db = kwdbquery.Kw_db(os.environ['KW_SERVER'], 
                          os.environ['KW_DB'])
  arch_db = hst_archdbquery.HST_Arch_db(os.environ['ARCH_SERVER'], 
                                os.environ['ARCH_DB'])
  all_keywords = instrument.all_keywords()
  all_keywords.append("EXPSTART")
  dataset_name = "J8CW08011"
  opusutil.PrintMsg("I","DBs opens and set-up complete...")
  Sources = datasources.DBsources(all_keywords, dataset_name, kw_db, arch_db)
  # connect to CDBS db
  cdbs_db = Cdbs_db(os.environ['REFFILE_SERVER'], 
                    os.environ['REFFILE_DB'])
  for aSource in Sources._sources:
    opusutil.PrintMsg("I","Trying "+str(aSource))
    reffilename = cdbs_db.find_reffile(instrument._name, reff, aSource)
    opusutil.PrintMsg("I", dataset_name + ": " +search_type+
                           ' reffile = '+reffilename)
  #
  testfile = "M9D1040MJ_BPX.FITS"
  opusutil.PrintMsg("I", testfile+' ref file type='+
    str(cdbs_db.get_ref_file_type("ACS", testfile)))
  kw_db.close()
  arch_db.close()
  cdbs_db.close()
