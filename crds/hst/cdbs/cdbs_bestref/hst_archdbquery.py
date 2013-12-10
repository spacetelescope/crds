import os
import string
import time

import opusutil
import archdbquery
import siname

class HST_Arch_db(archdbquery.Arch_db):
  """
=======================================================================
Class: HST_Arch_db

Description:
------------
This class provides access to HST-specific relations in the archive catalog.
It inherits common function from the archdbquery.Arch_db class.

Methods:
--------
empty_best - Find the list of datasets with empty "best" reference file fields
             in the *_ref_data table for an instrument
empty_switches - Find the list of datasets with empty calibration switch values
                 in the *_ref_data table for an instrument
get_asn_members - searches the dbrows structure, retrieved earlier from
                  get_top_asn(), for all association members for the given 
                  dataset name
get_top_asn - searches the "assoc_member" table and returns all of the entries 
              for a given "top-level" association
insert_sms_data - inserts a new row
update_ads_start_end - Updates the start and end time fields in a row 
                       archive_data_set_all

History:
--------
10/01/02 xxxxx MSwam     Initial version
03/18/04 49551 MSwam     Add queries for Ingest redesign
09/13/06 56017 MSwam     Subclass from Arch_db
07/15/10 57271 MSwam     remove db retry parameter
=======================================================================
  """
  def __init__(self, server, dbname):
    #
    # call Superclass constructor
    archdbquery.Arch_db.__init__(self, server, dbname)

  """
=======================================================================
Name: empty_best

Description:
------------
This function searches the *_ref_data table in the archive catalog
for a given instrument, and returns a list of dataset names for any
entries that contain one or more NULL values in the "best" reference
file fields.

Arguments:
----------
anInstrument - an instrument object

Returns: a list of dataset names

History:
--------
10/01/02 xxxxx MSwam     Initial version
09/08/10 64432 MSwam     change =NULL to is NULL
=======================================================================
  """
  def empty_best(self, anInstrument):
    #
    # start the query
    prefix = siname.get_ref_data_prefix(anInstrument._name)
    querytxt = ("SELECT "+prefix+"_data_set_name FROM "+
                string.lower(anInstrument._name)+"_ref_data "+
                "WHERE ")

    # add to the query for each reference file type
    for reff in anInstrument._reffiles:
      querytxt = (querytxt + prefix + "_best_"+string.lower(reff._keyword) +
                 " is NULL or ")

    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt[:-3], result)
    return result

  """
=======================================================================
Name: empty_switches

Description:
------------
Find the list of datasets with empty switch values for an instrument.

Arguments:
----------
instr - name of instrument to process
switch_file - filename holding calibration switch names

Returns: a list of dataset names

History:
--------
10/01/02 xxxxx MSwam     Initial version
09/08/10 64432 MSwam     change =NULL to is NULL
=======================================================================
  """
  def empty_switches(self, instr, switch_file):
    #
    # get names of switches from configured file
    switches = opusutil.FileToList(switch_file)
    if len(switches) == 0:
      opusutil.PrintMsg("E","Empty switch list for "+switch_file)
      return []

    # translate for WFPC-2 difference between switch file and db names
    if instr == "wf2": instr = "wfpc2"
    prefix = siname.get_ref_data_prefix(string.upper(instr))

    # build the query to check for empty values
    querytxt = ("SELECT " + prefix + "_data_set_name from " + instr +
                  "_ref_data WHERE ")
    need_or = 0
    for switch in switches:
      if need_or:
        querytxt = querytxt + " or "
      querytxt = (querytxt + prefix + "_best_" + string.lower(switch) +
                 " is NULL")
      need_or = 1
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    return result

  """
======================================================================

 Name: get_top_asn

 Purpose: Searches the "assoc_member" table of the archive database
          and returns all of the entries for a given "top-level" association

          A "top-level" association is one that has one or more matching 
          entries in the assoc_member.asm_asn_id field.
          For example, J8NR01010 is a top-level asn, while J8NR01011 is not.

 Arguments:
   datasetname (I)  - name of the dataset to look up

 Returns: 
   result - a list of dictionaries containing the full assoc_member
            rows of all matching entries

 History:
 --------
 10/01/02 xxxxx MSwam     Initial version
 01/06/09       Sherbert  added ORDER BY to ensure test order correct
========================================================================
  """
  def get_top_asn(self, datasetname):
    #
    # build the query template
    querytxt = ("SELECT * FROM assoc_member "+
                "WHERE asm_asn_id = '" + string.upper(datasetname) + "' "
                "ORDER BY asm_obsnum" )
    #
    # get results in a list of dictionaries
    result = [{}]
    self.zombie_select(querytxt, result)
    return result

  """
=======================================================================
Name: get_asn_members

Description:
------------
This function searches the dbrows structure, retrieved earlier from the
"assoc_member" table of the archive database, for all association
members for the given dataset name.  The given name could be the
top-level asn or one of the product asns.  If the given name is the
top-level asn, then ALL of the members for all products are
returned.  If a specific product asn name is given, only the members
for that product are returned.

For example, J8C107080 is a top-level association, while J8C107081 is
a product asn.

Arguments:
----------
dbrows  - list of dictionaries holding assoc_member rows
datasetname (I)  - name of the dataset to get members for

Returns: a list of association member names

History:
--------
10/01/02 xxxxx MSwam     Initial version
=======================================================================
  """
  def get_asn_members(self, dbrows, datasetname):

    members = []
    #
    # first try a search for the given dataset name as a product asn
    found = 0
    searchval = string.upper(datasetname)
    for arow in dbrows:
      if arow['asm_data_set_name'] == searchval:
        #
        # found product asn, convert product type to member type,
        # unless dither product (DTH) then use ALL
        opusutil.PrintMsg("D","found product asn "+datasetname)
        if arow['asm_member_type'] == "PROD-DTH":
          member_type = "ALL"
        else:
          member_type = string.replace(arow['asm_member_type'],"PROD", "EXP")
        found = 1
        break
    if not found:
      # an empty list
      opusutil.PrintMsg("D","no product asn found for "+datasetname)
      return members
    #
    # now build a list of all asn members with the matching type
    for arow in dbrows:
      if ((member_type == "ALL" and arow['asm_member_type'][:3] == "EXP") or 
         (arow['asm_member_type'] == member_type)):
        opusutil.PrintMsg("D","found member "+arow['asm_data_set_name'])
        members.append(arow['asm_data_set_name'])
    #
    return members

  """
=======================================================================
Name: insert_sms_data

Description:
------------
This function inserts a new row in the sms_data table, after first
deleting the row if it already exists.

Arguments:
----------
archive_class, 
data_set_name,  This value gets uppercased before loading
generation_date, 
mission, 
file_extension,
file_name

Returns:
--------
none

History:
--------
01/21/04 49551 MSwam     Initial version
=======================================================================
  """
  def insert_sms_data(self, archive_class, data_set_name,
                         generation_date, pdb_id, calendar):
    #
    # delete, if present
    querytxt = ("DELETE FROM sms_data WHERE "+
             "sms_archive_class = '"+archive_class+"' "+
             "and sms_data_set_name = '"+string.upper(data_set_name)+"' "+
             "and sms_generation_date = '"+generation_date+"' ")
    opusutil.PrintMsg("I","attempting "+querytxt)
    #
    try:
      self._DB.query(querytxt)
      self._DB.executeUpdate()
    except:
      opusutil.PrintMsg("D","nothing to delete?")
    #
    # now insert
    querytxt = ("INSERT sms_data ("+
             "sms_archive_class, sms_data_set_name, sms_generation_date, "+
             "sms_pdb_id, sms_calendar) values ("+
          "'"+archive_class+"','"+string.upper(data_set_name)+
          "','"+generation_date+"',"+
          "'"+pdb_id+"','"+calendar+"')" )
    opusutil.PrintMsg("I","attempting "+querytxt)
    #
    self._DB.query(querytxt)
    self._DB.executeUpdate()
    #
    return

  """
=======================================================================
Name: update_ads_start_end

Description:
------------
Updates the start and end time fields in a row of the archive_data_set_all
table.

Arguments:
----------
instr - name of instrument to process
switch_file - filename holding calibration switch names

Returns: a list of dataset names

History:
--------
01/21/04 49754 MSwam     Initial version
=======================================================================
  """
  def update_ads_start_end(self, archive_class, dataset, start_time_str,
                           end_time_str):
    #
    querytxt = ("UPDATE archive_data_set_all set "+
                "ads_start_time = '"+start_time_str+
                "', ads_end_time = '"+end_time_str+
                "' WHERE ads_data_set_name = '"+string.upper(dataset)+
                "' and ads_archive_class = '"+archive_class+ "' ")
    #
    opusutil.PrintMsg("I","attempting: "+querytxt)
    self._DB.query(querytxt)
    self._DB.executeUpdate()
    return

  """
=======================================================================
Name: insert_ingest_data_set_info

Description:
------------
This function inserts a new row in the ingest_data_set_info
table.

Arguments:
----------
data_id,
dataset,
generation_date,
archive_class,
dataset_name,     This value gets uppercase before loading
mission,
ingest_request_id,
pipeline_source,
subdir,
file_count

Returns:
--------
none

History:
--------
01/21/04 49551 MSwam     Initial version
04/16/04 50823 J.Baum    Remove db_time_now arg and use DB function getdate()
02/21/05 53048 MSwam     Remove obsolete fields
12/03/07 59094 MSwam     Moved from SHARE to allow Kepler-specific version
=======================================================================
  """
  def insert_ingest_data_set_info(self, data_id, dataset,
                         generation_date, archive_class,
                         dataset_name, mission,
                         ingest_request_id, pipeline_source,
                         subdir, file_count):
    #
    # assign default values
    delay_default = "999"
    install_default = "N"
    data_set_size_default = "0.0"
    nsa_req_date_default = " "
    nsa_rsp_date_default = " "
    log_file_name_default = " "

    #
    querytxt = ("INSERT ingest_data_set_info ("+
                "ids_group_data_id, ids_group_name, ids_generation_date, "+
                "ids_archive_class, ids_data_set_name, ids_mission, "+
                "ids_ins_request_id, ids_data_source, ids_receipt_date, "+
                "ids_path_name, ids_file_count, ids_clean_delay_days, "+
                "ids_install_flag, ids_data_set_size, "+
                "ids_nsa_req_date, ids_nsa_rsp_date,"+
                "ids_log_file_name) values ("+
                "'"+data_id+"','"+dataset+"','"+generation_date+"',"+
                "'"+archive_class+"','"+string.upper(dataset_name)+
                "','"+mission+"',"+
        "'"+ingest_request_id+"','"+pipeline_source+"', getdate(),"+
        "'"+subdir+"',"+str(file_count)+","+delay_default+","+
        "'"+install_default+"',"+data_set_size_default+","+
        "'"+nsa_req_date_default+"','"+nsa_rsp_date_default+"',"+
        "'"+log_file_name_default+"')" )

    opusutil.PrintMsg("I","attempting "+querytxt)
    #
    self._DB.query(querytxt)
    self._DB.executeUpdate()
    #
    return


  """
=======================================================================
Name: pdq_summary_update

Description:
------------
This function queries the pdq_summary table for a given observations

Arguments:
----------
dataset

Returns:
--------
none

History:
--------
=======================================================================
  """
  def pdq_summary_update(self, dataset):

    from ac_pkg import get_pppssoo, uc_list_mems

    PPPSSOO = uc_list_mems( get_pppssoo( dataset ) )
    progID_UC  = PPPSSOO[0]
    obsetID_UC = PPPSSOO[1]
    obsnum_UC  = PPPSSOO[2]

    query  = "SELECT pdq_comment_1, pdq_comment_2, pdq_comment_3, pdq_quality "
    query += "FROM pdq_summary "
    query += "WHERE pdq_program_id='" + progID_UC + "'"
    query += "  AND pdq_obset_id='" + obsetID_UC + "'"
    query += "  AND pdq_obsnum='" + obsnum_UC + "'"

    msg = "query is " + str(query)
    opusutil.PrintMsg('D', msg, 'pdq_summary_update')

    #
    # get results in a list of dictionaries
    msg = "ARCH_DB error encountered.  "
    result = [{}]
    try:
        self.zombie_select(query, result)
        ## Index: clustered, unique - 
        ## pdq_primary_index   pdq_program_id, pdq_obset_id, pdq_obsnum 
        ## "You can not get two rows for any products only one row per product."
        ## Lisa G. assures me, therefore I need not check for >1 row returned
    except:
        return [{'msg':msg, 'query':query}]
    return result
    





