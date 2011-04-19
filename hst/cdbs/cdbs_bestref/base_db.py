import os
import string
import time
import sys

import stpydb
import opusutil

# exceptions thrown
class DBConnectionProblem(Exception):
  pass

class TooManyDBErrors(Exception):
  pass

class Base_db:
  """
=======================================================================
Class: Base_db

Description:
------------
This class is a base class providing common function needed by all
of the database-specific db query classes.

Members:
--------
_server = name of database server
_dbname = name of database
_DB = database object used to gain db access

Methods:
--------
connect     - connects to the database
close       - closes the database connection
zombie_select - run an SQL SELECT query
chunked_zombie_update - wrap an SQL update in row-change limits and
                        run an SQL UPDATE query
listSqueeze - converts a doubly-dimensioned list ([][]) with only single
              elements in the 1st dimension to a singly dimensioned list,
              with each entry trimmed of trailing blanks

History:
--------
10/01/02 xxxxx MSwam     Initial version
04/08/04 50605 Sontag    Force use of traditional 32-bit DB calls
06/13/05 53120 Sontag    Take 32-bit Sybase fallback path from env var
02/05/09 61864 MSwam     Remove 32-bit fallback and db retries
02/12/09 61864 MSwam     Well, keep 32-bit fallback to support Kepler
07/15/10 65561 MSwam     set retry to an unused, default=0 parameter
01/03/11 67113 MSwam     improve the unit test code to exercise more functions
=======================================================================
  """
  def __init__(self, server, dbname, notUsed=0):
    have64bit = False
    if sys.maxint > 2147483647:
       have64bit = True
    #
    if not have64bit:
      # need to assign the 32-bit Sybase fallback for 32-bit Python
      assert os.environ.has_key('SYBASE_32_FALLBACK'), \
         "Required env var \"SYBASE_32_FALLBACK\" not found."
      os.environ['SYBASE'] = os.environ['SYBASE_32_FALLBACK']

    if (os.environ.has_key('SYBASE_OCS')):
       os.environ['SYBASE_OCS'] = ''

    # Initialize members
    self._server = server
    self._dbname = dbname
    self._DB = None
    self.connect()

  """
======================================================================

 Name: connect

 Purpose: Connects to the database.

 History:
 --------
 12/13/07 58974 MSwam     rethrow caught exception to get all possible info

========================================================================
  """
  def connect(self):
    # connect to db
    try:
      self._DB = stpydb.stpydb(self._server, self._dbname)
    except:
      opusutil.PrintMsg("E","Failure to connect to database "+
                        self._server+":"+self._dbname)
      # rethrow so we get all possible information
      raise

  """
======================================================================

 Name: close

 Purpose: Closes an open database object.

========================================================================
  """
  def close(self):
    self._DB.close()

  """
=======================================================================
Name: zombie_select

Description:
------------
Executes an SQL query and returns the result.

NOTE: The "zombie" label is legacy from when a retry loop used to exist 
      and was INFINITE.  Either the query would
      eventually succeed or the process would have to be killed to stop it
      (hence, the zombie).  Retries are no longer performed, as they
      weren't really able to recover from anything.

Arguments:
----------
querytxt - the SQL text of the query to run
result - structure for query results to be returned in

Returns: a list of lists

History:
--------
10/01/02 xxxxx MSwam     Initial version
02/05/09 61864 MSwam     Remove retries
=======================================================================
  """
  def zombie_select(self, querytxt, result):
    #
    opusutil.PrintMsg("D",querytxt)
    self._DB.query(querytxt)
    self._DB.executeAll(result)
    #
    return result

  """
=======================================================================
Name: chunked_zombie_update

Description:
------------
Wraps an SQL UPDATE query in row-limiting code (chunk) and runs the query.
This is done to break up any resulting large update set into smaller chunks that
won't choke the replication server and DB logs.

NOTE: The "zombie" label is legacy from when an INFINITE retry used to be
      part of the code.  Either the query would
      eventually succeed or the process would have to be killed to stop it
      (hence, the zombie).  Retries are no longer performed, as they
      could never really recover from anything.

Arguments:
----------
the_query - the SQL text of the UPDATE query to run
updatelimit - number of row updates allowed in each update "chunk"

Returns: none

History:
--------
10/01/02 xxxxx MSwam     Initial version
02/05/09 61864 MSwam     Remove retries
03/17/10 64273 MSwam     Need to catch zero-row exception for Linux/PyODBC
=======================================================================
  """
  def chunked_zombie_update(self, the_query, updatelimit):
    #
    # set up loop limiting code
    querytxt = "declare @the_count int "
    querytxt = querytxt + "set rowcount "+str(updatelimit)+" "
    querytxt = querytxt + "select @the_count = "+str(updatelimit)+" "
    querytxt = querytxt + "while (@the_count = "+str(updatelimit)+") "
    querytxt = querytxt + "begin "

    # add the passed query UPDATE statement
    querytxt = querytxt + the_query

    # complete loop limiting code
    querytxt = querytxt + "  select @the_count = @@rowcount "
    querytxt = querytxt + "end"

    # define and run the query
    opusutil.PrintMsg("D",querytxt)
    self._DB.query(querytxt)
    try:
      self._DB.executeUpdate()
    except TypeError:
      # a common occurence of this exception is when ZERO rows are
      # found to update, so let's ASSUME that happened until we find
      # a case that proves otherwise
      opusutil.PrintMsg("W","STPYDB exception most likely indicates ZERO updated rows from query: "+querytxt)
    return

  """
=======================================================================
Name: update

Description:
------------
Runs a database UPDATE query WITHOUT "chunking" the updates.

Arguments:
----------
the_query - the SQL text of the UPDATE query to run

Returns: none

History:
--------
09/08/10  MSwam  65360  first version
=======================================================================
  """
  def update(self, querytxt):
    #
    # define and run the query
    opusutil.PrintMsg("D",querytxt)
    self._DB.query(querytxt)
    try:
      self._DB.executeUpdate()
    except TypeError:
      # a common occurence of this exception is when ZERO rows are
      # found to update, so let's ASSUME that happened until we find
      # a case that proves otherwise
      opusutil.PrintMsg("W","STPYDB exception most likely indicates ZERO updated rows from query: "+querytxt)
    return

  """
=======================================================================
Name: listSqueeze

Description:
------------
A common DB query is to perform a select on a single field but get 
back more than one match.  These come back from stpydb in a doubly-dimensioned
list, where the last dimension of each list item is 1 (index=0).
(e.g. results[[]] = result[0][0], result[1][0], result[2][0], etc.
This utility will convert such a list into a singly-dimensioned list,
with each entry trimmed of trailing space, to make it easier to work with.
(e.g. result[0], result[1], result[2], etc.)

Exceptions:
----------
An assertion exception is raised if the last dimension of each list item
is not 1, as expected.

Arguments:
----------
results - the list of lists that needs conversion

Returns:
---------
newlist - the singly dimensioned list created

History:
--------
09/19/07 58120 MSwam     initial version
=======================================================================
  """
  def listSqueeze(self, results):
    #
    newlist = []
    for anItem in results: 
      assert len(anItem) == 1,("base_db::listSqueeze: length of "+
                               str(anItem)+" not 1")
      newlist.append(anItem[0].rstrip())
    #
    return newlist


