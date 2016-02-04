"""This module defines the API for CRDS clients.   Functions defined here make
remote service calls to the CRDS server to obtain mapping or reference files and
cache them locally.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import os.path
import base64
import re
import zlib
from crds import python23

if sys.version_info < (3,0,0):
    from urllib2 import urlopen
else:
    from urllib.request import urlopen

from .proxy import CheckingProxy

# heavy versions of core CRDS modules defined in one place, client minimally
# dependent on core for configuration, logging, and  file path management.
from crds import utils, log, config
from crds.client import proxy
from crds.log import srepr

from crds.exceptions import ServiceError, CrdsLookupError, CrdsNetworkError, CrdsDownloadError
from crds.python23 import *

# ==============================================================================

__all__ = [
           "get_default_context",
           "get_context_by_date",
           "get_server_info",
           "get_cached_server_info",  # deprecated
           "cache_references",
           
           "set_crds_server", 
           "get_crds_server",
         
           "list_mappings",
           "list_references",

           "get_file_chunk",
           "get_url",
           "get_file_info",
           "get_file_info_map",
           "get_sqlite_db",
           
           "get_mapping_names",
           "get_reference_names",
           
           "dump_references",
           "dump_mappings",
           "dump_files",

           "get_best_references",
           "cache_best_references",
           
           "get_dataset_headers_by_id",
           "get_dataset_headers_by_instrument",
           "get_dataset_ids",
           "get_best_references_by_ids",
           "get_best_references_by_header_map",

           "get_required_parkeys",
           "get_affected_datasets",
           "get_context_history",

           "push_remote_context",
           "get_remote_context",
           ]

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
        log.warning("CRDS_SERVER_URL does not start with https://  ::", url)
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
        log.warning("CRDS_SERVER_URL does not start with https://  ::", url)
    return url

set_crds_server(URL)

# =============================================================================

@utils.cached
def list_mappings(observatory=None, glob_pattern="*"):
    """Return the list of mappings associated with `observatory`
    which match `glob_pattern`.
    """
    return [str(x) for x in S.list_mappings(observatory, glob_pattern)]

@utils.cached
def list_references(observatory=None, glob_pattern="*"):
    """Return the list of references associated with `observatory`
    which match `glob_pattern`.
    """
    return [str(x) for x in S.list_references(observatory, glob_pattern)]

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

@utils.cached
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
    
def get_file_chunk(pipeline_context, filename, chunk):
    """Return the ith `chunk` of data from `filename` as well as the
    total number of chunks.   It is assumed that every file has
    at least one chunk.
    
    Returns (chunks, size, sha1sum, chunk_str)
    where chunks, size, and sha1sum are invariant totals.
    
    Note that `chunks` is determined by the server since it's a loading issue.
    """
    chunks, data = S.get_file_chunk(pipeline_context, filename, chunk)
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
    if files is not None:
        files = tuple(sorted(files))
    if fields is not None:
        fields = tuple(sorted(fields))
    return _get_file_info_map(observatory, files, fields)

@utils.cached
def _get_file_info_map(observatory, files, fields):
    infos = S.get_file_info_map(observatory, files, fields)
    return infos

def get_total_bytes(info_map):
    """Return the total byte count of file info map `info_map`."""
    try:
        return sum([long(info_map[name]["size"]) for name in info_map if "NOT FOUND" not in info_map[name]])
    except Exception as exc:
        log.error("Error computing total byte count: ", str(exc))
        return -1

def get_sqlite_db(observatory):
    """Download the CRDS database as a SQLite database."""
    assert not config.get_cache_readonly(), "Readonly cache, updating the SQLite database cannot be done."""
    encoded_compressed_data = S.get_sqlite_db(observatory)
    data = zlib.decompress(base64.b64decode(encoded_compressed_data))
    path = config.get_sqlite3_db_path(observatory)
    utils.ensure_dir_exists(path)
    with open(path, "wb+") as db_out:
        db_out.write(data)
    return path

