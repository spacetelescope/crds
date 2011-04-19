#!/usr/bin/env python

import sys                  # access to command-line args
import string               # string functions
import opusutil             # utilites like PrintMsg

# python modules for this application
import os
import getopt

# local modules for this application
import hst_archdbquery
import cdbsquery
import kwdbquery
import datasources
import xmlReferenceFileDefs
import siname
import bestref_algorithm

#NOTE: the following keywords get added "on the fly" in this code
#      since they are needed for the selection algorithms but are NOT
#      part of the reference_file_defs.xml content (for good reasons):
#
#      TEXPSTRT (STIS exposure start time)
#      EXPSTART (all other SIs exposure start time)
#      TARGNAME (for NIC SAADFILE selection)
#
# History:
# 07/14/2009  63053  MSwam  first version
# 05/10/2010  49175  MSwam  replace CDBS_DB,SERVER with REFFILE_DB,SERVER
#====================================================================
def add_these_keywords(anInstrument, all_keywords):
  #
  # add the exposure start time keyword for use_after queries
  if anInstrument._name == "STIS":
    # STIS has to be different (argh)
    all_keywords.append("TEXPSTRT")
  else:
    all_keywords.append("EXPSTART")

  # add target for NIC SAADFILE case
  all_keywords.append("TARGNAME")

  return



#--------------------------------------------------------------------------
def update_files_usage():
  opusutil.PrintMsg('F','Interactive Usage: update_files [-h] [-o sqloutfile] -i instrument | -d dataset ')
  return

#--------------------------------------------------------------------------
#
# Name: update_files_interactive
#
# Description: Performs command line parsing and set-up for BESTREF
#              update of NULL best_* fields in the archive catalog.
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
def update_files_interactive():
  #
  # parse command line arguments
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:o:d:", 
                   ["help","instrument=","sqloutfile=","dataset="])
  except getopt.GetoptError:
    # print help information and exit:
    update_files_usage()
    sys.exit(1)

  # assign option defaults
  instrument = None
  sqloutfile = None
  dataset = None

  # parse options
  for flag, value in opts:
    if flag in ("-h", "--help"):
      update_files_usage()
      sys.exit(1)
    if flag in ("-i", "--instrument"):
      instrument = value
    if flag in ("-o", "--sqloutfile"):
      sqloutfile = value
    if flag in ("-d", "--dataset"):
      dataset = value

  # verify required args
  if instrument == None and dataset == None:
    update_files_usage()
    sys.exit(1)

  # load the master reference file descriptions
  xmlreffile = opusutil.StretchFile("OPUS_DEFINITIONS_DIR:reference_file_defs.xml")
  anXmlmaster = xmlReferenceFileDefs.XMLReferenceFileDefs(xmlreffile)

  # run the update_files computations
  update_files(instrument, dataset, sqloutfile, anXmlmaster)
  return

#-------------------------------------------------------------------------
# 
# Name: update_files
#
# Description: Computes the best reference files for all NULL best_* fields
#              in an instrument's archive catalog *_ref_data table.
#
# Input:
# instrument - name of instrument to process (if not dataset mode)
# dataset - name of dataset to process (if not instrument mode)
# sqloutfile - name of the output file for SQL commands
# anXmlmaster - the master XML object holding ref file definitions
#
# Environment variables:
# KW_SERVER - keyword database server
# KW_DB - name of keyword database
# ARCH_SERVER - archive database server
# ARCH_DB - name of archive database
# CDBS_SERVER - CDBS database server
# CDBS_DB - name of CDBS database
#
# Output: a file of SQL in sqloutfile
#
# Exceptions: MissingRequiredFiles - one or more required reference
#                                    files could not be found
#
# History:
# -------- -----  --------  --------------------------------------
# 09/23/02 xxxxx  MSwam     first version
# 10/29/04 51433  MSwam     catch bestref_algorithm errors and skip
# 11/22/06 57062  MSwam     add TARGNAME for NIC SAADFILE selection
# 05/21/07 57570  MSwam     no more DB retries
# 10/09/07 57618  Sherbert  Add a debug and tweak another for more info
# 07/15/10 57271  MSwam     remove db retry parameter
#
#-------------------------------------------------------------------------
def update_files(instrument, single_dataset, sqloutfile, anXmlmaster):
  #
  if instrument:
    # process all qualifying datasets for an instrument
    # locate keywords needed for the instrument
    anInstrument = anXmlmaster._the_master.find_instrument(
                                                  string.upper(instrument))
  else: # single dataset mode
    anInstrument = anXmlmaster._the_master.find_instrument(
                                      siname.WhichInstrument(single_dataset))

  all_keywords = anInstrument.all_keywords()

  # connect to the archive db
  arch_db = hst_archdbquery.HST_Arch_db(os.environ['ARCH_SERVER'], 
                                os.environ['ARCH_DB'])
  if instrument:
    #
    # query the archive catalog for the list of dataset names to process
    # (they have one or more NULL entries in their best_* fields)
    datasets = arch_db.empty_best(anInstrument)
  else: 
    # single dataset mode
    datasets = [[]]
    datasets[0].append(string.upper(single_dataset))

  if len(datasets) == 0:
    # nothing to do
    opusutil.PrintMsg("I","No empty BEST fields for "+anInstrument._name)
    sys.exit(0)
  opusutil.PrintMsg("I","Found "+str(len(datasets))+" datasets to process")
  opusutil.PrintMsg("D",str(datasets))

  # add special keywords needed in queries but not part of the normal
  #   file selection algorithm and CDBS
  #
  add_these_keywords(anInstrument, all_keywords)

  #
  # connect to keyword db and CDBS db
  kw_db = kwdbquery.Kw_db(os.environ['KW_SERVER'], 
                          os.environ['KW_DB'])
  reffile_db = cdbsquery.Cdbs_db(os.environ['REFFILE_SERVER'], 
                                 os.environ['REFFILE_DB'])

  # open the output file, if provided, or use stdout
  if (sqloutfile):
    outfd = open(sqloutfile, "w")
  else:
    outfd = sys.stdout

  # loop through the datasets needing computation
  update_count = 0
  for dataset in datasets:
    #
    # get the field values for this dataset
    opusutil.PrintMsg("I",dataset[0]+": getting db fields============================ ")
    opusutil.PrintMsg("D","Call datasources.DBsources with all_keywords: "+str(all_keywords))
    Source = datasources.DBsources(all_keywords, dataset[0], kw_db, arch_db)
    opusutil.PrintMsg("D",'input done,keywords='+str(Source._sources[0]._keywords))

    # fill ref file keywords
    try:
      num_missing = bestref_algorithm.update_ref_files(anInstrument, Source, 
                                                     reffile_db)
    except:
      opusutil.PrintMsg("E","Error during BESTREF calculations. Skipping.")
      continue
 
    # if any required files were missing, warn
    if num_missing:
      opusutil.PrintMsg("W",dataset[0]+
                        ": "+str(num_missing)+" reference files missing.")

    # write the reference file updates to their output destination
    #
    Source.output(anInstrument, outfd)
    update_count = update_count + Source._sources[0]._num_changed
  
  # end the query output, if any written
  if update_count > 0:
    outfd.write("go\n")
  outfd.close()
  #
  # close the database connections
  reffile_db.close()
  arch_db.close()
  kw_db.close()
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
update_files_interactive()
sys.exit(0)

