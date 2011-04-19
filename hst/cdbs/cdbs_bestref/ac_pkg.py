#!/usr/bin/env python
##------------------------------------------------------------------------------
##
## ac_pkg.py
##
##  This is a package of modules which can be shared...
##  Use 'pydoc ac_pkg' to see list of Modules and doctests.
##
## If no docstring is provided, then the comment block above the method
## is displayed by pydoc.  Alas, if there is a docstring, for a doctest, e.g.,
## then the comment block above is left out.  Therefore, to get consistent 
## results out of pydoc, when there is no doctest, the comment block will
## be completely above the def line for the method.  But when there is a 
## doctest, I have moved the comment block into the docstring, with a minimal 
## method name above it.
## 
## I personally find code with pre-definition comments much easier to read.
## Alas, pydoc disagrees.
## 
##
## History:
## yy/mm/dd PR    Who        Description
## -------- ----- ---------- ---------------------------------------------------
## 08/12/29 60896 Sherbert   First attempt at creating package
## 09/06/12 62840 Sherbert   unexpected uncalibrated COS ASNs
## 09/08/07 63029 Sherbert   undo above and begin clean up of sys.exit()
## 
##------------------------------------------------------------------------------

import os
import sys
import glob
import getopt
import shutil 
import opusutil
from opusutil_pyfits import  *

## Global variables (in this package only)
pkgName = 'ac_pkg'

## STPYDB_DEBUG will print the query
## MSG_REPORT_LEVEL being set will print query base_db's way
## DB_VERBOSE = 1 will print the query my way
## I would like to see either no query or the query only printed
##     once, not mutliple times.  But since I only want to print 
##     it when MSG_REPORT_LEVEL is up, it will be printed twice
##     because base_db uses it.
## SO, I want to know if STPYDB_DEBUG is set, and if so, I will 
## NOT print the debug messages for SQL queries if MSG_REPORT_LEVEL
## is also set.  That way the query is printed twice at most!  
try:
    DB_VERBOSE = os.environ['STPYDB_DEBUG']
    msg = "STPYDB_DEBUG set, setting DB_VERBOSE to " + str(DB_VERBOSE)
except:
    try:
        os.environ['MSG_REPORT_LEVEL']
        DB_VERBOSE = 1
        msg = "MSG_REPORT_LEVEL set, setting DB_VERBOSE to " + str(DB_VERBOSE)
    except:
        DB_VERBOSE = 0
        msg = "setting DB_VERBOSE to " + str(DB_VERBOSE)

opusutil.PrintMsg('D', msg)

## exit variables
ALL_IS_WELL = 0
GO_ABSENT = 102          #this exit status is in the FATAL range for XPOLL
QUIT_THIS_DATASET = 1    #this exit status is mapped and will allow

true  = 1
false = 0


##------------------------------------------------------------------------------
## banner
##------------------------------------------------------------------------------
def banner():
    """
##------------------------------------------------------------------------------
##
## Method: banner
## Purpose: Print separator
## Suggested usage: at very beginning of processing a new obs
##                  just before sys.exit(GO_ABSENT)
##
## Returns: nothing
##
##------------------------------------------------------------------------------

    """
    banner=">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
    print banner
    return 