@utils.cached
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
    header = { str(key):str(value) for (key,value) in header.items() }
    try:
        bestrefs = S.get_best_references(pipeline_context, dict(header), reftypes)
    except Exception as exc:
        raise CrdsLookupError(str(exc))
    # Due to limitations of jsonrpc,  exception handling is kludged in here.
    for filetype, refname in bestrefs.items():
        if "NOT FOUND" in refname:
            if "NOT FOUND n/a" == refname:
                log.verbose("Reference type", srepr(filetype), "not applicable.", verbosity=80)
            else:
                raise CrdsLookupError("Error determining best reference for " + 
                                      srepr(filetype) + " = " + 
                                      str(refname)[len("NOT FOUND"):])
    return bestrefs

def get_best_references_by_ids(context, dataset_ids, reftypes=None, include_headers=False):
    """Get best references for the specified `dataset_ids` and reference types.  If
    reftypes is None,  all types are returned.
    
    Returns { dataset_id : { reftype: bestref, ... }, ... }
    """
    try:
        bestrefs = S.get_best_references_by_ids(context, dataset_ids, reftypes, include_headers)
    except Exception as exc:
        raise CrdsLookupError(str(exc))
    return bestrefs

def get_best_references_by_header_map(context, header_map, reftypes=None):
    """Get best references for header_map = { dataset_id : header, ...}, } and reference types
    where a header is a dictionary of matching parameters.
      
    If reftypes is None,  all types are returned.
    
    Returns { dataset_id : { reftype: bestref, ... }, ... }
    """
    try:
        bestrefs_map = S.get_best_references_by_header_map(context, header_map, reftypes)
    except Exception as exc:
        raise CrdsLookupError(str(exc))
    return bestrefs_map

@utils.cached
def get_default_context(observatory=None):
    """Return the name of the latest pipeline mapping in use for processing
    files for `observatory`.  
    """
    return str(S.get_default_context(observatory))

@utils.cached
def get_context_by_date(date, observatory=None):
    """Return the name of the first operational context which precedes `date`."""
    return str(S.get_context_by_date(date, observatory))

@utils.cached
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
        info["reference_url"] = info.pop("reference_url")["unchecked"]
        info["mapping_url"] = info.pop("mapping_url")["unchecked"]
        return info
    except ServiceError as exc:
        raise CrdsNetworkError("network connection failed: " + srepr(get_crds_server()) + " : " + str(exc))

get_cached_server_info = get_server_info

def get_server_version():
    """Return the API version of the current CRDS server."""
    info = get_server_info()
    return info["crds_version"]["str"]

def get_dataset_headers_by_id(context, dataset_ids, datasets_since=None):
    """Return { dataset_id : { header } } for `dataset_ids`."""
    context = os.path.basename(context)
    return S.get_dataset_headers_by_id(context, dataset_ids, datasets_since)
    
def get_dataset_ids(context, instrument, datasets_since=None):
    """Return [ dataset_id, ...] for `instrument`."""
    context = os.path.basename(context)
    return S.get_dataset_ids(context, instrument, datasets_since)

@utils.cached
def get_required_parkeys(context):
    """Return a mapping from instruments to lists of parameter names required to
    compute bestrefs under `context`,  i.e. matching header keys.
    
    { instrument : [ matching_parkey_name, ... ], ... }
    """
    context = os.path.basename(context)
    return S.get_required_parkeys(context)

def get_dataset_headers_by_instrument(context, instrument, datasets_since=None):
    """Return { dataset_id : { header } } for `instrument`."""
    max_ids_per_rpc = get_server_info().get("max_headers_per_rpc", 5000)
    ids = get_dataset_ids(context, instrument, datasets_since)
    headers = {}
    for i in range(0, len(ids), max_ids_per_rpc):
        id_slice = ids[i : i + max_ids_per_rpc]
        log.verbose("Dumping datasets for", repr(instrument), "ids", i , "of", len(ids), verbosity=20)
        header_slice = get_dataset_headers_by_id(context, id_slice)
        headers.update(header_slice)
    return headers

