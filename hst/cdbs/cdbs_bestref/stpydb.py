#
##########################################################################
#
#                       *** Version 0.9 ***
#
# File:     stpydb.py
#
# Purpose:  This module contains a class, called stpydb, which is an
#           STScI-specific Python layer over public domain Python APIs.
#	    The layer is currently only supporting SYBASE.
#
#           See documentation in the stpydb class below for details.
#
# Public Members:    
#   __init__            - Constructor that sets up connection
#   getParamModeChar    - Returns the query param substitution char
#   setParamModeChar    - Defines the query param substitution char
#   setParam            - Defines value for a named parameter
#   query               - Pass a query string
#   execute             - Executes the query returning one row at a time
#   executeAll          - Executes the query returning all rows
#   executeUpdate       - Executes an update/insert/delete query
#   close               - Shuts down the connection
#   clear               - Clears an unfinished query
#   rowcount            - Returns #rows affected by a query
#   beginTransaction    - Starts a transaction on a given connection
#   commitTransaction   - Commits a transaction on a given connection
#   rollbackTransaction - Aborts a transaction on a given connection
#   getDescription      - Returns meta data info on last select query
#   printDescription    - Prints meta data report on last select query
#   callproc            - Run a stored procedure
#
# Modification History:
#    Date       Who     Notes
#    ---------- ------- -------------------------------------------------
#    12/10/1999 Bauer   Original implementation v0.1.  Lots of assistance 
#                       Danny Jones and Don Chance
#    02/20/2000 Chance  Significant updates to 0.1 release. 
#    03/10/2000 Bauer   Bug fixes per Kia's testing and code review
#    03/22/2000 Chance  Fixed many small problems found by Kia
#    06/14/2000 Chance  Fixed rowcount for updates
#    04/18/2001 Chance  Fixed bug in error path of stpydbConnection constructor 
#    07/25/2001 Chance  Populate self.args in error handler class
#    03/11/2003 Chance  Make error message more generic; removed returns from
#                       class constructors
#    03/04/2005 Reinhart Mods to stpydbGetenv to allow running on Mac OS X
#    07/05/2006 Chance  Updated for thread safety and 0.37 version of Sybase module
#    06/17/2006 Chance  Fix bugs introduced with 0.37 change 
#    05/09/2007 Chance  Detect dead connections
#    05/17/2007 Chance  modified for Sybase 0.38
#
##########################################################################
#

__version__ = "5/17/07"

import os, sys, string
from types import *
from time import *

#
# Support up to 10 seperate connections (similar to OpenSTDB)
#
MAX_CONN = 10

#
##########
#
# Globals
#
##########
#

#
# Declare a list of static connection lists that will allow the
# connections to be persistent across modules
#
connList          = [False] * MAX_CONN

#
# Provide debug feature for run time query debugging
#
debugMode         = False
debugStringPrefix = ""
debugFileOn       = False
debugFile         = ""
startClock        = 0.0
endClock          = 0.0
firstTime         = True
CONNECTION_MAX_AGE= 3600.
#
# Assume default parameter recognition character is @.  This is modelled
# after OpenSTDB, but this interface allows you to change this through the
# setParamModeChar call.
#
paramModeChar     = '@'

#
##########################################################################
#
# Class:   stpydbErrorHandler
#
# Purpose: Handles any errors from this package that result from either a
#          programming error or database error.  If these errors are not 
#	   trapped the application will exit.
#          and the handler will exit after diplaying error condition.
#
##########################################################################
#

class stpydbErrorHandler(StandardError):

    def __init__(self, args):
            print "\n *** stpydb detected fatal error: ", args
            self.args = args

#
##########################################################################
#
# Class:   stpydbCursor (private)
#
# Purpose: A wrapper around class for database cursors.  This is needed
#	   when the database supports the notion of a cursor for reading
#	   from the database.
#
#	   The methods provided here directly correspond to the cursor
#	   methods from the Python Database API.
#
##########################################################################
#

class stpydbCursor:

    def __init__(self, myConnection, id):
        self.inuseFlag    = True
        self.id           = id
        self.myConnection = myConnection
        self.myCursor     = self.myConnection.cursor()

    def clear(self):
        self.inuseFlag   = False
        self.myCursor.clear()
        return None

    def reserve(self):
        self.inuseFlag   = True
        return None

    def close(self):
        self.myCursor.close()

    def execute(self, query):
        self.myCursor.execute(query)

    def fetchone(self):
        return self.myCursor.fetchone()

    def fetchall(self):
        return self.myCursor.fetchall()

    def description(self):
        return self.myCursor.description

    def callproc(self, name, params = ()):
        return self.myCursor.callproc(name, params)

    def getRowcount(self):
        return self.myCursor.rowcount
    
