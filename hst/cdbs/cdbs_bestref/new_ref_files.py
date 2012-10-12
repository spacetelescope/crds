#!/usr/bin/env python

import sys                  # access to command-line args
import string               # string functions
import opusutil             # utilites like PrintMsg

# python modules for this application
import os
import getopt
import time

# local modules for this application
import cdbsquery
import xmlReferenceFileDefs
import siname
import datasources

# leave these keywords out of the ACS BIAS file selection test
#
ACS_BIAS_LEAVE_OUT = ['NUMROWS','NUMCOLS','XCORNER','YCORNER','LTV1','LTV2', 
                      'CCDCHIP']

# leave these keywords out of the WFC3 BIAS file selection test
#
WFC3_BIAS_LEAVE_OUT = ['APERTURE','SUBARRAY']

# leave these keywords out of the COS SPWCS file selection test
#
COS_SPWCS_LEAVE_OUT = ['EXPTYPE']

# leave these out of the WFPC2 FLAT file selection test
WFPC2_FLAT_LEAVE_OUT = ['LRFWAVE','FILTNAM1','FILTNAM2','IMAGETYP']

SM4_DATE = '2009/05/14 12:00:00'  # date beyond which an exposure was
                                  # taken in the SM4 configuration
                                  # (May 14 2009)
                                  #  after HST was captured by
                                  #  the shuttle during SM4, and
                                  #  pre-SM4 exposures had ceased)

#--------------------------------------------------------------------------
def new_files_usage():
  opusutil.PrintMsg('F','Interactive Usage: new_files [-h] [-o sqloutfile] [-l updatelimit]')
  return

#--------------------------------------------------------------------------
#
# Name: new_files_interactive
#
# Description: Performs command line parsing and set-up for BESTREF
#              update of a NEW reference file delivery.
#
# Inputs: global sys.argv (command line arguments)
#          
# Notes: Reads reference file definitions from an XML file.
#        Will EXIT (status=1) if incorrect command line arguments
#        are found.  This is a FATAL error.
#
# History:
#   date    opr     who     reason
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
#
#--------------------------------------------------------------------------
def new_files_interactive():
  #
  # parse command line arguments
  try:
    opts, args = getopt.getopt(sys.argv[1:], "ho:l:", 
                   ["help","sqloutfile=","updatelimit="])
  except getopt.GetoptError:
    # print help information and exit:
    new_files_usage()
    sys.exit(1)

  # assign option defaults
  sqloutfile = None
  updatelimit = 5000

  # parse options
  for flag, value in opts:
    if flag in ("-h", "--help"):
      new_files_usage()
      sys.exit(1)
    if flag in ("-o", "--sqloutfile"):
      sqloutfile = value
    if flag in ("-l", "--updatelimit"):
      updatelimit = value

  # load the master reference file descriptions
  xmlreffile = opusutil.StretchFile("OPUS_DEFINITIONS_DIR:reference_file_defs.xml")
  anXmlmaster = xmlReferenceFileDefs.XMLReferenceFileDefs(xmlreffile)

  # run the new_files computations
  new_files(sqloutfile, updatelimit, anXmlmaster)
  return

