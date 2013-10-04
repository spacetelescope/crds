"""This module defines the API for CRDS clients.   Functions defined here make
remote service calls to the CRDS server to obtain mapping or reference files and
cache them locally.
"""
import os
import os.path
import base64
import urllib2
import tarfile
import math
import re

from .proxy import CheckingProxy, ServiceError, CrdsError

# heavy versions of core CRDS modules defined in one place, client minimally
# dependent on core for configuration, logging, and  file path management.
from crds import utils, log, config

# ==============================================================================

class CrdsNetworkError(CrdsError):
    """First network service call failed, nominally connection refused."""
    
class CrdsLookupError(CrdsError, LookupError):
    """Filekind NOT FOUND for some reason defined in the exception string."""
    
class CrdsDownloadError(CrdsError):
    """Error downloading data for a reference or mapping file."""

__all__ = [
           "get_default_context",
           "get_context_by_date",
           "get_server_info",
           "cache_references",
           
           "set_crds_server", 
           "get_crds_server",
         
           "list_mappings",
           "get_file_chunk",
           "get_url",
           "get_file_info",
           "get_file_info_map",
           
           "get_mapping_names",
           "get_reference_names",
           
           "dump_references",
           "dump_mappings",
           "dump_files",

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

# ============================================================================

# Server for CRDS services and mappings

URL_SUFFIX = "/json/"

JWST_OPS_SERVER = 'https://jwst-crds.stsci.edu'
HST_OPS_SERVER = 'https://hst-crds.stsci.edu'
JWST_TEST_SERVER = 'https://jwst-crds-test.stsci.edu'
HST_TEST_SERVER = 'https://hst-crds-test.stsci.edu'

URL = os.environ.get("CRDS_SERVER_URL", "https://crds-serverless-mode.stsci.edu")

S = None    # Proxy server

def set_crds_server(url):
    """Configure the CRDS JSON services server to `url`,  
    e.g. 'http://localhost:8000'
    """
    if not url.startswith("https://") and "localhost" not in url:
        log.warning("CRDS_SERVER_URL does not start with https://")
    if url.endswith("/"):
        url = url[:-1]
    global URL, S
    URL = url + URL_SUFFIX
    S = CheckingProxy(URL, version="1.0")
    
def get_crds_server():
    """Return the base URL for the CRDS JSON RPC server.
    """
    url = URL[:-len(URL_SUFFIX)]
    if not url.startswith("https://") and "localhost" not in url:
        log.warning("CRDS_SERVER_URL does not start with https://")
    return url

set_crds_server(URL)

# ============================================================================

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

def get_checksum_flag():
    """Return True if the environment is configured for checksums."""
    return bool(os.environ.get("CRDS_DOWNLOAD_CHECKSUMS", "1"))
        
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
    infos = S.get_file_info_map(observatory, files, fields)
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


def get_default_context(observatory=None):
    """Return the name of the latest pipeline mapping in use for processing
    files for `observatory`.  
    """
    return str(S.get_default_context(observatory))

def get_context_by_date(date, observatory=None):
    """Return the name of the first operational context which precedes `date`."""
    return str(S.get_context_by_date(date, observatory))
    
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
        raise CrdsNetworkError("network connection failed: " + srepr(get_crds_server()) + " : " + str(exc))

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

@utils.cached
def get_cached_server_info():
    return get_server_info()

class FileCacher(object):
    """FileCacher gets remote files with simple names into a local cache.
    """
    def __init__(self):
        self.info_map = {}
    
    def get_local_files(self, pipeline_context, names, ignore_cache=False, raise_exceptions=True, api=1):
        """Given a list of basename `mapping_names` which are pertinent to the 
        given `pipeline_context`,   cache the mappings locally where they can 
        be used by CRDS.
        """
        if isinstance(names, dict):
            names = names.values()
        localpaths = {}
        
        # Add in GEIS format "conjugate" data files,  .rmaps specify only .rXh
        names2 = names[:]
        for refname in names2:
            if re.match("\w+\.r[0-9]h$", refname):
                names.append(refname[:-1]+"d")

        downloads = []
        for i, name in enumerate(names):
            localpath = self.locate(pipeline_context, name)
            if (not os.path.exists(localpath)):
                downloads.append(name)
            elif ignore_cache:
                downloads.append(name)
                with log.error_on_exception("Ignore_cache=True and Failed removing existing", repr(name)):
                    os.chmod(localpath, 0666)
                    os.remove(localpath)
            localpaths[name] = localpath
        if downloads:
            bytes = self.download_files(pipeline_context, downloads, localpaths, raise_exceptions)
        else:
            log.verbose("Skipping download for cached files", names, verbosity=30)
            bytes = 0
        if api == 1:
            return localpaths
        else:
            return localpaths, len(downloads), bytes

    def observatory_from_context(self, pipeline_context):
        if "jwst" in pipeline_context:
            observatory = "jwst"
        elif "hst" in pipeline_context:
            observatory = "hst"
        else:
            import crds.rmap
            observatory = crds.rmap.get_cached_mapping(pipeline_context).observatory
        return observatory

    def locate(self, pipeline_context, name):
        observatory = self.observatory_from_context(pipeline_context)
        return config.locate_file(name, observatory=observatory)

    def download_files(self, pipeline_context, downloads, localpaths, raise_exceptions=True):
        """Serial file-by-file download."""
        obs = self.observatory_from_context(pipeline_context)
        self.info_map = get_file_info_map(obs, downloads, ["sha1sum", "size"])
        bytes = 0
        for name in downloads:
            try:
                if "NOT FOUND" in self.info_map[name]:
                    raise CrdsDownloadError("file is not known to CRDS server.")
                bytes += self.download(pipeline_context, name, localpaths[name])
            except Exception, exc:
                if raise_exceptions:
                    raise
                else:
                    log.error("Failure downloading file", repr(name), ":", str(exc))
        return bytes

    def download(self, pipeline_context, name, localpath):
        """Download a single file."""
        log.verbose("Fetching", repr(name), "to", repr(localpath), verbosity=10)
        try:
            utils.ensure_dir_exists(localpath)
            if get_download_mode() == "http":
                generator = self.get_data_http(pipeline_context, name)
            else:
                generator = self.get_data_rpc(pipeline_context, name)
            bytes = 0
            with open(localpath, "wb+") as outfile:
                for data in generator:
                    outfile.write(data)
                    bytes += len(data)
            self.verify_file(pipeline_context, name, localpath)
            return bytes
        except Exception, exc:
            # traceback.print_exc()
            try:
                os.remove(localpath)
            except Exception:
                pass
            raise CrdsDownloadError("Error fetching data for " + srepr(name) + 
                                     " from context " + srepr(pipeline_context) + 
                                     " at server " + srepr(get_crds_server()) + 
                                     " with mode " + srepr(get_download_mode()) +
                                     " : " + str(exc))
            
    def get_data_rpc(self, pipeline_context, file):
        """Yields successive manageable chunks for `file` fetched via jsonrpc."""
        chunk = 0
        chunks = 1
        while chunk < chunks:
            stats = utils.TimingStats()
            stats.increment("bytes", CRDS_DATA_CHUNK_SIZE)
            chunks, data = get_file_chunk(pipeline_context, file, chunk)
            status = stats.status("bytes")
            log.verbose("Transferred RPC", repr(file), chunk, " of ", chunks, "at", status[1])
            chunk += 1
            yield data
    
    def get_data_http(self, pipeline_context, file):
        """Yield the data returned from `file` of `pipeline_context` in manageable chunks."""
        url = self.get_url(pipeline_context, file)
        return self._get_data_http(url, file)

    def _get_data_http(self, url, file):
        """Yield the data returned from `url` in manageable chunks."""
        chunks = int(math.ceil(long(self.info_map[file]["size"]) / CRDS_DATA_CHUNK_SIZE))
        log.verbose("Fetching URL ", repr(url))
        try:
            infile = urllib2.urlopen(url)
            chunk = 0
            stats = utils.TimingStats()
            stats.increment("bytes", CRDS_DATA_CHUNK_SIZE)
            data = infile.read(CRDS_DATA_CHUNK_SIZE)
            status = stats.status("bytes")
            while data:
                log.verbose("Transferred HTTP", repr(file), "chunk", chunk, "of", chunks, "at", status[1])
                yield data
                chunk += 1
                stats = utils.TimingStats()
                stats.increment("bytes", CRDS_DATA_CHUNK_SIZE)
                data = infile.read(CRDS_DATA_CHUNK_SIZE)
                status = stats.status("bytes")
        finally:
            try:
                infile.close()
            except UnboundLocalError:   # maybe the open failed.
                pass

    def get_url(self, pipeline_context, file, checking="unchecked"):
        """Return the URL used to fetch `file` of `pipeline_context`."""
        info = get_cached_server_info()
        observatory = self.observatory_from_context(pipeline_context)
        if config.is_mapping(file):
            url = info["mapping_url"][checking][observatory]
        else:
            url = info["reference_url"][checking][observatory]
        if not url.endswith("/"):
            url += "/"
        return url + file

    def verify_file(self, pipeline_context, filename, localpath):
        """Check that the size and checksum of downloaded `filename` match the server."""
        remote_info = self.info_map[filename]
        local_length = os.stat(localpath).st_size
        original_length = long(remote_info["size"])
        basename = os.path.basename(localpath)
        if original_length != local_length:
            raise CrdsDownloadError("downloaded file size " + str(local_length) +
                                    " does not match server size " + str(original_length))
        if not get_checksum_flag():
            log.verbose("Skipping sha1sum with CRDS_DOWNLOAD_CHECKSUMS=False")
        elif remote_info["sha1sum"] not in ["", "none"]:
            original_sha1sum = remote_info["sha1sum"]
            local_sha1sum = utils.checksum(localpath)
            if original_sha1sum != local_sha1sum:
                raise CrdsDownloadError("downloaded file " + repr(filename) + " sha1sum " + repr(local_sha1sum) +
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
        obs = self.observatory_from_context(pipeline_context)
        self.info_map = get_file_info_map(obs, downloads, ["sha1sum", "size"])
        bundlepath = config.get_crds_config_path() 
        bundlepath += "/" + "crds_bundle.tar.gz"
        utils.ensure_dir_exists(bundlepath, 0700)
        for name in localpaths:
            if name not in downloads:
                log.verbose("Skipping existing file", repr(name), verbosity=10)
        self.fetch_bundle(bundlepath, downloads)
        bytes = self.unpack_bundle(bundlepath, downloads, localpaths)
        for name in downloads:
            self.verify_file(pipeline_context, name, localpaths[name])
        return bytes

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
        generator = self._get_data_http(url, name)
        with open(bundlepath, "wb+") as outfile:
            for data in generator:
                outfile.write(data)
        
    def unpack_bundle(self, bundlepath, downloads, localpaths):
        """Unpack the files listed in `downloads` from the archive at `bundlepath`
        storing the extracted files at paths defined by `localpaths`.
        """
        bytes = 0
        with tarfile.open(bundlepath) as tar:
            for name in sorted(downloads):
                member = tar.getmember(name)
                file = tar.extractfile(member)
                utils.ensure_dir_exists(localpaths[name])
                with open(localpaths[name], "w+") as localfile:
                    log.verbose("Unpacking download", repr(name), "to", repr(localpaths[name]), verbosity=10)
                    contents = file.read()
                    localfile.write(contents)
                    bytes += len(contents)
        return bytes
                    
MAPPING_CACHER = BundleCacher()

# ==============================================================================

def dump_mappings(pipeline_context, ignore_cache=False, mappings=None, raise_exceptions=True, api=1):
    """Given a `pipeline_context`, determine the closure of CRDS mappings for it and 
    cache them on the local file system.
    
    If mappings is not None,  sync exactly that list of mapping names,  not their closures.
    
    Returns:   { mapping_basename :   mapping_local_filepath ... }   (api=1)
               { mapping_basename :   mapping_local_filepath ... }, downloads, bytes   (api=2)
    """
    assert isinstance(ignore_cache, bool)
    if mappings is None:
        mappings = get_mapping_names(pipeline_context)
    return MAPPING_CACHER.get_local_files(
        pipeline_context, mappings, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions, api=api)
  
def dump_references(pipeline_context, baserefs=None, ignore_cache=False, raise_exceptions=True, api=1):
    """Given a pipeline `pipeline_context` and list of `baserefs` reference 
    file basenames,  obtain the set of reference files and cache them on the
    local file system.
    
    If `basrefs` is None,  sync the closure of references referred to by `pipeline_context`.
    
    Returns:   { ref_basename :   reference_local_filepath ... }   (api=1)
               { ref_basename :  reference_local_path }, downloads, bytes  (api=2)
    """
    if baserefs is None:
        baserefs = get_reference_names(pipeline_context)
    baserefs = list(baserefs)
    for refname in baserefs:
        if "NOT FOUND" in refname:
            log.verbose("Skipping " + srepr(refname))
            baserefs.remove(refname)
    return FILE_CACHER.get_local_files(
        pipeline_context, baserefs, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions, api=api)
    
def dump_files(pipeline_context, files, ignore_cache=False, raise_exceptions=True):
    """Unified interface to dump any file in `files`, mapping or reference.
    
    Returns localpaths,  downloads count,  bytes downloaded
    """
    if files is None:
        files = get_mapping_names(pipeline_context)
    mappings = [ os.path.basename(file) for file in files if config.is_mapping(file) ]
    references = [ os.path.basename(file) for file in files if not config.is_mapping(file) ]
    if mappings:
        m_paths, m_downloads, m_bytes = dump_mappings(
            pipeline_context, mappings=mappings, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions, api=2)
    else:
        m_paths, m_downloads, m_bytes = {}, 0, 0
    if references:
        r_paths, r_downloads, r_bytes = dump_references(
            pipeline_context, baserefs=references, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions, api=2)
    else:
        r_paths, r_downloads, r_bytes = {}, 0, 0
    return dict(m_paths.items()+r_paths.items()), m_downloads + r_downloads, m_bytes + r_bytes
    
def cache_references(pipeline_context, bestrefs, ignore_cache=False):
    """Given a pipeline `pipeline_context` and `bestrefs` mapping,  obtain the
    set of reference files and cache them on the local file system.
    
    bestrefs    { reference_keyword :  reference_basename } 
    
    Returns:   { reference_keyword :  reference_local_filepath ... }   
    """
    wanted = []
    for filetype, refname in bestrefs.items():
        if isinstance(refname, tuple):
            wanted.extend(list(refname))
        elif isinstance(refname, dict):
            wanted.extend(refname.values())
        elif isinstance(refname, basestring):
            if "NOT FOUND" in refname:
                if "n/a" in refname.lower():
                    log.verbose("Reference type", repr(filetype), 
                                "NOT FOUND.  Ignoring.")
                else:
                    raise CrdsLookupError("Error determining best reference for " + 
                                          repr(str(filetype)) + " = " + 
                                          str(refname)[len("NOT FOUND"):])
            else:
                wanted.append(refname)
        else:
            raise CrdsLookupError("Unhandled bestrefs return value type for " + repr(str(filetype)))
    localrefs = FILE_CACHER.get_local_files(pipeline_context, wanted, ignore_cache=ignore_cache)
    refs = {}
    for filetype, refname in bestrefs.items():
        if isinstance(refname, tuple):
            refs[str(filetype)] = tuple([str(localrefs[name]) for name in refname])
        elif isinstance(refname, dict):
            refs[str(filetype)] = { name : str(localrefs[name]) for name in refname }
        elif isinstance(refname, basestring):
            if "NOT FOUND" in refname:
                refs[str(filetype)] = str(refname)
            else:
                refs[str(filetype)] = str(localrefs[refname])
        else:  # can't really get here.
            raise CrdsLookupError("Unhandled bestrefs return value type for " + repr(str(filetype)))
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

