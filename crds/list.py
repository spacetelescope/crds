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
    """Command line script for listing information about CRDS reference and mapping files."""

    description = """Command line script for listing information about CRDS reference and mapping files."""
        
    epilog = """    
    Contexts to list can be specified explicitly:
    
    % python -m crds.list  --contexts hst_0001.pmap hst_0002.pmap --references
    vb41935ij_bia.fits 
    vb41935kj_bia.fits 
    ...
    
    Contexts to list can be specified as a range:
    
    % python -m crds.list --range 1:2 --references
    vb41935lj_bia.fits 
    vb41935oj_bia.fits
    ...
    
    Contexts to list can be specified as --all contexts:
    
    % python -m crds.list --all --mappings
    hst.pmap 
    hst_0001.pmap 
    hst_0002.pmap 
    hst_acs.imap 
    hst_acs_0001.imap 
    hst_acs_0002.imap 
    hst_acs_atodtab.rmap 
    ...
    
    The paths of locally cached mappings (files already synced to your computer) can be listed:
    
    % python -m crds.list --cached-mappings
    
    The paths of locally cached references (files already synced to your computer) can be listed:
    
    % python -m crds.list --cached-references

    In both cases adding --full-path causes the path of the file within the CRDS cache to be printed.

    The contents of mappings or references (header only) can be printed to stdout like this:

    % python -m crds.list --contexts jwst-fgs-linearity-edit jwst-nirspec-linearity-edit --cat --add-filename | grep parkey
    CRDS  : INFO     Symbolic context 'jwst-fgs-linearity-edit' resolves to 'jwst_fgs_linearity_0008.rmap'
    CRDS  : INFO     Symbolic context 'jwst-nirspec-linearity-edit' resolves to 'jwst_nirspec_linearity_0009.rmap'
    /cache/path/mappings/jwst/jwst_fgs_linearity_0008.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),
    /cache/path/mappings/jwst/jwst_nirspec_linearity_0009.rmap:     'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.SUBARRAY.NAME'), ('META.OBSERVATION.DATE', 'META.OBSERVATION.TIME')),

    References need to be catted explicitly,  but the list can come from the above methods of listing references:

    % python -m crds.list --cat jwst_nirspec_dark_0036.fits
    CRDS  : INFO     Symbolic context 'jwst-operational' resolves to 'jwst_0167.pmap'
    ########################################################################################################################
    File:  '/grp/crds/jwst/references/jwst/jwst_nirspec_dark_0036.fits'
    ########################################################################################################################
    {'A1_COL_C': '8.9600000e+002',
    'A1_CONF1': '2.1846000e+004',
    ...
    }
    """
    
    def add_args(self):
        self.add_argument('--references', action='store_true', dest="list_references",
            help='print names of reference files referred to by contexts')
        self.add_argument('--mappings', action='store_true', dest="list_mappings",
            help='print names of mapping files referred to by contexts')
        self.add_argument("--cached-references", action="store_true",
            help="prints the paths of all references in the local cache.")
        self.add_argument("--cached-mappings", action="store_true",
            help="prints the paths of all mappings in the local cache.")
        self.add_argument("--full-path", action="store_true",
            help="prints the full paths of files for --cached-references and --cached-mappings.")
        self.add_argument("--datasets", nargs="+", dest="datasets", default=None,
            help="prints matching parameters for the specified dataset ids.")
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
        super(ListScript, self).add_args()
        
    def main(self):
        """List files."""
        if self.args.list_references:
            self.list_references()
        if self.args.list_mappings:
            self.list_mappings()
        if self.args.cached_references:
            self.list_cached_references()
        if self.args.cached_mappings:
            self.list_cached_mappings()
        if self.args.datasets is not None:
            self.list_datasets()
        if self.args.config:
            self.list_config()
        if self.args.cat is not None:
            self.cat_files()
        if self.args.operational_context:
            print(self.default_context)
        if self.args.remote_context:
            print(self.remote_context)

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
        
    def list_datasets(self):
        """List dataset header info for self.args.datasets with respect to self.args.context"""
        for context in self.contexts:
            with log.error_on_exception("Failed fetching dataset parameters with repect to", repr(context), 
                                        "for", repr(self.args.datasets)):
                pars = api.get_dataset_headers_by_id(context, self.args.datasets)
                pmap = rmap.get_cached_mapping(context)
                for (dataset_id, header) in pars.items():
                    if isinstance(header, python23.string_types):
                        log.error("No header for", repr(dataset_id), ":", repr(header)) # header is reason
                        continue
                    header2 = pmap.minimize_header(header)
                    header2.pop("REFTYPE", None)
                    log.info("Dataset pars for", repr(dataset_id), "with respect to", repr(context) + ":\n",
                             log.PP(header2))
                    
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
        for key in selected:
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
