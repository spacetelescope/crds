import sys
import os
import StringIO

sys.stdout = StringIO.StringIO()
from jsonrpc.proxy import ServiceProxy
sys.stdout = sys.__stdout__

URL_SUFFIX = "/json/"
URL = os.environ.get("CRDS_URL", 'http://localhost:8000') + URL_SUFFIX

def set_crds_server(url):
    if not re.match("http://(\w+\.?)*\w(:\d+)?/", url):
        raise ValueError("Invalid URL " + repr(url))
    global URL
    URL = url + URL_SUFFIX
    
def get_crds_server():
    return URL[:-len(URL_SUFFIX)]

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
    header = dict(header)
    S = ServiceProxy(URL)
    references = S.get_best_refs(observatory, header)["result"]
    return references

