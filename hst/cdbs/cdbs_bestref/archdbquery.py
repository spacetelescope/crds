import os
import string
import time

import opusutil
import base_db

# exceptions thrown
class DBConnectionProblem(Exception):
  pass

class NoExtensionFound(Exception):
  pass

class Arch_db(base_db.Base_db):
  """
=======================================================================
Class: Arch_db

Description:
------------
This class provides access to relations in the archive catalog.
It inherits common function from the base_db.Base_db class.

Methods:
--------
get_rm_control - Reads all the ingest_rm_control entries for a
                      given mission into a map, keyed on data_id
count_archive_data_set_all - count of entries given search parms
count_archive_files - count of entries given search parms
count_ingest_data_set_info_ddgm - count of entries given ddgm search parms
count_ingest_data_set_info_reqid - count of entries given ingest_request_id
get_ingest_data_set_info_reqid - return map of field values for a row
insert_ingest_data_set_info - inserts a new row
get_long_extensions - read a subset of the ingest_long_extension table

History:
--------
10/01/02 xxxxx MSwam     Initial version
03/18/04 49551 MSwam     Add queries for Ingest redesign
09/13/06 56506 MSwam     Moved mission-independent functions to SHARE
07/15/10 65561 MSwam     replace db retry with unused default=0 parameter
=======================================================================
  """
  def __init__(self, server, dbname, notUsed=0):
    #
    # call Superclass constructor
    base_db.Base_db.__init__(self, server, dbname)

  """
======================================================================

 Name: get_rm_control

 Purpose: Searches the "ingest_rm_control" table of the archive database
          and returns all of the rows for a given mission.

 Arguments:
   mission (I)  - like HST

 Returns: 
   result - a list of lists containing the ingest request manager (rm)
             control parameters

 History:
 --------
 10/01/02 xxxxx MSwam     Initial version
========================================================================
  """
  def get_rm_control(self, mission):
    #
    # build the query template
    querytxt = ("SELECT * FROM "+
                "ingest_rm_control WHERE irc_mission = '" + mission + "'")
    #
    # get results in a list of dictionaries
    result = [{}]
    self.zombie_select(querytxt, result)
    
    # convert to a dictionary of dictionaries, keyed on data_id
    dict = {}
    for i in result:
      dict[i['irc_data_id']] = i
    return dict

  """
=======================================================================
Name: count_archive_data_set_all

Description:
------------
This function returns a count of the archive_data_set_all entries
in the archive catalog for a given mission, archive_class, data_set_name,
and generation_date.

All arguments except generation_date are uppercased in the database query.

Arguments:
----------
mission
archive_class
data_set_name
generation_date

Returns: a count of the table entries for the given search parms

History:
--------
01/21/04 49551 MSwam     Initial version
=======================================================================
  """
  def count_archive_data_set_all(self, mission, archive_class,
                                 data_set_name, generation_date):
    #
    querytxt = ("SELECT COUNT(*) FROM archive_data_set_all WHERE "+
                "ads_mission = '"+string.upper(mission)+"' and "+
                "ads_archive_class = '"+string.upper(archive_class)+"' and "+
                "ads_data_set_name = '"+string.upper(data_set_name)+"' and "+
                "ads_generation_date = '"+generation_date+"'")

    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    return result

  """
=======================================================================
Name: count_archive_files

Description:
------------
This function returns a count of the archive_files entries
in the archive catalog for a given mission, archive_class, data_set_name,
and generation_date.

All arguments except generation_date are uppercased in the database query.

Arguments:
----------
mission
archive_class
data_set_name
generation_date

Returns: a count of the table entries for the given search parms

History:
--------
01/21/04 49551 MSwam     Initial version
=======================================================================
  """
  def count_archive_files(self, mission, archive_class,
                                 data_set_name, generation_date):
    #
    querytxt = ("SELECT COUNT(*) FROM archive_files WHERE "+
                "afi_mission = '"+string.upper(mission)+"' and "+
                "afi_archive_class = '"+string.upper(archive_class)+"' and "+
                "afi_data_set_name = '"+string.upper(data_set_name)+"' and "+
                "afi_generation_date = '"+generation_date+"'")

    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    return result

  """
=======================================================================
Name: count_ingest_data_set_info_ddgm

Description:
------------
This function returns a count of the entries in the ingest_data_set_info
table searched on data_id (d), dataset_name (d), generation_date (g), and 
mission (m).

Arguments:
----------
data_id
dataset_name
generation_date
mission

Returns:
--------
list of lists where the first item is the row count

History:
--------
01/21/04 49551 MSwam     Initial version
=======================================================================
  """
  def count_ingest_data_set_info_ddgm(self, data_id, dataset_name,
                                 generation_date, mission):
    #
    querytxt = ("SELECT COUNT(*) FROM ingest_data_set_info WHERE "+
                "ids_group_data_id = '"+data_id+"' and "+
                "ids_group_name = '"+dataset_name+"' and "+
                "ids_generation_date = '"+generation_date+"' and "+
                "ids_mission = '"+mission+"' ")
    #
    # get results in a list of dictionaries
    result = [[]]
    self.zombie_select(querytxt, result)
    return result

  """
=======================================================================
Name: count_ingest_data_set_info_reqid

Description:
------------
This function returns a count of the entries in the ingest_data_set_info
table searched on ingest_request_id.

Arguments:
----------
ingest_request_Id

Returns:
--------
list of lists where the first item is the row count

History:
--------
01/21/04 49551 MSwam     Initial version
=======================================================================
  """
  def count_ingest_data_set_info_reqid(self, ingest_request_id):
    #
    querytxt = ("SELECT COUNT(*) FROM ingest_data_set_info WHERE "+
                "ids_ins_request_id = '"+ingest_request_id+"' ")
    #
    # get results in a list of dictionaries
    result = [[]]
    self.zombie_select(querytxt, result)
    return result

  """
=======================================================================
Name: get_ingest_data_set_info_reqid

Description:
------------
This function returns a list of select fields in a ingest_data_set_info row
searched on ingest_request_id.

Arguments:
----------
ingest_request_Id

Returns:
--------
list of lists containing the field values for the selected row OR
None if a matching row was not found

History:
--------
01/21/04 49551 MSwam     Initial version
=======================================================================
  """
  def get_ingest_data_set_info_reqid(self, ingest_request_id):
    #
    querytxt = ("SELECT ids_group_name, ids_group_data_id, "+
                "ids_archive_class, "+
                "convert(char(12),ids_generation_date,102)+ "+
                "convert(char(12),ids_generation_date,108), "+
                "ids_mission, "+
                "convert(char(12),ids_receipt_date,102)+ "+
                "convert(char(12),ids_receipt_date,108) "+
                "FROM ingest_data_set_info WHERE "+
                "ids_ins_request_id = '"+ingest_request_id+"' ")
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result) 
    return result

  """
=======================================================================
Name: ids_latest_receipt

Description:
------------
This function returns a list of select fields in a ingest_data_set_info row
searched on mission, dataset, and data_id using the MAXIMUM receipt date.

Arguments:
----------
mission
dataset
data_id

Returns:
--------
list of lists containing the field values for the selected row OR
None if a matching row was not found

History:
--------
06/28/04 50703 MSwam     Initial version
=======================================================================
  """
  def ids_latest_receipt(self, mission, dataset, data_id):
    #
    # 109=hh:mm:sss
    querytxt = ("SELECT "+
                "convert(char(12),ids_generation_date,102)+ "+
                "convert(char(12),ids_generation_date,108) "+
                "FROM ingest_data_set_info WHERE ids_receipt_date = "+
                "(SELECT MAX(ids_receipt_date) from ingest_data_set_info WHERE "+
                "ids_mission = '"+mission+"' and "+
                "ids_group_name = '"+dataset+"' and "+
                "ids_group_data_id = '"+data_id+"' )" )
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result) 
    return result

  """
=======================================================================
Name: get_ids_fields_gen_date

Description:
------------
This function returns a list of select fields in a ingest_data_set_info row
searched on mission, dataset, data_id, and generation_date.

Arguments:
----------
mission
dataset
data_id
gen_date

Returns:
--------
list of lists containing the field values for the selected row OR
None if a matching row was not found

History:
--------
06/28/04 50703 MSwam     Initial version
=======================================================================
  """
  def get_ids_fields_gen_date(self, mission, dataset, data_id, gen_date):
    #
    querytxt = ("SELECT ids_data_set_name, ids_archive_class, "+
                "ids_ins_request_id, ids_path_name "+
                "FROM ingest_data_set_info WHERE "+
                "ids_mission = '"+mission+"' and "+
                "ids_group_name = '"+dataset+"' and "+
                "ids_group_data_id = '"+data_id+"' and "+
                "ids_generation_date = '"+gen_date+"' " )
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result) 
    return result

  """
=======================================================================
Name: update_ids_for_cleaning

Description:
------------
Updates the ids_install_flag = E and ids_clean_delay_days for all
records matching a given mission, dataset, data_id, and gen_date.
Uses the clean delay value from the ingest_cleanup table, joined
through the archive class.

Arguments:
----------
mission
dataset
data_id
gen_date

Returns: none

History:
--------
06/28/04 50703 MSwam     Initial version
01/12/05 52142 MSwam     set clean delay appropriate for archive class
=======================================================================
  """
  def update_ids_for_cleaning(self, mission, dataset, data_id, gen_date):
    #
    querytxt = ("UPDATE ingest_data_set_info SET "+
                "ids_install_flag = 'E', "+
                "ids_clean_delay_days = icl_clean_delay_days "+
                "FROM ingest_data_set_info ids, ingest_cleanup icl "+
                "WHERE ids_archive_class = icl_archive_class and "+
                "ids_mission = '"+mission+"' and "+
                "ids_group_name = '"+dataset+"' and "+
                "ids_group_data_id = '"+data_id+"' and "+
                "ids_generation_date = '"+gen_date+"' " )
    #
    opusutil.PrintMsg("I","attempting: "+querytxt)
    self._DB.query(querytxt)
    self._DB.executeUpdate()
    return

  """
=======================================================================
Name: get_ifi_rows

Description:
------------
This function returns a list of select fields for ingest_files rows
searched on mission, dataset, archive_class, and generation_date.

Arguments:
----------
mission
dataset
archive_class
gen_date

Returns:
--------
list of lists containing the field values for the selected rows OR
None if a matching row was not found

History:
--------
06/28/04 50703 MSwam     Initial version
=======================================================================
  """
  def get_ifi_rows(self, mission, dataset, archive_class, gen_date):
    #
    querytxt = ("SELECT ifi_file_name "+
                "FROM ingest_files WHERE "+
                "ifi_mission = '"+mission+"' and "+
                "ifi_data_set_name = '"+dataset+"' and "+
                "ifi_archive_class = '"+archive_class+"' and "+
                "ifi_generation_date = '"+gen_date+"' " )
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result) 
    return result

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
Name: insert_ingest_files

