"""This module is a command line script which lists the reference and/or
mapping files associated with the specified contexts by consulting the CRDS
server.   More generally it's for printing out information on CRDS files.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import os.path
import sys
from collections import OrderedDict
import json

from astropy.io import fits

import crds
from crds.core import config, log, python23, rmap, heavy_client, cmdline
from crds.core import crds_cache_locking
from crds import data_file

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
    5. Listing global default and installed pipeline contexts
    6. Resolving context specifiers into literal context names

    --------------------------------------------------------------------------
    0. Configuration information governing the behavior of CRDS for simple
    configurations can be dumped:

    % python -m crds.list --status
    CRDS Version = '7.0.7, bump-version, 7432326'
    CRDS_MODE = 'auto'
    CRDS_PATH = '/Users/jmiller/crds_cache_ops'
    CRDS_SERVER_URL = 'https://jwst-crds.stsci.edu'
    Effective Context = 'jwst_0204.pmap'
    Last Synced = '2016-09-20 08:00:09.115330'
    Python Executable = '/Users/jmiller/anaconda/bin/python'
    Python Version = '3.5.2.final.0'
    Readonly Cache = False

    More comprehensive configuration information is also available for advanced
    configurations:

    % python -m crds.list --config
    ... lots of info ....

    --------------------------------------------------------------------------
   1. Files known by the CRDS server to belong to specified contexts can be listed
    even if the files are not installed in a local CRDS Cache.

    The --mappings command recursively evaluates and includes all the sub-mappings,
    i.e. imaps and pmaps, of the specified contexts.

    Contexts to list can be specified in a variety of ways:

    -- To list the references contained by several contexts
    
    % python -m crds.list  --references --contexts hst_0001.pmap hst_0002.pmap ...
    vb41935ij_bia.fits 
    vb41935kj_bia.fits 
    ...
    
    -- To list the references in a numerical range of contexts

    % python -m crds.list --references --range 1:2 --references
    vb41935lj_bia.fits 
    vb41935oj_bia.fits
    ...

    -- To list all mappings, even those not referenced by an imap or pmap
    
    % python -m crds.list --mappings --all
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
    
    % python -m crds.list --cached-mappings --full-path
    ...

    % python -m crds.list --cached-references --full-path
    ...

    In both cases adding --full-path prints the path of the file within the CRDS cache.

    These are merely simple directory listings which ignore the context specifiers
    and can be grep'ed for finer grained answers.

    --------------------------------------------------------------------------
    3. The contents of cached mappings or references (header only) can be printed to stdout like this:

    % python -m crds.list --contexts jwst-fgs-linearity-edit jwst-nirspec-linearity-edit --cat --add-filename | grep parkey
    CRDS - INFO - Symbolic context 'jwst-fgs-linearity-edit' resolves to 'jwst_fgs_linearity_0008.rmap'
    CRDS - INFO - Symbolic context 'jwst-nirspec-linearity-edit' resolves to 'jwst_nirspec_linearity_0009.rmap'
    /cache/path/mappings/jwst/jwst_fgs_linearity_0008.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
    /cache/path/mappings/jwst/jwst_nirspec_linearity_0009.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),

    this prints the contents of the specified rmaps.

    The -edit specifier above refers to mappings contained by the default starting point (.pmap) of future
    server submissions.  It tracks on-going submission work that precedes the adoption of a new context
    as the default in use by the pipeline.

    crds.list --cat can be applied to references and prints out the reference metadata that CRDS views
    abstractly as the file header.

    References need to be catted explicitly by name,  but the list can come from the --references command
    explained above:

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
    JCL403010:JCL403ECQ
    JCL403010:JCL403EEQ
    JCL403010:JCL403EGQ
    JCL403010:JCL403EIQ
    JCL403010:JCL403EKQ
    JCL403010:JCL403EMQ
    JCL403010:JCL403EOQ
    JCL403010:JCL403EQQ
    JCL403010:JCL403ESQ
    JCL403010:JCL403EUQ

    Headers available can possibly vary by CRDS context and will be dumped for
    every specified or implicit context.  Generally the default context is
    sufficient.  Often all exposures of an association have identical
    parameters but CRDS is designed so that this does not have to be the case.

    These dataset header services require setting CRDS_SERVER_URL to a valid CRDS server to
    provide a source for the headers.

   --------------------------------------------------------------------------
    5. Information about the default context can be printed.  There are two variations and a subtle distinction:

    % python m crds.list --operational-context
    jwst_0204.pmap 

    lists the context which has been *commanded* as default on the CRDS server.

    While:

    % crds list --remote-context jwst-ops-pipeline
    jwst_0101.pmap
    
    lists the context which is *in actual use* in the associated archive pipeline as reported by
    a cache sync echo.

    During the interval between commanding a new default on the CRDS server and syncing the pipeline
    CRDS cache,  the commanded and actual pipeline contexts can differ.

   --------------------------------------------------------------------------
    6. Resolving context specifiers

    Some CRDS tools, including crds.list and crds.sync, support multiple
    mechanisms for specifying context.  The --resolve-contexts command
    interprets those specifiers into a non-recursive list of literal mapping
    names and prints them out.  --resolve-contexts differs from --mappings
    because it does not implicitly include all sub-mappings of the specified
    contexts.

    % crds list --resolve-contexts --all
    jwst.pmap
    jwst_0000.pmap
    jwst_0001.pmap
    jwst_0002.pmap
    jwst_0003.pmap
    ...

    % crds list --resolve-contexts --last 5
    jwst_0205.pmap
    jwst_0206.pmap
    jwst_0207.pmap
    jwst_0208.pmap
    jwst_0209.pmap

    % crds list --resolve-contexts  --contexts jwst-miri-dark-operational 
    jwst_miri_dark_0012.rmap

    % crds list --resolve-contexts --contexts jwst-niriss-superbias-2016-01-01T00:00:00
    jwst_niriss_superbias_0005.rmap
    """
    def __init__(self, *args, **keys):
        super(ListScript, self).__init__(*args, **keys)
        self.show_context_resolution = False
    
    def add_args(self):
        """Add switches unique to crds.list."""

        self.add_argument('--references', action='store_true', dest="list_references",
            help='print names of reference files referred to by contexts')
        self.add_argument('--mappings', action='store_true', dest="list_mappings",
            help='print names of mapping files referred to by contexts')
        self.add_argument("--cached-references", action="store_true",
            help="print the paths of all references in the local cache. very primitive.")
        self.add_argument("--cached-mappings", action="store_true",
            help="print the paths of all mappings in the local cache. very primitive.")
        self.add_argument("--cached-pickles", action="store_true",
            help="print the paths of all pickles in the local cache. very primitive.")
        self.add_argument("--full-path", action="store_true",
            help="print the full paths of listed files.")

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
        self.add_argument("--json-headers", action="store_true", dest="json_headers",
            help="print out header parameters in JSON format suited for crds.bestrefs and grepping.")

        self.add_argument("--config", action="store_true", dest="config",
            help="print CRDS configuration information.")

        self.add_argument("--status", action="store_true", dest="status",
            help="print brief, basic, CRDS configuration information.")

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
        self.add_argument("--resolve-contexts", action="store_true", dest="resolve_contexts",
            help="print the literal names of the contexts defined by the command line context specifiers.")

        self.add_argument("--required-parkeys", action="store_true",
            help="print the names of the parkeys required to compute bestrefs for the specified mappings.")

        super(ListScript, self).add_args()
        
    def main(self):
        """List files."""
        if self.args.cat is not None: # including []
            return self.cat_files()

        if self.args.operational_context:
            print(self.default_context)
            return
        if self.args.remote_context:
            print(self.remote_context)
            return

        if self.args.resolve_contexts:
            self.list_resolved_contexts()
                    
        if self.args.list_references:
            self.list_references()
        if self.args.list_mappings:
            self.list_mappings()
        if self.args.cached_references:
            self.list_cached_references()
        if self.args.cached_mappings:
            self.list_cached_mappings()
        if self.args.cached_pickles:
            self.list_cached_pickles()

        if self.args.dataset_ids:
            self.list_dataset_ids()
        if self.args.dataset_headers:
            self.list_dataset_headers()

        if self.args.config:
            self.list_config()
        if self.args.status:
            self.list_status()

        if self.args.required_parkeys:
            self.list_required_parkeys()

    def list_resolved_contexts(self):
        """Print out the literal interpretation of the contexts implied by the script's
        context specifiers.
        """
        self.show_context_resolution = True
        for context in self.contexts:
            print(context)

    @property
    def remote_context(self):
        """Print the name of the context in use at pipeline `self.args.remote_context`
        as recorded on the server after being pushed by the crds.sync tool in the pipeline.
        """
        self.require_server_connection()
        with log.error_on_exception("Failed resolving remote context"):
            return api.get_remote_context(self.observatory, self.args.remote_context)

    def cat_files(self):
        """Print out the files listed after --cat or implied by a combination of 
        explicitly specified contexts and --mappings or --references.
        
        --files is not allowed.
        
        """
        # --cat files...   specifying *no* files still triggers --cat logic
        # --contexts context-specifiers [including --all --last --range...]
        # context specifiers can be symbolic and will be resolved.
        # --cat @file is allowed

        mappings = self.get_context_mappings() if self.args.list_mappings else []
        references = self.get_context_references() if self.args.list_references else []        
        catted_files = self.get_words(self.args.cat) + mappings + references

        # This could be expanded to include the closure of mappings or references
        for name in catted_files:
            with log.error_on_exception("Failed dumping:", repr(name)):
                path = self.locate_file(name) 
                if path != "N/A":
                    self._cat_file(path)
                    
    def _cat_file(self, path):
        """Print out information on a single reference or mapping at `path`."""
        self._cat_banner("File:", os.path.abspath(path), delim="#", bottom_delim="-")
        if config.is_reference(path):
            self._cat_header(path)
            if path.endswith(".fits"):
                self._cat_banner("Fits Info:", delim="-")
                fits.info(path)
                self._cat_array_properties(path)
        else:
            self._cat_text(path)

    def _cat_banner(self, *args, **keys):
        """Print a banner for --cat for `name` and return the filepath of `name`."""
        delim = keys.get("delim","#")
        bottom_delim = keys.get("bottom_delim", None)
        if delim:
            print(delim*80)
        print(*args)
        if bottom_delim:
            print(bottom_delim*80)
        
    def _cat_array_properties(self, path):
        """Print out the CRDS interpretation of every array in `path`,  currently FITS only."""
        i = 0
        with data_file.fits_open(path) as hdulist:
            for hdu in hdulist:
                with log.warn_on_exception("Can't load array properties for HDU[" + str(i) +"]"):
                    if i > 0:
                        extname = hdu.header["EXTNAME"]
                        self._cat_banner("CRDS Array Info [" + repr(extname) + "]:", delim="-")
                        props = data_file.get_array_properties(path, hdu.header["EXTNAME"])
                        props = { prop:value for (prop,value) in props.items() if value is not None }
                        print(log.PP(props))
                i += 1

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
        
    def list_cached_pickles(self):
        """List the pickle paths in the local cache."""
        _print_list(rmap.list_pickles("*", self.observatory, full_path=self.args.full_path))
        
    def list_cached_references(self):
        """List the reference paths in the local cache."""
        _print_list(rmap.list_references("*", self.observatory, full_path=self.args.full_path))
        
    def list_dataset_headers(self):
        """List dataset header info for self.args.dataset_headers with respect to self.args.context"""
        
        # Support @-files for ids specified on command line
        ids = self.get_words(self.args.dataset_headers)
        
        for context in self.contexts:
            with log.error_on_exception("Failed fetching dataset parameters with repect to", repr(context), 
                                        "for", repr(self.args.dataset_headers)):
                pars = api.get_dataset_headers_unlimited(context, ids)
                pmap = crds.get_cached_mapping(context)
                for requested_id in ids:
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
                                header2["CRDS_CTX"] = context
                                self.dump_header(context, returned_id, header2)
                            if self.args.first_id_expansion_only:
                                break
                            
    def dump_header(self, context, header_id, header):
        """Print out dataset `header` for `id` and `context` in either .json or multi-line formats."""
        if self.args.json_headers:
            json_header = { header_id : header }
            print(json.dumps(json_header))
        else:
            print("Dataset pars for", repr(header_id), "with respect to", repr(context) + ":\n",
                  log.PP(header))

    def list_dataset_ids(self):
        """Print out the dataset ids associated with the instruments specified as command line params."""
        for instrument in self.args.dataset_ids:
            with log.error_on_exception("Failed reading dataset ids for", repr(instrument)):
                for context in self.contexts:
                    ids = api.get_dataset_ids(context, instrument)
                    for dataset_id in ids:
                        if len(self.contexts) > 1:
                            print(context, dataset_id)
                        else:
                            print(dataset_id)

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

    def list_status(self):
        """Print out *basic* configuration info about the current environment and server."""
        info = config.get_crds_env_vars()
        server = self.server_info
        pyinfo = _get_python_info()
        status = OrderedDict(
            [("CRDS_PATH", info.get("CRDS_PATH", "undefined")),
             ("CRDS_SERVER_URL", info.get("CRDS_SERVER_URL", "undefined")),
             ("CRDS_MODE", info["CRDS_MODE"]),
             ("Readonly Cache", self.readonly_cache),
             ("Cache Locking", crds_cache_locking.status()),
             ("Effective Context", heavy_client.get_processing_mode(self.observatory)[1]),
             ("Last Synced", server.last_synced),
             ("CRDS Version", heavy_client.version_info()),
             ("Python Version", pyinfo["Python Version"]),
             ("Python Executable", pyinfo["Python Executable"]),
             ])
        _print_dict(None, status)

    def list_required_parkeys(self):
        """Print out the parkeys required for matching using the specified contexts."""
        
        for name in self.contexts:
            mapping = crds.get_cached_mapping(name)
            if isinstance(mapping, rmap.PipelineContext):
                log.divider(name="Parkeys required for " + repr(mapping.basename), func=log.write)
                _print_dict("", mapping.get_required_parkeys())
            elif isinstance(mapping, rmap.InstrumentContext):
                for name in sorted(mapping.selections):
                    try:
                        rmapping = mapping.get_rmap(name)
                    except (crds.exceptions.IrrelevantReferenceTypeError,
                            crds.exceptions.OmitReferenceTypeError):
                        print(name +":", repr("N/A"))
                    else:
                        print(name + ":",  rmapping.get_required_parkeys())
            else:
                print(name + ":",  mapping.get_required_parkeys())
        
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
    if title:
        print(title)
    if dictionary:
        for key in sorted(selected):
            try:
                print(("\t" if title else "") + key + " = " + repr(dictionary[key]))
            except Exception:
                print(("\t" if title else "") + key + " = " + repr(getattr(dictionary, key)))
    else:
        print("\t" + "none")

def _print_list(files):
    """Print `files` one file per line."""
    for filename in files:
        print(filename)

if __name__ == "__main__":
    sys.exit(ListScript()())