##------------------------------------------------------------------------------
## Method: envSetUp
##
## Purpose:
##     return a dictionary of what ENV vars are needed.
##     { envVar:value, ... }
##
## Input:
##     source: 'env' or 'cmdLine'
##     envVarArray: ?
##
##
##------------------------------------------------------------------------------
def envSetUp(source, envVarArray):
    methodName = pkgName + '-envSetUp' 
    vars = {}
    count = 0
    if source == 'env':
        msg1 = " input arguments from environment: \n"
        opusutil.PrintMsg('D', 'Processing env vars', methodName )
        ## Set up environ variables required if there are no arguments 
        for envMem in envVarArray:
            try:
                vars[envMem] = os.environ[envMem]
            except:
                msg = envMem + ' must be defined in environment. ' 
                opusutil.PrintMsg( 'E', msg, methodName )
                count = count + 1
        
        if count:
            msg = 'Missing one or more required environment variables.'
            raise RuntimeError, msg

    else:
        opusutil.PrintMsg('D', 'Processing cmd line vars', 'envSetUp')
        ## Read command line arguments 
        try:
            opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
        except getopt.GetoptError, msg:
            # print help information and exit:
            raise RuntimeError, msg
 
        ## parse options
        for flag, value in opts:
            if flag in ("-h", "--help"):
                msg = "Here is the usage statement"
               #raise RuntimeError, msg
                raise AttributeError, msg
 
        ## Number of parameters on command line must match size of envVarArray
        ## True number of arguments does NOT count the command name...
        numArgs = len(sys.argv) - 1
        if numArgs != len(envVarArray):
             msg = "Number of arguments incorrect. "
             raise AttributeError, msg

        ## Else assign args to vars in expected order (barf)
        i = 0
        for envMem in envVarArray:
            vars[envMem] = args[i]
            i = i + 1
 
        msg1 = " input arguments on command line: \n"
    
    msg1 = "Received these "+ str( len(vars) ) + msg1
    msg2 = ""
    for var in vars:
        msg2=msg2 + var + "  = " + vars[var]   + " \n"
    msg3 = msg1+msg2
    opusutil.PrintMsg('D', msg3)

    return vars



##------------------------------------------------------------------------------
## verify_SI
##------------------------------------------------------------------------------
def verify_SI(dataset, si):
    """
##------------------------------------------------------------------------------
## 
## Method: verify_SI
##
## Purpose: Verify dataset is an observation of the provided instrument
## 
## Inputs:
##     - dataset -- name of observation
##     - si      -- name of science instrument (si) that observation is expected 
##                  to have used.  Verification based solely on first character 
##                  of dataset name, therefore parallels NOT allowed.
## Returns: 
##     1 -- (true)  dataset was taken with provided si
##  or 0 -- (false) first char of dataset name does  NOT match what is expected
##                  for provided si
## 
##------------------------------------------------------------------------------

    >>> verify_SI('l9v214010', 'COS')
    1
    >>> verify_SI('n6277w010', 'COS')
    0
    """
    from siname import WhichInstrument

    msg = "Calling siname.WhichInstrument(" + dataset + ")"
    opusutil.PrintMsg('D', msg)

    try:
        instrument = WhichInstrument(dataset)
    except :
        instrument = "xxx"

    msg = "instrument is " + instrument
    opusutil.PrintMsg('D', msg)
    if  instrument != si :
        msg = "Not a[n] " + si + " observation "
        opusutil.PrintMsg('D', msg)
        return false
    else:
        return true


##------------------------------------------------------------------------------
##
## Method: verify_n_cd_to_dir
## 
## Purpose: 
##     Verify existence of and cd to provided dir
##
## Input: this_dir -- dir to cd to
##
## Returns: 0 -- always good else goes absent
##
## Exceptions:
##    RuntimeError if list of files does not match expected sets
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/10 63318 Sherbert   continue clean up of sys.exit()
##
##------------------------------------------------------------------------------
def verify_n_cd_to_dir(this_dir):
    methodName = pkgName + '-verify_n_cd_to_dir' 
    ## move to working directory
    if not os.path.exists(this_dir):
        msg = this_dir + " directory does not exist"
        banner()
        raise RuntimeError, msg
    try: 
        ## do I even want to cd there?
        ## If not, must pass this_dir around which I currently do NOT do
        os.chdir(this_dir)
    except:
        msg  = "Failed to set directory to " + this_dir
        msg += "\n" 
        banner()
        raise RuntimeError, msg
    
    msg = "set directory to " + this_dir
    opusutil.PrintMsg('I', msg)
    return 0