#========================================================================
# TEST 
# History:
# --------
# 10/09/07 57618 Sherbert   Use correct class
#========================================================================
if __name__ == "__main__":
    # connect to ARCH db
    dbobj = HST_Arch_db(os.environ['ARCH_SERVER'], 
                    os.environ['ARCH_DB'])
    dbrows = dbobj.get_top_asn("J8C107080")

    ## These are not the ideal unit tests as where the disagreement is
    ## is NOT specified when assert detects false. But better than nothing?
    assert dbrows == [{'asm_program_id': '8C1', 'asm_obsnum': '081', 'asm_asn_id': 'J8C107080', 'asm_member_name': 'J8C107081', 'asm_data_set_name': 'J8C107081', 'asm_member_type': 'PROD-CRJ', 'asm_obset_id': '07'}, {'asm_program_id': '8C1', 'asm_obsnum': 'DK ', 'asm_asn_id': 'J8C107080', 'asm_member_name': 'J8C107DKQ', 'asm_data_set_name': 'J8C107DKQ', 'asm_member_type': 'EXP-CRJ', 'asm_obset_id': '07'}, {'asm_program_id': '8C1', 'asm_obsnum': 'DL ', 'asm_asn_id': 'J8C107080', 'asm_member_name': 'J8C107DLQ', 'asm_data_set_name': 'J8C107DLQ', 'asm_member_type': 'EXP-CRJ', 'asm_obset_id': '07'}], "ERROR testing get_top_asn"

