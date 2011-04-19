#!/usr/bin/env python

# exit codes
NOT_OK = 1
OK = 0

# modules for OPUS internal poller
import sys                  # access to command-line args
import string               # string functions
import opusutil             # utilites like PrintMsg
import re                   # regular expression handling
import traceback            # printing of stack traces 

# python modules for this application
import os
import getopt

# local modules for this application
import datasources
import cdbsquery
import hst_archdbquery
import kwdbquery
import xmlReferenceFileDefs
import siname
import base_poller
import bestref_algorithm

# constants
ALL_VALUES = 1      # includes db SQL for all ref files, whether changed or not

# exceptions
class MissingIORonCommandLine(Exception):
  pass

class NarrowOfOrbObjectFailed(Exception):
  pass

class FailedToRegisterPipelineApp(Exception):
  pass

class UsageError(Exception):
  pass

class NotFitsOrDbInput(Exception):
  pass

class MissingRequiredFiles(Exception):
  pass

class FailedResourceInit(Exception):
  pass

class PollingFailed(Exception):
  pass

class HaltEvent(Exception):
  pass

class DatasetNotFoundInOSF(Exception):
  pass

class Bestref(base_poller.InternalPoller):
  """
########################################################################
Class: Bestref

Description:
------------
The class for interactive or pipeline Bestref determination.
Allows determination of the best set of reference files for a given
exposure.

Members:
--------
mode = indicates if input/output mode is fits or database
inpath = directory for input files (if not DB input mode)
trlpath = directory for trailer file to be updated
sqloutfile = name of SQL output file, if output mode is database
ref_select_file = name of the file holding reference file definitions
anXmlmaster = master object holding reference file rules
cdbs_dbobj  = database object for accessing reference file tables

Methods:
--------
usage() - prints an interactive usage message and raises an exception

History:
--------
09/23/02 49175 MSwam     change from CDBS_DB,SERVER to REFFILE_DB,SERVER
07/15/10 57271 MSwam     remove db retry parameter

########################################################################
  """
  def __init__(self):
    # initialize members
    self._mode = "fits"
    self._inpath = None
    self._trlpath = None
    self._sqloutfile = None
    self._ref_select_file = None
    self._anXmlmaster = None
    self._cdbs_dbobj = None
    self._cdbs_server = os.environ['REFFILE_SERVER']
    self._cdbs_db     = os.environ['REFFILE_DB']
    self._arch_server = os.environ['ARCH_SERVER']
    self._arch_db     = os.environ['ARCH_DB']
    self._kw_server   = os.environ['KW_SERVER']
    self._kw_db       = os.environ['KW_DB']

  def initialize(self):
    #
    # call superclass constructor
    base_poller.InternalPoller.__init__(self)

  #--------------------------------------------------------------------------
  def usage(self):
    opusutil.PrintMsg('F','Interactive Usage: bestref.py [-h] [-m fits|db|dball] [-o sqloutfile] [-r ref_select_file] -d datasetname')
    raise UsageError

  #--------------------------------------------------------------------------
  #
  # Name: interactive
  #
  # Description: Performs command line parsing and set-up for BESTREF
  #              processing in interactive mode.  Runs the BESTREF
  #              task for the command-line arguments given.
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
  # 10/12/09 63764  MSwam     support XPOLL version
  # 10/16/09 63764  MSwam     more changes for XPOLL version
  #
  #--------------------------------------------------------------------------
  def interactive(self):
    #
    # parse command line arguments
    try:
      opts, args = getopt.getopt(sys.argv[1:], "hm:d:o:r:", 
                   ["help","mode=","datasetname=","sqloutfile=","ref_select_file="])
    except getopt.GetoptError:
      # print help information and raise exception
      self.usage()

    # initialize
    dataset = None

    # parse options
    for flag, value in opts:
      if flag in ("-h", "--help"):
        self.usage()
      if flag in ("-m", "--mode"):
        self._mode = value
      if flag in ("-d", "--datasetname"):
        dataset = value
      if flag in ("-o", "--sqloutfile"):
        self._sqloutfile = value
      if flag in ("-r", "--ref_select_file"):
        self._ref_select_file = value

    # verify required args
    if dataset == None:
      # no command line dataset, so try to pick up OSF_DATASET env var
      try:
        dataset = os.environ['OSF_DATASET']
        opusutil.PrintMsg("D","found OSF_DATASET="+dataset)
      except KeyError:
        opusutil.PrintMsg("E","FAILED to find OSF_DATASET")
        self.usage()

    # read file of dataset names, if provided
    if dataset[0] == "!":
      # a file of dataset names is being provided
      datasets = opusutil.FileToList(dataset[1:])
    else:
      datasets = []
      datasets.append(dataset)
    opusutil.PrintMsg("D","datasets="+str(datasets))

    # if reference file XML rules file was not specified, try env var
    if self._ref_select_file == None:
      try:
        # try env var first
        ref_select_filename = os.environ['REF_SELECT_FILE']
        opusutil.PrintMsg("D","REF_SELECT_FILE="+ref_select_filename)
      except KeyError:
        # use default if env var not supplied
        ref_select_filename = "OPUS_DEFINITIONS_DIR:reference_file_defs.xml"
        opusutil.PrintMsg("D","DEFAULT used for REF_SELECT_FILE: "+
                               ref_select_filename)
      # locate the file on disk
      self._ref_select_file = opusutil.StretchFile(ref_select_filename)
 
    # load the master reference file descriptions
    self._anXmlmaster = xmlReferenceFileDefs.XMLReferenceFileDefs(
                           self._ref_select_file)
 
    # connect to reffile db
    self._cdbs_dbobj = cdbsquery.Cdbs_db(self._cdbs_server,
                                         self._cdbs_db)
    
    # set the directory for file input
    try:
      self._inpath = os.environ['INPATH']
      opusutil.PrintMsg("D","INPATH="+self._inpath)
    except KeyError:
      # default to current directory
      self._inpath = os.getcwd()
      opusutil.PrintMsg("D","DEFAULT used for INPATH: "+self._inpath)

    # set the directory/flag for trailer file use
    using_trl = 0
    try:
      self._trlpath = os.environ['TRLPATH']
      using_trl = 1
      opusutil.PrintMsg("D","TRLPATH="+self._trlpath)
    except KeyError:
      # default to current directory
      self._trlpath = os.getcwd()
      opusutil.PrintMsg("D","DEFAULT used for TRLPATH: "+self._trlpath)

    # run the bestref computations
    for aDataset in datasets:
      if using_trl:
         opusutil.OpenTrl(self._trlpath + os.sep + aDataset + ".trx")
         opusutil.PrintMsg("I","----- REF started for: "+aDataset+" -----")

      self.do_bestref(aDataset)

      if using_trl:
         opusutil.PrintMsg("I","----- REF ended for: "+aDataset+" -----")
         opusutil.CloseTrl()

    # close the database connection
    self._cdbs_dbobj.close()

    return

  #-------------------------------------------------------------------------
  # 
  # Name: pipeline_init
  #
  # Description: Initialization for pipeline mode, including reading
  #              XML file of reference file specs and resource file
  #              parameters for controlling the task.
  #
  # History:
  # -------- -----  --------  --------------------------------------
  # 09/23/02 xxxxx  MSwam     first version
  #
  #-------------------------------------------------------------------------
  def pipeline_init(self):
    # obtain resource items in a dictionary and assign to globals
    #
    try:
      resource_items = base_poller.InternalPoller.get_resource_items(self,
                            ["INPATH",
                             "TRLPATH",
                             "MODE",
                             "SQLOUTFILE",
                             "REF_SELECT_FILE",
                             "REFFILE_SERVER",
                             "REFFILE_DB",
                             "ARCH_SERVER",
                             "ARCH_DB",
                             "KW_SERVER",
                             "KW_DB"] )
    except:
      opusutil.PrintMsg("E","failed to get required resource entry")
      raise
    #
    opusutil.PrintMsg("I","Resource items read.")
    self._mode = resource_items['MODE']
    self._inpath = resource_items['INPATH']
    self._trlpath = resource_items['TRLPATH']
    self._sqloutfile = resource_items['SQLOUTFILE']
    self._ref_select_file = resource_items['REF_SELECT_FILE']
    self._cdbs_server = resource_items['REFFILE_SERVER']
    self._cdbs_db = resource_items['REFFILE_DB']
    self._arch_server = resource_items['ARCH_SERVER']
    self._arch_db = resource_items['ARCH_DB']
    self._kw_server = resource_items['KW_SERVER']
    self._kw_db = resource_items['KW_DB']
    #
    # read the XML-format reference file information from disk
    try:
      xmlfilename = opusutil.StretchFile(self._ref_select_file)
      self._anXmlmaster = xmlReferenceFileDefs.XMLReferenceFileDefs(xmlfilename)
    except:
      opusutil.PrintMsg("E","Failed to read XML file: "+xmlfilename)
      raise
    #
    # connect to the reference file database
    self._cdbs_dbobj = cdbsquery.Cdbs_db(self._cdbs_server,
                                         self._cdbs_db)
    return

  #-------------------------------------------------------------------------
  # 
  # Name: do_bestref
  #
  # Description: Computes the best reference files for a dataset.
  #
  # Input:
  # dataset - name of the dataset to process
  #
  # Environment variables:
  # KW_SERVER - keyword database server
  # KW_DB - name of keyword database
  # ARCH_SERVER - archive database server
  # ARCH_DB - name of archive database
  #
  # Output: updated FITS headers or a file of SQL in sqloutfile
  #
  # Exceptions: MissingRequiredFiles - one or more required reference
  #                                    files could not be found
  #
  # Notes: Will EXIT (status=1) if an unknown i/o mode is given
  #        (only fits and db are currently supported).
  #
  # History:
  # -------- -----  --------  --------------------------------------
  # 09/23/02 xxxxx  MSwam     first version
  # 02/25/05 51433  MSwam     add dball mode to show all values
  # 09/20/06 56376  MSwam     add TARGNAME
  #
  #-------------------------------------------------------------------------
  def do_bestref(self, dataset):
    #
    # locate keywords needed for the instrument
    anInstrument = self._anXmlmaster._the_master.find_instrument(
                                        siname.WhichInstrument(dataset))
    all_keywords = anInstrument.all_keywords()

    # add target for NIC SAADFILE case
    all_keywords.append("TARGNAME")

    # load keyword values from the data source
    if self._mode == "fits":
      #
      # add the exposure start time keyword possibilities for 
      # use_after queries
      all_keywords.append("PSTRTIME")
      all_keywords.append("TVSTART")
      all_keywords.append("DATE-OBS")
      all_keywords.append("TIME-OBS")
      Source = datasources.FITSsources(all_keywords, dataset, 
                                             self._inpath)
    elif self._mode[:2] == "db":
      #
      # connect to keyword and archive dbs
      kw_dbobj = kwdbquery.Kw_db(self._kw_server,
                                 self._kw_db)

      arch_dbobj = hst_archdbquery.HST_Arch_db(self._arch_server,
                                    self._arch_db)
      # add the exposure start time keyword for use_after queries
      if anInstrument._name == "STIS":
        all_keywords.append("TEXPSTRT")
      else:
        all_keywords.append("EXPSTART")
      #
      Source = datasources.DBsources(all_keywords, dataset, kw_dbobj, arch_dbobj)
      #
      # close db connection that is no longer needed
      arch_dbobj.close()
    else:
      opusutil.PrintMsg("E","Unknown input/output mode (not fits or db)")
      raise NotFitsOrDbInput
    opusutil.PrintMsg("D",'input done,keywords='+str(Source._sources))

    # fill ref file keywords
    num_missing = bestref_algorithm.update_ref_files(anInstrument, Source, 
                                                     self._cdbs_dbobj)

    # if any required files were missing, raise an exception
    if num_missing:
      opusutil.PrintMsg("E","One or more reference files missing.")
      raise MissingRequiredFiles

    # write the reference file updates to their output destination
    if self._mode == "fits":
      Source.output(anInstrument)
    elif self._mode[:2] == "db":
      #
      # open the output file, if provided, or use stdout
      if (self._sqloutfile):
        outfd = open(self._sqloutfile, "w")
      else:
        outfd = sys.stdout
      if self._mode == "dball":
        # includes all values, whether changed or not
        Source.output(anInstrument, outfd, ALL_VALUES)
      else:
        Source.output(anInstrument, outfd)
      outfd.close()
      # close db connection
      kw_dbobj.close()
    #
    return

  #-------------------------------------------------------------------------
  # Name: processHaltEvent
  #
  # Description: Handle a HALT event (override base class).
  #
  # History:
  # -------- -----  --------  --------------------------------------
  # 02/25/05 51433  MSwam     use base poller class
  #
  #-------------------------------------------------------------------------
  def processHaltEvent(self, event):
    #
    opusutil.PrintMsg("I","Received HALT event. Stopping.")
    self._cdbs_dbobj.close()
    raise HaltEvent


  #-------------------------------------------------------------------------
  # Name: processOsfEvent
  #
  # Description: Handle OSF events in pipeline mode.
  #
  # History:
  # -------- -----  --------  --------------------------------------
  # 09/23/02 xxxxx  MSwam     first version
  # 08/06/04 49860  Sontag    Changed an IDL field name
  # 12/17/04 51433  MSwam     Use proper IGNEVT name
  # 02/25/05 51433  MSwam     Use base_poller base class
  #
  #-------------------------------------------------------------------------
  def processOsfEvent(self, event):
    # get trigger info
    dataset, data_id = self.getDatasetDataidFromOsfEvent(event)

    try:
      opusutil.OpenTrl(self._trlpath + os.sep + dataset + ".trx")
    except:
      # any exception marks the OSF with OSF_ERROR
      traceback.print_exc()
      #
      # an error occurred during trailer opening, set the OSF to failed
      try:
        opusutil.PrintMsg("E","closing event with OSF_ERROR")
        self._papp.closeEvent("OSF_ERROR", event.eid)
      except:
        traceback.print_exc()
        opusutil.PrintMsg("E","Failed to close OSF_ERROR event")
      return

    opusutil.PrintMsg("I","----- REF started for: "+dataset+" -----")
    try:
      self.do_bestref(dataset)
    except:
      # any other exception marks the OSF with OSF_ERROR
      traceback.print_exc()
      #
      # an error occurred during processing, set the OSF
      try:
        opusutil.PrintMsg("E","closing event with OSF_ERROR")
        self._papp.closeEvent("OSF_ERROR", event.eid)
      except:
        traceback.print_exc()
        opusutil.PrintMsg("E","Failed to close OSF_ERROR event")
      opusutil.PrintMsg("I","----- REF ended for: "+dataset+" -----")
      opusutil.CloseTrl()
      return

    try:
      self._papp.closeEvent("OSF_NORMAL", event.eid)
    except:
      traceback.print_exc()
      opusutil.PrintMsg("E","Failed to close OSF_NORMAL event")
    opusutil.PrintMsg("I","----- REF ended for: "+dataset+" -----")
    opusutil.CloseTrl()

#-------------------------------------------------------------------------
# The main routine. Handles interactive and pipeline mode.
#
# History:
# -------- -----  --------  --------------------------------------
# 02/25/05 51433  MSwam     first version
#
#-------------------------------------------------------------------------
#
# initialize
try:
  poller = Bestref()
  poller.initialize()
  poller.pipeline_init()
#
except base_poller.InteractiveMode:
  opusutil.PrintMsg("I","Running command-line mode.")
  try:
    poller.interactive()
  except UsageError:
    sys.exit(NOT_OK)
  except:
    traceback.print_exc()
    opusutil.PrintMsg("F","Command-line mode Failed.")
    sys.exit(NOT_OK)
  sys.exit(OK)
#
except:
  traceback.print_exc()
  opusutil.PrintMsg("E","initialization failed")
  sys.exit(NOT_OK)

opusutil.PrintMsg("I","Pipeline set-up complete.")
try:
  poller.run()
except HaltEvent:
  sys.exit(OK)
except:
  traceback.print_exc()
  opusutil.PrintMsg("E","pipeline_process failed")
  sys.exit(NOT_OK)