#========================================================================
# TEST 
#========================================================================
if __name__ == "__main__":
  dbobj = Base_db(os.environ['OPUS_SERVER'], 
                  os.environ['OPUS_DB'])
  result = [[]]
  querytxt = "SELECT count(*) from validation"
  dbobj.zombie_select(querytxt, result)
  opusutil.PrintMsg("I","count from validation table = "+str(result))

  querytxt = ("INSERT dads_archive (dataset_name, archclass, archdate,"+
    "reqdate, reqtype, response, disk_date, file_cnt, path,"+
    "tape_date, saveset, archv_tape, catalog_date) VALUES ("+
    "'TEST_DSET','ACS','Jan 1 1990 12:00AM','Jan 2 1990 12:00AM','1234',"+
    "'MY_RESP','Jan 3 1990 12:00AM',99,'PATHNAME','Jan 4 1990 12:00AM',"+
    "'SAVESET_VALUE','ARCHVT','Jan 31 1990 12:00:00:000AM')")
  dbobj._DB.query(querytxt)
  dbobj._DB.executeUpdate()

  ## SELECT the just-inserted row
  result = [[]]
  querytxt = "SELECT * from dads_archive WHERE dataset_name = 'TEST_DSET'"
  dbobj.zombie_select(querytxt, result)
  opusutil.PrintMsg("I","SELECT from dads_archive table = "+str(result))

  ## UPDATE
  querytxt = ("UPDATE dads_archive SET archclass = 'BCS' WHERE "+
              "dataset_name = 'TEST_DSET'")
  dbobj._DB.query(querytxt)
  dbobj._DB.executeUpdate()

  ## confirm UPDATE via another SELECT
  result = [[]]
  querytxt = "SELECT * from dads_archive WHERE dataset_name = 'TEST_DSET'"
  dbobj.zombie_select(querytxt, result)
  opusutil.PrintMsg("I","SELECT from dads_archive table with archclass now BCS = "+str(result))

  ## DELETE
  querytxt = ("DELETE FROM dads_archive WHERE archclass = 'BCS' and "+
              "dataset_name = 'TEST_DSET'")
  ## THIS FORM FAILS UNDER MS SQL WITH A STPYDB ERROR:
  ##('24000', '[24000] [FreeTDS][SQL Server]Invalid cursor state (0) (SQLExecDirectW)')
  ##dbobj.chunked_zombie_update(querytxt, 10)
  dbobj.update(querytxt)

  ## confirm DELETE via another SELECT
  result = [[]]
  querytxt = "SELECT * from dads_archive WHERE dataset_name = 'TEST_DSET'"
  dbobj.zombie_select(querytxt, result)
  opusutil.PrintMsg("I","SELECT from dads_archive AFTER DELETE = "+str(result))

  ## ALL DONE
  dbobj.close()
  opusutil.PrintMsg("I","DONE.")
