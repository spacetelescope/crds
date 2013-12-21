"""This module defines CRDS customizations for the HST ACS instrument."""

import sys

from crds import log, utils, timestamp

from collections import defaultdict

# ===========================================================================    

#   This section contains matching customizations.

ACS_HALF_CHIP_COLS = 2048         #used in custom bias selection algorithm

SM4 = timestamp.reformat_date("2009-05-14 00:00:00.000000")
# date beyond which an exposure was
# taken in the SM4 configuration
# (day 2009.134 = May 14 2009,
#  after HST was captured by 
#  the shuttle during SM4, and
#  pre-SM4 exposures had ceased)

def precondition_header(rmap, header):
    """This is the original buggy header preconditioning function for ACS which
    applied to all types but only really affected BIASFILE.  It mutates dataset headers
    prior to performing bestrefs matching.   It is located and called by default when
    the rmap says nothing about hooks.
    """
    header = dict(header)
    if rmap.filekind == "biasfile":
        return precondition_header_biasfile_v1(rmap, header)
    else:
        return header
    
def precondition_header_biasfile_v1(rmap, header_in):
    """Mutate the incoming dataset header based upon hard coded rules
    and the header's contents.   This is an alternative to generating
    an equivalent and bulkier rmap.
    """
    header = dict(header_in)
    log.verbose("acs_biasfile_precondition_header:", header)
    exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
    if (exptime < SM4):
        #if "APERTURE" not in header or header["APERTURE"] == "UNDEFINED":
        log.verbose("Mapping pre-SM4 APERTURE to N/A")
        header["APERTURE"] = "N/A"
    try:
        numcols = int(float(header["NUMCOLS"]))
    except ValueError:
        log.verbose("acs_biasfile_selection: bad NUMCOLS.")
        sys.exc_clear()
    else:
        header["NUMCOLS"] = utils.condition_value(str(numcols))
        # if pre-SM4 and NUMCOLS > HALF_CHIP
        exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
        if (exptime < SM4):
            if numcols > ACS_HALF_CHIP_COLS:
                if header["CCDAMP"] in ["A","D"]: 
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp A or D " +
                                "to AD for NUMCOLS = " + header["NUMCOLS"])
                    header["CCDAMP"] = "AD"
                elif header["CCDAMP"] in ["B","C"]:  
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp B or C " +
                                "to BC for NUMCOLS = " + header["NUMCOLS"])
                    header["CCDAMP"] = "BC"
    if header['DETECTOR'] == "WFC" and \
        header['XCORNER'] == "0.0" and header['YCORNER'] == "0.0":
        log.verbose("acs_biasfile_selection: precondition_header halving NUMROWS")
        try:
            numrows = int(float(header["NUMROWS"])) / 2
        except ValueError:
            log.verbose("acs_biasfile_selection: bad NUMROWS.")
            sys.exc_clear()
        else:
            header["NUMROWS"] = utils.condition_value(str(numrows)) 
    return header     # XXXXXX RETURN NOW !!!!

# ===========================================================================    

#   This section contains generation and update customizations.

"""
def _fallback_biasfile(header_in):
    header = _precondition_header_biasfile(header_in)
    log.verbose("No matching BIAS file found for",
               "NUMCOLS=" + repr(header['NUMCOLS']),
               "NUMROWS=" + repr(header['NUMROWS']),
               "LTV1=" + repr(header['LTV1']),
               "LTV2=" + repr(header['LTV2']))
    log.verbose("Trying full-frame default search")
    if header['DETECTOR'] == "WFC":
        header["NUMCOLS"] = "4144.0"
        header["NUMROWS"] = "2068.0"
        header["LTV1"] = "24.0"
        header["LTV2"] = "0.0"
    else:
        header["NUMCOLS"] = "1062.0"
        header["NUMROWS"] = "1044.0"
        header["LTV1"] = "19.0"
        if header['CCDAMP'] in ["C","D"]:
            header["LTV2"] = "0.0"
        else: # assuming HRC with CCDAMP = A or B
            header["LTV2"] = "20.0"
    return header

def fallback_header(rmap, header):
    return None
    if rmap.filekind == "biasfile":
        # log.info("x", end="",sep="")
        return _fallback_biasfile(header)
    else:
        None
"""

BIASFILE_PARKEYS = ('DETECTOR', 'CCDAMP', 'CCDGAIN', 'APERTURE', 'NAXIS1', 'NAXIS2', 
                    'LTV1', 'LTV2', 'XCORNER', 'YCORNER', 'CCDCHIP')

