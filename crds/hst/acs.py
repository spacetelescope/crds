"""Master ACS hooks module,  importer of versioned hooks."""

from .acs_v1 import precondition_header_acs_biasfile_v1  # , acs_biasfile_filter
from .acs_v2 import precondition_header_acs_biasfile_v2, fallback_header_acs_biasfile_v2, acs_biasfile_filter, acs_darkfile_filter

#
# This section contains relevant code from cdbsquery.py and explanation,  such as it is.
# cdbsquery.py was/is part of CDBS.  This module is about capturing those quirks in different
# ways for CRDS.
#
'''
This is special case code which CDBS implements in cdbsquery.py
(see crds/hst/cdbs/cdbs_bestrefs/cdbsquery.py or get the latest from Mike Swam / OPUS)

Fundamentally, cdbsquery searches the reference file database
(reffile_ops...) which enumerates how specific dataset header
configurations map onto reference files.  Each row of reffile_ops maps
one instrument configuration and date onto the reference file which
handles it.  Some files are used in many rows.  Each column of a row
specifies the value of a particular parameter.

reffile_ops matching parameters, and other things,  are specified in the CDBS file
reference_file_defs.xml.   Parameters listed here are important in some way for
matching.

Ideally,  CDBS and CRDS implement something like:

   match(dataset parameters, reference parameters) --> reference.

Here dataset and reference correspond to the tuples of relevant header values
or database values.  1:1,  match them up,  shebang.

CDBS does the matching as a single SQL query against refile_ops...  cdbsquery
builds the SQL which constrains each parameter to the configuration of one dataset.

CRDS encodes the matching parameters of reference_file_ops in a
more compact way,  the rmaps.   The rmaps are interpreted by CRDS code
in selectors.py rather than by a SQL engine.

In practice,  CDBS special case code like that below does this:

   match(f(dataset parameters), reference parameters) -->  reference or g(dataset)

There are a few kinds of hacks:

1. The special case code excludes some dataset parameters from
matching in the reference database.  There might be no column for that
parameter but it is needed later.

2. The special case code fudges some of the dataset parameters,
replacing dataset[X] with f(dataset),  where the fudged value of one
matching parameter may depend on the value of many other parameters.

3. Sometimes fallback code,  g(dataset),  is used as a secondary solution
when the primary solution fails to obtain a match.

In CDBS:

"dataset" can come from the dadsops database (there are many servers and variants).

"dataset" can come from a FITS header.

At match time,  "reference" comes from the reffile_ops database.   Matching is
done by doing a gigantic anded SQL query which equates reffile_ops columns with
specific dataset values,  doing a gigantic anded SQL query,  and also choosing
the maximum applicable USEAFTER.  In cdbsquery,  the query is built one
parameter at a time.   Some parameters are omitted from the query.

At new reference submission time, "reference" comes from the ref file
header and is exploded in to refile_ops database rows.

In CRDS:

"dataset" comes from the same places, either a database or dataset file header.

At rmap generation time,  "reference" comes from the reffile_ops database and
is encoded into rmaps.

At new file submission time, "reference" comes from the reference file
headers and must be appropriately matched against rmaps to see where
to insert or replace files.   This is batch reference submission / refactoring.

At match time, essentially "reference" comes from the rmaps and
matching is done by recursively executing CRDS selector.py Selector code
on nested selectors.

# ================================================================================

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

    except Exception:
      traceback.print_exc()
      opusutil.PrintMsg("E","Failed time conversion for exposure start.")
      raise FailedTimeConversion
    #
    return exposure_start, beyond_SM4


  def acs_bias_file_selection(self, querynum, thereffile, aSource, beyond_SM4):
    querytxt = ""
    #
    # add the file selection fields
    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        opusutil.PrintMsg("D",'found a file select restricted: '+
                               k._restrictions)
        if (not eval(k._restrictions)):    # CDBS code comment
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
'''
