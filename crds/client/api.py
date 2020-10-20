"""This module defines the API for CRDS clients.   Functions defined here make
remote service calls to the CRDS server to obtain mapping or reference files and
cache them locally.
"""
import os
import os.path
import base64
import re
import zlib
import html
from urllib import request
import warnings
import json
import ast

# ==============================================================================

# heavy versions of core CRDS modules defined in one place, client minimally
# dependent on core for configuration, logging, and  file path management.
# import crds
from crds.core import utils, log, config, constants
from crds.core.log import srepr

from crds.core.exceptions import ServiceError, CrdsLookupError
from crds.core.exceptions import CrdsNetworkError, CrdsDownloadError
from crds.core.exceptions import CrdsRemoteContextError

from . import proxy
from .proxy import CheckingProxy

# ==============================================================================

__all__ = [
    "get_default_observatory",
    "get_default_context",
    "get_context_by_date",
    "get_server_info",
    "get_cached_server_info",  # deprecated
    "cache_references",

    "set_crds_server",
    "get_crds_server",

    "list_mappings",
    "list_references",

    "get_url",      # deprecated
    "get_flex_uri",
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
    "get_aui_best_references",
    "get_best_references_by_header_map",

    "get_required_parkeys",
    "get_affected_datasets",
    "get_context_history",

    "push_remote_context",
    "get_remote_context",

    "jpoll_pull_messages",
    "jpoll_abort",

    "get_system_versions",
    ]

# ============================================================================

# Server for CRDS services and mappings

URL_SUFFIX = "/json/"

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
    """Returns a URL for the specified pmap, imap, or rmap file.   DEPRECATED
    """
    utils.deprecate(
        "crds.client.get_mapping_url()", "2020-09-01", "crds.client.get_flex_uri()")
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
    """Returns a URL for the specified reference file.    DEPRECATED
    """
    utils.deprecate(
        "crds.client.get_reference_url()", "2020-09-01", "crds.client.get_flex_uri()")
    return S.get_reference_url(pipeline_context, reference)

def get_url(pipeline_context, filename):
    """Return the URL for a CRDS reference or mapping file.   DEPRECATED
    """
    utils.deprecate(
        "crds.client.get_url()", "2020-09-01", "crds.client.get_flex_uri()")
    return S.get_url(pipeline_context, filename)

def get_flex_uri(filename, observatory=None):
    """If environment variables define the base URI for `filename`, append
    filename and return the combined URI.

    If no environment override has been specified, obtain the base URI from
    the server_info config,  append filename, and return the combined URI.

    If `filename` is a config file and no environment override is defined,
    return "none".
    """
    if observatory is None:
        observatory = get_default_observatory()
    uri = config.get_uri(filename)
    if uri == "none":
        info = get_server_info()
        if config.is_config(filename):
            uri = _unpack_info(info, "config_url", observatory)
        elif config.is_pickle(filename):
            uri = _unpack_info(info, "pickle_url", observatory)
        elif config.is_mapping(filename):
            uri = _unpack_info(info, "mapping_url", observatory)
        elif config.is_reference(filename):
            uri = _unpack_info(info, "reference_url", observatory)
        else:
            raise CrdsError("Can't identify file type for:", srepr(filename))
        if uri == "none":
            return uri
        if not uri.endswith("/"):
            uri += "/"
        uri += filename
    return uri

def _unpack_info(info, section, observatory):
    """Return info[section][observatory] if info[section] is defined.
    Otherwise return "none".
    """
    sect = info.get(section)
    if sect:
       return sect[observatory]
    else:
        return "none"

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
    """Memory cached version of get_file_info_map() service."""
    infos = S.get_file_info_map(observatory, files, fields)
    return infos

def get_total_bytes(info_map):
    """Return the total byte count of file info map `info_map`."""
    try:
        return sum([int(info_map[name]["size"]) for name in info_map if "NOT FOUND" not in info_map[name]])
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
        raise CrdsLookupError(str(exc)) from exc
    return bestrefs

def get_best_references_by_ids(context, dataset_ids, reftypes=None, include_headers=False):
    """Get best references for the specified `dataset_ids` and reference types.  If
    reftypes is None,  all types are returned.

    Returns { dataset_id : { reftype: bestref, ... }, ... }
    """
    try:
        bestrefs = S.get_best_references_by_ids(context, dataset_ids, reftypes, include_headers)
    except Exception as exc:
        raise CrdsLookupError(str(exc)) from exc
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
        raise CrdsLookupError(str(exc)) from exc
    return bestrefs_map


