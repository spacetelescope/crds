import sys
import os
import StringIO
import os.path
import base64

import crds.rmap as rmap
import crds.log as log
import crds.utils as utils

# ==============================================================================

sys.stdout = StringIO.StringIO()
from jsonrpc.proxy import ServiceProxy
sys.stdout = sys.__stdout__

# ==============================================================================

URL_SUFFIX = "/json/"
URL = os.environ.get("CRDS_URL", 'http://localhost:8000') + URL_SUFFIX

# ==============================================================================
def set_crds_server(url):
    if not re.match("http://(\w+\.?)*\w(:\d+)?/", url):
        raise ValueError("Invalid URL " + repr(url))
    global URL
    URL = url + URL_SUFFIX
    
def get_crds_server():
    return URL[:-len(URL_SUFFIX)]

# ==============================================================================

class CheckingProxy(ServiceProxy):
    def __call__(self, *args, **keys):
        jsonrpc = ServiceProxy.__call__(*args, **keys)
        if jsonrpc["error"] is not None:
            raise ServiceError(jsonrpc["error"])
        return jsonrpc["result"]

S = CheckingProxy(URL)

# ==============================================================================

def get_mapping_data(context, mapping):
    """Returns the contents of the specified pmap, imap, or rmap file
    as a string.
    """
    return S.get_mapping_data(context, mapping)
    
def get_mapping_names(context="hst.pmap"):
    """Get the complete set of pmap, imap, and rmap basenames required
    for the specified context.   context can be an observatory, pipeline,
    or instrument context.
    """
    return S.get_mapping_names(context)

def get_reference_data(context, reference):
    """Returns the contents of the specified reference file as a string.
    """
    return S.get_reference_data(context, reference)
    
def get_reference_names(context="hst.pmap"):
    """Get the complete set of reference file basenames required
    for the specified context.
    """
    return S.get_reference_names(context)

def get_best_refs(header, context="hst.pmap"):
    """Return the dictionary mapping { filetype : reference_basename ... }
    corresponding to the given `header`
    """
    return S.get_best_refs(observatory, dict(header))

# ==============================================================================

class FileCacher(object):
    def _transfer_to_local_file(name,  localpath):   
        utils.ensure_dir_exists(localpath)
        contents = self._get_data(context, name)
        open(localpath,"w+").write(mapping_contents)

    def get_local_files(self, context, names, ignore_cache=False):
        """Given a list of basename `mapping_names` which are pertinent to the given
        pipeline `context`,   cache the mappings locally where they can be used
        by CRDS.
        """
        if isinstance(names, dict):
            names = names.values()
        locator = self._get_locator(rmap.context_to_observatory(context))
        localpaths = {}
        for name in names:
            localpath = locator(name)
            if (not os.path.exists(localpath)) or ignore_cache:
                log.verbose("Cache miss. Fetching ", repr(name), "to", repr(localpath))
                self._transfer_to_local_file(name, localpath)
            else:
                log.verbose("Cache hit ", repr(name), "at", repr(localpath))
        localpaths[name] = localpath
        return localpaths

# ==============================================================================

class MappingCacher(FileCacher):
    def _get_data(self, context, name):
        return get_mapping_data(context, name)
    
    def _get_locator(self, observatory):
        return rmap.get_object("crds." + observatory + ".locate.locate_mapping")

MAPPING_CACHER = MappingCacher()

# ==============================================================================

class ReferenceCacher(FileCacher):
    def _get_data(self, context, name):
        return get_reference_data(context, name)
    
    def _get_locator(self, observatory):
        return rmap.get_object("crds." + observatory + ".locate.locate_reference")

REFERENCE_CACHER = ReferenceCacher()

# ==============================================================================

def cache_mappings(context, ignore_cache=False):
    """Given a pipeline `context`, determine the closure of CRDS mappings and cache them
    on the local file system.
    
    Returns:   { mapping_basename :   mapping_local_filepath ... }   
    """
    mappings = get_mapping_names(context)
    return MAPPING_CACHER.get_local_files(context, mappings, ignore_cache=ignore_cache)
    
def cache_references(context, header, ignore_cache=False):
    """Given a pipeline `context` and dataset `header` union, determine the appropriate
    set of reference files and cache them on the local file system.   
    
    Returns:   { reference_keyword :   reference_local_filepath ... }   
    """
    bestrefs = get_best_refs(context, header)
    return REFRENCE_CACHER.get_local_files(context, bestrefs, ignore_cache=ignore_cache)
    
