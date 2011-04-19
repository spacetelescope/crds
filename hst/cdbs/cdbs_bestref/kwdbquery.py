# python modules used
import os
import string

# local modules used
import opusutil
import siname
import base_db

# exceptions raised
class NoMatchingKWDBField(Exception):
  pass

class MultipleKeywordMappings(Exception):
  pass

class NoMatchingRows(Exception):
  pass

class IncorrectNumberOfRows(Exception):
  pass

class Kw_db(base_db.Base_db):
  """
=======================================================================
Class: Kw_db 

Description:
------------
This class provides access to relations in the keyword database.
It inherits common function from the base_db.Base_db class.

Methods:
--------

History:
--------
10/01/02 xxxxx MSwam     Initial version
07/15/10 57271 MSwam     remove db retry parameter

=======================================================================
  """
  def __init__(self, server, dbname):
    #
    # call Superclass constructor
    base_db.Base_db.__init__(self, server, dbname)

  def keyword_mapping(self, instrument_name, keyword_name):
    """
=======================================================================
Name: keyword_mapping

Description:
------------
This function composes a database query against the Keyword database to
find the archive catalog field that maps to a particular header keyword
name.   The "dads_keywords" and "hda_fields" tables are used for the
lookup.  If multiple possibilities are found, a reduction algorithm is
applied:
	- if archive table is a "*_ref_data" table, use it
	- if archive table is a "*science*" table, use it

If the reduction fails to result in just a single table and field, it is
assumed that the corresponding instrument "_ref_data" table is the
source (this will be proven for sure later).

Arguments:
----------
DBobj (I)           - open database object that will execute the database query
instrument_name (I) - name of the instrument being processed
keyword_name (I)    - name of the keyword to look for in the archive catalog

Exceptions:
-----------
MultipleKeywordMappings - map reduction to a single archive field failed

Returns:
--------
Name of archive catalog table and field that maps to the search keyword name

History:
--------
10/01/02 xxxxx MSwam     Initial version
09/20/06 56376 MSwam     fix bug in multiple hit resolution
=======================================================================
    """
    # Method: keyword_mapping(self, instrument_name, keyword_name)
    #
    # build the query template
    querytxt = ("SELECT dkw_fieldname, hda_tablename " +
                "FROM dads_keywords d, hda_fields h " +
                "WHERE dkw_fieldname = hda_fieldname and " +
                "dkw_keyword = '" + keyword_name + "' and " +
                "dkw_real_instrument = '"+ instrument_name + "' ")
    #
    # get results in a list of dictionaries
    result = [{}]
    self.zombie_select(querytxt, result)
    #
    count = len(result)
    if count == 0:
      # no matching keyword database field?
      opusutil.PrintMsg("D","No matching KWDB "+instrument_name+ " field for "+
                        keyword_name+", assuming ref_data")
      #
      # ASSume the ref_data table for this instrument should be used
      return (string.lower(instrument_name)+"_ref_data",
              siname.get_ref_data_prefix(instrument_name) + "_" +
              string.lower(keyword_name) )
    #
    # if one entry, then a good match
    elif count == 1:
      return (result[0]['hda_tablename'], result[0]['dkw_fieldname'])
    #
    # multiple hits, try list reduction
    else:
      for entry in result:
         #
         # check tablename (field 2) for "ref_data"
         if string.find(entry['hda_tablename'],"_ref_data") > -1:
            return (entry['hda_tablename'], entry['dkw_fieldname'])
      #
      # no reduction yet, try next
      for entry in result:
         #
         # check tablename (field 2) for "science"
         if string.find(entry['hda_tablename'],"science") > -1:
            return (entry['hda_tablename'], entry['dkw_fieldname'])
      #
      # no reduction possible, ERROR
      opusutil.PrintMsg("E","kwdb.keyword_mapping: Unable to reduce "+
         "from "+str(result))
      raise MultipleKeywordMappings

  def field_check(self, fieldname):
    """
=======================================================================
Name: field_check

Description:
------------
This function searches the "hda_fields" table of the keyword database
to see if a particular archive catalog field exists.

Arguments:
----------
DBobj (I)        - open database object that will execute the database query
fieldname (I)    - name of the archive catalog field to look up

Exceptions:
-----------
NoMatchingKWDBField - failed to map to any archive catalog field (zero found)

History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
    """
    # Method: field_check(self, fieldname)
    #
    # build the query template
    querytxt = ("SELECT COUNT(*) FROM hda_fields " +
                "WHERE hda_fieldname = '" + fieldname + "'")
    #
    # get results in a list of dictionaries
    result = [[]]
    self.zombie_select(querytxt, result)
    if result[0][0] > 0:
       # found one
       return
    else:
      opusutil.PrintMsg("D","No archive catalog field called "+fieldname)
      raise NoMatchingKWDBField


  def getCOSifmCopySuffixes( self ):
    """
=======================================================================
Name: getCOSifmCopySuffixes

Description:
------------
Return a dictionary of COS ifm_suffix-es keyed on ifm_fileclass  
for ifm_filclass LIKE classHint and ifm_suffix LIKE suffixHint
classHint and suffixHint are defined below.

Arguments:
----------
DBobj (I)        - open database object that will execute the database query

Returns:
----------
fileClass_fileSuffix - a dictionary of class, suffix pairs

Exceptions:
-----------
NoMatchingRows - failed to find any results (zero records)
IncorrectNumberOfRows -- we expect exactly 4 rows, or we need to change 

History:
--------
12/19/08 60896 Sherbert  Move to this file
08/07/09 60329 Sherbert  exceptions should be raise-ed, not return-ed
=======================================================================
    """
    # Method: getCOSifmCopySuffixes( self )
