"""This module is a command line script which lists the match tuples associated
with a reference file.

% crds matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits
lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' OBSTYPE='IMAGING' FW1OFFST='N/A' FW2OFFST='N/A' FWSOFFST='N/A' DATE-OBS='1997-01-01' TIME-OBS='00:00:00'

A number of command line switches control output formatting.

The api function find_full_match_paths() returns a list of "match paths",  lists of parkey value assignment tuples:
"""
import sys
import os.path
from collections import defaultdict
from pprint import pprint as pp   # doctests

import crds
from crds.core import log, utils, cmdline, selectors
from crds.client import api

# ===================================================================

def test():
    """Run any doctests."""
    import doctest, crds.matches
    return doctest.testmod(crds.matches)

# ===================================================================

def find_full_match_paths(context, reffile):
    """Return the list of full match paths for `reference` in `context` as a
    list of tuples of tuples.   Each inner tuple is a (var, value) pair.

    Returns [((context_tuples,),(match_tuple,),(useafter_tuple,)), ...]

    >>> pp(find_full_match_paths("hst.pmap", "q9e1206kj_bia.fits"))
    [((('observatory', 'hst'), ('instrument', 'acs'), ('filekind', 'biasfile')),
      (('DETECTOR', 'HRC'),
       ('CCDAMP', 'A'),
       ('CCDGAIN', '4.0'),
       ('APERTURE', '*'),
       ('NUMCOLS', '1062'),
       ('NUMROWS', '1044'),
       ('LTV1', '19.0'),
       ('LTV2', '20.0'),
       ('XCORNER', 'N/A'),
       ('YCORNER', 'N/A'),
       ('CCDCHIP', 'N/A')),
      (('DATE-OBS', '2006-07-04'), ('TIME-OBS', '11:32:35'))),
     ((('observatory', 'hst'), ('instrument', 'acs'), ('filekind', 'biasfile')),
      (('DETECTOR', 'HRC'),
       ('CCDAMP', 'A'),
       ('CCDGAIN', '4.0'),
       ('APERTURE', '*'),
       ('NUMCOLS', 'N/A'),
       ('NUMROWS', 'N/A'),
       ('LTV1', 'N/A'),
       ('LTV2', 'N/A'),
       ('XCORNER', 'N/A'),
       ('YCORNER', 'N/A'),
       ('CCDCHIP', 'N/A')),
      (('DATE-OBS', '2006-07-04'), ('TIME-OBS', '11:32:35')))]
    """
    ctx = crds.get_pickled_mapping(context, cached=True)  # reviewed
    return ctx.file_matches(reffile)

def find_match_paths_as_dict(context, reffile):
    """Return the matching parameters for reffile as a list of dictionaries, one dict for
    each match case giving the parameters of that match.

    >>> pp(find_match_paths_as_dict("hst.pmap", "q9e1206kj_bia.fits"))
    [{'APERTURE': '*',
      'CCDAMP': 'A',
      'CCDCHIP': 'N/A',
      'CCDGAIN': '4.0',
      'DATE-OBS': '2006-07-04',
      'DETECTOR': 'HRC',
      'LTV1': '19.0',
      'LTV2': '20.0',
      'NUMCOLS': '1062',
      'NUMROWS': '1044',
      'TIME-OBS': '11:32:35',
      'XCORNER': 'N/A',
      'YCORNER': 'N/A',
      'filekind': 'biasfile',
      'instrument': 'acs',
      'observatory': 'hst'},
     {'APERTURE': '*',
      'CCDAMP': 'A',
      'CCDCHIP': 'N/A',
      'CCDGAIN': '4.0',
      'DATE-OBS': '2006-07-04',
      'DETECTOR': 'HRC',
      'LTV1': 'N/A',
      'LTV2': 'N/A',
      'NUMCOLS': 'N/A',
      'NUMROWS': 'N/A',
      'TIME-OBS': '11:32:35',
      'XCORNER': 'N/A',
      'YCORNER': 'N/A',
      'filekind': 'biasfile',
      'instrument': 'acs',
      'observatory': 'hst'}]
    """
    matches = find_full_match_paths(context, reffile)
    return [ _flatten_items_to_dict(match) for match in matches ]

