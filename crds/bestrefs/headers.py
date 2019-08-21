"""This module is a command line script which handles comparing the best
reference recommendations for a particular context and dataset files.

For more details on the several modes of operations and command line parameters browse the source or run:

% crds bestrefs --help
"""
import json
import gc

# ===================================================================

import crds
from crds.core import log, utils, heavy_client
from crds.core.exceptions import CrdsError
from crds import data_file, matches
from crds.client import api

import pickle

# ===================================================================

MIN_DATE = "1900-01-01 00:00:00"
MAX_DATE = "9999-01-01 23:59:59"

# ===================================================================
# There's a problem with using CDBS as a gold standard in getting consistent results between
# DADSOPS DB (fast) and running command line OPUS bestrefs (slow but definitive).   This is kludged
# around here with a two tiered scheme for getting dataset headers:  first load headers from a primary
# source:  files or DADSOPS.  Next update headers from a pickle file computed "elsewhere".   Elsewhere
# is a script that ssh'es to a DMS machine for each dataset and runs OPUS bestrefs,  then eventually
# saves a pickle.
# It is also possible to run solely off of a pickle file(s) (which decouples from the database,  useful for
# both consistency/control and to take a load off the database.)


class HeaderGenerator:
    """Generic source for lookup parameters and historical comparison results."""

    def __init__(self, context, sources, datasets_since):
        self.context = context
        self.observatory = None if context is None else utils.file_to_observatory(context)
        self.sources = sources
        self.headers = {}
        self._datasets_since = datasets_since

    def __iter__(self):
        """Return the sources from self with EXPTIME >= self.datasets_since."""
        for source in sorted(self.sources):
            with log.error_on_exception("Failed loading source", repr(source),
                                        "from", repr(self.__class__.__name__)):
                instrument = utils.header_to_instrument(self.header(source))
                exptime = matches.get_exptime(self.header(source))
                since = self.datasets_since(instrument)
                # since == None when no command line argument given.
                if since is None or exptime >= since:
                    yield source
                else:
                    log.verbose("Dropping source", repr(source),
                                "with EXPTIME =", repr(exptime),
                                "< --datasets-since =", repr(since))

    def datasets_since(self, instrument):
        """Return the earliest dataset processed cut-off date for `instrument`.

        If a universal since-date is in effect,  just return it.

        If the since-date varies by instrument, but is not defined for `instrument`, return
        a value equivalent to the end-of-time since it means that no references for `instrument`
        were identified by --datsets-since=auto.
        """
        if isinstance(self._datasets_since, dict):
            return self._datasets_since.get(instrument.lower(),  MIN_DATE)
        else:
            return self._datasets_since

    def header(self, source):
        """Return the full header corresponding to `source`.   If header is a string, raise an exception."""
        header = self._header(source)
        if isinstance(header, str):
            raise CrdsError("Failed to fetch header for " + repr(source) + ": " + repr(header))
        else:
            return dict(header)

    def _header(self, source):
        """Return the full header corresponding to `source`.   Source is a dataset id or filename."""
        return self.headers[source]

    def get_lookup_parameters(self, source):
        """Return the parameters corresponding to `source` used to drive a best references lookup."""
        return add_instrument(self.header(source))

    def get_old_bestrefs(self, source):
        """Return the historical best references corresponding to `source`.  Always define old bestrefs
        in terms of filekind/typename rather than in terms of FITS keyword.
        """
        header = add_instrument(self.header(source))
        instrument = utils.header_to_instrument(header)
        pmap = crds.get_pickled_mapping(self.context)
        result = {}
        for filekind in pmap.get_imap(instrument).selections:
            keyword = pmap.locate.filekind_to_keyword(filekind)
            filekind = filekind.upper()
            try:
                result[filekind] = header[keyword]
            except KeyError:
                result[filekind] = header.get(filekind, "UNDEFINED")
        return result

    def save_pickle(self, outpath, only_ids=None):
        """Write out headers to `outpath` file which can be a Python pickle or .json"""
        if only_ids is None:
            only_hdrs = self.headers
        else:
            only_hdrs = {dataset_id: hdr for (dataset_id, hdr) in self.headers.items() if dataset_id in only_ids}
        log.info("Writing all headers to", repr(outpath))
        if outpath.endswith(".json"):
            with open(outpath, "w+") as pick:
                for dataset, header in sorted(only_hdrs.items()):
                    pick.write(json.dumps({dataset: header}) + "\n")
        elif outpath.endswith(".pkl"):
            with open(outpath, "wb+") as pick:
                pickle.dump(only_hdrs, pick)
        log.info("Done writing", repr(outpath))

    def update_headers(self, headers2, only_ids=None):
        """Incorporate `headers2` updated values into `self.headers`.  Since `headers2` may be incomplete,
        do param-by-param update.   Nominally,  this is to add OPUS bestrefs corrections (definitive) to DADSOPS
        database bestrefs (fast but not definitive).
        """
        if only_ids is None:
            only_ids = headers2.keys()

        items = headers2.items()
        for dataset_id, header in items:
            if isinstance(header, str):
                log.warning("Skipping bad dataset", dataset_id, ":", headers2[dataset_id])
                del headers2[dataset_id]

        # Munge for consistent case and value formatting regardless of source
        headers2 = {dataset_id:
                    {key.upper(): bestrefs_condition(val) for (key, val) in headers2[dataset_id].items()}
                    for dataset_id in headers2 if dataset_id in only_ids}

        # replace param-by-param,  not id-by-id, since headers2[id] may be partial
        for dataset_id in headers2:
            if dataset_id not in self.headers:
                self.headers[dataset_id] = {}
            header1, header2 = self.headers[dataset_id], headers2[dataset_id]
            for key in header2:
                if key not in header1 or header1[key] != header2[key]:
                    header1[key] = header2[key]

    def handle_updates(self, all_updates):
        """Base handle_updates() updates the loaded headers with the computed bestrefs for use
        with --save-pickle.
        """
        for dataset in sorted(all_updates):
            updates = all_updates[dataset]
            if updates:
                log.verbose("-" * 120)
                for update in sorted(updates):
                    new_ref = update.new_reference.upper()
                    if new_ref != "N/A":
                        new_ref = new_ref.lower()
                    self.headers[dataset][update.filekind.upper()] = new_ref


