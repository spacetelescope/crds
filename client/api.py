"""This module defines the API for CRDS clients.   Functions defined here make
remote service calls to the CRDS server to obtain mapping or reference files and
cache them locally.
"""
import os
import os.path
import base64
import re
import urllib2

from .proxy import CheckingProxy, ServiceError, CrdsError

# heavy versions of core CRDS modules defined in one place, client minimally
# dependent on core for configuration, logging, and  file path management.
from crds import utils, log, config

# ==============================================================================

class CrdsNetworkError(CrdsError):
    """First network service call failed, nominally connection refused."""
    
class CrdsLookupError(CrdsError):
    """Filekind NOT FOUND but applicable according to current parameters."""
    
class CrdsDownloadError(CrdsError):
    """Error downloading data for a reference or mapping file."""

def download_exc(pipeline_context, name, exc):    
    """Generate a standard exception message for download exceptions."""
    return CrdsDownloadError("Error fetching data for " + srepr(name) + 
                            " from context " + srepr(pipeline_context) + 
                            " at server " + srepr(get_crds_server()) +
                            " : " + str(exc))

# ==============================================================================

__all__ = [
           "get_default_context",
           "get_server_info",
           "cache_references",
           
           "set_crds_server", 
           "get_crds_server",
         
           "list_mappings",
           "get_mapping_names",
           "get_mapping_url", 

           "get_reference_names",
           "get_reference_url",
           
           "dump_references",
           "dump_mappings",

           "get_best_references",
           "cache_best_references",
           
           "CrdsError",
           "CrdsLookupError",
           "CrdsNetworkError",
           "CrdsDownloadError",
           "ServiceError",
           
           # deprecated
           "cache_best_references_for_dataset",
           "get_minimum_header",           
           ]

# ============================================================================

# Server for CRDS services and mappings

URL_SUFFIX = "/json/"

JWST_TEST_SERVER = 'http://jwst-crds.stsci.edu'
HST_TEST_SERVER = 'http://hst-crds.stsci.edu'
URL = os.environ.get("CRDS_SERVER_URL", "http://not-a-crds-server.stsci.edu")

S = None    # Proxy server

def set_crds_server(url):
    """Configure the CRDS JSON services server to `url`,  
    e.g. 'http://localhost:8000'
    """
    if url.endswith("/"):
        url = url[:-1]
    global URL, S
    URL = url + URL_SUFFIX
    S = CheckingProxy(URL, version="1.0")

    
def get_crds_server():
    """Return the base URL for the CRDS JSON RPC server.
    """
    return URL[:-len(URL_SUFFIX)]

set_crds_server(URL)

def get_download_mode():
    """Return the mode used to download references and mappings,  either normal
    "http" file transfer or json "rpc" based.   In theory HTTP optimizes better 
    with direct support for static files from Apache,  but RPC is more flexible
    and works through firewalls.   The key distinction is that HTTP mode can
    work with a server which is not the same as the CRDS server (perhaps an
    archive server).   Once/if a public archive server is available with normal 
    URLs,  that wopuld be the preferred means to get references and mappings.
    """
    mode = os.environ.get("CRDS_DOWNLOAD_MODE", "rpc").lower()
    assert mode in ["http","rpc"], \
        "Invalid CRDS_DOWNLOAD_MODE setting.  Use 'http' (preferred) " + \
        "or 'rpc' (through firewall)."
    return mode

# =============================================================================
def srepr(o):
    """Return the repr() of the str() of `o`"""
    return repr(str(o))

def list_mappings(observatory=None, glob_pattern="*"):
    """Return the list of mappings associated with `observatory`
    which match `glob_pattern`.
    """
    return [str(x) for x in S.list_mappings(observatory, glob_pattern)]

def get_mapping_url(pipeline_context, mapping):
    """Returns a URL for the specified pmap, imap, or rmap file.
    """
    return S.get_mapping_url(pipeline_context, mapping)

def is_known_mapping(mapping):
    """Return True iff `mapping` is a known/official CRDS mapping file."""
    try:
        return len(get_mapping_url(mapping, mapping)) > 0
    except ServiceError:
        return False
    
def get_mapping_data(pipeline_context, mapping):
    """Returns the contents of the specified pmap, imap, or rmap file
    as a string.
    """
    try:
        return S.get_mapping_data(pipeline_context, mapping)
    except ServiceError, exc:
        raise download_exc(pipeline_context, mapping, exc)
        
