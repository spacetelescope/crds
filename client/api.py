"""This module defines the API for CRDS clients.   Functions defined here make
remote service calls to the CRDS server to obtain mapping or reference files and
cache them locally.
"""
import os
import os.path
import base64
import re
import urllib2
import traceback
import tarfile

from .proxy import CheckingProxy, ServiceError, CrdsError

# heavy versions of core CRDS modules defined in one place, client minimally
# dependent on core for configuration, logging, and  file path management.
import crds
from crds import utils, log, config

# ==============================================================================

class CrdsNetworkError(CrdsError):
    """First network service call failed, nominally connection refused."""
    
class CrdsLookupError(CrdsError):
    """Filekind NOT FOUND but applicable according to current parameters."""
    
class CrdsDownloadError(CrdsError):
    """Error downloading data for a reference or mapping file."""

__all__ = [
           "get_default_context",
           "get_server_info",
           "cache_references",
           
           "set_crds_server", 
           "get_crds_server",
         
           "list_mappings",
           "get_file_chunk",
           "get_url",
           "get_file_info",
           
           "get_mapping_names",
           "get_reference_names",
           
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

CRDS_DATA_CHUNK_SIZE = 2**23   # 8M, HTTP, sha1sum,  but maybe not RPC.

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
    mode = os.environ.get("CRDS_DOWNLOAD_MODE", "http").lower()
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
    
def get_file_chunk(pipeline_context, file, chunk):
    """Return the ith `chunk` of data from `file` as well as the
    total number of chunks.   It is assumed that every file has
    at least one chunk.
    
    Returns (chunks, size, sha1sum, chunk_str)
    where chunks, size, and sha1sum are invariant totals.
    
    Note that `chunks` is determined by the server since it's a loading issue.
    """
    chunks, data = S.get_file_chunk(pipeline_context, file, chunk)
    return chunks, base64.b64decode(data)

def get_url(pipeline_context, filename):
    """Return the URL for a CRDS reference or mapping file."""
    return S.get_url(pipeline_context, filename)

def get_file_info(pipeline_context, filename):
    """Return a dictionary of CRDS information about `filename`."""
    return S.get_file_info(pipeline_context, filename)

def get_file_info_map(observatory, files=None, fields=None):
    """Return the info { filename : { info } } on `files` of `observatory`.
    `fields` can be used to limit info returned to specified keys.
    """
    infos = S.get_info_map(observatory, files, fields)
    return infos

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

'''
def get_best_references_by_header_map(pipeline_context, header_map, reftypes=None):
    """Get best references for each dataset in a map of ids to headers,  `header_map`,  
    relative to `pipeline_context`.
    
    pipeline_context  CRDS context for lookup,   e.g.   'hst_0001.pmap'
    header_map       { name: { lookup_parameter : value } } dictionary of named headers
    reftypes         If None,  return all reference types;  otherwise return 
                     best refs for the specified list of reftypes. 

    Returns          { name : { reftype : reference_basename ... } }
    
    Raises           CrdsLookupError,  typically for problems with header values
    """
    try:
        bestrefs = S.get_best_references_by_header_map(pipeline_context, dict(header_map), reftypes)
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

def get_best_references_by_ids(pipeline_context, datasets, reftypes=None):
    """Get best references for list of `datasets` ids relative to `pipeline_context`.
    
    pipeline_context  CRDS context for lookup,   e.g.   'hst_0001.pmap'
    datasets         [ dataset_id, ... ]   e.g. ["I9ZF01010", "I9MF01012"]
    reftypes         If None,  return all reference types;  otherwise return 
                     best refs for the specified list of reftypes. 

    Returns          { id: { reftype : reference_basename ... } }
    
    Raises           CrdsLookupError,  typically for problems with header values
    """
    try:
        bestrefs = S.get_best_references_by_ids(pipeline_context, datasets, reftypes)
    except Exception, exc:
        raise CrdsLookupError(str(exc))
    return bestrefs
'''

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

def get_dataset_headers_by_id(context, dataset_ids):
    """Return { dataset_id : { header } } for `dataset_ids`."""
    return S.get_dataset_headers_by_id(context, dataset_ids)

def get_dataset_headers_by_instrument(context, instrument):
    """Return { dataset_id : { header } } for `instrument`."""
    return S.get_dataset_headers_by_instrument(context, instrument)

def get_dataset_ids(context, instrument):
    """Return [ dataset_id, ...] for `instrument`."""
    return S.get_dataset_ids(context, instrument)

# ==============================================================================

HARD_DEFAULT_OBS = "jwst"

def get_server_observatory():
    """Return the default observatory according to the server, or None."""
    try:
        pmap = get_default_context()
    except Exception:
        server_obs = None
    else:
        server_obs = observatory_from_string(pmap)
    return server_obs

def get_default_observatory():
    """Based on the environment, cache, and server,  determine the default observatory.
    
    1. CRDS_OBSERVATORY env var
    2. CRDS_SERVER_URL env var
    3. Observatory(Server default context)
    4. jwst
    """
    return os.environ.get("CRDS_OBSERVATORY", None) or \
           observatory_from_string(get_crds_server()) or \
           get_server_observatory() or \
           "jwst"

def observatory_from_string(string):
    """If "jwst" or "hst" is in `string`, return it,  otherwise return None."""
    if "jwst" in string:
        return "jwst"
    elif "hst" in string:
        return "hst"
    else:
        return None

# ==============================================================================

class FileCacher(object):
    """FileCacher gets remote files with simple names into a local cache.
    """
    def get_local_files(self, pipeline_context, names, ignore_cache=False, raise_exceptions=True):
        """Given a list of basename `mapping_names` which are pertinent to the 
        given `pipeline_context`,   cache the mappings locally where they can 
        be used by CRDS.
        """
        if isinstance(names, dict):
            names = names.values()
        localpaths = {}
        downloads = []
        for i, name in enumerate(names):
            localpath = self.locate(pipeline_context, name)
            if (not os.path.exists(localpath)) or ignore_cache:
                downloads.append(name)
            localpaths[name] = localpath
        if downloads:
            self.download_files(pipeline_context, downloads, localpaths, raise_exceptions)
        else:
            log.verbose("Skipping download for cached files", names, verbosity=10)
        return localpaths

    def locate(self, pipeline_context, name):
        if "jwst" in pipeline_context:
            observatory = "jwst"
        elif "hst" in pipeline_context:
            observatory = "hst"
        else:
            import crds
            observatory = crds.get_cached_mapping(pipeline_context).observatory
        return config.locate_file(name, observatory=observatory)

    def download_files(self, pipeline_context, downloads, localpaths, raise_exceptions=True):
        """Serial file-by-file download."""
        for name in downloads:
            try:
                self.download(pipeline_context, name, localpaths[name])
            except Exception, exc:
                if raise_exceptions:
                    raise
                else:
                    log.error("Failure downloading file", repr(name), ":", str(exc))

    def download(self, pipeline_context, name, localpath):
        """Download a single file."""
        log.verbose("Fetching", repr(name), "to", repr(localpath), verbosity=10)
        try:
            utils.ensure_dir_exists(localpath)
            if get_download_mode() == "http":
                generator = self.get_data_http(pipeline_context, name)
            else:
                generator = self.get_data_rpc(pipeline_context, name, localpath)
            with open(localpath, "wb+") as outfile:
                for data in generator:
                    outfile.write(data)
            self.verify_file(pipeline_context, name, localpath)
        except Exception, exc:
            # traceback.print_exc()
            try:
                os.remove(localpath)
            except Exception, exc:
                log.error("Failed removing failed download for", 
                          repr(localpath),":", str(exc))
            raise CrdsDownloadError("Error fetching data for " + srepr(name) + 
                                     " from context " + srepr(pipeline_context) + 
                                     " at server " + srepr(get_crds_server()) + 
                                     " with mode " + srepr(get_download_mode()) +
                                     " : " + str(exc))
            
    def get_data_rpc(self, pipeline_context, file, localpath):
        """Yields successive manageable chunks for `file` fetched via jsonrpc."""
        chunk = 0
        chunks = 1
        while chunk < chunks:
            chunks, data = get_file_chunk(pipeline_context, file, chunk)
            log.verbose("Transferred RPC", repr(file), chunk, " of ", chunks)
            chunk += 1
            yield data
    
    def _get_data_http(self, url):
        """Yield the data returned from `url` in manageable chunks."""
        # url = get_url(pipeline_context, file)
        log.verbose("Fetching URL ", repr(url))
        try:
            infile = urllib2.urlopen(url)
            chunk = 0
            data = infile.read(CRDS_DATA_CHUNK_SIZE)
            while data:
                log.verbose("Transferred HTTP", repr(file), "chunk", chunk)
                yield data
                chunk += 1
                data = infile.read(CRDS_DATA_CHUNK_SIZE)
        finally:
            try:
                infile.close()
            except UnboundLocalError:   # maybe the open failed.
                pass

    def get_data_http(self, pipeline_context, file):
        """Yields successive manageable chunks of `file` fetched by http.
        Unlike earlier versions of the protocol which requested the URL from
        the server,  the URL used is static,  essentially /get/<file>,  and
        the server brokers and redirects the request to the real download server.
        """
        url = get_crds_server() + "/get/" + file
        return self._get_data_http(url)

    def verify_file(self, pipeline_context, filename, localpath):
        """Check that the size and checksum of downloaded `filename` match the server."""
        remote_info = get_file_info(pipeline_context, filename)
        local_length = os.stat(localpath).st_size
        original_length = long(remote_info["size"])
        basename = os.path.basename(localpath)
        if original_length != local_length:
            raise CrdsDownloadError("downloaded file size " + str(local_length) +
                                    " does not match server size " + str(original_length))
        if remote_info["sha1sum"] not in ["", "none"]:
            original_sha1sum = remote_info["sha1sum"]
            local_sha1sum = utils.checksum(localpath)
            if original_sha1sum != local_sha1sum:
                raise CrdsDownloadError("downloaded file sha1sum " + repr(local_sha1sum) +
                                        " does not match server sha1sum " + repr(original_sha1sum))
        else:
            log.verbose("Skipping sha1sum check since server doesn't know it.")

FILE_CACHER = FileCacher()

# ==============================================================================

class BundleCacher(FileCacher):
    """BundleCacher gets remote files into a local cache by requesting a bundle
    of any missing files and then unpacking it.
    """
    def download_files(self, pipeline_context, downloads, localpaths, raise_exceptions=True):
        """Download a list of files as an archive bundle and unpack it."""
        bundlepath = config.get_crds_config_path() 
        bundlepath += "/" + "crds_bundle.tar.gz"
        utils.ensure_dir_exists(bundlepath, 0700)
        for name in localpaths:
            if name not in downloads:
                log.verbose("Skipping existing file", repr(name), verbosity=10)
        self.fetch_bundle(bundlepath, downloads)
        self.unpack_bundle(bundlepath, downloads, localpaths)
        
    def fetch_bundle(self, bundlepath, downloads):
        """Ask the CRDS server for an archive of the files listed in `downloads`
        and store the archive in filename `bundlepath`.
        """
        bundle = os.path.basename(bundlepath)
        url = get_crds_server() + "/get_archive/" + bundle + "?"
        for i, name in enumerate(sorted(downloads)):
            url = url + "file" + str(i) + "=" + name + "&"
            log.verbose("Adding", repr(name), "to download request.", verbosity=60)
        url = url[:-1]
        generator = self._get_data_http(url)
        with open(bundlepath, "wb+") as outfile:
            for data in generator:
                outfile.write(data)
        
    def unpack_bundle(self, bundlepath, downloads, localpaths):
        """Unpack the files listed in `downloads` from the archive at `bundlepath`
        storing the extracted files at paths defined by `localpaths`.
        """
        with tarfile.open(bundlepath) as tar:
            for name in sorted(downloads):
                member = tar.getmember(name)
                file = tar.extractfile(member)
                utils.ensure_dir_exists(localpaths[name])
                with open(localpaths[name], "w+") as localfile:
                    log.verbose("Unpacking download", repr(name), "to", repr(localpaths[name]), verbosity=10)
                    contents = file.read()
                    localfile.write(contents)
                    
MAPPING_CACHER = BundleCacher()

# ==============================================================================

def dump_mappings(pipeline_context, ignore_cache=False, mappings=None):
    """Given a `pipeline_context`, determine the closure of CRDS mappings for it and 
    cache them on the local file system.
    
    If mappings is not None,  sync exactly that list of mapping names,  not their closures.
    
    Returns:   { mapping_basename :   mapping_local_filepath ... }   
    """
    assert isinstance(ignore_cache, bool)
    if mappings is None:
        mappings = get_mapping_names(pipeline_context)
    return MAPPING_CACHER.get_local_files(
        pipeline_context, mappings, ignore_cache=ignore_cache)
  
def dump_references(pipeline_context, baserefs=None, ignore_cache=False, raise_exceptions=True):
    """Given a pipeline `pipeline_context` and list of `baserefs` reference 
    file basenames,  obtain the set of reference files and cache them on the
    local file system.
    
    If `basrefs` is None,  sync the closure of references referred to by `pipeline_context`.
    
    Returns:   { ref_basename :   reference_local_filepath ... }
    """
    if baserefs is None:
        baserefs = get_reference_names(pipeline_context)
    baserefs = list(baserefs)
    for refname in baserefs:
        if "NOT FOUND" in refname:
            log.verbose("Skipping " + srepr(refname))
            baserefs.remove(refname)
    return FILE_CACHER.get_local_files(
        pipeline_context, baserefs, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions)
    
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
    localrefs = FILE_CACHER.get_local_files(
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
    dump_mappings(context, ignore_cache=ignore_cache)
    ctx = crds.get_cached_mapping(context)
    return ctx.get_minimum_header(dataset)