#--------------------------------------------------------------------------
#
# Name: keywords_and_instruments
#
# Description: Determines the CDBS keywords needed to choose
#              this reference file type, and also the list of
#              instruments it applies to, if it is a MULTI-instrument
#              type.
#
# Inputs: 
#          
# History:
#   date    opr     who     reason
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
# 03/24/03 xxxxx  MSwam     add special case for ACS BIAS
# 04/15/09 62457  MSwam     another special case for WFC3 BIAS
# 01/27/11 66490  MSwam     add COS SPWCSTAB special case
#
#--------------------------------------------------------------------------
def keywords_and_instruments(cdbs_inst, cdbs_type, anXmlmaster):
    #
    # initialize
    cdbs_keywords = []
    update_inst = []
    #
    # SPECIAL CASE for instrument = MULTI
    #
    if cdbs_inst == "MULTI":
      # loop through all instruments,
      # and save all instrument names that use this ref file type
      # for later arch_db update
      #
      for anInstrument in anXmlmaster._the_master._instruments:
        try:
          opusutil.PrintMsg("D","MULTI inst: ...checking "+
             anInstrument._name+" for "+cdbs_type)
          #
          # make sure the instrument is supported by CDBS
          siname.supported_by_CDBS(anInstrument._name)
          reffile = anInstrument.find_reffile(cdbs_type)
          #
          # the keyword list gets appended to for each instrument
          # (duplicates will be thrown out later)
          #
          reffile.all_keywords(cdbs_keywords)
          update_inst.append(anInstrument._name)
          opusutil.PrintMsg("D","MULTI inst: =>adding "+anInstrument._name)
        except:
          # not all instruments may have this type or be supported
          pass
    else:
      # just one instrument applies
      #
      anInstrument = anXmlmaster._the_master.find_instrument(cdbs_inst)
      reffile = anInstrument.find_reffile(cdbs_type)
      reffile.all_keywords(cdbs_keywords)
      #
      # SPECIAL CASE: ACS BIAS (I hate that!)
      if anInstrument._name == "ACS" and reffile._keyword == "BIASFILE":
        #
        # delete ACS BIAS file selection keywords that cannot be
        # supported by the standard algorithm (they require special
        # code; see cdbsquery.acs_biasfile
        i = 0
        while i < len(cdbs_keywords):
          if (cdbs_keywords[i] in ACS_BIAS_LEAVE_OUT):
            del cdbs_keywords[i]
          else:
            i = i + 1
      #
      # ANOTHER SPECIAL CASE: WFC3 BIAS (I REALLY hate that!)
      elif anInstrument._name == "WFC3" and reffile._keyword == "BIASFILE":
        #
        # delete WFC3 BIAS file selection keywords that cannot be
        # supported by the standard algorithm (they require special
        # code; see cdbsquery.wfc3_biasfile
        i = 0
        while i < len(cdbs_keywords):
          if (cdbs_keywords[i] in WFC3_BIAS_LEAVE_OUT):
            del cdbs_keywords[i]
          else:
            i = i + 1
      #
      # YET ANOTHER SPECIAL CASE: COS SPWCS (Grrrr....)
      elif anInstrument._name == "COS" and reffile._keyword == "SPWCSTAB":
        #
        # delete COS SPWCS file selection keywords that cannot be
        # supported by the standard algorithm (at present we will try
        # WITHOUT adding special code...)
        i = 0
        while i < len(cdbs_keywords):
          if (cdbs_keywords[i] in COS_SPWCS_LEAVE_OUT):
            del cdbs_keywords[i]
          else:
            i = i + 1
      #
      # AND ANOTHER: WFPC2 FLAT (well its almost the NORM now, isn't it?)
      elif anInstrument._name == "WFPC2" and reffile._keyword == "FLATFILE":
        #
        # delete WFPC2 FLAT file selection keywords that cannot be
        # supported by the standard algorithm (they require special
        # code; see cdbsquery.wfpc2_flatfile
        i = 0
        while i < len(cdbs_keywords):
          if (cdbs_keywords[i] in WFPC2_FLAT_LEAVE_OUT):
            del cdbs_keywords[i]
          else:
            i = i + 1
      #
      update_inst.append(anInstrument._name)
    #
    opusutil.PrintMsg("D","leaving keywords_and_instruments, cdbs_keywords="+str(cdbs_keywords))
    return cdbs_keywords, update_inst

#--------------------------------------------------------------------------
#
# Name: get_useafter
#
# Description: Performs a database query against the CDBS database
#              to get the useafter_date for a reference file.
#
# Inputs: 
#   cdbs_prefix - the prefix of the CDBS database tables to read
#   reffilename - the name of the reference file to look up
#   reffile_db - an open REFFILE database object
#          
# Output:
#   useafter_date - useafter value from the database
#
# History:
#   date    opr     who     reason
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
#
#------------------------------------------------------------------------
def get_useafter(cdbs_prefix, reffilename, reffile_db):
    #
    querytxt = ("SELECT DISTINCT convert(char(12),useafter_date,101)+" +
                       "convert(char(12),useafter_date,108) FROM " +
                cdbs_prefix + "_file WHERE "+
                "file_name = '"+reffilename+"'")
    opusutil.PrintMsg("D","querytxt="+querytxt)  
    #
    # define the query and fill a list of lists with result
    useafter_date = [[]]
    reffile_db.zombie_select(querytxt, useafter_date)
    if len(useafter_date) == 0:
      opusutil.PrintMsg("E","Failed to find useafter date with query="+
                        querytxt)
      raise MissingUseAfterDate
    #
    return useafter_date[0][0]