Description:
------------
This function inserts a new row in the ingest_files
table.

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
  def insert_ingest_files(self, archive_class, data_set_name,
                         generation_date, mission, file_extension,
                         file_name):
    #
    # assign default values
    checksum_status = "NONE"
    file_type_default = " "
    pre_compress_size_default = "0.0"
    post_compress_size_default = "0.0"
    verify_status_default = " "
    checksum_default = "0"
    #
    querytxt = ("INSERT ingest_files ("+
             "ifi_archive_class, ifi_data_set_name, ifi_generation_date, "+
             "ifi_mission, ifi_file_extension, ifi_file_name, "+
             "ifi_checksum_status, ifi_file_type, ifi_pre_compress_size, "+
             "ifi_post_compress_size, ifi_verify_status, "+
             "ifi_checksum) values ("+
          "'"+archive_class+"','"+string.upper(data_set_name)+
          "','"+generation_date+"',"+
          "'"+mission+"','"+file_extension+"','"+file_name+"',"+
          "'"+checksum_status+"','"+file_type_default+"',"+
              pre_compress_size_default+","+post_compress_size_default+","+
          "'"+verify_status_default+"',"+checksum_default+")" )
    opusutil.PrintMsg("I","attempting "+querytxt)
    #
    self._DB.query(querytxt)
    self._DB.executeUpdate()
    #
    return

  """
=======================================================================
Name: get_long_extensions

Description:
------------
Reads a subset of the ingest_long_ext table into a map.
Uses the product/exposure flag and mission passed to determine which 
subset of table to read.

Arguments:
----------
mission - name of the mission
is_product - Y/N indicating if extension is from a product or exposure

Returns: a map of short extensions keyed on long extension

History:
--------
03/18/04 49551 MSwam     Initial version
=======================================================================
  """
  def get_long_extensions(self, mission, is_product):
    #
    # build the query
    querytxt = ("SELECT ile_long_ext, ile_file_extension "
                "FROM ingest_long_ext WHERE "+
                "ile_mission = '"+mission+"' and "+
                "ile_is_product = '"+is_product+"'")
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    #
    if len(result) == 0:
      opusutil.PrintMsg("D","No product translation found for "+
                        mission+","+is_product)
      return {}
    #
    # format the result into a map, keyed on long extension
    theMap = {}
    for i in result:
      theMap[i[0]] = i[1]
    #
    return theMap

  """
=======================================================================
Name: ile_file_extension

Description:
------------
Reads the ile_file_extension field from the ingest_long_ext table, given
the search criteria of an ile_mission and ile_long_ext.

Arguments:
----------
mission - name of the mission
long_ext - long extension value to look up

Returns: a short extension value or an empty list

History:
--------
07/03/08 60170 MSwam     Initial version
=======================================================================
  """
  def ile_file_extension(self, mission, long_ext):
    #
    # build the query
    querytxt = ("SELECT ile_file_extension "
                "FROM ingest_long_ext WHERE "+
                "ile_mission = '"+mission+"' and "+
                "ile_long_ext = '"+long_ext+"'")
    #
    # get results in a list of lists
    result = [[]]
    self.zombie_select(querytxt, result)
    #
    if len(result) == 0:
      opusutil.PrintMsg("D","No short extension translation found for "+
                        mission+","+long_ext)
    #
    return result


#========================================================================
# TEST 
#========================================================================
if __name__ == "__main__":
  # connect to ARCH db
  dbobj = Arch_db(os.environ['ARCH_SERVER'], 
                  os.environ['ARCH_DB'])
  longext = dbobj.get_long_extensions("FUSE","Y")
  opusutil.PrintMsg("I",str(longext))
  dbobj.close()