def get_mapping_names(pipeline_context):
    """Get the complete set of pmap, imap, and rmap basenames required
    for the specified pipeline_context.   context can be an observatory, 
    pipeline, or instrument context.
    """
    return [str(x) for x in S.get_mapping_names(pipeline_context)]

def get_reference_url(pipeline_context, reference):
    """Returns a URL for the specified reference file.
    """
    return S.get_reference_url(pipeline_context, reference)
    
def get_reference_data(pipeline_context, reference):
    """Returns the contents of the specified reference file as a string.
    """
    try:
        data = S.get_reference_data(pipeline_context, reference)
    except ServiceError, exc:
        raise download_exc(pipeline_context, reference, exc)
    return base64.b64decode(data)

def get_reference_names(pipeline_context):
    """Get the complete set of reference file basenames required
    for the specified pipeline_context.
    """
    return [str(x) for x in S.get_reference_names(pipeline_context)]

def get_best_references(pipeline_context, header, reftypes=None):
    """Get best references for dict-like `header` relative to 
    `pipeline_context`.
    
    pipeline_context  CRDS context for lookup,   e.g.   'hst_0001.pmap'
    header            dict-like mapping { lookup_parameter : value }
    reftypes         If None,  return all reference types;  otherwise return 
                     best refs for the specified list of reftypes. 

    Returns          { reftype : reference_basename ... }
    
    Raises           CrdsLookupError,  typically for problems with header values
    """
    try:
        bestrefs = S.get_best_references(pipeline_context, dict(header), reftypes)
    except Exception, exc:
        raise CrdsLookupError(str(exc))
    # Due to limitations of jsonrpc,  exception handling is kludged in here.
    for filetype, refname in bestrefs.items():
        if "NOT FOUND" in refname:
            if "NOT FOUND n/a" == refname:
                log.verbose("Reference type", srepr(filetype), "not applicable.")
            else:
                raise CrdsLookupError("Error determining best reference for " + 
                                      srepr(filetype) + " = " + 
                                      str(refname)[len("NOT FOUND"):])
    return bestrefs

def get_default_context(observatory=None):
    """Return the name of the latest pipeline mapping in use for processing
    files for `observatory`.  
    """
    return str(S.get_default_context(observatory))

def get_server_info():
    """Return a dictionary of critical parameters about the server such as:
    
    operational_context  - the context in use in the operational pipeline

    edit_context         - the context which was last edited, not 
                           necessarily archived or operational yet.   

    crds*                - the CRDS package versions on the server.
    
    This is intended as a single flexible network call which can be used to
    initialize a higher level getreferences() call,  providing information on
    what context, software, and network mode should be used for processing.
    """
    try:
        info = S.get_server_info()
        info["server"] = get_crds_server()
        return info
    except ServiceError, exc:
        raise CrdsNetworkError("network connection failed: " + srepr(get_crds_server()))

# ==============================================================================

class FileCacher(object):
    """FileCacher is an abstract base class which gets remote files
    with simple names into a local cache.
    """
    def _rpc_get_data(self, pipeline_context, name):
        """Fetch the data for `name` via CRDS service and return it.
        """
        return self._get_data(pipeline_context, name)  # Get via jsonrpc

    def _http_get_data(self, pipeline_context, name):
        """Fetch the data for `name` as a URL and return it.
        """
        try:
            url = self._get_url(pipeline_context, name)
            log.verbose("Fetching URL ", repr(url))
            return urllib2.urlopen(url).read()
        except Exception, exc:
            raise download_exc(pipeline_context, name, exc)
        
    def _download(self, pipeline_context, name):
        if get_download_mode() == "http":
            return self._http_get_data(pipeline_context, name)
        else:
            return self._rpc_get_data(pipeline_context, name)
            
    def get_local_files(self, pipeline_context, names, ignore_cache=False):
        """Given a list of basename `mapping_names` which are pertinent to the 
        given `pipeline_context`,   cache the mappings locally where they can 
        be used by CRDS.
        """
        if isinstance(names, dict):
            names = names.values()
        localpaths = {}
        for i, name in enumerate(names):
            localpath = self._locate(pipeline_context, name)
            if (not os.path.exists(localpath)) or ignore_cache:
                log.verbose("Cache miss. Fetching[%d]" % i, repr(name), 
                            "to", repr(localpath))
                utils.ensure_dir_exists(localpath)
                contents = self._download(pipeline_context, name)
                open(localpath,"w+").write(contents)
            else:
                log.verbose("Cache hit.  Skipping[%d]" % i, repr(name), 
                            "at", repr(localpath))
            localpaths[name] = localpath
        return localpaths

    def _locate(self, pipeline_context, name):
        if "jwst" in pipeline_context:
            observatory = "jwst"
        elif "hst" in pipeline_context:
            observatory = "hst"
        else:
            import crds
            observatory = crds.get_cached_mapping(pipeline_context).observatory
        return config.locate_file(name, observatory=observatory)