#--------------------------------------------------------------------------
#
# Name: wfpc2_flatfile
#
# Description: A special case exists for WFPC2 FLT.
#              The filter order is irrelevant in the file selection
#              but the CDBS ref files were not expanded to
#              indicate this so the code must handle it.  The code
#              creates a special search that tries the filter values
#              in either order.
#
#              This code should only be called once for the FLT, as
#              it handles both filters.
#
# Inputs: 
#   aSource - a CDBS data source object
#   field_prefix - the field prefix for building the query
#   querytxt - the database query text that has already been started
#          
# Output:
#   querytxt - the updated database query text
#
# History:
#   date    opr     who     reason
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
#
#------------------------------------------------------------------------
def wfpc2_flatfile(aSource, field_prefix, querytxt):
  opusutil.PrintMsg("D","adding file selection for both FILTERs")
  querytxt = (querytxt + 
                " and ((" + 
                field_prefix + "filter1 = " +
                str(aSource._keywords["FILTER1"][0]) + " and "+
                field_prefix + "filter2 = " +
                str(aSource._keywords["FILTER2"][0]) + ") or (" +
                field_prefix + "filter1 = " +
                str(aSource._keywords["FILTER2"][0]) + " and "+
                field_prefix + "filter2 = " +
                str(aSource._keywords["FILTER1"][0]) + ")) " )

  return querytxt


def reformat_MMDDYYYYHHMMSS(inDate):
    """Reformat a date from MM/DD/YYYY HH:MM:SS to YYYY/MM/DD HH:MM:SS"""
    #
    YYYYMMDDHHMMSS_date = (inDate[6:10]+"/"+
                           inDate[0:2]+"/"+
                           inDate[3:5]+
                           inDate[10:] )
    #print ("inDate="+inDate+", sortable form="+YYYYMMDDHHMMSS_date)
    return YYYYMMDDHHMMSS_date