def get_aui_best_references(date, dataset_ids):
    """Get best references for date and reference types
    where a header is a dictionary of matching parameters.

    Returns { dataset_id : { reftype: bestref, ... }, ... }
    """
    try:
        bestrefs_map = S.get_aui_best_references(date, dataset_ids)
    except Exception as exc:
        raise CrdsLookupError(str(exc)) from exc
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
    info = _get_server_info()
    info["server"] = get_crds_server()
    # The original CRDS info struct features both "checked" and "unchecked"
    # versions of the download URLs where the unchecked version is a simple
    # static file which has been used exclusively for performance reasons.
    # This should eventually be simplified to a single URL which will nominally
    # be the unchecked version.  Roughly 2020-09-01 is should be possible to
    # simplify the server config and remove the code below from future
    # clients...  while older clients will continue to work with the simplified
    # server.
    if "unchecked" in info.get("reference_url", "UNDEFINED"):
        info["reference_url"] = info["reference_url"]["unchecked"]
    if "unchecked" in info.get("mapping_url", "UNDEFINED"):
        info["mapping_url"] = info["mapping_url"]["unchecked"]
    if "unchecked" in info.get("config_url", "UNDEFINED"):
        info["config_url"] = info["config_url"]["unchecked"]
    if "unchecked" in info.get("pickle_url", "UNDEFINED"):
        info["pickle_url"] = info["pickle_url"]["unchecked"]
    # Add fallback download_metadata for using new client with old servers
    # Put into direct-from-server encoded form decoded later get_download_metadata()
    # but stored in server_config as is.
    if "download_metadata" not in info:
        metadata = get_file_info_map(
            get_default_observatory(), fields=["size", "sha1sum"])
        info["download_metadata"] = proxy.crds_encode(metadata)
    return info

@utils.cached
def get_download_metadata():
    "Defer and cache decoding of download_metadata field of server info."""
    info = get_server_info()
    return proxy.crds_decode(info["download_metadata"])

def _get_server_info():
    """Fetch the server info dict.   If CRDS_CONFIG_URI is set then
    download that URL and load json from the contents.  Otherwise,
    call the CRDS server JSONRPC get_server_info() API.

    Returns  server info dict
    """
    config_uri = config.get_uri("server_config")
    try:
        if config_uri != "none":
            log.verbose(f"Loading config from URI '{config_uri}'.")
            content = utils.get_uri_content(config_uri)
            info = ast.literal_eval(content)
            info["status"] = "uri"
            info["connected"] = False
        else:
            config_uri = f"JSON RPC service at '{get_crds_server()}'"
            info = S.get_server_info()
            log.verbose("Connected to server at", srepr(get_crds_server()))
            info["status"] = "server"
            info["connected"] = True
    except Exception as exc:
        raise CrdsNetworkError(
            f"Failed downloading cache config from: {config_uri}:",
            srepr(exc)) from exc
    return info

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
    """return { dataset_id:header, ...} for every `dataset_id` for `instrument`."""
    log.verbose("Dumping datasets for", repr(instrument))
    ids = get_dataset_ids(context, instrument, datasets_since)
    return dict(get_dataset_headers_unlimited(context, ids))

def get_dataset_headers_unlimited(context, ids):
    """Generate (dataset_id, header) for `ids`,  potentially more
    `ids` than can be serviced with a single JSONRPC request.
     If there is a failure fetching parameters for dataset_id,
    `header` will be returned as a string / error message.
    """
    max_ids_per_rpc = get_server_info().get("max_headers_per_rpc", 500)
    for i in range(0, len(ids), max_ids_per_rpc):
        log.verbose("Dumping dataset headers", i , "of", len(ids), verbosity=20)
        id_slice = ids[i : i + max_ids_per_rpc]
        header_slice = get_dataset_headers_by_id(context, id_slice)
        for item in header_slice.items():
            yield item

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
    try:
        return S.push_remote_context(observatory, kind, key, context)
    except Exception as exc:
        raise CrdsRemoteContextError(
            "Server error setting pipeline context",
            (observatory, kind, key, context)) from exc

def get_remote_context(observatory, pipeline_name):
    """Get the name of the default context last pushed from `pipeline_name` and
    presumed to be operational.
    """
    try:
        return S.get_remote_context(observatory, pipeline_name)
    except Exception as exc:
        raise CrdsRemoteContextError(
            "Server error resolving context in use by pipeline",
            (observatory, pipeline_name)) from exc