def bestrefs_condition(value):
    """Condition header keyword value to normal form,  converting NOT FOUND N/A to N/A."""
    val = utils.condition_value(value)
    if val == "NOT FOUND N/A":
        val = "N/A"
    return val

# ===================================================================

# FileHeaderGenerator uses a deferred header loading scheme which incrementally reads each header
# from a file as processing is going on via header().   The "pickle correction" scheme works by
# pre-loading the FileHeaderGenerator with pickled headers...  which prevents the file from ever being
# accessed (except possibly to update the headers).


class FileHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and old bestrefs from dataset files."""

    def _header(self, filename):
        """Get the best references recommendations recorded in the header of file `dataset`."""
        gc.collect()
        if filename not in self.headers:
            self.headers[filename] = data_file.get_free_header(filename, (), None, self.observatory)
        return self.headers[filename]

    def handle_updates(self, all_updates):
        """Write best reference updates back to dataset file headers."""
        super(FileHeaderGenerator, self).handle_updates(all_updates)
        for source in sorted(all_updates):
            updates = all_updates[source]
            if updates:
                log.verbose("-" * 120)
                update_file_bestrefs(self.context, source, updates)

# ===================================================================


class DatasetHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from dataset ids.   Server/DB bases"""

    def __init__(self, context, datasets, datasets_since):
        """"Contact the CRDS server and get headers for the list of `datasets` ids with respect to `context`."""
        super(DatasetHeaderGenerator, self).__init__(context, datasets, datasets_since)
        server = api.get_crds_server()
        log.info("Dumping dataset parameters from CRDS server at", repr(server), "for", repr(datasets))
        self.headers = api.get_dataset_headers_by_id(context, datasets)
        log.info("Dumped", len(self.headers), "of", len(datasets), "datasets from CRDS server at", repr(server))

        # every command line id should correspond to 1 or more headers
        for source in self.sources:
            if self.matching_two_part_id(source) not in self.headers.keys():
                log.warning("Dataset", repr(source), "isn't represented by downloaded parameters.")

        # Process according to downloaded 2-part ids,  not command line ids.
        self.sources = sorted(self.headers.keys())

    def matching_two_part_id(self, source):
        """Convert any command line dataset id into it's matching two part id.

        matching_two_part_id(<association>)                  -->  <association>  : <first_member>

        matching_two_part_id(<association>:<member>)         -->  <association>  : <member>
        matching_two_part_id(<unassociated>)                 -->  <unassociated> : <unassociated>
        matching_two_part_id(<unassociated>:<unassociated>)  -->  <unassociated> : <unassociated>
        """
        parts = [_normalize_jwst_id_part(part) for part in source.split(":")]
        assert 1 <= len(parts) <= 2, "Invalid dataset id " + repr(source)
        try:    # when specifying datasets with 1-part id, return first of "associated ids"
                # when specifying datasets with 2-part id,
            if len(parts) == 1:
                return sorted(dataset_id for dataset_id in self.headers if parts[0] in dataset_id)[0]
            else:
                return source
        except Exception:
            return source