#   print "At top of getCOSifmCopySuffixes"

    ## Lisa S. created the ingeset_files_mapping entries so that it would
    ## be easy to pick out the suffixes COS cataloging expects
    ## by ending fileClass in "2", and suffix with "copy".
    ## As of Dec 2008, we expect 4 COS rows to match.
    classHint  = "%2"
    suffixHint = "%copy"

    query0 = "SELECT ifm_fileclass, ifm_suffix "
    query1 = "  FROM ingest_files_mapping "
    query2 = " WHERE ifm_instrument = 'COS' "
    query3 = "   AND ifm_fileclass LIKE '" + classHint + "' "
    query4 = "   AND ifm_suffix LIKE '" + suffixHint + "' " 
    query5 = "ORDER BY ifm_data_id, ifm_open_order "

    ## To send to db
    query = query0 + query1 + query2 + query3 + query4 + query5

    ## zombie_select returns a list of lists
    results=[[]]
    self.zombie_select(query, results)

    if len(results) == 0:
        raise NoMatchingRows
    elif len(results) != 4:
        raise IncorrectNumberOfRows, str(results)
    else:
        ## Create a dictionary to return
        fileClass_fileSuffix = {}
        ## Turn the list of lists into a much more useful dictionary
        for result in results:
            ## Make the first item the key and the 2nd the value in a dict
            fileClass_fileSuffix[result[0]] =  result[1]
        return fileClass_fileSuffix


#========================================================================
# TEST 
# % python kwdbquery.py
#========================================================================
if __name__ == "__main__":
  # connect to KWDB db
  kw_db = Kw_db(os.environ['KW_SERVER'], 
                os.environ['KW_DB'])
  try:
    field = kw_db.keyword_mapping("WFPC2", "ATODFILE")
  except:
    opusutil.PrintMsg("I","succeeded in finding parsing function ")
  #
  table, field = kw_db.keyword_mapping("ACS", "FLASHCUR")
  opusutil.PrintMsg("I",'found '+table+" "+field)
  table, field = kw_db.keyword_mapping("ACS", "DETECTOR")
  opusutil.PrintMsg("I",'found '+table+" "+field)
  try:
    kw_db.field_check("acr_data_set_name")
  except:
    opusutil.PrintMsg("E","ERROR: The field_check call for acr_data_set_name " +
                          "should have worked.")
  opusutil.PrintMsg("I","The field_check call for acr_data_set_name worked.")
  try:
    kw_db.field_check("acc_data_set_name")
    opusutil.PrintMsg("E","ERROR: The field_check call for acc_data_set_name " +
                          "should have failed.")
  except:
    opusutil.PrintMsg("I","The field_check call for acc_data_set_name failed " +
                      "as expected.")
    pass
  kw_db.close()