# ==============================================================================

def jpoll_pull_messages(key, since_id=None):
    """Return a list of jpoll json message objects from the channel associated
    with `key` sent after datetime string `since` or since the last pull if
    since is not specified.
    """
    messages = []
    for msg in S.jpoll_pull_messages(key, since_id):
        decoded = utils.Struct(msg)
        decoded.data = html.unescape(decoded.data)
        messages.append(decoded)
    return messages

def jpoll_abort(key):
    """Request that the process writing to jpoll terminate on its next write."""
    return S.jpoll_abort(key)

# ==============================================================================

def get_system_versions(master_version, context=None):
    """Return the versions Struct associated with cal s/w master_version as
    defined by `context` which can be defined as "null", "none", or None to use
    the default context, or with any other valid date based context specifier.
    """
    return utils.Struct(S.get_system_versions(master_version, str(context)))

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
    obs = config.OBSERVATORY.get()
    if obs != "none":
        return obs
    return observatory_from_string(get_crds_server()) or \
           get_server_observatory() or \
           "jwst"

def observatory_from_string(string):
    """If an observatory name is in `string`, return it,  otherwise return None."""
    for observatory in constants.ALL_OBSERVATORIES:
        if observatory in string:
            return observatory
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

class FileCacher:
    """FileCacher gets remote files with simple names into a local cache."""
    def __init__(self, pipeline_context, ignore_cache=False, raise_exceptions=True):
        self.pipeline_context = pipeline_context
        self.observatory = self.observatory_from_context()
        self.ignore_cache = ignore_cache
        self.raise_exceptions = raise_exceptions
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
            if not os.path.exists(localpath):
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
        return localpaths, len(downloads), n_bytes

    def observatory_from_context(self):
        """Determine the observatory from `pipeline_context`,  based on name if possible."""
        import crds
        for observatory in constants.ALL_OBSERVATORIES:
            if observatory in self.pipeline_context:
                return observatory
        else:
            observatory = crds.get_pickled_mapping(self.pipeline_context).observatory  # reviewed
        return observatory

    def locate(self, name):
        """Return the standard CRDS cache location for file `name`."""
        return config.locate_file(name, observatory=self.observatory)

    def catalog_file_size(self, name):
        """Return the size of file `name` based on the server catalog."""
        return int(self.info_map[os.path.basename(name)]["size"])

    def download_files(self, downloads, localpaths):
        """Serial file-by-file download."""
        download_metadata = get_download_metadata()
        self.info_map = {}
        for filename in downloads:
            self.info_map[filename] = download_metadata.get(filename, "NOT FOUND unknown to server")
        if config.writable_cache_or_verbose("Readonly cache, skipping download of (first 5):", repr(downloads[:5]), verbosity=70):
            bytes_so_far = 0
            total_files = len(downloads)
            total_bytes = get_total_bytes(self.info_map)
            for nth_file, name in enumerate(downloads):
                try:
                    if "NOT FOUND" in self.info_map[name]:
                        raise CrdsDownloadError("file is not known to CRDS server.")
                    bytes, path = self.catalog_file_size(name), localpaths[name]
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
            raise CrdsDownloadError(
                "Error fetching data for", srepr(name),
                "at CRDS server", srepr(get_crds_server()),
                "with mode", srepr(config.get_download_mode()),
                ":", str(exc)) from exc
        except:  #  mainly for control-c,  catch it and throw it.
            self.remove_file(localpath)
            raise

    def remove_file(self, localpath):
        """Removes file at `localpath`."""
        log.verbose("Removing file", repr(localpath))
        try:
            os.remove(localpath)
        except Exception:
            log.verbose("Exception during file removal of", repr(localpath))

    def download_core(self, name, localpath):
        """Download and verify file `name` under context `pipeline_context` to `localpath`."""
        if config.get_download_plugin():
            self.plugin_download(name, localpath)
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
        plugin_cmd = plugin_cmd.replace("${FILE_SIZE}", self.info_map[filename]["size"])
        plugin_cmd = plugin_cmd.replace("${FILE_SHA1SUM}", self.info_map[filename]["sha1sum"])
        log.verbose("Running download plugin:", repr(plugin_cmd))
        status = os.WEXITSTATUS(os.system(plugin_cmd))
        if status != 0:
            if status == 2:
                raise KeyboardInterrupt("Interrupted plugin.")
            else:
                raise CrdsDownloadError(
                    "Plugin download fail status =", repr(status),
                    "with command:", srepr(plugin_cmd))

    def get_data_http(self, filename):
        """Yield the data returned from `filename` of `pipeline_context` in manageable chunks."""
        url = self.get_url(filename)
        try:
            infile = request.urlopen(url)
            file_size = utils.human_format_number(self.catalog_file_size(filename)).strip()
            stats = utils.TimingStats()
            data = infile.read(config.CRDS_DATA_CHUNK_SIZE)
            while data:
                stats.increment("bytes", len(data))
                status = stats.status("bytes")
                bytes_so_far = " ".join(status[0].split()[:-1])
                log.verbose("Transferred HTTP", repr(url), bytes_so_far, "/", file_size, "bytes at", status[1], verbosity=20)
                yield data
                data = infile.read(config.CRDS_DATA_CHUNK_SIZE)
        except Exception as exc:
            raise CrdsDownloadError(
                "Failed downloading", srepr(filename),
                "from url", srepr(url), ":", str(exc)) from exc
        finally:
            try:
                infile.close()
            except UnboundLocalError:   # maybe the open failed.
                pass

    def get_url(self, filename):
        """Return the URL used to fetch `filename` of `pipeline_context`."""
        return get_flex_uri(filename, self.observatory)

    def verify_file(self, filename, localpath):
        """Check that the size and checksum of downloaded `filename` match the server."""
        remote_info = self.info_map[filename]
        local_length = os.stat(localpath).st_size
        original_length = int(remote_info["size"])
        if original_length != local_length and config.get_length_flag():
            raise CrdsDownloadError(
                "downloaded file size", local_length,
                "does not match server size", original_length)
        if not config.get_checksum_flag():
            log.verbose("Skipping sha1sum with CRDS_DOWNLOAD_CHECKSUMS=False")
        elif remote_info["sha1sum"] not in ["", "none"]:
            original_sha1sum = remote_info["sha1sum"]
            local_sha1sum = utils.checksum(localpath)
            if original_sha1sum != local_sha1sum:
                raise CrdsDownloadError(
                    "downloaded file", srepr(filename),
                    "sha1sum", srepr(local_sha1sum),
                    "does not match server sha1sum", srepr(original_sha1sum))
        else:
            log.verbose("Skipping sha1sum check since server doesn't know it.")

