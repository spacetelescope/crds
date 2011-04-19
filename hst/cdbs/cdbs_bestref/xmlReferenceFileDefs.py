# python modules
import string
import os
import xml.dom.minidom

# local modules
import instReferenceFileDefs
import opusutil

class XMLReferenceFileDefs:
  """
#####################################################################
Class: XMLReferenceFileDefs

Description:
------------
This class parses an XML file of reference file definitions into
objects.  The objects are described in module "instReferenceFileDefs".
The parsing is performed using the dom model.

Members:
--------
_the_master - a master object of reference file information

History:
--------
10/01/02 xxxxx MSwam     first version
#####################################################################
  """
  def __init__(self, xmlfile):
    ####################################
    # the constructor
    ####################################
    # create an empty master object to be filled with ref file information
    self._the_master = instReferenceFileDefs.InstReferenceFileDefs()
    #
    # set up for parsing an XML file of ref file information
    dom = xml.dom.minidom.parse(xmlfile)
    #
    # begin the parse with the top-level XML tag
    self.handleReferencefiles(dom)
    #
    # release the resources
    dom.unlink()

  def getText(self, nodelist):
    ########################################################
    #
    # a utility function for building up a text string from
    # the XML file
    #
    ########################################################
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    # at this point rc is NOT of string type (unicode?)
    return string.strip(str(rc))

  def handleReferencefiles(self, thedoc):
    #############################################
    #
    # REFERENCE_FILES
    #   contains at least one INSTRUMENT
    #
    #############################################
    instruments = thedoc.getElementsByTagName("INSTRUMENT")
    self.handleInstruments(instruments)

  def handleInstruments(self, instruments):
    #############################################
    #
    # one or more INSTRUMENTs
    #
    #############################################
    for instrument in instruments:
       self.handleInstrument(instrument)

  def handleInstrument(self, instrument):
    #############################################
    #
    # each INSTRUMENT contains
    #   one INSTRUMENT_NAME
    #   one INSTRUMENT_MISSING_FILE
    #   one or more REFFILE
    #
    #############################################
    instrument_name = instrument.getElementsByTagName("INSTRUMENT_NAME")[0]
    anInstrument = instReferenceFileDefs.InstReferenceFiles(self.getText(instrument_name.childNodes))
    instrument_missing_file = instrument.getElementsByTagName("INSTRUMENT_MISSING_FILE")[0]
    anInstrument.set_missing_file(self.getText(instrument_missing_file.childNodes))
    reffiles = instrument.getElementsByTagName("REFFILE")
    self.handleReffiles(reffiles, anInstrument)
    #
    # INSTRUMENT parsing complete, add to master object
    self._the_master.append(anInstrument)

  def handleReffiles(self, reffiles, anInstrument):
    #############################################
    #
    # one or more REFFILEs
    #
    #############################################
    for reffile in reffiles:
       self.handleReffile(reffile, anInstrument)

  def handleReffile(self, reffile, anInstrument):
    #############################################
    #
    # each REFFILE contains
    #   one REFFILE_TYPE
    #   one REFFILE_KEYWORD
    #   one REFFILE_FORMAT
    #   one REFFILE_REQUIRED (OPTIONAL)
    #   one REFFILE_SWITCH (OPTIONAL)
    #   one REFFILE_FUNCTION (OPTIONAL)
    #   one or more FILE_SELECTION (OPTIONAL)
    #   one or more ROW_SELECTION (OPTIONAL)
    #   one RESTRICTION (OPTIONAL)
    #
    #############################################
    reffileType = reffile.getElementsByTagName("REFFILE_TYPE")[0]
    reffileKeyword = reffile.getElementsByTagName("REFFILE_KEYWORD")[0]
    reffileFormat = reffile.getElementsByTagName("REFFILE_FORMAT")[0]
    aReffile = instReferenceFileDefs.Reffile(self.getText(reffileType.childNodes),
                              self.getText(reffileKeyword.childNodes),
                              self.getText(reffileFormat.childNodes) )
    #
    # optional text fields need try/except 
    try:
       reffileFunction = reffile.getElementsByTagName("REFFILE_FUNCTION")[0]
       aReffile.set_function(self.getText(reffileFunction.childNodes))
    except:
      pass
    try:
       reffileRequired = reffile.getElementsByTagName("REFFILE_REQUIRED")[0]
       aReffile.set_required(self.getText(reffileRequired.childNodes))
    except:
      pass
    try:
       reffileSwitch= reffile.getElementsByTagName("REFFILE_SWITCH")[0]
       aReffile.set_switch(self.getText(reffileSwitch.childNodes))
    except:
      pass
    #
    # optional containers do not need try/except
    file_selections = reffile.getElementsByTagName("FILE_SELECTION")
    self.handleFileSelections(file_selections, aReffile)
    row_selections = reffile.getElementsByTagName("ROW_SELECTION")
    self.handleRowSelections(row_selections, aReffile)
    #
    # optional text fields need try/except 
    try:
       restriction = reffile.getElementsByTagName("RESTRICTION")[0]
       restriction_test = reffile.getElementsByTagName("RESTRICTION_TEST")[0]
       aReffile.set_restrictions(self.getText(restriction_test.childNodes))
    except:
       pass
    #
    # REFFILE parsing complete, add to master object
    anInstrument.append(aReffile)
  
  def handleFileSelections(self, file_selections, aReffile):
    ###############################################
    #
    # one or more FILE_SELECTIONs
    #
    ###############################################
    for file_selection in file_selections:
       self.handleFileSelection(file_selection, aReffile)

  def handleFileSelection(self, file_selection, aReffile):
    ###############################################
    #
    # each FILE_SELECTION contains
    #   one FILE_SELECTION_FIELD 
    #   one FILE_SELECTION_TEST (OPTIONAL)
    #
    ###############################################
    fileSelectionField = file_selection.getElementsByTagName(
                         "FILE_SELECTION_FIELD")[0]
    #
    # optional text fields need try/except 
    try:
      fileSelectionTest = file_selection.getElementsByTagName(
                             "FILE_SELECTION_TEST")[0]
      aReffile._file_selections.append(instReferenceFileDefs.Selection(
                               self.getText(fileSelectionField.childNodes),
                               self.getText(fileSelectionTest.childNodes)))
    except:
      aReffile._file_selections.append(instReferenceFileDefs.Selection(
                               self.getText(fileSelectionField.childNodes)))

  def handleRowSelections(self, row_selections, aReffile):
    ###############################################
    #
    # one or more ROW_SELECTIONs
    #
    ###############################################
    for row_selection in row_selections:
       self.handleRowSelection(row_selection, aReffile)

  def handleRowSelection(self, row_selection, aReffile):
    ###############################################
    #
    # each ROW_SELECTION contains
    #   one ROW_SELECTION_FIELD 
    #   one ROW_SELECTION_TEST (OPTIONAL)
    #
    ###############################################
    rowSelectionField = row_selection.getElementsByTagName(
                        "ROW_SELECTION_FIELD")[0]
    #
    # optional text fields need try/except 
    try:
         rowSelectionTest = row_selection.getElementsByTagName(
                            "ROW_SELECTION_TEST")[0]
         aReffile._row_selections.append(instReferenceFileDefs.Selection(
                                 self.getText(rowSelectionField.childNodes),
                                 self.getText(rowSelectionTest.childNodes)))
    except:
         aReffile._row_selections.append(instReferenceFileDefs.Selection(
                                 self.getText(rowSelectionField.childNodes)))


#########################################################################
# TEST
# % python xmlReferenceFileDefs.py
#########################################################################
if __name__ == "__main__":
  xmlreffile = opusutil.StretchFile("OPUS_DEFINITIONS_DIR:reference_file_defs.xml")
  xmlmaster = XMLReferenceFileDefs(xmlreffile)
  wfpc2 = xmlmaster._the_master.find_instrument("WFPC2")
  wfpc2_bias = wfpc2.find_reffile("BAS")
  all_keywords = wfpc2.all_keywords()
  opusutil.PrintMsg("I",'all keywords: '+str(all_keywords))
