import sys
import os
import StringIO
import os.path

import crds.rmap as rmap
import crds.log as log

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

def get_mapping_data(mapping):
    """Returns the contents of the specified pmap, imap, or rmap file
    as a string.
    """
    S = ServiceProxy(URL)
    data = S.get_mapping_data(mapping)
    return data["result"]
    
def get_mapping_names(context="hst"):
    """Get the complete set of pmap, imap, and rmap basenames required
    for the specified context.   context can be an observatory, pipeline,
    or instrument context.
    """
    S = ServiceProxy(URL)
    resp = S.get_mapping_names(context)
    return resp["result"]

def get_reference_data(mapping):
    """Returns the contents of the specified reference file as a string.
    """
    S = ServiceProxy(URL)
    data = S.get_reference_data(mapping)
    return data["result"]
    
def get_reference_names(context="hst"):
    """Get the complete set of reference file basenames required
    for the specified context.
    """
    S = ServiceProxy(URL)
    resp = S.get_reference_names(context)
    return resp["result"]

def get_best_refs(header, observatory="hst"):
    """Return the dictionary mapping { filetype : reference_basename ... }
    corresponding to the given `header`
    """
    header = dict(header)
    S = ServiceProxy(URL)
    references = S.get_best_refs(observatory, header)["result"]
    return references

# ==============================================================================

def retrieve_mappings(observatory, mapping_names):
    locator = rmap.get_object("crds." + observatory + ".locate.locate_mapping")
    for name in mapping_names:
        localpath = locator(name)
        if not os.path.exists(localpath):
            log.verbose("Cache miss. Fetching ", repr(name), "to", repr(localpath))
            # mapping_contents = get_mapping_data(name)
            # open(localpath,"w+").write(mapping_contents)
        else:
            log.verbose("Cache hit ", repr(name), "at", repr(localpath))
            
def retrieve_references(observatory, reference_names):
    if isinstance(reference_names, dict):
        reference_names = reference_names.values()
    locator = rmap.get_object("crds." + observatory + ".locate.locate_reference")
    for name in reference_names:
        localpath = locator(name)
        if not os.path.exists(localpath):
            log.verbose("Cache miss. Fetching ", repr(name), "to", repr(localpath))
            # mapping_contents = get_mapping_data(name)
            # open(localpath,"w+").write(mapping_contents)
        else:
            log.verbose("Cache hit ", repr(name), "at", repr(localpath))