##------------------------------------------------------------------------------
## COSfileTypes
##------------------------------------------------------------------------------
def COSfileTypes( files ):
    """
##------------------------------------------------------------------------------
##
## Method: COSfileTypes
##
## Determine the type of COS observation (ASN, ACQ, EXP) by looking at the 
## files the rootname has on-disk
##
## Inputs:
##    filenames
##    
##
## Returns:
##    list of [type, filename] 
##    where type can be ACQ (target acquisition)
##                      ASN (association)
##                   or EXP (exposure)
##    and filename is the file whose suffix determined the type
##                   This is the file that will need to be copied.
##                   For an EXPosure, that is always the SPT file.
##
## Exceptions:
##    RuntimeError if list of files does not match expected sets
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/07 63029 Sherbert   undo 62840 and begin clean up of sys.exit()
##
##------------------------------------------------------------------------------

    >>> files = ['l9v214020_asn.fits', 'l9v214020_jnk.fits', 'l9v214020_trl.fits', 'l9v214020_x1dsum.fits' ]
    >>> COSfileTypes( files )
    ['ASN', 'l9v214020_jnk.fits']
    >>> files = ['l9v223g6q_rawacq.fits', 'l9v223g6q_spt.fits', 'l9v223g6q_trl.fits']
    >>> COSfileTypes( files )
    ['ACQ', 'l9v223g6q_rawacq.fits']
    >>> files = ['l9v205aas_rawtag.fits', 'l9v205aas_spt.fits', 'l9v205aas_trl.fits']
    >>> COSfileTypes( files )
    ['EXP', 'l9v205aas_spt.fits']
    >>> files = ['la8p01270_asn.fits' ]
    >>> COSfileTypes( files )
    Traceback (most recent call last):
    ...
    RuntimeError: Could not find a file to copy (see PR 60896) from this list of files: ['la8p01270_asn.fits']
    """
    methodName = pkgName + '-COSfileTypes' 
 
    ## Expect most observations are neither ACQs nor ASNs
    ## And treat members and singletons the same (exposures)
    for filename in files:
        ## First get rid of directory spec
        ## Then split filename on period
        ## Then split rootname on _first_ underscore from left
        suffix = os.path.basename(filename).split('.')[0].split('_',1)[1]
        debug = "current suffix   is " + suffix
        opusutil.PrintMsg('D', debug)
        ## ACQ observations will have a suffix containing acq
        ## ASN observations will have a suffix containing jnk
        ## EXP will be anything that did not match above,
        ##     but still has a file contaiing spt
        if suffix.find('acq') >= 0 and not suffix.find('copy') >= 0:
            type = "ACQ"
            return [type, filename]

        if suffix.find('jnk') >= 0 and not suffix.find('copy') >= 0:
            type = "ASN"
            return [type, filename]

        ## If the above all fail, save the spt name as default
        if suffix.find('spt') >= 0 and not suffix.find('copy') >= 0:
            type = "EXP"
            return [type, filename]

    ## If we get here, then no appropriate files were found, so exit
    msg = "Could not find a file to copy (see PR 60896) from this list of files: "
    raise RuntimeError( msg + str(files) )
    ## raising an exception seems like the right thing to do
    ## - calling program can use try/except instead of checking for a priori 
    ##   known bad value.
    ## - packages of modules should NOT be using sys.exit
    ##   I knew this when I wrote it, just didn't realize raise was a replacement



##------------------------------------------------------------------------------
##
## Method: getIFMcopySuffixes
##
## Return a dictionary of fileSuffixes keyed on fileClass
##
## Inputs:
##    KW_SERVER for keyword database
##    KW_DB     for keyword database
##
## Returns:
##    fileClass_fileSuffix (dictionary)
##
## Exceptions:
##    RuntimeError if list of files does not match expected sets
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/07 63029 Sherbert   begin clean up of sys.exit()
##
##------------------------------------------------------------------------------
def getIFMcopySuffixes( KW_SERVER, KW_DB):
    methodName = pkgName + '-getIFMcopySuffixes' 

    import kwdbquery
    kw_db = kwdbquery.Kw_db( KW_SERVER, KW_DB)

    results=[[]]
    fileClass_fileSuffix = {}

    ## Currently expect COS ifm_fileclass to end in "2" for
    ## COS ifm_suffix-es ending in "copy"

    ## Perform one database query then use the results in the script
    try: 
        fileClass_fileSuffix = kw_db.getCOSifmCopySuffixes()
    ## Any of these exceptions would break all observations, 
    ## so caller may want to go absent
    except kwdbquery.NoMatchingRows:
        kw_db.close()
        ## This could only mean 0 rows returned
        msg  = "Found NO COS ingest_files_mapping results for query "
        msg += "in kwdbquery.getCOSifmCopySuffixes() " 
        raise RuntimeError, msg
    except kwdbquery.IncorrectNumberOfRows, errMsg:
        kw_db.close()
        ## This would not be good:  unexpected number of cases 
        msg  = "Found incorrect number of ifm_suffix values matching '%copy' "
        msg += "from kwdbquery.getCOSifmCopySuffixes() query.  " 
        msg += "Query results are " + str(errMsg) + "."
        raise RuntimeError, msg
    except:
        ## Although seeing the Trace may be useful, I can make process
        ## go absent if I catch here
        kw_db.close()
        msg  = "Unknown exception encounterd in "
        msg += "kwdbquery.getCOSifmCopySuffixes() "
        raise RuntimeError, msg

    kw_db.close()
    return fileClass_fileSuffix