#
##########################################################################
#
# Class:   stpydbConnection (private)
#
# Purpose: A wrapper around class over the Python DB API connection.
#          It is used to store the userName, serverName, dbmsName and other
#          connection specific information.
#
##########################################################################
#

class stpydbConnection:

    def __init__(self,
                 userName,                # Username
                 serverName,              # Database server name
                 dbmsName,                # Database name
                 systemType):             # Database type - always SYBASE
					  # for the initial implementation
	#				  
        # Constructor used to establish connection to the database.  It
        # contains the necessary parameters needed to make a connection
        # as outlined in the formal parameter list below.
	#				  
        global debugMode

        if systemType == "SYBASE":
            import Sybase     
            try:
                password = getSTScIdatabasePassword(userName, serverName)
		if password != None:
                    # auto_commit = 1 turns chained transactions OFF
                    self.entryPoint = \
			Sybase.connect(serverName, userName, password, auto_commit=1, datetime='auto')
		else:
                    raise stpydbErrorHandler("Cannot determine password - failed connection (%s,%s,%s)" % \
			(serverName, dbmsName, userName))
            except Sybase.Error, e:
                print e
                raise stpydbErrorHandler("Failed connection (%s,%s,%s)" %
			(serverName, dbmsName, userName))
        else:
            raise stpydbErrorHandler, "Unsupported database type: " + systemType

        self.userName    = userName		# Store connection info
        self.serverName  = serverName
        self.dbmsName    = dbmsName
        self.cursorDict  = {}			# Set up empty cursor dictionary
        self.start       = time()

    def getCursor(self):
        #
	# Finds the first available cursor in the cursor dictionary.  The
	# cursor dictionary is used so that we can optimally store this
	# information across modules using this layer, and avoid issuing
	# new cursors inadvertantly or unnecessarily.
	# 
        for cursor in self.cursorDict.values():
            if not cursor.inuseFlag:
                # 
                # Look what I found! A previously established cursor that 
		# is not currently being used.
                # 
                cursor.reserve()
                if debugMode:
                    stpydbDebug("Reusing cursor #%i" % cursor.id)
                    stpydbDebug(" ")
                return cursor
        else:
	    #	
            # No cursors or they're all in use.  Create new cursor and return it
	    #
            if self.cursorDict.keys():
                id = max(self.cursorDict.keys())+1
            else:
                id = 0
            self.cursorDict[id] = stpydbCursor(self.entryPoint, id)
            if debugMode:
                stpydbDebug("Creating new cursor #%i" % id)
                stpydbDebug(" ")
            return self.cursorDict[id]

    def is_locked(self):
        return self.entryPoint.is_locked()

    def is_alive(self):
        return self.entryPoint.is_alive()

    def age(self):
        return time() - self.start


#
##########################################################################
#
# Function:   stpydbGetenv 
#
# Purpose:    Returns the value of an environment variable (Unix) or 
#	      logical/symbol (VMS).  The input 'var' should be a string.
#	      This code was borrowed from the SPST python utilities.  
#	      It could be removed when VMS version is not supported.
#
##########################################################################
#

def stpydbGetenv(var):

    if (sys.platform[:3] == "sun") or (sys.platform == "darwin"):
        try:
            return os.environ[var]
        except KeyError:
            return None

    else:				# Assume you are on VMS
        import vms_sys
        dict = vms_sys.trnlnm(0,'LNM$DCL_LOGICAL',var,None,(('LNM$_INDEX', 0), ('LNM$_STRING', None)))
        if dict['status'] == 1:
            return dict['LNM$_STRING']
        else:
            return None

#
##########################################################################
#
# Function:   getSTScIdatabasePassword (private)
#
# Purpose:    Determines the password for the user running the Python
#	      script - the password is needed to log into the database
#             when establishing a connection.  If the password cannot be
#	      determined for any reason None is returned.
#
##########################################################################
#

