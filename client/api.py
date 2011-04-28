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

def get_mapping_data(context, mapping):
    """Returns the contents of the specified pmap, imap, or rmap file
    as a string.
    """
    S = ServiceProxy(URL)
    data = S.get_mapping_data(context, mapping)
    return data["result"]
    
def get_mapping_names(context="hst.pmap"):
    """Get the complete set of pmap, imap, and rmap basenames required
    for the specified context.   context can be an observatory, pipeline,
    or instrument context.
    """
    S = ServiceProxy(URL)
    resp = S.get_mapping_names(context)
    return resp["result"]

def get_reference_data(context, reference):
    """Returns the contents of the specified reference file as a string.
    """
    S = ServiceProxy(URL)
    data = S.get_reference_data(context, reference)
    if data["error"]:
        raise RuntimeError("Service failure: " + repr(data["error"]))
    return base64.b64decode(data["result"])
    
def get_reference_names(context="hst.pmap"):
    """Get the complete set of reference file basenames required
    for the specified context.
    """
    S = ServiceProxy(URL)
    resp = S.get_reference_names(context)
    return resp["result"]

def get_best_refs(header, context="hst.pmap"):
    """Return the dictionary mapping { filetype : reference_basename ... }
    corresponding to the given `header`
    """
    header = dict(header)
    S = ServiceProxy(URL)
    references = S.get_best_refs(observatory, header)["result"]
    return references

# ==============================================================================

def retrieve_mappings(context, mapping_names, ignore_cache=False):
    observatory = rmap.context_to_observatory(context)
    locator = rmap.get_object("crds." + observatory + ".locate.locate_mapping")
    for name in mapping_names:
        localpath = locator(name)
        if (not os.path.exists(localpath)) or ignore_cache:
            log.verbose("Cache miss. Fetching ", repr(name), "to", repr(localpath))
            mapping_contents = get_mapping_data(context, name)
            utils.ensure_dir_exists(localpath)
            open(localpath,"w+").write(mapping_contents)
        else:
            log.verbose("Cache hit ", repr(name), "at", repr(localpath))
            
def retrieve_references(context, reference_names, ignore_cache=False):
    observatory = rmap.context_to_observatory(context)
    if isinstance(reference_names, dict):
        reference_names = reference_names.values()
    locator = rmap.get_object("crds." + observatory + ".locate.locate_reference")
    for name in reference_names:
        localpath = locator(name)
        if (not os.path.exists(localpath)) or ignore_cache:
            log.verbose("Cache miss. Fetching ", repr(name), "to", repr(localpath))
            reference_contents = get_reference_data(context, name)
            utils.ensure_dir_exists(localpath)
            open(localpath,"w+").write(reference_contents)
        else:
            log.verbose("Cache hit ", repr(name), "at", repr(localpath))