def get_affected_datasets(observatory, old_context=None, new_context=None):
    """Return a structure describing the ids affected by the last context change."""
    return utils.Struct(S.get_affected_datasets(observatory, old_context, new_context))

def get_context_history(observatory):
    """Fetch the history of context transitions, a list of history era tuples:

     Returns:  [ (start_date, context_name, description), ... ]
    """
    return sorted(tuple(x) for x in S.get_context_history(observatory))

def push_remote_context(observatory, kind, key, context):
    """Upload the specified `context` of type `kind` (e.g. "operational") to the
    server,  informing the server of the actual configuration of the local cache
    for critical systems like pipelines,  not average users.   This lets the server
    display actual versus commanded (Set Context) operational contexts for a pipeline.
    """
    return S.push_remote_context(observatory, kind, key, context)

def get_remote_context(observatory, pipeline_name):
    """Get the name of the default context last pushed from `pipeline_name` and
    presumed to be operational.
    """
    return S.get_remote_context(observatory, pipeline_name)

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

def file_progress(activity, name, path, bytes, bytes_so_far, total_bytes, nth_file, total_files):
    """Output progress information for `activity` on file `name` at `path`."""
    return "{activity}  {path!s:<55}  {bytes} bytes  ({nth_file} / {total_files} files) ({bytes_so_far} / {total_bytes} bytes)".format(
        activity=activity, 
        path=path, 
        bytes=utils.human_format_number(bytes),
        nth_file=nth_file+1, 
        total_files=total_files, 
        bytes_so_far=utils.human_format_number(bytes_so_far).strip(), 
        total_bytes=utils.human_format_number(total_bytes).strip())

# ==============================================================================