# ==============================================================================

def dump_mappings3(pipeline_context, ignore_cache=False, mappings=None, raise_exceptions=True):
    """Given a `pipeline_context`, determine the closure of CRDS mappings for it and
    cache them on the local file system.

    If mappings is not None,  sync exactly that list of mapping names,  not their closures.

    Returns:   { mapping_basename :   mapping_local_filepath ... }, downloads, bytes
    """
    assert isinstance(ignore_cache, bool)
    if mappings is None:
        mappings = get_mapping_names(pipeline_context)
    mappings = list(reversed(sorted(set(mappings))))
    return FileCacher(pipeline_context, ignore_cache, raise_exceptions).get_local_files(mappings)

def dump_mappings(*args, **keys):
    """See dump_mappings3.

    Returns { mapping_basename :   mapping_local_filepath ... }
    """
    return dump_mappings3(*args, **keys)[0]

def dump_references3(pipeline_context, baserefs=None, ignore_cache=False, raise_exceptions=True):
    """Given a pipeline `pipeline_context` and list of `baserefs` reference
    file basenames,  obtain the set of reference files and cache them on the
    local file system.

    If `basrefs` is None,  sync the closure of references referred to by `pipeline_context`.

    Returns:  { ref_basename :  reference_local_path }, downloads, bytes
    """
    if baserefs is None:
        baserefs = get_reference_names(pipeline_context)
    baserefs = list(baserefs)
    for refname in baserefs:
        if "NOT FOUND" in refname:
            log.verbose("Skipping " + srepr(refname), verbosity=70)
            baserefs.remove(refname)
    baserefs = sorted(set(baserefs))
    return FileCacher(pipeline_context, ignore_cache, raise_exceptions).get_local_files(baserefs)

def dump_references(*args, **keys):
    """See dump_references3.

    Returns { ref_basename :  reference_local_path }
    """
    return dump_references3(*args, **keys)[0]