# ==============================================================================

class MappingCacher(FileCacher):
    _get_data = staticmethod(get_mapping_data)
    _get_url = staticmethod(get_mapping_url)
    
MAPPING_CACHER = MappingCacher()

# ==============================================================================

class ReferenceCacher(FileCacher):
    _get_data = staticmethod(get_reference_data)
    _get_url = staticmethod(get_reference_url)

REFERENCE_CACHER = ReferenceCacher()

# ==============================================================================

def dump_mappings(pipeline_context, ignore_cache=False):
    """Given a `pipeline_context`, determine the closure of CRDS mappings and 
    cache them on the local file system.
    
    Returns:   { mapping_basename :   mapping_local_filepath ... }   
    """
    assert isinstance(ignore_cache, bool)
    mappings = get_mapping_names(pipeline_context)
    return MAPPING_CACHER.get_local_files(
        pipeline_context, mappings, ignore_cache=ignore_cache)
  
def dump_references(pipeline_context, baserefs=None, ignore_cache=False):
    """Given a pipeline `pipeline_context` and list of `baserefs` reference 
    file basenames,  obtain the set of reference files and cache them on the
    local file system.   
    
    Returns:   { ref_basename :   reference_local_filepath ... }
    """
    if baserefs is None:
        baserefs = get_reference_names(pipeline_context)
    baserefs = list(baserefs)
    for refname in baserefs:
        if "NOT FOUND" in refname:
            log.verbose("Skipping " + srepr(refname))
            baserefs.remove(refname)
    return REFERENCE_CACHER.get_local_files(
        pipeline_context, baserefs, ignore_cache=ignore_cache)
    
def cache_references(pipeline_context, bestrefs, ignore_cache=False):
    """Given a pipeline `pipeline_context` and `bestrefs` mapping,  obtain the
    set of reference files and cache them on the local file system.
    
    bestrefs    { reference_keyword :  reference_basename } 
    
    Returns:   { reference_keyword :  reference_local_filepath ... }   
    """
    bestrefs2 = dict(bestrefs)
    for filetype, refname in bestrefs2.items():
        if "NOT FOUND" in refname:
            if "n/a" in refname.lower():
                log.verbose("Reference type", repr(filetype), 
                            "NOT FOUND.  Ignoring.")
                del bestrefs2[filetype]
            else:
                raise CrdsLookupError("Error determining best reference for " + 
                                      repr(str(filetype)) + " = " + 
                                      str(refname)[len("NOT FOUND"):])
    localrefs = REFERENCE_CACHER.get_local_files(
        pipeline_context, bestrefs2, ignore_cache=ignore_cache)
    refs = {}
    for filetype, refname in bestrefs.items():
        if "NOT FOUND" in refname:
            refs[str(filetype)] = str(refname)
        else:
            refs[str(filetype)] = str(localrefs[refname])
    return refs

def cache_best_references(pipeline_context, header, ignore_cache=False, reftypes=None):
    """Given the FITS `header` of a dataset and a `pipeline_context`, determine
    the best set of reference files for processing the dataset,  cache them 
    locally,  and return the mapping  { filekind : local_file_path }.
    """
    best_refs = get_best_references(pipeline_context, header, reftypes=reftypes)
    local_paths = cache_references(pipeline_context, best_refs, ignore_cache)
    return local_paths

# =====================================================================================================

# These functions are deprecated and only work when the full CRDS library is installed,  and only for 
# some data file formats (.fits).

def cache_best_references_for_dataset(pipeline_context, dataset, 
                                      ignore_cache=False):
    """
    determine the best set of reference files,  cache the references
    locally,  and return the mapping  { filekind : local_file_path }.
    """
    header = get_minimum_header(pipeline_context, dataset, ignore_cache)
    return cache_best_references(pipeline_context, header, ignore_cache)

def get_minimum_header(context, dataset, ignore_cache=False):
    """Given a `dataset` and a `context`,  extract relevant header 
    information from the `dataset`.
    """
    import crds.rmap
    dump_mappings(context, ignore_cache)
    ctx = crds.get_cached_mapping(context)
    return ctx.get_minimum_header(dataset)