def _flatten_items_to_dict(match_path):
    """Given a `match_path` which is a sequence of parameter items and sub-paths,  return
    a flat dictionary representation:

    returns   { matchinhg_par:  matching_par_value, ...}
    """
    result = {}
    for par in match_path:
        if len(par) == 2 and isinstance(par[0], str) and isinstance(par[1], str):
            result[par[0]] = par[1]
        else:
            result.update(_flatten_items_to_dict(par))
    return result

def get_minimum_exptime(context, references):
    """Return the minimum EXPTIME for the list of `references` with respect to `context`.
    This is used to define the potential reprocessing impact of new references,  since
    no dataset with an earlier EXPTIME than a reference is typically affected by the
    reference,  particularly with respect to the HST USEAFTER approach.

    >>> get_minimum_exptime("hst.pmap", ["q9e1206kj_bia.fits"])
    '2006-07-04 11:32:35'
    """
    return min([_get_minimum_exptime(context, ref) for ref in references])

def _get_minimum_exptime(context, reffile):
    """Given a `context` and a `reffile` in it,  return the minimum EXPTIME for all of
    it's match paths constructed from DATE-OBS and TIME-OBS.
    """
    path_dicts = find_match_paths_as_dict(context, reffile)
    exptimes = [ get_exptime(path_dict) for path_dict in path_dicts ]
    return min(exptimes)


DATE_TIME_PAIRS = [
    ("DATE-OBS", "TIME-OBS"),
    ("META.OBSERVATION.DATE", "META.OBSERVATION.TIME"),
    ("META_OBSERVATION_DATE", "META_OBSERVATION_TIME"),
    ]

def get_exptime(match_dict):
    """Given a `match_dict` dictionary of matching parameters for one match path,
    return the EXPTIME for it or 1900-01-01 00:00:00 if no EXPTIME can be derived.
    """
    for dt_pair in DATE_TIME_PAIRS:
        try:
            return match_dict[dt_pair[0]] + " " + match_dict[dt_pair[1]]
        except KeyError:
            continue
    else:
        log.verbose("matches.exp_time:  no exptime value found. returning worst case 1900-01-01 00:00:00.")
        return "1900-01-01 00:00:00"

# ===================================================================

