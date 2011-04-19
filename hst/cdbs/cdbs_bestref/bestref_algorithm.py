
import opusutil             # utilites like PrintMsg

# local modules for this application
import cdbsquery

#-------------------------------------------------------------------------
# 
# Name: update_ref_files
#
# Description: Computes the best reference files for each keyword
#              source within a dataset.
#              The ref file names are stored in the header keywords
#              within each keyword source object.
#
# Input:
# anInstrument - an Instrument object
# Source - a datasource object
# cdbs_db - an open CDBS database object
#
# Returns: num_missing - a count of missing reference files
#
# History:
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
#
#-------------------------------------------------------------------------
def update_ref_files(anInstrument, Source, cdbs_db):
  num_missing = 0
  for aSource in Source._sources:
    #
    # fill ref file keywords
    for reff in anInstrument._reffiles:

      # set default, in case no file is found
      filename = anInstrument._missing_file

      # if a restriction applies to this reffile, make sure it is satisfied
      if reff._restrictions:
        if (not eval(reff._restrictions)):
          opusutil.PrintMsg("D",'Restriction not met ('+reff._restrictions+
                                ') Set file to N/A and skip.')
          aSource.change_keyword_val(reff, 'N/A', 'N/A')
          continue
        else:
          opusutil.PrintMsg("D",'Restriction OK, continue.')

      # execute special selection method if specified
      if reff._function:
        opusutil.PrintMsg("D",'reffile will be filled by: '+reff._function)
        try:
          exec(reff._function)
        except cdbsquery.ZeroRowsFound, querytxt:
          #
          # the reffile was not found, decide if that is unacceptable
          try:
            filename = cdbs_db.missing_reffile(reff, aSource, querytxt, 
                                                 anInstrument._missing_file)
          except cdbsquery.MissingRequiredFile:
            num_missing = num_missing + 1
      else:
        #
        # query CDBS for the reffile name
        try:
          filename = cdbs_db.find_reffile(anInstrument._name, reff, 
                                            aSource)
        except cdbsquery.ZeroRowsFound, querytxt:
          #
          # the reffile was not found, decide if that is unacceptable
          try:
            filename = cdbs_db.missing_reffile(reff, aSource, querytxt,
                                                 anInstrument._missing_file) 
          except cdbsquery.MissingRequiredFile:
            num_missing = num_missing + 1
      #
      # save reference filename
      aSource.change_keyword_val(reff, filename, anInstrument._missing_file)
 
    opusutil.PrintMsg("D",'before output,keywords='+str(aSource._keywords))
  #
  return num_missing