#   opusutil.PrintMsg("I",str(dbrows))
    members = dbobj.get_asn_members(dbrows, "J8C107081")
    assert members == ['J8C107DKQ', 'J8C107DLQ'], "ERROR testing get_asn_members"
#   opusutil.PrintMsg("I",str(members))
    longext = dbobj.get_long_extensions("FUSE","Y")
    assert longext == {'00all3histfcal': 'HSH', '00nvo4ttagfcal': 'TVL', '00quk3ttagfcal': 'TQH', '00quk2histfcal': 'HQM', '00quk3histfcal': 'HQH', '00nvo3histfcal': 'HVH', '00nvo2histfcal': 'HVM', '00sic2ttagf': 'T4I', '00all1ttagfcal': 'TSP', '00lif2histf': 'H2I', '00all1histfcal': 'HSP', '00quk4ttagfcal': 'TQL', '00spechistf': 'H0I', '00nvo4histfcal': 'HVL', '00airgttagf': 'T0B', '00sic1ttagf': 'T3I', 'asnftxt': 'ASS', '00ano4ttagfcal': 'TNL', '00quk2ttagfcal': 'TQM', 'asnftrl': 'AST', '00quk1ttagfcal': 'TQP', '00nvo3ttagfcal': 'TVH', '00lif1ttagf': 'T1I', '00all2ttagfcal': 'TSM', '00quk4histfcal': 'HQL', 'asnf': 'ASN', '00lif1histf': 'H1I', '00sic1histf': 'H3I', '00ano1ttagfcal': 'TNP', '00all4histfcal': 'HSL', '00nvo1ttagfcal': 'TVP', '00quk1histfcal': 'HQP', '00nvo2ttagfcal': 'TVM', '00lif2ttagf': 'T2I', '00ano3ttagfcal': 'TNH', '00nvo1histfcal': 'HVP', '00ano2ttagfcal': 'TNM', '00specttagf': 'T0I', '00all3ttagfcal': 'TSH', '00all2histfcal': 'HSM', '00all4ttagfcal': 'TSL', '00sic2histf': 'H4I'}, "ERROR testing get_long_extensions"