##------------------------------------------------------------------------------
## Method: rmOldFile
##
## Purpose: 
##     Need to do remove a file from 2 diff methods, so moved here
##
## Inputs:
##     filename - name of file to be removed
##     methodName -- name of calling method for output message
##
## Returns: 0 
##
##------------------------------------------------------------------------------
def rmOldFile(filename, methodName):
    if os.path.exists(filename):
        os.unlink(filename)
        msg = "Removed existing " + filename
        opusutil.PrintMsg('W', msg )

    return 0 


##------------------------------------------------------------------------------
##
## Method: createNewFile
##
## Purpose: 
##     Simple copy of a file.  Method determines new name from rootname and 
##     suffix provided.  Uses provided original file for source name.
##
## Inputs:
##    rootname
##    suffix   -- suffix for new file
##    source   -- file to copy
##
## Returns:
##    0 if copy is successful
##
## Exceptions:
##    RuntimeError if copy fails
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/07 63029 Sherbert   begin clean up of sys.exit()
##
##------------------------------------------------------------------------------
def createNewFile( rootname, suffix, source  ):

    methodName = pkgName + '-createNewFile'

    newName = rootname + "_" + suffix + ".fits"
    ## Do NOT add a separator unless there is a preceding pathname
    ## for source file.  Otherwise, instead of "./newFile", we get
    ## "/newFile" and permission errors when we try to write the file.
    srcDir = os.path.dirname(source) 
    if len(srcDir) > 0:
        srcDir = srcDir + os.sep 
    newFile = srcDir + newName

    ## Not entirely certain I want to remove newName or newFile?
    rmOldFile(newFile, methodName)

    msg = "Copy " + os.path.basename(source) + " to " + newName
    opusutil.PrintMsg('I', msg)
    shutil.copyfile( source, newFile ) 
    ## Is there a way to check success?
    if os.path.exists( newFile ):
        ## Success
        return 0
    else:
        ## Failure
        msg = "Copy error for " + source
        raise RuntimeError, msg

##------------------------------------------------------------------------------
##
## Method: createNewSPT
##
## Purpose: 
##     Calls the method to create the new SPT files based on information 
##     already collected.  Wrapper around makeSPTcopy so same messaging 
##     can be reused and cleans up the main code.
##
## Inputs:
##    rootname 
##    suffix   -- suffix for new file
##    source   -- file to copy
##    ext      -- e.g. SNAP1 or SNAP2
##
## Returns:
##    0 if copy is successful
##
## Exceptions:
##    RuntimeError if copy fails
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/07 63029 Sherbert   begin clean up of sys.exit()
##
##------------------------------------------------------------------------------
def createNewSPT( rootname, newSuffix, source, ext ):
        ## This should be source: rootname + "_spt.fits"
        newName = rootname + "_" + newSuffix + ".fits"
        oldSuf = os.path.basename(source).split('.')[0].split('_',1)[1]
        ## I like this debug because it shows me what I send to method
        msg  = "makeSPTcopy(" +rootname+", "+oldSuf+", "
        msg += newSuffix+", " +ext+ ")"
        opusutil.PrintMsg("D", msg)
        cpStat = makeSPTcopy(rootname, oldSuf, newSuffix, ext )
        if cpStat:
            ## Failure
            msg = "Copy error for " + source
            raise RuntimeError, msg
        else:
            ## Success
            return 0