def _normalize_jwst_id_part(part):
    """Converts jw88600071001_02101_00001_nrs1  --> jw88600071001_02101_00001.nrs.   The former is
    common notation for most dataset usages,  the latter is the official form for the web API to
    the archive parameter service for JWST.
    """
    if "_" in part and "." not in part:  # not HST and common JWST parlance
        bits = part.split("_")
        fileSetName = "_".join(bits[:-1])
        detector = bits[-1]
        return fileSetName + "." + detector   # Formal archive API
    else:
        return part

class InstrumentHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of instrument names.  Server/DB based."""

    def __init__(self, context, instruments, datasets_since, save_pickles, server_info):
        """"Contact the CRDS server and get headers for the list of `instruments` names with respect to `context`."""
        super(InstrumentHeaderGenerator, self).__init__(context, [], datasets_since)
        self.instruments = instruments
        self.sources = self.determine_source_ids()
        self.save_pickles = save_pickles
        try:
            self.segment_size = server_info.max_headers_per_rpc
        except Exception:
            self.segment_size = 5000

    def determine_source_ids(self):
        """Return the dataset ids for all instruments."""
        server = api.get_crds_server()
        source_ids = []
        for instrument in self.instruments:
            since_date = self.datasets_since(instrument)
            if since_date:
                log.info("Dumping dataset parameters for", repr(instrument), "from CRDS server at", repr(server),
                         "since", repr(since_date))
            else:
                log.info("Dumping dataset parameters for", repr(instrument), "from CRDS server at", repr(server))
            instr_ids = api.get_dataset_ids(self.context, instrument, self.datasets_since(instrument))
            log.info("Downloaded ", len(instr_ids), "dataset ids for", repr(instrument), "since", repr(since_date))
            source_ids.extend(instr_ids)
        return sorted(source_ids)  # sort is needed to match generic __iter__() sort. assumes instruments don't shuffle

    def _header(self, source):
        """Return the header associated with dataset id `source`,  fetching the surround segment of
        headers if `source` is not already in the cached set of headers.
        """
        if source not in self.headers:
            self.fetch_source_segment(source)
        return self.headers[source]

    def fetch_source_segment(self, source):
        """Return the segment of dataset ids which surrounds id `source`."""
        try:
            index = self.sources.index(source) // self.segment_size
        except ValueError as exc:
            raise CrdsError("Unknown dataset id " + repr(source)) from exc
        lower = index * self.segment_size
        upper = (index + 1) * self.segment_size
        segment_ids = self.sources[lower:upper]
        log.verbose("Dumping", len(segment_ids), "datasets from indices", lower, "to",
                    lower + len(segment_ids), verbosity=20)
        dumped_headers = api.get_dataset_headers_by_id(self.context, segment_ids)
        log.verbose("Dumped", len(dumped_headers), "datasets", verbosity=20)
        if self.save_pickles:  # keep all headers,  causes memory problems with multiple instruments on ~8G ram.
            self.headers.update(dumped_headers)
        else:  # conserve memory by keeping only the last N headers
            self.headers = dumped_headers