#--------------------------------------------------------------------------
#
# Name: file_selection_fields
#
# Description: Applies reference file selection fields to build up
#              a database query.   The query is assumed to have already
#              been started, and each reference file selection field
#              that applies will be appended to the query text.
#              If a field has a field restriction test, the test
#              must pass before the field is applied to the query.
#
#              NOTE: A special case exists for the ACS BIAS.
#                    It has a restriction that gets tested for,
#                    but is hard-coded to have no file selection tests.
#
#              NOTE: A special case exists for WFPC2 FLT.
#                    The filter order is irrelevant in the file selection
#                    but the CDBS ref files were not expanded to
#                    indicate this so the code must handle it.
#
#              NOTE: A special case exists for the WFC3 BIAS.
#                    It has a restriction that gets tested for,
#                    but is hard-coded to have no file selection tests.
#
# Inputs: 
#   cdbs_prefix - used to test for ACS special case
#   aSource - a CDBS data source object
#   theReffile - a reference file object
#   field_prefix - the field prefix for building the query
#   querytxt - the database query text that has already been started
#          
# Output:
#   querytxt - the updated database query text
#
# History:
#   date    opr     who     reason
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
# 04/15/09 62457  MSwam     add WFC3 BIAS special case
# 09/14/12 72156  MSwam     leave ACS APERTURE out for pre-SM4 BIASES
#------------------------------------------------------------------------
def file_selection_fields(cdbs_prefix, aSource, theReffile, field_prefix, 
                          useafter_date, querytxt):
  #
  # add file selection fields
  for k in theReffile._file_selections:
    if k._restrictions:
      # see if the restriction allows this file selection field
      if (not eval(k._restrictions)):
        opusutil.PrintMsg("D","file selection restriction NOT met: "+
                                k._restrictions)
        continue
    # 
    # SPECIAL CASE: ACS BIAS
    # Leave out certain fields since the ACS BIAS uses
    # special code to perform its BIAS selection and the standard
    # algorithm to include all file_selection fields would not work.
    #
    if (cdbs_prefix == "acs" and theReffile._keyword == "BIASFILE" and
        k._field in ACS_BIAS_LEAVE_OUT):
      continue
    #
    # 2nd ACS BIAS special adjustment: leave APERTURE OUT of selection for
    # pre-SM4 useafter dates
    #
    if (cdbs_prefix == "acs" and theReffile._keyword == "BIASFILE" and
        k._field == "APERTURE"):
      useafter_YYYYMMDDHHMMSS = reformat_MMDDYYYYHHMMSS(useafter_date)
      if useafter_YYYYMMDDHHMMSS < SM4_DATE:
        opusutil.PrintMsg("I",
                 "pre-SM4 useafter, leaving APERTURE off ACS BIAS selection")
        continue

    # 
    # SPECIAL CASE: WFC3 BIAS
    # Leave out certain fields since the WFC3 BIAS uses
    # special code to perform its BIAS selection and the standard
    # algorithm to include all file_selection fields would not work.
    #
    if (cdbs_prefix == "wfc3" and theReffile._keyword == "BIASFILE" and
        k._field in WFC3_BIAS_LEAVE_OUT):
      continue

    if cdbs_prefix == "wfpc2" and theReffile._keyword == "FLATFILE":
      # SPECIAL CASE: WFPC2 FLAT
      # part1: Leave out certain fields since the WFPC2 FLAT uses
      # special code to perform its file selection and the standard
      # algorithm to include all file_selection fields would not work.
      #
      if (k._field in WFPC2_FLAT_LEAVE_OUT):
        continue

      # part2: the filter order must be made irrelevant
      # process for FILTER1, ignore FILTER2 (handled in the code)
      if k._field == "FILTER1":
        querytxt = wfpc2_flatfile(aSource, field_prefix, querytxt)
      continue

    #
    # apply the file selection field
    # (first as a string, but if that fails, as a number converted to 
    #  string since numbers don't get quoted, and strings do)
    opusutil.PrintMsg("D","adding file selection "+k._field)
    try:
      querytxt = (querytxt + " and " + field_prefix + 
                        string.lower(k._field) + " = '" +
                        aSource._keywords[k._field][0] + "' ")
    except TypeError:
      querytxt = (querytxt + "and " + field_prefix + 
                        string.lower(k._field) + " = " +
                        str(aSource._keywords[k._field][0]) + " ")
  #
  return querytxt

#--------------------------------------------------------------------------
#
# Name: find_stop_date
#
# Description: Performs a database query against the CDBS database
#              to locate the "stop" date, or date that indicates
#              the end of the use-after period for a particular
#              reference file.  If no bracketing CDBS entry exists
#              for this reference file, today's date is the stop date.
#
# Inputs: 
#   cdbs_prefix - the prefix of the CDBS database tables to read
#   useafter_date - the useafter_date for the reference file
#   aSource - a CDBS data source object containing keywords and values
#   theReffile - a reference file object containing selection criteria
#   reffile_db - an open CDBS database object
#          
# Output:
#   stop_date - the end of the useafter period for a reference file
#
# History:
#   date    opr     who     reason
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
#
#------------------------------------------------------------------------
def find_stop_date(cdbs_prefix, ref_data_prefix, useafter_date, aSource, 
                   theReffile, reffile_db):
    #
    # find STOP_DATE for the useafter period
    #   build base query
    querytxt = ("SELECT convert(char(12),useafter_date,101)+" +
                       "convert(char(12),useafter_date,108) FROM " +
                cdbs_prefix + "_file f, " + cdbs_prefix + "_row r WHERE " +
                "f.file_name = r.file_name and "+
                "f.expansion_number = r.expansion_number and " +
                "f.reference_file_type = '" + theReffile._type + "' and " +
                "f.reject_flag = 'N' and f.opus_flag = 'Y' and " +
                "f.useafter_date > '" + useafter_date + "' and " +
                "f.archive_date is not null and f.opus_load_date is not null ")

    # add the file selection fields and finish the query
    querytxt = file_selection_fields(cdbs_prefix, aSource, theReffile, 
                                     "r.", useafter_date, querytxt)
    querytxt = querytxt + " order by f.useafter_date"
    opusutil.PrintMsg("D","querytxt="+querytxt)  

    # define the query and fill a list of lists with result
    stop_date = [[]]
    reffile_db.zombie_select(querytxt, stop_date)
    if len(stop_date) == 0:
      opusutil.PrintMsg("I","No stop date found. Using today.")
      return time.strftime("%m/%d/%Y %H:%M:%S",time.localtime(time.time()))
    #
    return stop_date[0][0]