##------------------------------------------------------------------------------
##
## Method: getSuffix
##
## Purpose: 
##     Since it is the same error check for all file copies
##     use a method to do it.  Cleans up main.
##
## Input:
##    status -- return status from file copy method
##    source -- file whose copy failed
##
## Returns: 
##    prints a message, and 
##    returns 0 -- success
##
## Exceptions:
##    RuntimeError if list of files does not match expected sets
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/07 63029 Sherbert   begin clean up of sys.exit()
## 09/08/10 63318 Sherbert   Add a test
##
##------------------------------------------------------------------------------
def getSuffix ( suffixChoices, key ):
    """
    >>> hash = {'1':'one', '2':'two'}
    >>> getSuffix ( hash, '2' )
    'two'
    >>> getSuffix ( hash, '3' )
    Traceback (most recent call last):
    ...
    RuntimeError: Could NOT find key 3 in ingest_files_mapping results:  {'1': 'one', '2': 'two'}
    """
    methodName = pkgName + '-getSuffix' 
    ## Same error check for all 
    try:
        suffix = suffixChoices[key] 
    except:
        msg  = "Could NOT find key " + key + " in ingest_files_mapping results:"
        msg += "  " + str(suffixChoices)
        raise RuntimeError, msg

    return suffix


##------------------------------------------------------------------------------
## get_lc_ASNmembers 
##------------------------------------------------------------------------------
def get_lc_ASNmembers( asnRootname ):
    """
##------------------------------------------------------------------------------
##
## Method: get_lc_ASNmembers 
##    Generate a list of lower-cased member rootnames 
##        NOT including products or anything missing
##
## Input:
##     asnRootname -- rootname for the association 
##
## Return:
##     members -- a list of present, non-PROD member rootnames in lower case
##
## Exceptions:
##    RuntimeError if list of files does not match expected sets
##
## History:
## yy/mm/dd PR    Who        Description
## 09/08/10 63318 Sherbert   continue clean up of sys.exit()
##
##------------------------------------------------------------------------------
#   This doctest is commented out because it contains hard-coded file locations.
#   This doctest will fail if message reporting is turned up.

#   >>> get_lc_ASNmembers("/var/tmp/n62b7w010")
#   ['n62b7wlmx', 'n62b7wlpx']
    >>> get_lc_ASNmembers("change11/dataLink/n62b7w010")
    Traceback (most recent call last):
    ...
    RuntimeError: Problem generating list of ASN members
    """

    methodName = pkgName + '-get_lc_ASNmembers' 
    members = []
    
    ## assoc_member table may not be filled yet, and 
    ## asn_members table would not give me a last char, so use ASN file
    ## Make sure there is a file with member information
    asnFile = asnRootname + "_asn.fits" 
    ## get_asn_members returns the capitalized rootnames
    MEMBERS = get_asn_members(asnFile)
    msg = "MEMBERS are: " + str(MEMBERS)
    opusutil.PrintMsg("D", msg)

    ## if get_asn_members returns an empty list, that is an error
    if MEMBERS == 1 or len(MEMBERS) <= 0:
        msg = "Problem generating list of ASN members"
        raise RuntimeError, msg

    ## Lower case the get_asn_members return
    members = lc_list_mems(MEMBERS)

    return members


##------------------------------------------------------------------------------
## is_asn 
##------------------------------------------------------------------------------
def is_asn( rootname ):
    """
##------------------------------------------------------------------------------
##
## Method: is_asn 
##    Determine if provided rootname is an ASN (ends in 0) or not
##
## Input:
##     rootname -- rootname for the observation
##
## Return:
##     true (is an ASN) or false (rootname does NOT end in 0)
##
##------------------------------------------------------------------------------
    
    >>> is_asn("l9v246c0s")
    0
    >>> is_asn("n62b7w010")
    1
    >>> is_asn("n62b7w03")
    Traceback (most recent call last):
    ...
    ValueError: input not correct length
    """

    if len(rootname) != 9:
        raise ValueError, 'input not correct length'

    if rootname[8] == "0":
        ## We know we have an ASN
        return true
    else:
        ## rootname does NOT end in 0
        return false

    return