def getSTScIdatabasePassword(userName, serverName):

    password = None			# Assume no password
    area     = stpydbGetenv("ACAREA")
    if area:
        fileName = area + userName + ".dat"
        pwdFile  = open(fileName, "r")
        allLines = pwdFile.readlines()
        pwdFile.close()

        for line in allLines:
            (server, tpassword) = string.split(line, " ")
            if server == serverName:
                password = tpassword[:-1]    # Get rid of newline
 
    return password

#
##########################################################################
#
# Function:   stpydbDebug (private)
#
# Purpose:    Used to print debug messages when requested by user.  Messages 
#	      are written to the screen or to the debug message file.   
#
##########################################################################
#

def stpydbDebug (debugString):
    global debugMode, debugFile, debugStringPrefix
    if debugMode:
        if debugFileOn:
            debugFile.write(debugString + '\n')    # Write out to debug file
        else:
            print debugStringPrefix, debugString   # Write to screen instead
						   # Prefix string only applies	
						   # to screen based debug 
    return None

#
##########################################################################
#
# Function:   stpydbPrintError (private)
#
# Purpose:    Used to print error messages when an interface error has 
#	      occurred in the database.
#
#	      Since the Python database API does not specify the structure of
#             the return value from an error, this function is database
#             module dependent.  HOWEVER, this error parameter may still 
#	      be Sybase specific!	
#
##########################################################################
#

def stpydbPrintError(error, queryString):
    print "Query : ", queryString
    if type(error[0][0]) is DictType:
        for key in error[0][0].keys():
            print key, ":", error[0][0][key]
    else:
        print error
        print "ERROR occurred in the database query."

#
##########################################################################
#
# Class:   stpydb
#
# Purpose: The main class for this module.  See the module header for
#	   details.  Only this class will obey the Python DOC standards for
#	   public documentation purposes.  The others do not because we do not
#	   want to publish these and encourage their usage.
#
# Databases Supported:
#		SYBASE - 2/2000
#
##########################################################################
#

