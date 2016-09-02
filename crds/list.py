"""This module is a command line script which lists the reference and/or
mapping files associated with the specified contexts by consulting the CRDS
server.   More generally it's for printing out information on CRDS files.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys

import crds
from crds import cmdline, rmap, log, config, heavy_client, python23, data_file
from crds.client import api

class ListScript(cmdline.ContextsScript):
    """Command line script for listing a variety of information about CRDS."""

    description = """crds.list prints out a variety of information about CRDS configuration, the
cache, reference and mapping files, default context names, and dataset headers
and ids used for CRDS reprocessing recommendations.
    """
        
    epilog = """
    General categories of information driven by switches include:

    0. Overall CRDS configuration
    1. CRDS server file lists
    2. CRDS cache file lists and paths
    3. Cached file contents or headers
    4. CRDS reprocessing dataset ids and parameters
    5. Simple listing of default contexts

    --------------------------------------------------------------------------
    0. Configuration information governing the behavior of CRDS can be dumped:

    % python -m crds.list --config
    CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
    CRDS Environment
        CRDS_ALLOW_BAD_PARKEY_VALUES = 'false'
        CRDS_ALLOW_BAD_REFERENCES = 'false'
        CRDS_ALLOW_BAD_RULES = 'false'
        CRDS_ALLOW_BAD_USEAFTER = 'false'
        CRDS_ALLOW_SCHEMA_VIOLATIONS = 'false'
        CRDS_DOWNLOAD_MODE = 'http'
        CRDS_FITS_IGNORE_MISSING_END = 'false'
        CRDS_FITS_VERIFY_CHECKSUM = 'false'
        CRDS_IGNORE_MAPPING_CHECKSUM = 'false'
        CRDS_MODE = 'auto'
        CRDS_PATH = '/Users/homer/crds_cache_test'
        CRDS_READONLY_CACHE = '0'
        CRDS_SERVER_URL = 'https://hst-crds-test.stsci.edu'
    CRDS Client Config
        cache_subdir_mode = 'instrument'
        crds = "<module 'crds' from '/Users/homer/work/workspace_crds/CRDS/crds/__init__.py'>"
        effective_context = 'hst_0462.pmap'
        readonly_cache = False
        server_url = 'https://hst-crds-test.stsci.edu'
        version = '7.0.4, master, 1f51071'
    CRDS Actual Paths
        config root = '/Users/homer/crds_cache_test/config/hst'
        mapping root = '/Users/homer/crds_cache_test/mappings/hst'
        reference root = '/Users/homer/crds_cache_test/references/hst'
    CRDS Server Info
        connected = True
        effective_mode = 'local'
        last_synced = '2016-09-01 12:16:28.686153'
        mapping_url = {'hst': 'https://hst-crds-test.stsci.edu/unchecked_get/mappings/hst/'}
        observatory = 'hst'
        operational_context = 'hst_0462.pmap'
        reference_url = {'hst': 'https://hst-crds-test.stsci.edu/unchecked_get/references/hst/'}
        status = 'server'
    Calibration Environment
        none
    Python Environment
    Python Executable = '/Users/homer/anaconda/bin/python'
    Python Version = '3.5.2.final.0'

    --------------------------------------------------------------------------
   1. Files known by the CRDS server to belong to specified contexts can be listed
    even if the files are not installed in a local CRDS Cache.

    Contexts to list can be specified in a variety of ways:
    
    % python -m crds.list  --contexts hst_0001.pmap hst_0002.pmap --references
    vb41935ij_bia.fits 
    vb41935kj_bia.fits 
    ...
    
    % python -m crds.list --range 1:2 --references
    vb41935lj_bia.fits 
    vb41935oj_bia.fits
    ...
    
    % python -m crds.list --all --mappings
    hst.pmap 
    hst_0001.pmap 
    hst_0002.pmap 
    hst_acs.imap 
    hst_acs_0001.imap 
    hst_acs_0002.imap 
    hst_acs_atodtab.rmap 
    ...

    --references, --mappings, or both can be listed.
    
    --------------------------------------------------------------------------
    2. Locally cached files (files already synced to your computer) can be listed:
    
    % python -m crds.list --cached-mappings
    ...

    % python -m crds.list --cached-references
    ...

    In both cases adding --full-path prints the path of the file within the CRDS cache.
    These are ultimately simple directory listings which ignore context specifiers.

    --------------------------------------------------------------------------
    3. The contents of cached mappings or references (header only) can be printed to stdout like this:

    % python -m crds.list --contexts jwst-fgs-linearity-edit jwst-nirspec-linearity-edit --cat --add-filename | grep parkey
    CRDS - INFO - Symbolic context 'jwst-fgs-linearity-edit' resolves to 'jwst_fgs_linearity_0008.rmap'
    CRDS - INFO - Symbolic context 'jwst-nirspec-linearity-edit' resolves to 'jwst_nirspec_linearity_0009.rmap'
    /cache/path/mappings/jwst/jwst_fgs_linearity_0008.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
    /cache/path/mappings/jwst/jwst_nirspec_linearity_0009.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),

    this prints the contents of the specified rmaps.

    References need to be catted explicitly by name,  but the list can come from the above methods of listing references:

    % python -m crds.list --cat jwst_nirspec_dark_0036.fits
    CRDS - INFO - Symbolic context 'jwst-operational' resolves to 'jwst_0167.pmap'
    ##########################################################################################
    File:  '/grp/crds/jwst/references/jwst/jwst_nirspec_dark_0036.fits'
    ##########################################################################################
    {'A1_COL_C': '8.9600000e+002',
    'A1_CONF1': '2.1846000e+004',
    ...
    }

   --------------------------------------------------------------------------
   4. Information about the dataset IDs and their associated parameters used
   for CRDS reprocessing can be printed:

    % python -m crds.list --dataset-headers jcl403010 --first-id --minimize-header
    CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
    CRDS - INFO - Dataset pars for 'JCL403010:JCL403ECQ' with respect to 'hst_0462.pmap':
    {'APERTURE': 'WFC1',
     'ATODCORR': 'OMIT',
     'BIASCORR': 'COMPLETE',
     'CCDAMP': 'ABCD',
     'CCDCHIP': '-999.0',
     'CCDGAIN': '2.0',
     'CRCORR': 'OMIT',
     'DARKCORR': 'COMPLETE',
     'DATE-OBS': '2016-02-20',
     'DETECTOR': 'WFC',
     'DQICORR': 'COMPLETE',
     'DRIZCORR': 'COMPLETE',
     'FILTER1': 'CLEAR1L',
     'FILTER2': 'F814W',
     'FLASHCUR': 'LOW',
     'FLATCORR': 'COMPLETE',
     'FLSHCORR': 'OMIT',
     'FW1OFFST': '0.0',
     'FW2OFFST': '0.0',
     'FWSOFFST': '0.0',
     'GLINCORR': 'UNDEFINED',
     'INSTRUME': 'ACS',
     'LTV1': '0.0',
     'LTV2': '0.0',
     'NAXIS1': '4144.0',
     'NAXIS2': '4136.0',
     'OBSTYPE': 'IMAGING',
     'PCTECORR': 'UNDEFINED',
     'PHOTCORR': 'COMPLETE',
     'RPTCORR': 'UNDEFINED',
     'SHADCORR': 'OMIT',
     'SHUTRPOS': 'A',
     'TIME-OBS': '17:32:29.666665',
     'XCORNER': '0.0',
     'YCORNER': '0.0',
     'dataset_id': 'JCL403010:JCL403ECQ'}

    Sometimes it's desirable to know the individual exposures CRDS associates with a product id:

    % python -m crds.list --dataset-headers jcl403010 --id-expansions-only
    CRDS - INFO - Symbolic context 'hst-operational' resolves to 'hst_0462.pmap'
    JCL403010:JCL403ECQ hst_0462.pmap
    JCL403010:JCL403EEQ hst_0462.pmap
    JCL403010:JCL403EGQ hst_0462.pmap
    JCL403010:JCL403EIQ hst_0462.pmap
    JCL403010:JCL403EKQ hst_0462.pmap
    JCL403010:JCL403EMQ hst_0462.pmap
    JCL403010:JCL403EOQ hst_0462.pmap
    JCL403010:JCL403EQQ hst_0462.pmap
    JCL403010:JCL403ESQ hst_0462.pmap
    JCL403010:JCL403EUQ hst_0462.pmap

    Headers available can possibly vary by CRDS context and will be dumped for
    every specified or implicit context.  Generally the default context is
    sufficient.  Often all exposures of an association have identical
    parameters but CRDS is designed so that this does not have to be the case.

    These dataset header services require setting CRDS_SERVER_URL to a valid CRDS server to
    provide a source for the headers.

   --------------------------------------------------------------------------
    5. Information about the default context can be printed.  There are two variations and a subtle distinction:

    % python m crds.list --operational-context
    CRDS - INFO - Symbolic context 'jwst-operational' resolves to 'jwst_0204.pmap'
    jwst_0204.pmap 

    lists the context which has been *commanded* as default on the CRDS server.

    While:

    % python -m crds.list --remote-context jwst-ops-pipeline
    CRDS - INFO - Symbolic context 'jwst-operational' resolves to 'jwst_0204.pmap'
    jwst_0101.pmap
    
    lists the context which is *in actual use* in the associated archive pipeline as reported by
    a cache sync echo.

    During the interval between commanding a new default on the CRDS server and syncing the pipeline
    CRDS cache,  the commanded and actual pipeline contexts can differ.
    """
    
    def add_args(self):
        """Add switches unique to crds.list."""

        self.add_argument('--references', action='store_true', dest="list_references",
            help='print names of reference files referred to by contexts')
        self.add_argument('--mappings', action='store_true', dest="list_mappings",
            help='print names of mapping files referred to by contexts')

        self.add_argument("--cached-references", action="store_true",
            help="print the paths of all references in the local cache.")
        self.add_argument("--cached-mappings", action="store_true",
            help="print the paths of all mappings in the local cache.")
        self.add_argument("--full-path", action="store_true",
            help="print the full paths of files for --cached-references and --cached-mappings.")

        self.add_argument("--dataset-ids-for-instruments", nargs="+", dest="dataset_ids", default=None, metavar="INSTRUMENTS",
            help="print the dataset ids known to CRDS associated for the specified instruments.")
        self.add_argument("--dataset-headers", nargs="+", dest="dataset_headers", default=None, metavar="IDS",
            help="print matching parameters for the specified dataset ids.")
        self.add_argument("--id-expansions-only", action="store_true", dest="id_expansions_only",
            help="print out only the <product>:<exposure> expansion associated with the specified --dataset-headers ids.")
        self.add_argument("--first-id-expansion-only", action="store_true", dest="first_id_expansion_only",
            help="print out only the first exposure ID (header or expanded) associated with a particular product ID.")
        self.add_argument("--minimize-headers", action="store_true", dest="minimize_headers",
            help="print out only header parameters required by a particular CRDS context.")

        self.add_argument("--config", action="store_true", dest="config",
            help="print CRDS configuration information.")

        self.add_argument("--cat", nargs="*", dest="cat", metavar="FILES", default=None,
            help="print the text of the specified mapping files.")
        self.add_argument("--keywords", nargs="+", 
            help="limited list of keywords to be catted from reference headers.")
        self.add_argument("--add-filenames", action="store_true",
            help="prefix each line of a cat'ed file with the filename.")

        self.add_argument("--operational-context", action="store_true", dest="operational_context",
            help="print the name of the operational context on the central CRDS server.")
        self.add_argument("--remote-context", type=str, metavar="PIPELINE", 
            help="print the name of the context reported as in use by the specified pipeline.")

        self.add_argument("--required-parkeys", action="store_true",
            help="print the names of the parkeys required to compute bestrefs for the specified mappings.")

        super(ListScript, self).add_args()
        
    def main(self):
        """List files."""
        if self.args.list_references:
            self.list_references()
        if self.args.list_mappings:
            self.list_mappings()
        if self.args.dataset_ids:
            self.list_dataset_ids()
        if self.args.dataset_headers:
            self.list_dataset_headers()
        if self.args.cached_references:
            self.list_cached_references()
        if self.args.cached_mappings:
            self.list_cached_mappings()
        if self.args.config:
            self.list_config()
        if self.args.cat is not None:
            self.cat_files()
        if self.args.operational_context:
            print(self.default_context)
        if self.args.remote_context:
            print(self.remote_context)
        if self.args.required_parkeys:
            self.list_required_parkeys()

    @property
    def remote_context(self):
        """Print the name of the context in use at pipeline `self.args.remote_context`
        as recorded on the server after being pushed by the crds.sync tool in the pipeline.
        """
        self.require_server_connection()
        return api.get_remote_context(self.observatory, self.args.remote_context)

    def cat_files(self):
        """Print out the files listed after --cat"""
        self.args.files = self.args.cat   # determine observatory from --cat files.

        # --cat files...   specifying *no* files still triggers --cat logic
        # XXXX not allowed --files files... @-files are permitted, containing file lists
        # --contexts context-specifiers [including --all --last --range...]
        # context specifiers can be symbolic and will be resolved.
        catted_files = self.args.cat + self.contexts
        if not self.args.contexts or (self.default_context not in self.args.contexts):
            try:
                catted_files.remove(self.default_context)
            except Exception:
                pass

        # This could be expanded to include the closure of mappings or references
        for name in catted_files:
            path = self.locate_file(name)
            path = self._cat_banner(path)
            if config.is_reference(path):
                self._cat_header(path)
            else:
                self._cat_text(path)

    def _cat_banner(self, name):
        """Print a banner for --cat for `name` and return the filepath of `name`."""
        print("#"*120)
        path = os.path.abspath(name)
        print("File: ", repr(path))
        print("#"*120)
        return path

    def _cat_text(self, path):
        """Dump out the contexts of a text file."""
        with open(path) as pfile:
            self._print_lines(path, pfile.readlines())
            
    def _cat_header(self, path):
        """Dump out the header associated with a reference file."""
        old = config.ALLOW_SCHEMA_VIOLATIONS.set(True)
        header = data_file.get_unconditioned_header(path)
        if self.args.keywords:
            header2 = {}
            for keyword in header:
                for substr in self.args.keywords:
                    if substr in keyword:
                        header2[keyword] = header[keyword]
        else:
            header2 = header
        self._print_lines(path, str(log.PP(header2)).splitlines())
        config.ALLOW_SCHEMA_VIOLATIONS.set(old)

    def _print_lines(self, path, lines):
        """Print `lines` to stdout,  optionally prefixing each line with `path`."""
        for line in lines:
            if self.args.add_filenames:
                print(path + ":", line.rstrip())
            else:
                print(line.rstrip())

    def list_references(self):
        """Consult the server and print the names of all references associated with
        the given contexts.
        """
        references = [ rmap.locate_file(filename, self.observatory) if self.args.full_path else filename
                       for filename in self.get_context_references() ]
        _print_list(references)
    
    def list_mappings(self):
        """Consult the server and print the names of all CRDS mappings associated 
        with the given contexts.
        """
        mappings = [ rmap.locate_file(filename, self.observatory) if self.args.full_path else filename
                       for filename in self.get_context_mappings() ]
        _print_list(mappings)
    
    def list_cached_mappings(self):
        """List the mapping paths in the local cache."""
        _print_list(rmap.list_mappings("*.*map", self.observatory, full_path=self.args.full_path))
        
    def list_cached_references(self):
        """List the reference paths in the local cache."""
        _print_list(rmap.list_references("*", self.observatory, full_path=self.args.full_path))
        
    def list_dataset_headers(self):
        """List dataset header info for self.args.dataset_headers with respect to self.args.context"""
        for context in self.contexts:
            with log.error_on_exception("Failed fetching dataset parameters with repect to", repr(context), 
                                        "for", repr(self.args.dataset_headers)):
                pars = api.get_dataset_headers_by_id(context, self.args.dataset_headers)
                pmap = crds.get_cached_mapping(context)
                for requested_id in self.args.dataset_headers:
                    for returned_id in sorted(pars.keys()):
                        if requested_id.upper() in returned_id.upper():
                            header = pars[returned_id]
                            if isinstance(header, python23.string_types):
                                log.error("No header for", repr(returned_id), ":", repr(header)) # header is reason
                                continue
                            if self.args.id_expansions_only:
                                print(returned_id, context if len(self.contexts) > 1 else "")
                            else:
                                if self.args.minimize_headers:
                                    header2 = pmap.minimize_header(header)
                                else:
                                    header2 = dict(header)
                                header2.pop("REFTYPE", None)
                                header2["dataset_id"] = returned_id
                                log.info("Dataset pars for", repr(returned_id), "with respect to", repr(context) + ":\n",
                                         log.PP(header2))
                            if self.args.first_id_expansion_only:
                                break

    def list_dataset_ids(self):
        """Print out the dataset ids associated with the instruments specified as command line params."""
        for instrument in self.args.dataset_ids:
            with log.error_on_exception("Failed reading dataset ids for", repr(instrument)):
                for context in self.contexts:
                    ids = api.get_dataset_ids(context, instrument)
                    for dataset_id in ids:
                        print(context, dataset_id)

    def list_config(self):
        """Print out configuration info about the current environment and server."""
        info = config.get_crds_env_vars()
        real_paths = config.get_crds_actual_paths(self.observatory)
        server = self.server_info
        current_server_url = api.get_crds_server()
        cache_subdir_mode = config.get_crds_ref_subdir_mode(self.observatory)
        pyinfo = _get_python_info()
        _print_dict("CRDS Environment", info)
        _print_dict("CRDS Client Config", { 
                "server_url" : current_server_url, 
                "cache_subdir_mode": cache_subdir_mode,
                "readonly_cache": self.readonly_cache,
                "effective_context": heavy_client.get_processing_mode(self.observatory)[1],
                "crds" : repr(crds),
                "version": heavy_client.version_info() 
                })
        _print_dict("CRDS Actual Paths", real_paths)
        _print_dict("CRDS Server Info", server, 
                    ["observatory", "status", "connected", "operational_context", "last_synced", 
                     "reference_url", "mapping_url", "effective_mode"])
        if self.observatory == "hst":
            cal_vars = { var : os.environ[var] for var in os.environ
                          if len(var) == 4 and var.lower().endswith("ref") }
            _print_dict("Calibration Environment", cal_vars)
        _print_dict("Python Environment", pyinfo)

    def list_required_parkeys(self):
        """Print out the parkeys required for matching using the specified contexts."""
        for name in self.contexts:
            mapping = crds.get_cached_mapping(name)
            log.divider(name="Parkeys required for " + repr(mapping.basename), func=log.write)
            _print_dict("", mapping.get_required_parkeys())
        
def _get_python_info():
    """Collect and return information about the Python environment"""
    pyinfo = {
        "Python Version" : ".".join(str(num) for num in sys.version_info),
        "Python Executable": sys.executable,
        }
    pypath = os.environ.get("PYTHON_PATH", None)
    if pypath:
        pyinfo["PYTHON_PATH"] = pypath
    return pyinfo
    
def _print_dict(title, dictionary, selected = None):
    """Print out dictionary `d` with a one line `title`."""
    if selected is None:
        selected = dictionary.keys()
    print(title)
    if dictionary:
        for key in sorted(selected):
            try:
                print("\t" + key + " = " + repr(dictionary[key]))
            except Exception:
                print("\t" + key + " = " + repr(getattr(dictionary, key)))
    else:
        print("\t" + "none")

def _print_list(files):
    """Print `files` one file per line."""
    for filename in files:
        print(filename)

if __name__ == "__main__":
    sys.exit(ListScript()())