def rmap_update_headers_acs_biasfile_v1(rmap, header_in):
    """Given a reference file header specifying the applicable cases for a reference,  this generates
    a weaker match case which may apply when the primary match fails.  Called to update rmaps
    with "fallback cases" when a file is submitted to the CRDS web site and it updates the rmap,
    in addition to the primary match cases from the unaltered header_in.  
    """
    header = dict(header_in)
    
    header["EXPTIME"] = timestamp.reformat_date(header_in["DATE-OBS"] + " " + header_in["TIME-OBS"])
    
    # 1. Simulate CDBS header pre-conditioning by mutating rmap and primary match
    
    if matches(header, EXPTIME=("<=", SM4)):
        header["APERTURE"] = "N/A"
    elif header["APERTURE"].strip() == "":
        header["APERTURE"] = "N/A"
        log.warning("rmap_update_headers_acs_biasfile_v1:  Changing APERTURE=='' to 'N/A'.")
    
    if matches(header, EXPTIME=("<=",SM4), NAXIS1=(">","2048"), CCDAMP="A"):
        header["CCDAMP"] = "AD"
    elif matches(header, EXPTIME=("<=",SM4), NAXIS1=(">","2048"), CCDAMP="D"):
        header["CCDAMP"] = "AD"
    elif matches(header, EXPTIME=("<=",SM4), NAXIS1=(">","2048"), CCDAMP="B"):
        header["CCDAMP"] = "BC"    
    elif matches(header, EXPTIME=("<=",SM4), NAXIS1=(">","2048"), CCDAMP="C"):
        header["CCDAMP"] = "BC"
    
    # CDBS was written from the dataset perspective,  so it halved dataset naxis2 to match reference naxis2
    # This code is adjusting the reference file perspective,  so it doubles reference naxis2 to match dataset naxis2
    # This change only applies to the first attempt.
    
    del header_1["EXPTIME"]
    header_1 = dict(header)
    if matches(header_1, DETECTOR="WFC", XCORNER="0.0", YCORNER="0.0"):
        with log.warn_on_exception("rmap_update_headers_acs_biasfile_v1: bad NAXIS2"):
            naxis2 = int(float(header_1["NAXIS2"]))
            header_1["NAXIS2"] = naxis2*2

    show_header_mutations(header_in, header_1)
    yield header_1

    # 2. Simulate full frame fallback search
    
    # The inverse of jamming the dataset header with canned matching values is
    # jamming the reference header with N/A's for those variables.   Thus,  when
    # a dataset header appears with any value,   it is matched against N/A, and
    # works the same as if it had been jammed to a value matching the reference.
    # Since N/A is weighted lower than a true match,  it acts as a fall-back if a
    # real match is also present.
    
    if matches(header, DETECTOR='WFC', NAXIS1='4144.0', NAXIS2='2068.0', LTV1='24.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='C', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='D', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='C|D', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='0.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])  
    elif matches(header, DETECTOR='HRC', CCDAMP='A', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='20.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='B', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='20.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    elif matches(header, DETECTOR='HRC', CCDAMP='A|B', NAXIS2='1044.0', NAXIS1='1062.0', LTV1='19.0', LTV2='20.0'):
        header = dont_care(header, ['NAXIS2','NAXIS1','LTV1', 'LTV2'])
    else:
        header = None
    
    if header is not None:
        show_header_mutations(header_in, header)
        yield header

def matches(header, **keys):
    """Nominally check each element of **keys for equality with the same key in `header`.
    
    If a value in **keys is a tuple, it should be of the form (operator_str, value) and the
    expression will be evaluated with respect to `header`.
    """
    header = { key:utils.condition_value(val) for (key,val) in header.items() }
    for var, val in keys.items():
        if isinstance(val, tuple):
            op, val = val
        else:
            op = "=="
        if not evaluate(var + op + repr(val), header, var):
            return False
    return True

def evaluate(expr, header, var):
    """eval `expr` with respect to `var` in `header`."""
    rval = eval(expr, {}, header)
    log.verbose("evaluate:", repr(expr), "-->", rval, expr.replace(var, repr(header[var])))
    return rval

def dont_care(header, vars):
    """Set vars in header to N/A."""
    header = dict(header)
    for var in vars:
        header[var] = "N/A"
    return header

def show_header_mutations(header_in, header):
    """Print out keys which changed between header_in and header."""
    for key in header:
        if key in header_in:
            if header[key] != header_in[key]:
                log.info("mutating", repr(key), header_in[key], "-->", header[key])
        else:
            log.info("mutating", repr(key), "added as", header[key])
    for key in header_in:
        if key not in header:
            log.info("mutating", repr(key), "deleted as", header_in[key])

# =============================================================================================

# This section contains RMAP GENERATION code. It is unversioned, plugging into hst_gentools/gen_rmap.py and
# running only at rmap generation time during system bootstrap.  It is closely related to 
# reference_match_fallback_header_biasfile which runs at rmap update time to add new files.

def acs_biasfile_filter(kmap):
    """APERTURE was added late as a matching parameter and so many existing references
    have an APERTURE value of '' in CDBS.   Where it's relevant,  it's actually defined.
    Here we change '' to * to make CRDS ignore it when it doesn't matter.   We also change 
    APERTURE to * for any useafter date which precedes SM4 (possibly they define APERTURE).
    
    add_fallback_to_kmap() duplicates the correct filemaps to simulate the fallback header lookup.
    """
    start_files = total_files(kmap)
    
    kmap2 = defaultdict(set)
    for match, fmaps in kmap.items():
        header = dict(zip(BIASFILE_PARKEYS, match))
        for f in fmaps:
            header["DATE-OBS"], header["TIME-OBS"] = f.date.split()
            for alt in rmap_update_headers_acs_biasfile_v1(None, header):
                new_match = tuple(alt[key] for key in BIASFILE_PARKEYS)
                kmap2[new_match].add(f)
    kmap2 = { match:sorted(kmap2[match]) for match in kmap2 }
    
    log.verbose("Final ACS BIASFILE kmap:\n", log.PP(kmap2))
                                           
    header_additions = [
        ("hooks",  {
            "precondition_header" : "none",
            "rmap_update_headers" : "rmap_update_headers_acs_biasfile_v1",
        }),
    ]

    dropped_files = start_files - total_files(kmap2)
    if dropped_files:  # bummer,  bug in my code...
        log.error("Dropped files:", sorted(dropped_files))

    return kmap2, header_additions

def total_files(kmap):
    total = set()
    for match, fmaps in kmap.items():
        total = total.union(set([fmap.file for fmap in fmaps]))
    return total
        
# =============================================================================================
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

'''