class stpydb:
    """A class for connecting to STScI databases.  Version: %s

    The **stpydb** class provides an STScI standard Python database 
    interface. **stpydb** should be used instead of directly using a 
    database specific implementation of the Python Datbase API.  Note 
    the current layer is currently only supporting SYBASE.

    The layer provides many enhancements and simplifications to the 
    Python API, and many of the ideas within come from the OpenSTDB 
    software also used at STScI.

    The **stpydb** layer was developed for several reasons:

    * We wanted to avoid using the original SYBASE implementation,
    called *ctsybasemodule,* directly due to its lack of conformance 
    with the Python Database API 2.0, and to work around some features 
    that did not work correctly or at all.

    * To deal with some STScI-specific database login issues we wanted to
    hide the login process from the users and development teams.

    * To standardize how we query the Sybase database at STScI from 
    Python, with the hope that if we migrate away from Sybase the 
    conversion process will be much simpler.

    * To simplify querying and provide some useful enhancements

    The following features are implemented in this database layer:

    * Query connections are **persistent between modules**. This saves
    the overhead of closing and reestablishing connections in each 
    Python module accessing the database.  This provides an alternative
    to passing around the databse object throughout the application to 
    access the database.

    * Run-time debug statements to show what queries are being executed and 
    some result informantion can be displayed by defining the STPYDB_DEBUG 
    environment variable to some prefix string to be displayed ahead of 
    debug messages:  
                     'setenv STPYDB_DEBUG ">> "' This can be very useful when debugging scripts (motivated by a similar 
    feature provided by OpenSTDB).  If STPYDB_DEBUG is set to '++ ', debugging
    will also be turned on for the underlying database module (ie, Sybase).

    * Named parameter support for queries, and run-time substitution 
    for the parameters prior to query execution.

    * Row counting for all select and update statements.

    * Execution of stored procedures.

    * Some Sybase data types are not supported.
    """ % __version__

    global connList, systemType
    global debugMode, debugStringPrefix, debugFileOn, firstTime
 
    myConnId        = 0
    queryInProgress = False

    def __init__(self,
             serverName = stpydbGetenv("DSQUERY"),     # Database server
             dbmsName   = stpydbGetenv("STPYDB_NAME"), # Database name
             moduleName = "",                          # Module name of caller
             dbsystemType = "SYBASE"):                 # Database type 

        """Constructor used to establish connection to the database.

        It contains the necessary parameters needed to make a connection
        as outlined in the formal parameter list above.

        Note the following example constructor calls: '

        import stpydb

        q1 = stpydb.stpydb() 

        q2 = stpydb.stpydb('R2D2', 'pstdev1') 

        q3 = stpydb.stpydb('R2D2', 'pstdev1', 'xyz.py')
 
        q4 = stpydb.stpydb(dbmsName='pstdev1')

        """

        global firstTime, debugMode, debugStringPrefix, debugFileOn, debugFile
        global systemType

        systemType  = dbsystemType
	errorString = ""

        #
        # Import the Sybase component only if SYBASE requested!
        #
        if systemType == "SYBASE":
            import Sybase		 # Done to hide Sybase error handling
            self.dbError = Sybase.Error  # in case this grows into others...
        else:
            raise stpydbErrorHandler("Unsupported Database %s" % systemType)

        self.userName                = os.environ["LOGNAME"]
        self.firstTimeExecutingQuery = False
        self.columnName              = {}
        self.serverName              = serverName
	if self.serverName == None:
	    errorString = "\n  -- Database server was not supplied and cannot " +\
			  "be determined!\n"
        self.dbmsName                = dbmsName
	if self.dbmsName == None:
	    errorString = errorString + \
			  "  -- Database name was not supplied and SYPYDB_NAME " + \
			  "environment variable has not been set!"
        self.queryString             = ""
        self.originalQueryString     = ""
        self.rowcount                = 0
        self.description             = None
        self.myCursor                = None           # We won't get a cursor 
						      # until we need it.

	if errorString != "":			      # Make sure params OK	
            raise stpydbErrorHandler(errorString)

        if firstTime:
            #
            # Set debugging levels based on existence run time
            # environment variable
            #
            firstTime = False
            if stpydbGetenv("STPYDB_DEBUG"):
                 debugMode         = True
                 debugStringPrefix = stpydbGetenv("STPYDB_DEBUG")
                 if systemType == "SYBASE" and debugStringPrefix == "++ ":
                     Sybase.debug_on()
                 if stpydbGetenv("STPYDB_DEBUG_FILE"):
                     debugFileOn   = True
                     debugFileName = stpydbGetenv("STPYDB_DEBUG_FILE")
                     debugFile     = open(debugFileName, 'w')
                     stpydbDebug(" ")
                     stpydbDebug("--------------------------------------------")
                     stpydbDebug("STPYDB_DEBUG_FILE:  " + debugFileName)
                     stpydbDebug("Created:             "+
                                     asctime(gmtime(time())))
                     stpydbDebug("--------------------------------------------")
                     stpydbDebug(" ")
            else:
                 debugMode = False

        #
        # Use a pre-existing connection IFF one exists for that database,
	# server, username combination.
        #
        for connId in range(MAX_CONN):
            if connList[connId]:
                if (self.serverName == connList[connId].serverName and
                    self.userName   == connList[connId].userName   and
                    self.dbmsName   == connList[connId].dbmsName   and
                    not connList[connId].is_locked()):

                    if connList[connId].is_alive() and connList[connId].age() < CONNECTION_MAX_AGE:
                        self.myConnId     = connId    # use persistent connection
                        self.myConnection = connList[self.myConnId]
                        break
                    else:
                        # the connection is dead, so delete it from the list
                        connList[connId] = False
        else:
            #
            # No valid connection exists, therefore we'll have to make a new 
	    # one.  Steps for this include:
	    #     1. Get a valid connection number
            #     2. Establish the new connection
            #     3. Store it in the persistent connection list
            #
            for connId in range(MAX_CONN):
                if not connList[connId]:
                    self.myConnId = connId

                    stpydbDebug(" ")
                    stpydbDebug("Setting up connection #%d:" % connId)
                    stpydbDebug("    User:     %s" % self.userName)
                    stpydbDebug("    Server:   %s" % self.serverName)
                    stpydbDebug("    Database: %s" % self.dbmsName)
                    stpydbDebug(" ")

                    self.myConnection = stpydbConnection(self.userName,
                                                         self.serverName,
                                                         self.dbmsName,
                                                         systemType)
		    #	
                    # Store the connection in the connection list, and then
		    # physically set up querying to that database by issuing an
		    # SQL use <database> statement.  If this fails the database
		    # does not exist on that server.
		    # 
                    connList[self.myConnId] = self.myConnection
                    use_statement = "use %s" % self.dbmsName
                    try:
                        self.myConnection.entryPoint.execute(use_statement)
                    except self.dbError, e:
                        stpydbPrintError(e, use_statement)
                        self.close()
                        raise stpydbErrorHandler("Cannot use database %s on server %s" %
                                                 (self.dbmsName, self.serverName))
                    break
            else:
                raise stpydbErrorHandler(
                    "No more available connections.  Maximum # of connections = %d" % MAX_CONN)


    def query(self, queryString):
	"""Builds up a query string for eventual execution.

        It continually concatenates the string passed into an internal buffer
        and ships it to the database when one of the execute methods is called.
	"""
        
        self.queryString = self.queryString + queryString + " "
        self.originalQueryString = self.queryString

    def execute(self, results, updateMode=False):
        """Executes a query.  One row is return through 'results'.

	Executes a *select* query (remember that the query has been built up 
	in the query() calls).  This is executed within a loop and the loop 
	will fire for each row that gets returned or processed.

        This method takes a parameter that can be either a Python list 
	or a Python dictionary. The query results are returned one row at 
	a time in 'results'.  

	* When the result is passed back as a list, you must get at the result 
	  data by indexing into the list.  This list is in column order of the  
	  query.  The column ordering starts at 0.  Note that this can get 
	  complicated for wildcard select statements or for large queries.  

	* When the result is passed back as a dictionary, you can obtain the 
	  column value by using the column name (exact name with correct case)
	  as the index to the dictionary.

        Note that query column names are determined defacto when possible.
        However, if you use an SQL feature such as an aggregate, you must 
        provide a column name for the dictionary interface to behave properly.

        Finally, useful run-time debug information can be obtained when the 
	appropriate settings have been made prior to execution by the user.

	See also:	executeAll() and executeUpdate()
        """

        global systemType

        if systemType == "SYBASE":		# Needed in case you enter
            import Sybase			# this package from this level	
        else:
            raise stpydbErrorHandler, "Unsupported Database " + systemType

        retStatus = None
        if not self.queryInProgress:
            self.rowcount = 0
            if debugMode:
                self.printQuery()               # Dump the query
            self.startClock = time()            # On your mark, get set, GO

            if updateMode:
                try:
                    self.myConnection.entryPoint._lock()
                    self.myConnection.entryPoint.execute(self.queryString)
                except self.dbError, e:
                    stpydbPrintError(e, self.queryString)
                    self.clear()
                    raise stpydbErrorHandler("Failed query")

                # Get rowcount from @@rowcount
                try:
                    self.rowcount = self.myConnection.entryPoint.execute("select @@rowcount")[0][0][0]
                    self.myConnection.entryPoint._unlock()
                except self.dbError, e:
                    stpydbPrintError(e, "select @@rowcount")
                    self.clear()
                    raise stpydbErrorHandler("Fetching of the rowcount has failed")
                
                self.queryInProgress = False
                self.queryString     = ""
                self.description     = None
                retStatus	     = None
            else:
                # get a cursor
                self.myCursor = self.myConnection.getCursor()
                try:
                    self.myCursor.execute(self.queryString)
                except self.dbError, e:
                    stpydbPrintError(e, self.queryString)
                    self.clear()
                    raise stpydbErrorHandler("Failed query")

                self.queryInProgress	     = True
                self.firstTimeExecutingQuery = True
                self.description = self.myCursor.description()

        if not updateMode:
            if type([]) == type(results):       # Handle list results

                if self.firstTimeExecutingQuery:
		    self.firstTimeExecutingQuery = False
                    del results[:]                # Clear out results list first

                retData = self.myCursor.fetchone()
                if retData != None:
		   #
		   # Got results, so clear out list and rewrite it
		   # 
                   retStatus     = "MoreRowsToFetch"
                   self.rowcount = self.rowcount + 1
                   del results[:]
                   for i in range(len(retData)):
                       results.append(retData[i])
                else:
                    retStatus = None
                    self.clear()
                    self.myCursor.clear()

            elif type({}) == type(results):       # Dictionary

                #
                # When execute is passed a dictionary, the following must occur:
                #       - First time through set up keys based on the
                #         column names.  This takes advantage of the
                #         powerful metadata interface in the Python DB API
                #       - Subsequent times through populate the
                #         dictionary key values

                # get the description meta data from python db api
                # build up a dictionary such that it has the column name
                # as the index and the value as the value

                if self.firstTimeExecutingQuery:
		    self.firstTimeExecutingQuery = False
                    #
                    # Make sure the results dictionary is empty
                    #
                    for key in results.keys():
                        del results[key]
                    #
                    # Build up dictionary keys with column names
                    #
                    columns = self.myCursor.description()
                    thisColumnNum = 0
                    for column in columns:
                        results[column[0]]	       = None
                        self.columnName[thisColumnNum] = column[0]
                        thisColumnNum	               = thisColumnNum + 1

                retData = self.myCursor.fetchone()

                if retData != None:
		   #
		   # Store data by key (i.e. by column name)
		   #
                   retStatus     = "MoreRowsToFetch"
                   self.rowcount = self.rowcount + 1
                   for i in range(len(retData)):
                       results[self.columnName[i]] = retData[i]
                else:
                    #
                    # End of rows reached - do the following:
                    #            - set retStatus to end of list condition
                    #            - clear up some flag settings
                    #
                    retStatus = None
                    self.clear()
                    self.myCursor.clear()

            else:
                raise TypeError(
                  "Unsupported results type in execute call.  Can only be a list or dictionary")

	if retStatus == None:
	    #
	    # End of query hit.  Dump result info if requested
	    # 	
            self.endClock = time()
            if updateMode:
                stpydbDebug("<Conn# = %d, Row# = %d, Secs# = %6.3f>"
                            % (self.myConnId, self.getRowcount(),
                               (self.endClock - self.startClock)))
            else:
                stpydbDebug("<Conn# = %d, Cursor# = %i, Row# = %d, Secs# = %6.3f>"
                            % (self.myConnId, self.myCursor.id, self.getRowcount(),
                               (self.endClock - self.startClock)))

        return retStatus

    def executeAll(self, results):
        """Executes a query and returns all rows at once through 'results'.
        
	Executes a *select* query (remember that the query has been built up 
	in the query() calls).  The entire query is exectued and returned 
	instead of returning one single row as in execute().

        This method takes a parameter that can be either a list of Python lists 
	or a list of Python dictionaries.  Again *all* query results are 
	returned.  See execute() for details on the list and dictionary that
	is returned to determine what method you want to use.

        Finally, useful run-time debug information can be obtained when the 
	appropriate settings have been made prior to execution by the user.

	See also:	execute() and executeUpdate()
	"""
	typeErrorString = \
          """Unsupported results type in executeAll() call.  Can only be 
          a list of lists or a list of dictionaries"""
        if type([]) == type(results):
            try:
                if type([]) == type(results[0]):
                    # Return a list of lists; Zero out all the sublists
                    del results[:]
                    thisResult = []
                else:
                    # Return list of dictionaries; Zero out all sub-whatevers
                    del results[:]
                    thisResult = {}
            except IndexError:
                self.clear()
                raise TypeError(typeErrorString)

        else:
            raise TypeError(typeErrorString)

        #
        # Call the execute() method one row at a time and build
        # up the results list of ...
        #
        while self.execute(thisResult):
            if type({}) == type(thisResult):
                results.append(thisResult.copy())
            else:
                results.append(thisResult[:])

        return None


    def executeUpdate(self):
	"""Executes an update, insert, or other SQL DML query on the connection.
        This should be used for executing any query that will change the 
	contents or settings in the database.

        Remember that the udpate query has been built up in the prior
        query() calls.  

        Useful run-time debug information can be obtained when the 
	appropriate settings have been made prior to execution by the user.

	See also:	execute() and executeAll() 
        """
        ignoreResults = []
        self.execute(ignoreResults, updateMode=True)
        return None

    def getRowcount(self):
        """Returns the rowcount of the previously executed query.

        You should not call this until after the query has completed execution.
	"""
        return self.rowcount

    def beginTransaction(self, name=None):
        """Activates a transaction on the current connection.

        The transaction must eventually be committed or rolled back via the
        commitTransaction() or rollbackTransaction() calls.  Failure to do this
        prior to the connection close (explicit or at image exit) will result
        in a rollback transaction.

        The optional name argument allows you to make use of the Sybase ability
        to nest and name transactions.

	Notes:

	* Not all databases support transactions - use this accordingly.

	* Nested transactions are supported IFF the database supports them.

        * Named trasactions are not currently supported in this interface.

	See also:	commitTransaction() and rollbackTransaction()
	"""
        self.myConnection.entryPoint.begin(name)

    def begin(self, name=None):
        "See beginTransaction."
        self.beginTransaction(name)

    def commitTransaction(self, name=None):
        """Commits the previous transaction.
        
	Commits a previously activated transaction on the current connection.
        If there is no transaction active the call may result in an 
	error (depending on the database server).

        The optional name argument allows you to make use of the Sybase ability
        to nest and name transactions.

	See also:	beginTransaction() and rollbackTransaction()
	"""
        self.myConnection.entryPoint.commit(name)

    def commit(self, name=None):
        "See commitTransaction."
        self.commitTransaction(name)

    def rollbackTransaction(self, name=None):
        """Execute a transaction rollback.
        
	Rolls back a previously activated transaction on the current connection.
        If there is no transaction active the call may result in an 
	error (depending on the database server).  A rollback means any
	updates applied during the transaction are erased and the database
	is rolled back to the state prior to the start of the transaction.

        The optional name argument allows you to make use of the Sybase ability
        to nest and name transactions.

	See also:	beginTransaction() and commitTransaction()
	"""
        self.myConnection.entryPoint.rollback(name)

    def rollback(self, name=None):
        "See rollbackTransaction."
        self.rollbackTransaction(name)

    def close(self):
        """Closes down a connection for the particular server and database combination.  

	Notes:

	1 No more queries can be executed on the object.  Attempting this
	will result in an error.

	2 This is normally *not called by the average Python utility!* 
	This is because the connection is automatically closed for you when
	the application terminates.  You should only use this when you 
	have a long running application, such as a GUI, where you do not
	want to hold open idle database resources for a long time.
        """
        stpydbDebug("Closing connection %i (%s,%s)" 
                    % (self.myConnId, self.serverName, self.dbmsName))
        connList[self.myConnId] = False
        try:
            self.myConnection.entryPoint.close()
        except self.dbError:
            raise stpydbErrorHandler("""Close failed. You may be trying to close an already closed connection""")
        return None

    def getDescription(self):
        """Get the description information.
        
	Returns a meta data information about the most recently executed
	select query.  This format of the data is lightly described in 
	the API - see that for further details.  At a high level it 
	contains column specific information including its name, data type, 
	size, and some other information. 

	Notes:

	* If you run this function before a query has been processed through
	execute() or executeAll() the return value will be None.

	* You can call the method printDescription() to get a feel for the 
	each element in the dictionary type of information that is returned.

	* The order of data in each tuple of the list is:
        
	    1 field name

            2 field type code
            
            3 field display size

            4 field internal size
            
            5 field precision
            
            6 field scale
            
            7 field nulls OK status

	See also:	printDescription()
        """
        return self.description

    def printDescription(self):
	"""Prints the descriptions of the query columns in the previously executed *select* statement.  

	See also:	getDescription()
        """
        descriptDict = self.getDescription()
        if not descriptDict:
            print "No description"
            return None
        for description in descriptDict:
            print "Field name    : ", description[0] 
            print "Type code     : ", description[1]
            print "Display size  : ", description[2]
            print "Internal size : ", description[3]
            print "Precision     : ", description[4]
            print "Scale         : ", description[5]
            print "Nulls OK?     : ", description[6]
            print " "
        return None

    def setParamModeChar(self, modeChar):
        """Allows you to override the default parameter substitution character.
       
        See also:	getParamModeChar()
        """
	global paramModeChar

        paramModeChar = modeChar
        return None

    def getParamModeChar(self):
        """Returns the parameter substitution character currently in use.
       
        See also:	setParamModeChar()
        """
	global paramModeChar

        return paramModeChar

    def setParam(self, paramName, value=None):
        """Set a parameter within a query.

	This is used to set the values for parameters in a query.  It 
	provides a generic parameter passing mechanism for your queries.
	This was originally done because the API query mechanisms did not
	work.

	Restrictions:
	 
        * Currently only parameter types String, Int, Long, and Float are
	supported.
	
	* Strings with nested single quoted may not work.

	paramName format Notes:

	* If paramName is a string, it is assumed to be the parameter 
	name and 'value' its value.

        * if paramName is a list with the first element a string, the
        first element is assumed to be the parameter name and the
        second the value.  The parameter 'value' is ignored.

        * If paramName is a list of lists, each sublist is a parameter
	name and value pair. The parameter 'value' is ignored.  
        """

        #
        # The paramters are scanned in the query by searching for a
        # parameter character.  The default for this interface is to
        # use an @ however this can be overriden via setParamModeChar
        #
        import re
        if isinstance(paramName, StringType):
            # If paramPairsList comes in as a string, recast it as a tuple
            # inside a list.
            paramPairsList = [(paramName, value)]
        elif ((type(paramName) == type([]) or type(paramName) == type(())) and
              (type(paramName[0]) == type("") and len(paramName) == 2)):
            paramPairsList = [paramName]
	elif ((type(paramName) == type([]) or type(paramName) == type(())) and
              (type(paramName[0]) == type([]) or type(paramName[0]) == type(()))):
	    paramPairsList = paramName 
        else:
            raise TypeError("""paramName must be one of the following:
            a string, a list, or a tuple.  If it is a list or tuple, the first
            element must also be a string, a list or tuple.""")
        
        for paramPair in paramPairsList:
            paramName  = paramPair[0]
            paramValue = paramPair[1]

            nParamName = paramModeChar + paramName

            if type(paramValue) is StringType:
                nParamValue = "'" + paramValue + "'"
            elif type(paramValue) in (IntType, LongType):
                nParamValue = "%d" % paramValue
            elif type(paramValue) is FloatType:
                nParamValue = "%f" % paramValue
            else:
                self.clear()
                raise TypeError(
                    "Unsupported parameter datatype: " + nParamName)

	    #	
            # Find and substitute the parameter value for the parameter name,
            # but only when the parameter name is followed by some
            # non-alphanumeric character.  Use regular expressions to handle
	    # the substitution.
	    #
            pattern = "(%s)(?=\W)" % nParamName  # See manual
            new_query_string = re.sub(pattern, nParamValue, self.queryString)
	    self.queryString = self.originalQueryString
            if self.queryString != new_query_string:
                self.queryString = new_query_string
            else:
                self.clear()
                raise stpydbErrorHandler(
                    "Invalid setParam call.  No such named parameter: " + nParamName)
        return None

    #
    # Private member that displays the query through the debug interface
    #
    def printQuery(self):

        import string
        stpydbDebug("")
        stpydbDebug("Executing query: ")
        stpydbDebug("--- --- --- --- --- ---")
        query_list = string.split(self.queryString)
        line = ""
        for word in query_list:
            if len(line + " " + word) > 80:
                stpydbDebug(line)
                line = " " + word
            else:
                line = line + " " + word
        stpydbDebug(line)
        stpydbDebug("--- --- --- --- --- ---\n")
        return None

    def clear(self):
        """Clears the current **stpydb object** for use in another query. 
	This must be done if you exit out of an execute() loop prior to 
	fetching all of the data.
        """
        self.queryString             = ""
        self.originalQueryString     = ""
        self.queryInProgress         = False
        self.firstTimeExecutingQuery = False
        if self.myCursor:
            self.myCursor.clear()

    def callproc(self, name, params = ()):
        """Execute a stored procedure.  Paramaters to the procedure can
        be a sequence or dictionary which contains one entry for each
        argument that the procedure expects. Examples:

            c.callproc('sp_who')
            c.callproc('sp_columns', ['pm_constants'])
            c.callproc('sp_columns', {'table_name': 'pm_constants', 'column_name': 'number_of_gyros'})

        A list of dictionaries is returned.
        """
        if debugMode:
            stpydbDebug("Executing stored procedure: %s" % name)
            if params:
                stpydbDebug("Parameters: %s" % str(params))
            stpydbDebug(" ")
        if isinstance(params, dict):
            # add @ to each key if it's not already there
            new_params = {}
            for key in params.keys():
                if str(key)[0] != '@':
                    newkey = '@' + str(key)
                else:
                    newkey = key
                new_params[newkey] = params[key]
            params = new_params

        Cursor = stpydbCursor(self.myConnection.entryPoint, 999)
        #Cursor.execute("SET CHAINED OFF")
        Cursor.callproc(name, params)
        ret  = Cursor.fetchall()
        desc = Cursor.description()
        keys = []
        Ldicts = []
        for col in desc:
            keys.append(col[0])
        for row in ret:
            Dict = {}
            for key, value in zip(keys, row):
                Dict[key] = value
            Ldicts.append(Dict)
        
        #Cursor.execute("SET CHAINED ON")
        self.rowcount = len(Ldicts)
        Cursor.close()
        return Ldicts

