class FileCacher(object):
    """FileCacher gets remote files with simple names into a local cache."""
    def __init__(self, pipeline_context, ignore_cache=False, raise_exceptions=True, api=1):
        self.pipeline_context = pipeline_context
        self.observatory = self.observatory_from_context()
        self.ignore_cache = ignore_cache
        self.raise_exceptions = raise_exceptions
        self.api = api
        self.info_map = {}
    
    def get_local_files(self, names):
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
            if re.match(r"\w+\.r[0-9]h$", refname):
                names.append(refname[:-1]+"d")

        downloads = []
        for name in names:
            localpath = self.locate(name)
            if name.lower() in ["n/a", "undefined"]:
                continue
            if (not os.path.exists(localpath)):
                downloads.append(name)
            elif self.ignore_cache:
                utils.remove(localpath, observatory=self.observatory)
                downloads.append(name)
                utils.remove(localpath, observatory=self.observatory)
            localpaths[name] = localpath
        if downloads:
            n_bytes = self.download_files(downloads, localpaths)
        else:
            log.verbose("Skipping download for cached files", sorted(names), verbosity=60)
            n_bytes = 0
        if self.api == 1:
            return localpaths
        else:
            return localpaths, len(downloads), n_bytes

    def observatory_from_context(self):
        """Determine the observatory from `pipeline_context`,  based on name if possible."""
        if "jwst" in self.pipeline_context:
            observatory = "jwst"
        elif "hst" in self.pipeline_context:
            observatory = "hst"
        else:
            import crds.rmap
            observatory = crds.rmap.get_cached_mapping(self.pipeline_context).observatory
        return observatory

    def locate(self, name):
        """Return the standard CRDS cache location for file `name`."""
        return config.locate_file(name, observatory=self.observatory)

    def download_files(self, downloads, localpaths):
        """Serial file-by-file download."""
        self.info_map = get_file_info_map(
                self.observatory, downloads, ["size", "rejected", "blacklisted", "state", "sha1sum", "instrument"])
        if config.writable_cache_or_verbose("Readonly cache, skipping download of (first 5):", repr(downloads[:5]), verbosity=70):
            bytes_so_far = 0
            total_files = len(downloads)
            total_bytes = get_total_bytes(self.info_map)
            for nth_file, name in enumerate(downloads):
                try:
                    if "NOT FOUND" in self.info_map[name]:
                        raise CrdsDownloadError("file is not known to CRDS server.")
                    bytes, path = long(self.info_map[name]["size"]), localpaths[name]
                    log.info(file_progress("Fetching", name, path, bytes, bytes_so_far, total_bytes, nth_file, total_files))
                    self.download(name, path)
                    bytes_so_far += os.stat(path).st_size
                except Exception as exc:
                    if self.raise_exceptions:
                        raise
                    else:
                        log.error("Failure downloading file", repr(name), ":", str(exc))
            return bytes_so_far
        return 0
    
    def download(self, name, localpath):
        """Download a single file."""
        # This code is complicated by the desire to blow away failed downloads.  For the specific
        # case of KeyboardInterrupt,  the file needs to be blown away,  but the interrupt should not
        # be re-characterized so it is still un-trapped elsewhere under normal idioms which try *not*
        # to trap KeyboardInterrupt.
        assert not config.get_cache_readonly(), "Readonly cache,  cannot download files " + repr(name)
        try:
            utils.ensure_dir_exists(localpath)
            return proxy.apply_with_retries(self.download_core, name, localpath)
        except Exception as exc:
            self.remove_file(localpath)
            raise CrdsDownloadError("Error fetching data for " + srepr(name) + 
                                     " from context " + srepr(self.pipeline_context) + 
                                     " at server " + srepr(get_crds_server()) + 
                                     " with mode " + srepr(config.get_download_mode()) +
                                     " : " + str(exc))
        except:  #  mainly for control-c,  catch it and throw it.
            self.remove_file(localpath)
            raise
        
    def remove_file(self, localpath):
        """Removes file at `localpath`."""
        log.verbose("Removing file", repr(localpath))
        try:
            os.remove(localpath)
        except:
            log.verbose("Exception during file removal of", repr(localpath))

    def download_core(self, name, localpath):
        """Download and verify file `name` under context `pipeline_context` to `localpath`."""
        if config.get_download_plugin():
            self.plugin_download(name, localpath)
        elif config.get_download_mode() == "rpc":
            generator = self.get_data_rpc(name)
            self.generator_download(generator, localpath)
        else:
            generator = self.get_data_http(name)
            self.generator_download(generator, localpath)
        self.verify_file(name, localpath)
        
    def generator_download(self, generator, localpath):
        """Read all bytes from `generator` until file is downloaded to `localpath.`"""
        with open(localpath, "wb+") as outfile:
            for data in generator:
                outfile.write(data)
                
    def plugin_download(self, filename, localpath):
        """Run an external program defined by CRDS_DOWNLOAD_PLUGIN to download filename to localpath."""
        url = self.get_url(filename)
        plugin_cmd = config.get_download_plugin()
        plugin_cmd = plugin_cmd.replace("${SOURCE_URL}", url)
        plugin_cmd = plugin_cmd.replace("${OUTPUT_PATH}", localpath)
        log.verbose("Running download plugin:", repr(plugin_cmd))
        status = os.system(plugin_cmd)
        if status != 0:
            if status == 2:
                raise KeyboardInterrupt("Interrupted plugin.")
            else:
                raise CrdsDownloadError("Plugin download fail status = {}".format(status))
        
    def get_data_rpc(self, filename):
        """Yields successive manageable chunks for `file` fetched via jsonrpc."""
        chunk = 0
        chunks = 1
        while chunk < chunks:
            stats = utils.TimingStats()
            stats.increment("bytes", config.CRDS_DATA_CHUNK_SIZE)
            chunks, data = get_file_chunk(self.pipeline_context, filename, chunk)
            status = stats.status("bytes")
            log.verbose("Transferred RPC", repr(filename), chunk, " of ", chunks, "at", status[1], verbosity=20)
            chunk += 1
            yield data
    
    def get_data_http(self, filename):
        """Yield the data returned from `filename` of `pipeline_context` in manageable chunks."""
        url = self.get_url(filename)
        try:
            infile = urlopen(url)
            chunk = 0
            stats = utils.TimingStats()
            stats.increment("bytes", config.CRDS_DATA_CHUNK_SIZE)
            data = infile.read(config.CRDS_DATA_CHUNK_SIZE)
            status = stats.status("bytes")
            while data:
                log.verbose("Transferred HTTP", repr(url), "chunk", chunk, "at", status[1], verbosity=20)
                yield data
                chunk += 1
                stats = utils.TimingStats()
                stats.increment("bytes", config.CRDS_DATA_CHUNK_SIZE)
                data = infile.read(config.CRDS_DATA_CHUNK_SIZE)
                status = stats.status("bytes")
        finally:
            try:
                infile.close()
            except UnboundLocalError:   # maybe the open failed.
                pass

    def get_url(self, filename):
        """Return the URL used to fetch `filename` of `pipeline_context`."""
        info = get_server_info()
        if config.is_mapping(filename):
            url = info["mapping_url"][self.observatory]
        else:
            url = info["reference_url"][self.observatory]
        if not url.endswith("/"):
            url += "/"
        return url + filename

    def verify_file(self, filename, localpath):
        """Check that the size and checksum of downloaded `filename` match the server."""
        remote_info = self.info_map[filename]
        local_length = os.stat(localpath).st_size
        original_length = long(remote_info["size"])
        if original_length != local_length:
            raise CrdsDownloadError("downloaded file size " + str(local_length) +
                                    " does not match server size " + str(original_length))
        if not config.get_checksum_flag():
            log.verbose("Skipping sha1sum with CRDS_DOWNLOAD_CHECKSUMS=False")
        elif remote_info["sha1sum"] not in ["", "none"]:
            original_sha1sum = remote_info["sha1sum"]
            local_sha1sum = utils.checksum(localpath)
            if original_sha1sum != local_sha1sum:
                raise CrdsDownloadError("downloaded file " + repr(filename) + " sha1sum " + repr(local_sha1sum) +
                                        " does not match server sha1sum " + repr(original_sha1sum))
        else:
            log.verbose("Skipping sha1sum check since server doesn't know it.")

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
    mappings = list(reversed(sorted(set(mappings))))
    return FileCacher(pipeline_context, ignore_cache, raise_exceptions, api).get_local_files(mappings)
  

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
    baserefs = sorted(set(baserefs))
    return FileCacher(pipeline_context, ignore_cache, raise_exceptions, api).get_local_files(baserefs)
    