class PickleHeaderGenerator(HeaderGenerator):
    """Generates lookup parameters and historical best references from a list of pickle files (or .json files)
    using successive updates to sets of header dictionaries.  Trailing pickles override leading pickles.
    """

    def __init__(self, context, pickles, datasets_since, only_ids=None):
        """"Contact the CRDS server and get headers for the list of `datasets` ids with respect to `context`."""
        super(PickleHeaderGenerator, self).__init__(context, pickles, datasets_since)
        for pickle in pickles:
            log.info("Loading file", repr(pickle))
            pick_headers = load_bestrefs_headers(pickle)
            if not self.headers:
                log.info("Loaded", len(pick_headers), "datasets from file", repr(pickle),
                         "completely replacing existing headers.")
                self.headers.update(pick_headers)   # replace all of dataset_id
            else:  # OPUS bestrefs don't include original matching parameters,  so full replacement doesn't work.
                log.info("Loaded", len(pick_headers), "datasets from file", repr(pickle),
                         "augmenting existing headers.")
                self.update_headers(pick_headers, only_ids=only_ids)
        self.sources = only_ids or self.headers.keys()

# ============================================================================

def load_bestrefs_headers(path):
    """Given `path` to a serialization file,  load  {dataset_id : header, ...}.
    Supports .pkl and .json.

    For easier editing and syntax error precision,  .json files are stored as
    one header per line.

    Also used by server to load mock parameters.
    """
    if path.endswith(".json"):
        headers = {}
        try:
            with open(path, "r") as pick:
                for line in pick:
                    if line.strip():
                        headers.update(json.loads(line))
        except ValueError:
            with open(path, "r") as pick:
                headers = json.load(pick)
    elif path.endswith(".pkl"):
        with open(path, "rb") as pick:
            headers = pickle.load(pick)
    else:
        raise ValueError("Valid serialization formats are .json and .pkl")
    return headers

def add_instrument(header):
    """Add INSTRUME keyword."""
    instrument = utils.header_to_instrument(header)
    header["INSTRUME"] = instrument
    header["META.INSTRUMENT.NAME"] = instrument
    return header

def update_file_bestrefs(context, dataset, updates):
    """Update the header of `dataset` with best reference recommendations
    `bestrefs` determined by context named `pmap`.
    """
    if not updates:
        return

    version_info = heavy_client.version_info()
    instrument = updates[0].instrument
    locator = utils.instrument_to_locator(instrument)
    prefix = locator.get_env_prefix(instrument)

    with data_file.fits_open(dataset, mode="update", do_not_scale_image_data=True, checksum=False) as hdulist:

        def set_key(keyword, value):
            """Set a single keyword value with logging,  bound to outer-scope hdulist."""
            log.verbose("Setting", repr(dataset), keyword, "=", value)
            hdulist[0].header[keyword] = value

        set_key("CRDS_CTX", context)
        set_key("CRDS_VER", version_info)

        for update in sorted(updates):
            new_ref = update.new_reference.upper()
            if new_ref != "N/A":
                new_ref = (prefix + new_ref).lower()
            keyword = locator.filekind_to_keyword(update.filekind)
            set_key(keyword, new_ref)

        # This is a workaround for a bug in astropy.io.fits handling of
        # FITS updates that are header-only and extend the header.
        # This statement appears to do nothing but *is not* pointless.
        for hdu in hdulist:
            hdu.data