class MatchesScript(cmdline.ContextsScript):
    """Command line script for printing reference selection criteria."""

    description = """
Prints out the selection criteria by which the specified references are matched with respect to the specified contexts.

The primary and original role of crds.matches is to interpret CRDS rules and report the matching criteria for specified
references.

A secondary function of crds.matches is to dump the matching criteria associated with particular dataset ids,
or all dataset ids for an instrument, according to the appropriate archive catalog (e.g. DADSOPS).
"""

    epilog = """
** crds.matches can dump reference file match cases with respect to particular contexts:

% crds matches  --contexts hst_0001.pmap --files lc41311jj_pfl.fits
lc41311jj_pfl.fits : ACS PFLTFILE DETECTOR='WFC' CCDAMP='A|ABCD|AC|AD|B|BC|BD|C|D' FILTER1='F625W' FILTER2='POL0V' DATE-OBS='1997-01-01' TIME-OBS='00:00:00'

% crds matches --contexts hst.pmap --files lc41311jj_pfl.fits --omit-parameter-names --brief-paths
lc41311jj_pfl.fits :  'WFC' 'A|ABCD|AC|AD|B|BC|BD|C|D' 'F625W' 'POL0V' '1997-01-01' '00:00:00'

% crds matches --contexts hst.pmap --files lc41311jj_pfl.fits --tuple-format
lc41311jj_pfl.fits : (('OBSERVATORY', 'HST'), ('INSTRUMENT', 'ACS'), ('FILEKIND', 'PFLTFILE'), ('DETECTOR', 'WFC'), ('CCDAMP', 'A|ABCD|AC|AD|B|BC|BD|C|D'), ('FILTER1', 'F625W'), ('FILTER2', 'POL0V'), ('DATE-OBS', '1997-01-01'), ('TIME-OBS', '00:00:00'))

** crds.matches can dump database matching parameters for specified datasets with respect to specified contexts:

% crds matches --datasets JBANJOF3Q --minimize-headers --contexts hst_0048.pmap hst_0044.pmap
JBANJOF3Q : hst_0044.pmap : APERTURE='WFC1-2K' ATODCORR='NONE' BIASCORR='NONE' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='NONE' DARKCORR='NONE' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='NONE' DRIZCORR='NONE' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='NONE' FLSHCORR='NONE' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='NONE' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NUMCOLS='UNDEFINED' NUMROWS='UNDEFINED' OBSTYPE='INTERNAL' PCTECORR='NONE' PHOTCORR='NONE' REFTYPE='UNDEFINED' SHADCORR='NONE' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'
JBANJOF3Q : hst_0048.pmap : APERTURE='WFC1-2K' ATODCORR='NONE' BIASCORR='NONE' CCDAMP='B' CCDCHIP='1.0' CCDGAIN='2.0' CRCORR='NONE' DARKCORR='NONE' DATE-OBS='2010-01-31' DETECTOR='WFC' DQICORR='NONE' DRIZCORR='NONE' FILTER1='F502N' FILTER2='F660N' FLASHCUR='OFF' FLATCORR='NONE' FLSHCORR='NONE' FW1OFFST='0.0' FW2OFFST='0.0' FWSOFFST='0.0' GLINCORR='NONE' INSTRUME='ACS' LTV1='-2048.0' LTV2='-1.0' NAXIS1='2070.0' NAXIS2='2046.0' OBSTYPE='INTERNAL' PCTECORR='NONE' PHOTCORR='NONE' REFTYPE='UNDEFINED' SHADCORR='NONE' SHUTRPOS='B' TIME-OBS='01:07:14.960000' XCORNER='1.0' YCORNER='2072.0'

** crds.matches can list all references which satisfy any filter constraints relevant to their bestref lookup.

% crds matches --contexts jwst-niriss-operational --files-from-contexts --filters META.INSTRUMENT.FILTER='F480M' --brief
CRDS - INFO - Symbolic context 'jwst-niriss-operational' resolves to 'jwst_niriss_0028.imap'
jwst_niriss_dark_0005.fits :  META.INSTRUMENT.DETECTOR='NIS' META.SUBARRAY.NAME='FULL'
jwst_niriss_gain_0001.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_ipc_0002.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_linearity_0005.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_mask_0004.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_photom_0017.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_readnoise_0001.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_saturation_0005.fits :  META.INSTRUMENT.DETECTOR='NIS'
jwst_niriss_superbias_0003.fits :  META.INSTRUMENT.DETECTOR='NIS' META.EXPOSURE.READPATT='*' META.SUBARRAY.NAME='N/A'
jwst_niriss_throughput_0008.fits :  META.INSTRUMENT.FILTER='F480M'
"""

    def add_args(self):
        super(MatchesScript, self).add_args()
        self.add_argument("--files", nargs="+", default=(),
            help="References for which to dump selection criteria.")
        self.add_argument("--files-from-contexts", action="store_true",
            help="Operate on all references referred to by the context parameters.")
        self.add_argument("--filters", nargs="+", default=(),
            help="Parameter constraints (key=value) which references matching on `key` must satisfy.  Unused parameters for a reference type are ignored.")
        self.add_argument("-b", "--brief-paths", action="store_true",
            help="Don't show the instrument and filekind clutter if already in filename.")
        self.add_argument("-o", "--omit-parameter-names", action="store_true",
            help="Hide the parameter names of the selection criteria,  just show the values.")
        self.add_argument("-t", "--tuple-format", action="store_true",
            help="Print the match info as Python tuples.")
        self.add_argument("-d", "--datasets", nargs="+",
            help="Dataset ids for which to dump matching parameters from DADSOPS or equivalent database.")
        self.add_argument("-i", "--instrument", type=str,
            help="Instrument for which to dump matching parameters from DADSOPS or equivalent database.")
        self.add_argument("-c", "--condition-values", action="store_true",
            help="When dumping dataset parameters, first apply CRDS value conditioning / normalization.")
        self.add_argument("-m", "--minimize-headers", action="store_true",
            help="When dumping dataset parameters,  limit them to matching parameters, excluding e.g. historical bestrefs.")

    def main(self):
        """Process command line parameters in to a context and list of
        reference files.   Print out the match tuples within the context
        which contain the reference files.
        """
        if self.matched_files:
            self.dump_reference_matches()
        elif self.args.datasets or self.args.instrument:
            self.dump_dataset_headers()
        else:
            self.print_help()
            log.error("Specify --files to dump reference match cases or --datasets to dump dataset matching parameters.")
        return log.errors()

    @property
    def matched_files(self):
        """Combine references from --files with references implied by --contexts parameters."""
        matched = list(self.files)
        if self.args.files_from_contexts:
            matched += list(self.get_context_references())
        return matched

    def dump_reference_matches(self):
        """Print out the match paths for the reference files specified on the
        command line with respect to the specified contexts.
        """
        for ref in self.matched_files:
            cmdline.reference_file(ref)
        for context in self.contexts:
            self.dump_match_tuples(context)

    def dump_dataset_headers(self):
        """Print out the matching parameters for the --datasets specified on
        the command line.
        """
        multi_context_headers = defaultdict(list)
        for context in self.contexts:
            if self.args.datasets:
                headers = api.get_dataset_headers_by_id(context, self.args.datasets)
            elif self.args.instrument:
                headers = api.get_dataset_headers_by_instrument(context, self.args.instrument)
            for dataset_id, header in headers.items():
                multi_context_headers[dataset_id].append((context, header))
        for dataset_id, context_headers in multi_context_headers.items():
            for (context, header) in context_headers:
                if self.args.condition_values:
                    header = utils.condition_header(header)
                if self.args.minimize_headers:
                    header = crds.get_cached_mapping(context).minimize_header(header)
                if len(self.contexts) == 1:
                    print(dataset_id, ":", log.format_parameter_list(header))
                else:
                    print(dataset_id, ":", context, ":", log.format_parameter_list(header))

    def locate_file(self, filename):
        """Override for self.files..."""
        return os.path.basename(filename)

    def dump_match_tuples(self, context):
        """Print out the match tuples for `references` under `context`.
        """
        ctx = context if len(self.contexts) > 1 else ""
        for ref in self.matched_files:
            matches = self.find_match_tuples(context, ref)
            if matches:
                for match in matches:
                    log.write(ctx, ref, ":", match)
            else:
                log.verbose(ctx, ref, ":", "none")

    def find_match_tuples(self, context, reffile):
        """Return the list of match representations for `reference` in `context`.
        """
        ctx = crds.get_cached_mapping(context)
        matches = ctx.file_matches(reffile)
        result = []
        for path in matches:
            prefix = self.format_prefix(path[0])
            if self.is_filtered(path):
                continue
            match_tuple = tuple([self.format_match_tup(tup) for section in path[1:] for tup in section])
            if self.args.tuple_format:
                if prefix:
                    match_tuple = prefix + match_tuple
            else:
                match_tuple = prefix + " " + " ".join(match_tuple)
            result.append(match_tuple)
        return result

    def is_filtered(self, path):
        """Return True is `path` meets all matching parameter constraints specified by --filters,
        otherwise False.
        """
        for filter in self.args.filters:
            key, value = (item.strip() for item in filter.split("="))
            for section in path[1:]:
                for tup in section:
                    if (tup[0].upper() == key.upper() and
                        value.upper() not in selectors.glob_list(tup[1].upper())):
                        return True
        return False

    def format_prefix(self, path):
        """Return any representation of observatory, instrument, and filekind."""
        if not self.args.brief_paths:
            if self.args.tuple_format:
                prefix = tuple([tuple([t.upper() for t in tup]) for tup in path])
            else:
                prefix = " ".join(tup[1].upper() for tup in path[1:])
        else:
            prefix = ""
        return prefix

    def format_match_tup(self, tup):
        """Return the representation of the selection criteria."""
        if self.args.tuple_format:
            return tup if not self.args.omit_parameter_names else tup[1]
        else:
            tup = tup[0], repr(tup[1])
            return "=".join(tup if not self.args.omit_parameter_names else tup[1:])

if __name__ == "__main__":
   sys.exit(MatchesScript()())