def dump_files(pipeline_context, files, ignore_cache=False, raise_exceptions=True):
    """Unified interface to dump any file in `files`, mapping or reference.
    
    Returns localpaths,  downloads count,  bytes downloaded
    """
    if files is None:
        files = get_mapping_names(pipeline_context)
    mappings = [ os.path.basename(name) for name in files if config.is_mapping(name) ]
    references = [ os.path.basename(name) for name in files if not config.is_mapping(name) ]
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
    return dict(list(m_paths.items())+list(r_paths.items())), m_downloads + r_downloads, m_bytes + r_bytes
    
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
        elif isinstance(refname, python23.string_types):
            if "NOT FOUND" in refname:
                if "n/a" in refname.lower():
                    log.verbose("Reference type", repr(filetype), 
                                "NOT FOUND.  Skipping reference caching/download.")
                else:
                    raise CrdsLookupError("Error determining best reference for " + 
                                          repr(str(filetype)) + " = " + 
                                          str(refname)[len("NOT FOUND"):])
            else:
                wanted.append(refname)
        else:
            raise CrdsLookupError("Unhandled bestrefs return value type for " + repr(str(filetype)))
    localrefs = FileCacher(pipeline_context, ignore_cache, raise_exceptions=False, api=1).get_local_files(wanted)
    refs = {}
    for filetype, refname in bestrefs.items():
        if isinstance(refname, tuple):
            refs[str(filetype)] = tuple([str(localrefs[name]) for name in refname])
        elif isinstance(refname, dict):
            refs[str(filetype)] = { name : str(localrefs[name]) for name in refname }
        elif isinstance(refname, python23.string_types):
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

