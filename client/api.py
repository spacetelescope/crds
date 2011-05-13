"""This module defines the API for CRDS clients.   Functions defined 
here make remote service calls to the CRDS server to obtain mapping
or reference files and cache them locally.
"""
import sys
import os
import os.path
import base64
import re
import urllib2

import crds.log as log
import crds.utils as utils

from crds.client.proxy import CheckingProxy

# ==============================================================================

URL_SUFFIX = "/json/"
URL = os.environ.get("CRDS_URL", 'http://localhost:8000')

# ==============================================================================
def set_crds_server(url):
    if not re.match("http://(\w+\.?)*\w(:\d+)?", url):
        raise ValueError("Invalid URL " + repr(url))
    global URL, S
    URL = url + URL_SUFFIX
    S = CheckingProxy(URL, version="1.0")

    
def get_crds_server():
    return URL[:-len(URL_SUFFIX)]

set_crds_server(URL)

# ==============================================================================

def get_mapping_url(pipeline_context, mapping):
    """Returns a URL for the specified pmap, imap, or rmap file.
    """
    return S.get_mapping_url(pipeline_context, mapping)
    
def get_mapping_data(pipeline_context, mapping):
    """Returns the contents of the specified pmap, imap, or rmap file
    as a string.
    """
    return S.get_mapping_data(pipeline_context, mapping)
    
def get_mapping_names(pipeline_context):
    """Get the complete set of pmap, imap, and rmap basenames required
    for the specified pipeline_context.   context can be an observatory, pipeline,
    or instrument context.
    """
    return S.get_mapping_names(pipeline_context)

def get_reference_url(pipeline_context, reference):
    """Returns a URL for the specified reference file.
    """
    return S.get_reference_url(pipeline_context, reference)
    
def get_reference_data(pipeline_context, reference):
    """Returns the contents of the specified reference file as a string.
    """
    return S.get_reference_data(pipeline_context, reference)
    
def get_reference_names(pipeline_context):
    """Get the complete set of reference file basenames required
    for the specified pipeline_context.
    """
    return S.get_reference_names(pipeline_context)

def get_best_refs(pipeline_context, header):
    """Return the dictionary mapping { filetype : reference_basename ... }
    corresponding to the given `header`
    """
    return S.get_best_refs(pipeline_context, dict(header))

# ==============================================================================

class FileCacher(object):
    """FileCacher is an abstract base class which gets remote files
    with simple names into a local cache.
    """
    def _transfer_to_local_file_rpc(self, pipeline_context, name, localpath):   
        utils.ensure_dir_exists(localpath)
        contents = self._get_data(pipeline_context, name)
        open(localpath,"w+").write(contents)

    def _transfer_to_local_file_http(self, pipeline_context, name, localpath):   
        utils.ensure_dir_exists(localpath)
        url = self._get_url(pipeline_context, name)
        contents = urllib2.urlopen(url).read()
        open(localpath,"w+").write(contents)

    def get_local_files(self, pipeline_context, names, ignore_cache=False):
        """Given a list of basename `mapping_names` which are pertinent to the given
        `pipeline_context`,   cache the mappings locally where they can be used
        by CRDS.
        """
        if isinstance(names, dict):
            names = names.values()
        localpaths = {}
        for i, name in enumerate(names):
            localpath = self._locate(pipeline_context, name)
            if (not os.path.exists(localpath)) or ignore_cache:
                log.verbose("Cache miss. Fetching[%d]" % i, repr(name), "to", repr(localpath))
                self._transfer_to_local_file_rpc(pipeline_context, name, localpath)
            else:
                log.verbose("Cache hit[%d]" % i, repr(name), "at", repr(localpath))
            localpaths[name] = localpath
        return localpaths

    def _locate(self, pipeline_context, name):
        return utils.get_object("crds." + utils.context_to_observatory(pipeline_context) + ".locate." + self._locator)(name)
    
# ==============================================================================

class MappingCacher(FileCacher):
    _get_data = staticmethod(get_mapping_data)
    _get_url = staticmethod(get_mapping_url)
    _locator = "locate_mapping"
    
MAPPING_CACHER = MappingCacher()

# ==============================================================================

class ReferenceCacher(FileCacher):
    _get_data = staticmethod(get_reference_data)
    _get_url = staticmethod(get_reference_url)
    _locator = "locate_reference"

REFERENCE_CACHER = ReferenceCacher()

# ==============================================================================

def cache_mappings(pipeline_context, ignore_cache=False):
    """Given a `pipeline_context`, determine the closure of CRDS mappings and cache them
    on the local file system.
    
    Returns:   { mapping_basename :   mapping_local_filepath ... }   
    """
    assert isinstance(ignore_cache, bool)
    mappings = get_mapping_names(pipeline_context)
    return MAPPING_CACHER.get_local_files(pipeline_context, mappings, ignore_cache=ignore_cache)
    
def dump_references(pipeline_context, baserefs, ignore_cache=False):
    """Given a pipeline `pipeline_context` and list of `baserefs` basenames,  obtain the
    set of reference files and cache them on the local file system.   
    
    Returns:   { ref_basename :   reference_local_filepath ... }   
    """
    return REFERENCE_CACHER.get_local_files(pipeline_context, baserefs, ignore_cache=ignore_cache)

def cache_references(pipeline_context, bestrefs, ignore_cache=False):
    """Given a pipeline `pipeline_context` and `bestrefs` mapping,  obtain the
    set of reference files and cache them on the local file system.   
    
    Returns:   { reference_keyword :   reference_local_filepath ... }   
    """
    for filetype, refname in bestrefs.items():
        if "NOT FOUND" in refname:
            log.verbose("Reference type", repr(filetype),"NOT FOUND.  Ignoring.")
            del bestrefs[filetype]
    localrefs = REFERENCE_CACHER.get_local_files(pipeline_context, bestrefs, ignore_cache=ignore_cache)
    refs = {}
    for filetype, refname in bestrefs.items():
        refs[filetype] = localrefs[refname]
    return refs