#-------------------------------------------------------------------------
# 
# Name: new_files
#
# Description: Applies new reference file deliveries against the
#              archive catalog *_ref_data tables.
#
# Input:
# sqloutfile - name of the output file for SQL commands
# updatelimit - max number of database updates peformed at a time
# anXmlmaster - the master XML object holding ref file definitions
#
# Environment variables:
# CDBS_SERVER - CDBS database server
# CDBS_DB - name of CDBS database
# REFFILE_SERVER - REFFILE database server
# REFFILE_DB - name of REFFILE database
#
# Output: a file of SQL in sqloutfile
#
# History:
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
# 10/20/04 51433  MSwam     fix up record limit for update
# 01/31/05 51433  MSwam     catch unsupported SI for MULTI mode
# 02/21/05 51433  MSwam     added the "= NULL" as an update condition
# 07/15/10 57271  MSwam     remove db retry parameter
#-------------------------------------------------------------------------
def new_files(sqloutfile, updatelimit, anXmlmaster):
  #
  # connect to the databases
  cdbs_db = cdbsquery.Cdbs_db(os.environ['CDBS_SERVER'], 
                              os.environ['CDBS_DB'])

  reffile_db = cdbsquery.Cdbs_db(os.environ['REFFILE_SERVER'], 
                                 os.environ['REFFILE_DB'])

  # check for new_cal_files entries
  newfiles = cdbs_db.get_new_cal_files()
  if len(newfiles) == 0:
    opusutil.PrintMsg("I","No new_cal_files entries to process.")
    sys.exit(0)

  # open SQL output file
  if (sqloutfile):
    outfd = open(sqloutfile, "w")
  else:
    outfd = sys.stdout

  # process each newly-released reference file,expansion number set
  #
  for newfile in newfiles:
    opusutil.PrintMsg("I","processing "+str(newfile))
    #
    # identify CDBS "instrument" (can include SYNPHOT and MULTI)
    cdbs_inst = siname.WhichCDBSInstrument(newfile[0])
    #
    if cdbs_inst == "SYNPHOT":
      # SYNPHOT just a pass-thru, no action
      continue

    # get CDBS tablename prefix for this instrument
    cdbs_prefix = siname.get_cdbs_prefix(cdbs_inst)

    # identify ref file type given the filename (query SI_file in CDBS_DB)
    cdbs_type = reffile_db.get_ref_file_type(cdbs_inst, newfile[0])
    opusutil.PrintMsg("D","inst="+str(cdbs_inst)+", type="+str(cdbs_type))

    # locate needed keywords and instruments for this reffile type 
    cdbs_keywords, update_inst = keywords_and_instruments(cdbs_inst, 
                                                          cdbs_type[0], 
                                                          anXmlmaster)
    opusutil.PrintMsg("D","cdbs_keywords="+str(cdbs_keywords))

    # load the selection values from the CDBS db source 
    # for this reffilename
    Source = datasources.CDBsources(cdbs_keywords, newfile, cdbs_prefix,
                                     reffile_db)

    # get the useafter date for this ref file
    useafter_date = get_useafter(cdbs_prefix, newfile[0], reffile_db)
    opusutil.PrintMsg("D","useafter_date="+str(useafter_date))


    # write updates for *_ref_data exposures matching useafter period and mode,
    # SPECIAL CASE when cdbs_inst == MULTI,
    #   updates ALL entries and could be for multiple instruments 
    #
    for inst in update_inst:
      theInstrument = anXmlmaster._the_master.find_instrument(inst)
      theReffile = theInstrument.find_reffile(cdbs_type[0])
      try:
        ref_data_prefix = siname.get_ref_data_prefix(inst)
      except siname.UnknownRefDataPrefix:
        # skip unsupported SIs for MULTI case
        opusutil.PrintMsg("D","Skipping "+str(inst))
        continue

      # this limits the update so that it doesn't overflow
      # tran logs and replication queue space.  All updates occur,
      # but happen in chunks.
      #
      outfd.write("declare @the_count int \n")
      outfd.write("set rowcount "+str(updatelimit)+"\n")
      outfd.write("select @the_count = "+str(updatelimit)+"\n")
      outfd.write("while (@the_count = "+str(updatelimit)+")\n")
      outfd.write("begin\n")
      #
      # SPECIAL CASE: MULTI updates all entries not already set
      #   (i.e. it applies for all time)
      #
      if cdbs_inst == "MULTI":
        #
        querytxt = ("  UPDATE "+string.lower(inst)+"_ref_data "+
                  "SET "+ref_data_prefix+"_best_"+
                  string.lower(theReffile._keyword)+" = '"+newfile[0]+"' " +
                  "WHERE "+ref_data_prefix+"_best_"+
                  string.lower(theReffile._keyword)+" != '"+newfile[0]+"' "+
                  "or "+ref_data_prefix+"_best_"+
                  string.lower(theReffile._keyword)+" is null")
        opusutil.PrintMsg("D","querytxt="+querytxt)
        outfd.write(querytxt+"\n")
      else:
        # find STOP_DATE for the useafter period
        # 
        stop_date = find_stop_date(cdbs_prefix, ref_data_prefix, useafter_date, 
                                   Source._sources[0], theReffile, reffile_db)
        opusutil.PrintMsg("D","stop_date="+str(stop_date))
        #
        # SPECIAL CASE: STIS uses different exposure start field
        if inst == "STIS":
          expstart_field = "texpstrt"
        else:
          expstart_field = "expstart"
 
        # begin the update query
        querytxt = ("  UPDATE "+string.lower(inst)+"_ref_data "+
                  "SET "+ref_data_prefix+"_best_"+
                  string.lower(theReffile._keyword)+" = '"+str(newfile[0])+"' ")

        querytxt = (querytxt + " WHERE ("+ref_data_prefix+"_best_"+
                  string.lower(theReffile._keyword)+" != '"+str(newfile[0])+"' or " +
                  ref_data_prefix+"_best_"+
                  string.lower(theReffile._keyword)+" is null) " +
                  "and "+ref_data_prefix+"_"+expstart_field+" >= "+
                 "'"+str(useafter_date)+"' and "+ref_data_prefix+"_"+expstart_field+
                  " < '"+str(stop_date)+"'")