#   opusutil.PrintMsg("I",str(longext))

    stuff = dbobj.pdq_summary_update( 'N626RO030' )
    ## There is no guarantee that stuff, a list of dicts [{}], will be ordered 
    ## in an expected way.  Therefore the logic to check it needs to be a 
    ## bit more complex... :(  
    opusutil.PrintMsg("I",str(stuff))
    for row in stuff:           ## row is a hash/ dictionary
        for item in row.iterkeys():
            if item == 'pdq_comment_1':
                assert row[item] == \
                       'Problem with NICMOS detector NIC3.  Observation may be degraded.', \
                       "ERROR testing pdq_summary_update, pdq_comment_1, N626RO030"
            if item == 'pdq_comment_2':
                assert row[item] == None, \
                       "ERROR testing pdq_summary_update, pdq_comment_2, N626RO030"
            if item == 'pdq_comment_3':
                assert row[item] == None, \
                       "ERROR testing pdq_summary_update, pdq_comment_3, N626RO030"
            if item == 'pdq_quality':
                assert row[item] == 'SIPROB', \
                       "ERROR testing pdq_summary_update, pdq_quality,   N626RO030"

    stuff = dbobj.pdq_summary_update( 'n6287w030' )
#   opusutil.PrintMsg("I",str(stuff))
    for row in stuff:           ## row is a hash/ dictionary
        for item in row.iterkeys():
            if item == 'pdq_comment_1':
                assert row[item] == None, \
                       "ERROR testing pdq_summary_update, pdq_comment_1, n6287w030"
            if item == 'pdq_comment_2':
                assert row[item] == None, \
                       "ERROR testing pdq_summary_update, pdq_comment_2, n6287w030"
            if item == 'pdq_comment_3':
                assert row[item] == None, \
                       "ERROR testing pdq_summary_update, pdq_comment_3, n6287w030"
            if item == 'pdq_quality':
                assert row[item] == None, \
                       "ERROR testing pdq_summary_update, pdq_quality,   n6287w030"

    dbobj.close()