##------------------------------------------------------------------------------
## get_pppssoo 
##------------------------------------------------------------------------------
def get_pppssoo( rootname ):
    """
##------------------------------------------------------------------------------
##
## Method: get_pppssoo 
##    Break down provided rootname into ppp ss and oo parts
##    giving a 3-char oo when input is some type of product
##
## Input:
##     rootname -- rootname for the observation
##
## Return:
##     an array [ppp, ss, oo]
##
## Exceptions:
##     ValueError -- if input is NOT exactly 9-chars in length
##
##------------------------------------------------------------------------------
    
    >>> get_pppssoo('l9v246c0s')
    ['9v2', '46', 'c0']
    >>> get_pppssoo('l9v214020')
    ['9v2', '14', '020']
    >>> get_pppssoo('l9V21402C')
    ['9V2', '14', '02C']
    >>> get_pppssoo('n62b7w03')
    Traceback (most recent call last):
    ...
    ValueError: input not correct length
    """

    import re

    if len(rootname) != 9:
        raise ValueError, 'input not correct length'

    lastchar = rootname[8]
    prodChar = re.compile(r'[0-9a-i]',re.IGNORECASE)

    ppp = rootname[1:4]
    ss  = rootname[4:6]
    if prodChar.match(lastchar): 
        ## Product, return 3 chars
        oo  = rootname[6:9]
    else:
        ## Not a product, return only 2 chars
        oo  = rootname[6:8]

    return [ppp, ss, oo]


##------------------------------------------------------------------------------
## lc_list_mems
##------------------------------------------------------------------------------
def lc_list_mems(inList):
    """
##------------------------------------------------------------------------------
##
## Method: lc_list_mems
##
## Purpose: 
##    To return an array with all members lower-cased
##
## Inputs:
##    - inList -- an array, preferrably of upper-cased strings
##                but should work even if members are integers
## Returns:
##    - lcList -- input array with all members lower-cased
##
##------------------------------------------------------------------------------

    >>> lc_list_mems(['L9V220E9S','DADDY','HELPmE'])
    ['l9v220e9s', 'daddy', 'helpme']
    >>> lc_list_mems([1234])
    [1234]
    """

    lcList = []

    ## Upper case the array members
    for member in inList:
        ## Make sure we only attempt to LC strings
        if isinstance(member,str):
           member  = member.lower()

        lcList.append(member)

    return lcList

##------------------------------------------------------------------------------
## uc_list_mems
##------------------------------------------------------------------------------
def uc_list_mems(inList):
    """
##------------------------------------------------------------------------------
##
## Method: uc_list_mems
##
## Purpose: 
##    To return an array with all members upper-cased
##
## Inputs:
##    - inList -- an array, preferrably of lower-cased strings
##                but should work even if members are integers
## Returns:
##    - ucList -- input array with all members upper-cased
##
##------------------------------------------------------------------------------

    >>> uc_list_mems(['l9v220e9s','daddy','helpMe'])
    ['L9V220E9S', 'DADDY', 'HELPME']
    >>> uc_list_mems([1234])
    [1234]
    """

    ucList = []

    ## Upper case the array members
    for member in inList:
        ## Make sure we only attempt to UC strings
        if isinstance(member,str):
           member  = member.upper()

        ucList.append(member)

    return ucList


##------------------------------------------------------------------------------
## subproduct_files
##------------------------------------------------------------------------------
def subproduct_files( fileArray ):
    ## Can really doctest this because it does NOT require files on disk
    """
##------------------------------------------------------------------------------
##
## Method: subproduct_files
##
## Purpose:
##    Return a list of subproduct files similar to input pathname.
##    An ASN rootname ends in 0, a subproduct ends in [1-9a-i]
##
## Input: 
##    an array of filenames, including path if you want
##    
## Returns:
##    subproductFiles -- an array of path/filenames of subproducts
## 
##------------------------------------------------------------------------------

    >>> inArray = ['change11/dataLink/ACS/l9v246c0s_corrtag_a.fits']
    >>> subproduct_files(inArray)
    []

    >>> inArray = ['Data/NIC/n62b7w030_asn.fits', 'Data/NIC/n62b7w030_saa.fits', 'Data/NIC/n62b7w031_fake.fits']
    >>> subproduct_files(inArray)
    ['Data/NIC/n62b7w031_fake.fits']

    >>> inArray = ['j8c103060.tra', 'j8c103060_asn.fits', 'j8c103061.tra', 'j8c103061_crj.fits', 'j8c103061_drz.fits', 'j8c103061_spt.fits', 'j8c103061_trl.fits']
    >>> subproduct_files(inArray)
    ['j8c103061.tra', 'j8c103061_crj.fits', 'j8c103061_drz.fits', 'j8c103061_spt.fits', 'j8c103061_trl.fits']
    """

    import re

    subproductFiles = []

    ## Determine the string to be like input filename
    for pathname in fileArray:
#       print "pathname is", pathname
        (dir, file) = os.path.split(pathname)
        root  = os.path.splitext(file)[0][0:9]
#       print "root is", root

        ## Sub-product rootnames end in [1-9a-i]
        subprodChar = re.compile(r'[1-9a-i]',re.IGNORECASE)
        lastchar = root[8]
        if subprodChar.match(lastchar): 
            subproductFiles.append(pathname) 
        
    return subproductFiles



##------------------------------------------------------------------------------
## uniqRoots
##------------------------------------------------------------------------------
def uniqRoots ( listOfFiles ):
    """
##------------------------------------------------------------------------------
##
## Method: uniqRoots
## 
## Purpose:  
##      generate a list of uniq ipppssoots from a list of 
##      HST-patterned FITS file names: ipppssoot_suf.fits.  
##      Any path parts are ignored.  Only file roots are returned.
##      If the input is anything else, the first 9-chars of 
##      the input are returned. (GIGO)
##
## Input:
##     a list of file names
##
## Return:
##     a list of uniq ipppssoots, i.e. the first 9-chars of filename,
##
##------------------------------------------------------------------------------

    >>> files = ['n3uy01080_asc.fits', 'n3uy01080_asn.fits', 'n3uy01080_mos.fits', 'n3uy01080_spt.fits', 'n3uy01080_trl.fits', 'n3uy01081_mos.fits', 'n3uy01081_spt.fits', 'n3uy01081_trl.fits']
    >>> uniqRoots( files )
    ['n3uy01080', 'n3uy01081']
    >>> files = ['n3uy01080.tra', 'couldBe_anything.laDeDa']
    >>> uniqRoots( files )
    ['n3uy01080', 'couldBe_a']
    >>> files = ['short.nm', 'squat', 'more_correct.length'] 
    >>> uniqRoots( files )
    ['more_corr']
    >>> files = ['these', 'inputs', 'are', 'all', 'too', 'short'] 
    >>> uniqRoots( files )
    Traceback (most recent call last):
    ...
    ValueError: Not a 9-char ipppssoot
    """
    ipppssoots = []
    for file in listOfFiles:
        ## Only interested in the file name, not the path
        thisRoot = os.path.split(file)[1][0:9]
        ## Minimal error checking
        if len(thisRoot) < 9:
            continue
        ## Create uniq list
        if thisRoot not in ipppssoots:
            ipppssoots.append(thisRoot)
    
    ## Minimal error checking
    if 0 == len(ipppssoots):
            raise ValueError, "Not a 9-char ipppssoot"

    ## return the uniq list
    return ipppssoots


##------------------------------------------------------------------------------
##
## Method: find_mos_saa
##
## Description: 
##     Generate a list of mos, saa files for rootname in current dir.
##     Written initially for NIC, but should work for any other instrument 
##     data where files contain "mos" or "saa" as their suffix.
##
## Inputs:
##    rootname
##
## Returns: 
##    file_list
##         - a list of files in current dir whose names contain "mos" or "saa"
##    
## History:
## mm/dd/yy PR     Who        What
## -------- ------ ---------- --------------------------------------------------
## 01/20/09 61586  Sherbert   Input for update_coord_keywords
## 
##------------------------------------------------------------------------------
def find_mos_saa( rootname ):
    file_list = []
    suffixes = ['mos', 'saa']
    for suffix in suffixes:
        curFile = rootname + "_" + suffix + ".fits"
        if os.path.exists(curFile):
            file_list.append(curFile)
    return file_list 




##==============================================================================
## Unittests
##==============================================================================
if __name__ == '__main__':
    import doctest
    doctest.testmod()
