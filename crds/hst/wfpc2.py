"""This module defines rmap matching and generation customizations for WFPC2."""

from crds.core import log, rmap

'''
def _precondition_header_flatfile(header_in):
    """Mutate the incoming dataset header based upon hard coded rules
    and the header's contents.
    """
    header = dict(header_in)
    subarray = header["SUBARRAY"]
    aperture = header["APERTURE"]
    if subarray == "T" and "SUB" not in aperture:
        header["APERTURE"] = "*"
    return header

def precondition_header(rmap, header):
    if rmap.filekind == "flatfile":
        return _precondition_header_flatfile(header)
    else:
        return header
'''

def fallback_header_wfpc2_flatfile_v1(rmap, header):
    """Compute a fallback header for WFPC2 BIASFILE."""
    filter1 = header["FILTER1"]
    filter2 = header["FILTER2"]
    log.verbose("Computing fallback header wfpc2 ", rmap.filekind,
                "swapping filter1 was" , filter1, "filter2 was", filter2)
    header["FILTER1"] = filter2
    header["FILTER2"] = filter1
    return header

'''
         if lrfwave > 3000 and lrfwave <= 4200:
            filename = "M3C10045U.R4H"
         elif lrfwave > 4200 and lrfwave <= 5800:
            filename = "M3C1004FU.R4H"
         elif lrfwave > 5800 and lrfwave <= 7600:
            filename = "M3C1004NU.R4H"
         elif lrfwave > 7600 and lrfwave <= 10000:
            filename = "M3C10052U.R4H"
'''

def wfpc2_flatfile_filter(kmap):
    log.info("Hacking WFPC2 Flatfile.")
    # :  ('MODE', 'FILTER1', 'FILTER2', 'IMAGETYP', 'FILTNAM1', 'FILTNAM2', 'LRFWAVE'), ('DATE-OBS', 'TIME-OBS')),
    kmap[('*',    '*',       '*',       'EXT',       'FR*',     '*',      '# >3000 and <=4200 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c10045u.r4h', comment='')]
    kmap[('*',    '*',       '*',       'EXT',       '*',     'FR*',      '# >3000 and <=4200 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c10045u.r4h', comment='')]

    kmap[('*',    '*',       '*',       'EXT',       'FR*',     '*',      '# >4200 and <=5800 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c1004fu.r4h', comment='')]
    kmap[('*',    '*',       '*',       'EXT',       '*',     'FR*',      '# >4200 and <=5800 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c1004fu.r4h', comment='')]

    kmap[('*',    '*',       '*',       'EXT',       'FR*',     '*',      '# >5800 and <=7600 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c1004nu.r4h', comment='')]
    kmap[('*',    '*',       '*',       'EXT',       '*',     'FR*',      '# >5800 and <=7600 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c1004nu.r4h', comment='')]

    kmap[('*',    '*',       '*',       'EXT',       'FR*',     '*',      '# >7600 and <=10000 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c10052u.r4h', comment='')]
    kmap[('*',    '*',       '*',       'EXT',       '*',     'FR*',      '# >7600 and <=10000 #')] = \
           [rmap.Filemap(date='1990-01-01 00:00:00', file='m3c10052u.r4h', comment='')]

    header_additions = [
        ("hooks", {
            "fallback_header" : "fallback_header_wfpc2_flatfile_v1",
        }),
    ]

    return kmap, header_additions


'''
      def wfpc2_flat_file_selection(self, querynum, thereffile, aSource):

    querytxt = ""
    #
    # add the file selection fields
    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        opusutil.PrintMsg("D",'found a file select restricted: '+
                               k._restrictions)
        if (not eval(k._restrictions)):   # CDBS comment code
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
'''