###
### SPECIAL CASE WFPC-2 FLATFILE selection (for linear ramp filters)
###   We need to leave the WFPC-2 linear ramp filters OUT of any modifications
###   resulting from delivery of a new WFPC-2 flat file, since the LRFs have
###   special hard-coded flats assigned to them (see cdbsquery.py and PR 63053).
###
        if (inst == "WFPC2" and
            theReffile._keyword == "FLATFILE"):

           querytxt = (querytxt + " and w2r_data_set_name not in "+
                       "(SELECT w2r_data_set_name from wfpc2_ref_data WHERE "+
                         "w2r_imagetyp = 'EXT' and " +
                   "(w2r_filtnam1 like 'FR%' or w2r_filtnam2 like 'FR%')) ")

        # add file selection fields
        querytxt = file_selection_fields(cdbs_prefix, Source._sources[0], 
                                         theReffile, ref_data_prefix+"_", 
                                         useafter_date,querytxt)
        opusutil.PrintMsg("D","querytxt="+querytxt)

        # write the update statement
        outfd.write(querytxt+"\n")
      #
      outfd.write("  select @the_count = @@rowcount\n")
      outfd.write("end\n")
      outfd.write("go\n")

  # close the database connections
  cdbs_db.close()
  reffile_db.close()
  outfd.close()
  return

#-------------------------------------------------------------------------
# The main routine. 
#
# History:
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
#
#-------------------------------------------------------------------------
#
new_files_interactive()
sys.exit(0)

