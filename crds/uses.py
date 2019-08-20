"""uses.py defines functions which will list the files which use a given
reference or mapping file.

>> from pprint import pprint as pp
>> pp(_findall_mappings_using_reference("v2e20129l_flat.fits"))
['hst.pmap',
 'hst_0001.pmap',
 'hst_0002.pmap',
 'hst_0003.pmap',
 'hst_0004.pmap',
 'hst_0005.pmap',
 'hst_0006.pmap',
 'hst_cos.imap',
 'hst_cos_0001.imap',
 'hst_cos_flatfile.rmap',
 'hst_cos_flatfile_0002.rmap']
"""
import sys
import os.path

from crds.core import config, cmdline, utils, log, rmap

@utils.cached
def load_all_mappings(observatory, pattern="*map"):
    """Return a dictionary mapping the names of all CRDS Mappings matching `pattern`
    onto the loaded Mapping object.
    """
    all_mappings = rmap.list_mappings(pattern, observatory)
    loaded = {}
    for name in all_mappings:
        with log.error_on_exception("Failed loading", repr(name)):
            loaded[name] = rmap.get_cached_mapping(name)
    return loaded

@utils.cached
def mapping_type_names(observatory, ending):
    """Return a mapping dictionary containing only mappings with names with `ending`."""
    return { name : mapping.mapping_names() + mapping.reference_names()
             for (name, mapping) in load_all_mappings(observatory).items()
             if name.endswith(ending) }

def uses_files(files, observatory, ending):
    """Alternate approach to uses that works by loading all mappings instead of grepping
    them on the file system.
    """
    referrers = set()
    for filename in files:
        config.check_filename(filename)
        loaded = mapping_type_names(observatory, ending)
        for_filename = set(name for name in loaded if filename in loaded[name])
        referrers |= for_filename
    return sorted(list(referrers))

def _findall_rmaps_using_reference(filename, observatory="hst"):
    """Return the basename of all reference mappings which mention `filename`."""
    return uses_files([filename], observatory, "rmap")

def _findall_imaps_using_rmap(filename, observatory="hst"):
    """Return the basenames of all instrument contexts which mention `filename`."""
    return uses_files([filename], observatory, "imap")

def _findall_pmaps_using_imap(filename, observatory="hst"):
    """Return the basenames of all pipeline contexts which mention `filename`."""
    return uses_files([filename], observatory, "pmap")

def _findall_mappings_using_reference(reference, observatory="hst"):
    """Return the basenames of all mapping files in the hierarchy which
    mentions reference `reference`.
    """
    mappings = []
    for rmap in _findall_rmaps_using_reference(reference, observatory):
        mappings.append(rmap)
        for imap in _findall_imaps_using_rmap(rmap, observatory):
            mappings.append(imap)
            for pmap in _findall_pmaps_using_imap(imap, observatory):
                mappings.append(pmap)
    return sorted(list(set(mappings)))

def _findall_mappings_using_rmap(rmap, observatory="hst"):
    """Return the basenames of all mapping files in the hierarchy which
    mentions reference mapping `rmap`.
    """
    mappings = []
    for imap in _findall_imaps_using_rmap(rmap, observatory):
        mappings.append(imap)
        for pmap in _findall_pmaps_using_imap(imap, observatory):
            mappings.append(pmap)
    return sorted(list(set(mappings)))

def uses(files, observatory="hst"):
    """Return the list of mappings which use any of `files`."""
    mappings = []
    for file_ in files:
        if file_.endswith(".rmap"):
            mappings.extend(_findall_mappings_using_rmap(file_, observatory))
        elif file_.endswith(".imap"):
            mappings.extend(_findall_pmaps_using_imap(file_, observatory))
        elif file_.endswith(".pmap"):
            pass  # nothing refers to a .pmap
        else:
            mappings.extend(_findall_mappings_using_reference(file_, observatory))
    return sorted(list(set(mappings)))

class UsesScript(cmdline.Script):
    """Command line script for printing rmaps using references,  or datasets using references."""

    description = """
Prints out the mappings which refer to the specified mappings or references.

Prints out the datasets which historically used a particular reference as defined by DADSOPS.

IMPORTANT:
   1. You must specify references or rules on which to operate with --files.
   2. You must set CRDS_PATH and CRDS_SERVER_URL to give crds.uses access to CRDS mappings and databases.
"""

    epilog = """
crds.uses can be invoked like this:

% crds uses --files n3o1022ij_drk.fits --hst
hst.pmap
hst_0001.pmap
hst_0002.pmap
hst_0003.pmap
...
hst_0041.pmap
hst_acs.imap
hst_acs_0001.imap
hst_acs_0002.imap
hst_acs_0003.imap
...
hst_acs_0008.imap
hst_acs_darkfile.rmap
hst_acs_darkfile_0001.rmap
hst_acs_darkfile_0002.rmap
hst_acs_darkfile_0003.rmap
...
hst_acs_darkfile_0005.rmap

"""
    def add_args(self):
        """Add command line parameters unique to this script."""
        super(UsesScript, self).add_args()
        self.add_argument("--files", nargs="+",
                          help="References for which to dump using mappings or datasets.")
        self.add_argument("-i", "--include-used", action="store_true", dest="include_used",
                          help="Include the used file in the output as the first column.")

    def main(self):
        """Process command line parameters in to a context and list of
        reference files.   Print out the match tuples within the context
        which contain the reference files.
        """
        if not self.args.files:
            self.print_help()
            sys.exit(-1)
        self.print_mappings_using_files()
        return log.errors()

    def locate_file(self, file_):
        """Just use basenames for identifying file references."""
        return os.path.basename(file_)

    def print_mappings_using_files(self):
        """Print out the mappings which refer to the specified mappings or references."""
        for file_ in self.files:
            for use in uses([file_], self.observatory):
                if self.args.include_used:
                    print(file_, use)
                else:
                    print(use)

def test():
    """Run the module doctest."""
    import doctest
    from . import uses
    return doctest.testmod(uses)

if __name__ == "__main__":
    sys.exit(UsesScript()())
