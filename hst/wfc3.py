"""
The special case handlers for WFC3 are now obsolete and this file does 
essentially nothing.   It is left as an illustration of implementing
rmap header substitutions,  dataset driven header overrides, and hard-coded
HST rmap files.
"""

import crds.log as log
import crds.rmap as rmap

# =======================================================================

"""
Header substitution notes:
--------------------------

The original CRDS rmap generator scraped rmap information from the CDBS web 
pages.   The CDBS web pages displayed un-expanded aperture values.   Later
CRDS switched to generating rmaps from the expanded rows found in the CDBS
database reffile_ops.   The expanded rows effectively have the substitutions
specified below already implemented.

Testing with the biasfile special case code found that it gives the wrong
answers for hundreds of cases.  Disabling the special case code reduced the
biasfile error count against the catalog to 26 over all datasets.  Further
refining best reference error counts using OPUS reduced the error counts
further,  possibly to zero,  indicating that the special case handling should
simply be turned off.

** See WFC3 TIR-2009-03, Changes to CDBS expansion and selection criteria
   for WFC3 UVIS bias reference files

DETECTOR = UVIS

For WFC3,  the aperture value listed in the reference file is expanded into
many CDBS records with replacement APERTUREs.  Best Reference matches the
APERTURE value in the dataset to the APERTURE value in CDBS records... not the
unexpanded APERTURE from the reference file header.

WFC3_EXPANDED_APERTURES as the form:

  {  (BINAXIS1, BINAXIS2, APERTURE)   :  [APERTURE_EXPANSIONS]  }

CRDS expands the reference file APERTURE at rmap creation time.

NOTE:  since switching to database driven rmap creation,  the substitution
source values no longer appear in the rmaps.

"""



header_substitutions = {
    "APERTURE" : {
        "FULLFRAME_4AMP" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER", "UVIS-QUAD","UVIS-QUAD-FIX","G280-REF",
        ),
        "QUAD_CORNER_SUBARRAYS" : (
            "UVIS-QUAD-SUB",
            "UVIS1-C512A-SUB", "UVIS1-C512B-SUB",
            "UVIS2-C512C-SUB", "UVIS2-C512D-SUB",
        ),
        "CHIP1_SUB_NOCORNERS" : (
            "UVIS1-2K4-SUB", "UVIS1-M512-SUB",
        ),
        "CHIP2_SUB_NOCORNERS" : (
            "UVIS2-2K4-SUB", "UVIS2-M512-SUB",
        ),
        "FULLFRAME_2AMP" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER",
        ),
        "CUSTOM_SUBARRAYS" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER", "UVIS-QUAD", "UVIS-QUAD-FIX", "G280-REF"
        ),
        "*" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER", "UVIS-QUAD", "UVIS-QUAD-FIX", "G280-REF"
        ),
    },
    'CCDAMP' : {
        'G280_AMPS' : ('ABCD','A','B','C','D','AC','AD','BC','BD'), 
    },
}

header_additions = [
    ("substitutions", header_substitutions),
]

# =========================================================================

"""example of adding a hard-coded rmap clause in HST:"""

def wfc3_biasfile_filter(kmap):
#     log.info("Hacking WFC3 Biasfile  APERTURE macros.   Adding t6i1733ei_bia.fits special case.")
#     kmap[('UVIS', 'G280_AMPS', 1.5, 1.0, 1.0, 'G280-REF', 'T')] = \
#       [rmap.Filemap(date='1990-01-01 00:00:00', file='t6i1733ei_bia.fits',
#               comment='Placeholder file. All values set to zero.--------------------------, 12047, Jun 18 2009 05:36PM')]
    return kmap, header_additions

# =========================================================================
"""Example of mutating dataset header values prior to match based on header."""


def precondition_header(rmap, header):
    if rmap.filekind == "biasfile":
        return header   # XXX do nothing
        return _precondition_header_biasfile(header)
    else:
        return header
    
def _precondition_header_biasfile(header_in):
    """Mutate the incoming dataset header based upon hard coded rules
    and the header's contents.
    """
    header = dict(header_in)
    subarray = header["SUBARRAY"]
    aperture = header["APERTURE"]
    if subarray == "T" and "SUB" not in aperture:
        header["APERTURE"] = "*"
    return header

'''
This is the original CDBS code for wfc3 biasfile which generates SQL for matching
dataset header values against the CDBS reference file database::


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
'''
    