def dump_files(pipeline_context=None, files=None, ignore_cache=False, raise_exceptions=True):
    """Unified interface to dump any file in `files`, mapping or reference.

    Returns localpaths,  downloads count,  bytes downloaded
    """
    if pipeline_context is None:
        pipeline_context = get_default_context()
    if files is None:
        files = get_mapping_names(pipeline_context)
    mappings = [ os.path.basename(name) for name in files if config.is_mapping(name) ]
    references = [ os.path.basename(name) for name in files if not config.is_mapping(name) ]
    if mappings:
        m_paths, m_downloads, m_bytes = dump_mappings3(
            pipeline_context, mappings=mappings, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions)
    else:
        m_paths, m_downloads, m_bytes = {}, 0, 0
    if references:
        r_paths, r_downloads, r_bytes = dump_references3(
            pipeline_context, baserefs=references, ignore_cache=ignore_cache, raise_exceptions=raise_exceptions)
    else:
        r_paths, r_downloads, r_bytes = {}, 0, 0
    return dict(list(m_paths.items())+list(r_paths.items())), m_downloads + r_downloads, m_bytes + r_bytes

# =====================================================================================================

def cache_best_references(pipeline_context, header, ignore_cache=False, reftypes=None):
    """Given the FITS `header` of a dataset and a `pipeline_context`, determine
    the best set of reference files for processing the dataset,  cache them
    locally,  and return the mapping  { filekind : local_file_path }.
    """
    best_refs = get_best_references(pipeline_context, header, reftypes=reftypes)
    local_paths = cache_references(pipeline_context, best_refs, ignore_cache)
    return local_paths

def cache_references(pipeline_context, bestrefs, ignore_cache=False):
    """Given a CRDS context `pipeline_context` and `bestrefs` dictionary, download missing
    reference files and cache them on the local file system.

    bestrefs    { reference_keyword :  reference_basename }

    Returns:   { reference_keyword :  reference_local_filepath ... }
    """
    wanted = _get_cache_filelist_and_report_errors(bestrefs)

    if config.S3_RETURN_URI:
        localrefs = {name: get_flex_uri(name) for name in wanted}
    else:
        localrefs = FileCacher(pipeline_context, ignore_cache, raise_exceptions=False).get_local_files(wanted)[0]

    refs = _squash_unicode_in_bestrefs(bestrefs, localrefs)

    return refs

def _get_cache_filelist_and_report_errors(bestrefs):
    """Compute the list of files to download based on the `bestrefs` dictionary,
    skimming off and reporting errors, and raising an exception on the last error seen.

    Return the list of files to download,  collapsing complex return types like tuples
    and dictionaries into a list of simple filenames.
    """
    wanted = []
    last_error = None
    for filetype, refname in bestrefs.items():
        if isinstance(refname, tuple):
            wanted.extend(list(refname))
        elif isinstance(refname, dict):
            wanted.extend(refname.values())
        elif isinstance(refname, str):
            if "NOT FOUND" in refname:
                if "n/a" in refname.lower():
                    log.verbose("Reference type", srepr(filetype),
                                "NOT FOUND.  Skipping reference caching/download.", verbosity=70)
                else:
                    last_error = CrdsLookupError(
                        "Error determining best reference for",
                        srepr(filetype), " = ", str(refname)[len("NOT FOUND"):])
                    log.error(str(last_error))
            else:
                log.verbose("Reference type", srepr(filetype), "defined as", srepr(refname))
                wanted.append(refname)
        else:
            last_error = CrdsLookupError(
                "Unhandled bestrefs return value type for", srepr(filetype))
            log.error(str(last_error))
    if last_error is not None:
        raise last_error
    return wanted

def _squash_unicode_in_bestrefs(bestrefs, localrefs):
    """Given bestrefs dictionariesy `bestrefs` and `localrefs`, make sure
    there are no unicode strings anywhere in the keys or complex
    values.
    """
    refs = {}
    for filetype, refname in bestrefs.items():
        if isinstance(refname, tuple):
            refs[str(filetype)] = tuple([str(localrefs[name]) for name in refname])
        elif isinstance(refname, dict):
            refs[str(filetype)] = { name : str(localrefs[name]) for name in refname }
        elif isinstance(refname, str):
            if "NOT FOUND" in refname:
                refs[str(filetype)] = str(refname)
            else:
                refs[str(filetype)] = str(localrefs[refname])
        else:  # can't really get here.
            raise CrdsLookupError(
                "Unhandled bestrefs return value type for", srepr(filetype))
    return refs

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
    import crds
    dump_mappings(context, ignore_cache=ignore_cache)
    ctx = crds.get_pickled_mapping(context)   # reviewed
    return ctx.get_minimum_header(dataset)
