"""This module encapsulates code related to determining the datasets which are affected
by table changes.   The nature of the optimization is that,  viewed as a file change,  CRDS
would think a new table "affects everything" and be forced to recommend reprocessing all datasets.
The code in this module is tasked with determining if the rows selected from two versions of
a table by particular dataset parameters are actually different.

If the rows are not different, then effectifvely the new version of the table should not cause
a dataset to be processed.

If the rows are different,  then the dataset should be reprocessed.
"""
from crds.core import rmap, log
from crds.io import tables
from crds.client import api

# ===================================================================

def is_reprocessing_required(dataset,  dataset_parameters, old_context, new_context, update):
    """This is the top level interface to crds.bestrefs running in "Affected Datasets" mode.

    It determines if reprocessing `dataset` with parameters `dataset_parameters` should be performed as
    a consequence of switching from `old_reference` to `new_reference`.  old_reference is assigned to dataset
    by old_context,  and new_reference is assigned to dataset by new_context.

    Parameters
    ----------
    dataset:
             id of dataset being reprocessed,  <assoc>:<member> or <unassoc>:<unassoc> format

    dataset_parameters:
                        { parameter : value, ...} for all matching parameters and row selection parameters

                        XXX row selection parameters not used in file selection may not be present until
                        XXX explicitly added to the CRDS interface to the DADSOPS parameter database...
                        XXX and possibly even to DADSOPS itself. Normally the row selections have only been
                        XXX done with direct access to dataset .fits files.

    old_context: loaded pmap or name of old context,  possibly for metadata or None

    new_context: loaded pmap or name of new context,  possibly for metadata

    update: Update object

    Returns
    -------
    True        IFF reprocessing should be done as a consequence of the table change.
    """

    log.verbose('is_reprocessing_required: Called with:\n',
                dataset, '\n',
                dataset_parameters, '\n',
                old_context, '\n',
                new_context, '\n',
                update,
                verbosity=100)

    # no old_context means "single context" mode,  always reprocess.
    if old_context is None:
        return True

    # NOTE: non-tables are treated in DeepLook as filekinds which aren't (or maybe someday are) handled,
    # hence reprocessed for now.

    # Reprocess for non-file special values.  Other code will decide what to do with the updates,
    # the point here is that table comparison isn't possible so filtering shouldn't be done.
    old_ref = update.old_reference.lower()
    new_ref = update.new_reference.lower()
    incomparable = ('n/a', 'undefined', 'not found')
    if old_ref.startswith(incomparable) or new_ref.startswith(incomparable):
        return True

    # mostly debug wrappers here,  allows simple string parameters to work and resolves cache paths.
    old_context = rmap.asmapping(old_context, cached=True)
    new_context = rmap.asmapping(new_context, cached=True)
    old_reference = old_context.locate_file(old_ref)
    new_reference = new_context.locate_file(new_ref)

    # Log that deep examination is occuring.
    log.verbose('Deep Reference examination between {} and {} initiated.'.format(old_reference, new_reference),
                verbosity=25)

    with log.error_on_exception("Failed fetching comparison reference tables:", repr([old_ref, new_ref])):
        api.dump_files(new_context.name, [old_ref, new_ref])

    # See if deep checking into the reference is possible.
    try:
        deep_look = DeepLook.from_filekind(update.instrument, update.filekind)

        dataset_id = dataset.split(':')[0]

        # **DEBUG**
        # ** Since we are not getting full headers, if this is a test
        # ** dataset, replace the headers.
        #log.verbose_warning('Forcing use of LBYX01010, regardless...', verbosity=25)
        #dataset_id = 'LBYX01010'           #***DEBUG: force headers regardless of actua data

        if dataset_id in deep_look.stub_input:
            log.verbose_warning('Substituting header for dataset "{}"'.format(dataset))
            dataset_parameters = deep_look.stub_input[dataset_id]['headers']
            log.verbose_warning('headers = ', dataset_parameters, verbosity=25)

        log.verbose(deep_look.preamble, 'Dataset headers = {}'.format(dataset_parameters), verbosity=75)
        log.verbose(deep_look.preamble, 'Comparing references {} and {}.'.format(old_reference, new_reference), verbosity=75)
        deep_look.are_different(dataset_parameters, old_reference, new_reference)

        log.verbose(deep_look.preamble, 'Reprocessing is {}required.'.format('' if deep_look.is_different else 'not '), verbosity=25)
        log.verbose(deep_look.preamble, deep_look.message, verbosity=25)
        return deep_look.is_different

    except DeepLookError as error:

        # Could not determine difference, therefore presume so.
        log.verbose_warning('Deep examination error: {}'.format(error.message), verbosity=25)
        log.verbose_warning('Deep examination failed, presuming reprocessing.', verbosity=25)
        return True


###########
# Utilities
###########
def str_to_number(val, strip=True):
    """Map string `input` to the simplest numerical type capable of parsing it.  If `input`
    will not parse for any type,  return it as-is,  optionally stripping whitespace.
    """

    types = [int, float, complex]

    result = None
    for typ in types:
        try:
            result = typ(val)
            break
        except Exception:
            continue

    if result is None:
        result = val.strip() if strip else val

    return result

def mode_select(table, constraints):
    """Return rows that match the constraints

    Parameters
    ----------
    table: simple table
           Table to examine

    constraints: {field: (value, cmpfn, **kargs}
                 For each field, compare the given value using the
                 the specified comparison function. The cmpfn looks like
                     bool = cmpfn(row[field], value, **kargs)

    Returns
    -------
    The next row that matches.
    """
    for row in table.rows:
        selected = True
        for field in constraints:
            field_index = table.colnames.index(field.upper())
            (value, cmpfn, args) = constraints[field]
            selected = selected & cmpfn(str_to_number(row[field_index]), value, args)

        if selected:
            yield row

def mode_equality(modes_a, modes_b):
    """Check if the modes are equal"""

    # Assume not equal
    equality = False

    # Must be the same length
    if len(modes_a) == len(modes_b):

        # Must have some length
        if len(modes_a) > 0:
            equality = (modes_a == modes_b)

        # Else, nothing compares, so basically equal
        else:
            equality = True

    # That's all folks
    return equality

###################
#
# Comparison functions
#
###################

def cmp_equal(table_value, matching_values, wildcards=()):
    """Value equality

    Parameters
    ----------
    table_value: obj
                 Value from a reference table.

    matching_values: obj or [obj,]
                     What to check against. May be singular or a list

    wildcards: [value,]
               Values that are considered "everything".
               If the table_value is a wildcard, equality is
               presumed.
"""

    # Presume not equal
    is_equal = False

    # Is this a wildcard?
    if table_value in wildcards:
        is_equal = True

    # Otherwise, do a direct match
    else:
        try:
            is_equal = (table_value in matching_values)
        except Exception:
            is_equal = (table_value == matching_values)

    # That's all folks.
    return is_equal



# ##############################
#
# DeepLook
#
# The rules.
#
###############################


class DeepLookError(Exception):
    """Deep Look error base class
    """

    def __init__(self, message):
        super(DeepLookError, self).__init__(message)
        self.message = message

    def __str__(self):
        return repr(self.message)

class DeepLook:
    """Base class to define how reference tables are deep-checked
    for differences between references
    """

    rules = {} # List of classes to use for rules.

    def __init__(self):

        # **DEBUG**
        # Define dummy data.
        # Remove when proper headers are retrievable
        self.stub_input = { # dataset => headers
        }

        # Preamble for log messages
        self.preamble = 'Rule {}:'.format(self.__class__.__name__)

        # Meta Values that may be found in header keywords
        self.metavalues = {}

        # Default mode fields
        self.mode_fields = {}

        # Default way to compare
        self.cmp_equal_parameters = (cmp_equal, {'wildcards': ['ANY']})

        # Basic presumption is that there is a difference unless
        # proven otherwise.
        self.is_different = True
        self.message = 'Comparision not done, presuming references are different.'


    @classmethod
    def from_filekind(cls, instrument, filekind):
        """Create the appropriate object for the type of reference file"""

        name = (instrument + '_' + filekind).lower()
        log.verbose('Instantiating rules for reference type {}.'.format(name), verbosity=25)
        if name in cls.rules:
            return  cls.rules[name]()
        else:
            raise DeepLookError('No rules for instrument {} and reference file kind {}'.format(instrument, filekind))

    def are_different(self, headers, old_reference, new_reference):
        """Do the deep examination of the reference files with-respect-to the given dataset headers

        Affects
        =======
            self.is_different: Sets True or False whether the references are different.
            self.message: Reason for current state of is_different
        """

        # Convert header keys to lowercase for consistency
        headers_low = dict((k.lower(), v) for k, v in headers.items())

        # Start off that the references are different.
        self.is_different = True
        self.message = 'Comparision started but not completed.'

        # Get values for the mode fields
        constraint_values = {}
        for field in self.mode_fields:
            constraint_values[field] = str_to_number(headers_low[field]) if field in headers_low else None
        if None in constraint_values.values():
            self.message = 'Not all mode fields are defined in the dataset.'
            return

        # Modify the constraint values if any "meta" values are
        # present.
        for key in constraint_values:
            if key in self.metavalues:
                if constraint_values[key] in self.metavalues[key]:
                    constraint_values[key] = self.metavalues[key][constraint_values[key]]

        # Read the references
        data_old = tables.tables(old_reference)[0]   # XXXX currently limited to FITS extension 1
        data_new = tables.tables(new_reference)[0]

        # Columns must be the same between tables.
        if sorted(data_old.colnames) != sorted(data_new.colnames):
            self.message = 'Columns are different between references.'
            return

        # Now that values are in hand, produce the full constraint
        # dictionary
        constraints = {}
        for field in self.mode_fields:
            constraints[field] = (constraint_values[field],) + self.mode_fields[field]

        log.verbose(self.preamble, 'Constraints are:\n', constraints, verbosity=75)

        # Reduce the tables to just those rows that match the mode
        # specifications.
        mode_rows_old = [repr(row) for row in mode_select(data_old, constraints)]
        mode_rows_new = [repr(row) for row in mode_select(data_new, constraints)]

        # Sort the rows
        mode_rows_old.sort()
        mode_rows_new.sort()

        log.verbose(self.preamble, 'Old reference matching rows:\n', mode_rows_old, verbosity=75)
        log.verbose(self.preamble, 'New reference matching rows:\n', mode_rows_new, verbosity=75)

        # Check on equality.
        # That's all folks.
        self.is_different = not mode_equality(mode_rows_old, mode_rows_new)

        if self.is_different:
            self.message = 'Selection rules have executed and the selected rows are different.'
        else:
            self.message = 'Selection rules have executed and the selected rows are the same.'


################################
#
# Rule for tables that cannot be examined
#
################################


class DeepLook_Default(DeepLook):
    def are_different(self, headers, old_reference, new_reference):

        self.is_different = True
        self.message = 'Reference type cannot be examined, by definition.'


#############################
#
# Rules for COS
#
#############################


class DeepLook_COS(DeepLook):
    """Generic class for all COS rules
    """

    def __init__(self):
        super(DeepLook_COS, self).__init__()

        # **DEBUG**
        # Define dummy data.
        # Remove when proper headers are retrievable
        self.stub_input = { # dataset => headers
            'xLA7803FKQ': {
                'headers': {
                    'opt_elem': 'G160M',
                    'cenwave':  '1600',
                    'aperture': 'WCA',
                    'segment':  'BOTH',
                },
            },
            'xLBYX01010': {
                'headers': {
                    'opt_elem': 'G140L',
                    'cenwave':  '1280',
                    'aperture': 'PSA',
                    'segment':  'FUVB',
                },
            },
            'xLB4P02050': {
                'headers': {
                    'opt_elem': 'G160M',
                    'cenwave':  '1600',
                    'aperture': 'PSA',
                },
            },
            'xLB4P07010': {
                'headers': {
                    'opt_elem': 'G140L',
                    'cenwave':  '1230',
                    'aperture': 'PSA',
                },
            },
            'xLB6M01030': {
                'headers': {
                    'opt_elem': 'G230L',
                    'cenwave':  '3000',
                    'aperture': 'PSA',
                },
            },
            'xLBK617010': {
                'headers': {
                    'opt_elem': 'G185M',
                    'cenwave':  '1986',
                    'aperture': 'PSA',
                },
            },
        }


class DeepLook_COSSegment(DeepLook_COS):
    """Tables that require SEGMENT only"""

    def __init__(self):
        super(DeepLook_COSSegment, self).__init__()

        self.mode_fields = {
            'segment': self.cmp_equal_parameters,
        }


class DeepLook_COSFullmode(DeepLook_COS):
    def __init__(self):
        super(DeepLook_COSFullmode, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'cenwave':  self.cmp_equal_parameters,
            'aperture': self.cmp_equal_parameters,
        }


class DeepLook_COSOpt_elem(DeepLook_COS):
    def __init__(self):
        super(DeepLook_COSOpt_elem, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
        }


class DeepLook_COSDISPTAB(DeepLook_COS):
    def __init__(self):
        super(DeepLook_COSDISPTAB, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'cenwave':  self.cmp_equal_parameters,
        }


class DeepLook_COSLAMPTAB(DeepLook_COS):
    def __init__(self):
        super(DeepLook_COSLAMPTAB, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'cenwave':  self.cmp_equal_parameters,
            'fpoffset': self.cmp_equal_parameters,
        }


class DeepLook_COSTDSTAB(DeepLook_COS):
    def __init__(self):
        super(DeepLook_COSTDSTAB, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'aperture': self.cmp_equal_parameters,
        }


class DeepLook_COSFullSegment(DeepLook_COS):
    def __init__(self):
        super(DeepLook_COSFullSegment, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'cenwave':  self.cmp_equal_parameters,
            'aperture': self.cmp_equal_parameters,
            'segment': self.cmp_equal_parameters,
        }



#############################
#
# Rules for STIS
#
#############################


class DeepLook_STIS(DeepLook):
    """Generic class for all STIS rules
    """

    def __init__(self):
        super(DeepLook_STIS, self).__init__()


class DeepLook_STISopt_elem(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISopt_elem, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
        }

class DeepLook_STISaperture(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISaperture, self).__init__()

        self.mode_fields = {
            'aperture': self.cmp_equal_parameters,
        }

class DeepLook_STIScenwave(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STIScenwave, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'cenwave': self.cmp_equal_parameters,
        }

class DeepLook_STISfullmode(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISfullmode, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'cenwave':  self.cmp_equal_parameters,
            'aperture': self.cmp_equal_parameters,
        }

class DeepLook_STISCCDTAB(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISCCDTAB, self).__init__()

        self.mode_fields = {
            'ccdamp': self.cmp_equal_parameters,
            'ccdgain': self.cmp_equal_parameters,
            'ccdoffst': self.cmp_equal_parameters,
            'binaxis1': self.cmp_equal_parameters,
            'binaxis2': self.cmp_equal_parameters,
        }

class DeepLook_STISLAMPTAB(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISLAMPTAB, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'lampset': self.cmp_equal_parameters,
            'sclamp': self.cmp_equal_parameters,
        }

class DeepLook_STISMLINTAB(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISMLINTAB, self).__init__()

        self.mode_fields = {
            'detector': self.cmp_equal_parameters,
        }

class DeepLook_STISWCPTAB(DeepLook_STIS):
    def __init__(self):
        super(DeepLook_STISWCPTAB, self).__init__()

        self.mode_fields = {
            'opt_elem': self.cmp_equal_parameters,
            'detector': self.cmp_equal_parameters,
        }


#############################
#
# Rules for ACS
#
#############################


class DeepLook_ACS(DeepLook):
    """Generic class for all STIS rules
    """

    def __init__(self):
        super(DeepLook_ACS, self).__init__()

class DeepLook_ACSCCDpars(DeepLook_ACS):
    def __init__(self):
        super(DeepLook_ACSCCDpars, self).__init__()

        self.mode_fields = {
            'ccdamp':   self.cmp_equal_parameters,
            'ccdchip':  self.cmp_equal_parameters,
            'ccdgain':  self.cmp_equal_parameters,
        }


class DeepLook_ACSDetector(DeepLook_ACS):
    def __init__(self):
        super(DeepLook_ACSDetector, self).__init__()

        self.mode_fields = {
            'detector': self.cmp_equal_parameters,
        }


class DeepLook_ACSCCDTAB(DeepLook_ACSCCDpars):
    def __init__(self):
        super(DeepLook_ACSCCDTAB, self).__init__()

        self.mode_fields.update({
            'binaxis1': self.cmp_equal_parameters,
            'binaxis2': self.cmp_equal_parameters,
        })

#############################
#
# Rules for WFC3
#
#############################


class DeepLook_WFC3(DeepLook):
    """Generic class for all STIS rules
    """

    def __init__(self):
        super(DeepLook_WFC3, self).__init__()


class DeepLook_WFC3BPIXTAB(DeepLook_WFC3):
    def __init__(self):
        super(DeepLook_WFC3BPIXTAB, self).__init__()

        self.mode_fields = {
            'ccdchip':  self.cmp_equal_parameters,
        }


###############
#
# Rule lookup  table
#
################

DeepLook.rules = {
    'cos_badttab':   DeepLook_Default,
    'cos_bpixtab':   DeepLook_COSSegment,
    'cos_brftab':    DeepLook_Default,
    'cos_brsttab':   DeepLook_COSSegment,
    'cos_deadtab':   DeepLook_COSSegment,
    'cos_disptab':   DeepLook_COSDISPTAB,
    'cos_fluxtab':   DeepLook_COSFullmode,
    'cos_gsagtab':   DeepLook_Default,
    'cos_hvtab':     DeepLook_Default,
    'cos_lamptab':   DeepLook_COSLAMPTAB,
    'cos_phatab':    DeepLook_COSOpt_elem,
    'cos_proftab':   DeepLook_COSFullSegment,
    'cos_spwcstab':  DeepLook_COSFullmode,
    'cos_tdstab':    DeepLook_COSTDSTAB,
    'cos_tracetab':  DeepLook_COSFullSegment,
    'cos_twozxtab':  DeepLook_COSFullSegment,
    'cos_walktab':   DeepLook_COSSegment,
    'cos_wcptab':    DeepLook_COSOpt_elem,
    'cos_xtractab':  DeepLook_COSFullmode,

    'stis_apdestab': DeepLook_STISaperture,
    'stis_apertab':  DeepLook_STISaperture,
    'stis_bpixtab':  DeepLook_STISopt_elem,
    'stis_ccdtab':   DeepLook_STISCCDTAB,
    'stis_cdstab':   DeepLook_STISopt_elem,
    'stis_crrejtab': DeepLook_Default,
    'stis_disptab':  DeepLook_STIScenwave,
    'stis_echsctab': DeepLook_STISopt_elem,
    'stis_exstab':   DeepLook_STISopt_elem,
    'stis_gactab':   DeepLook_Default,
    'stis_halotab':  DeepLook_STISopt_elem,
    'stis_idctab':   DeepLook_Default,
    'stis_inangtab': DeepLook_Default,
    'stis_lamptab':  DeepLook_STISLAMPTAB,
    'stis_mlintab':  DeepLook_STISMLINTAB,
    'stis_mofftab':  DeepLook_Default,
    'stis_pctab':    DeepLook_Default,
    'stis_phottab':  DeepLook_STIScenwave,
    'stis_riptab':   DeepLook_STISopt_elem,
    'stis_sdctab':   DeepLook_STISfullmode,
    'stis_sptrctab': DeepLook_STIScenwave,
    'stis_srwtab':   DeepLook_STISopt_elem,
    'stis_tdctab':   DeepLook_Default,
    'stis_tdstab':   DeepLook_STISopt_elem,
    'stis_teltab':   DeepLook_STISopt_elem,
    'stis_wcptab':   DeepLook_STISWCPTAB,
    'stis_xtractab': DeepLook_STISfullmode,

    'acs_atodtab':   DeepLook_ACSCCDpars,
    'acs_bpixtab':   DeepLook_ACSCCDpars,
    'acs_ccdtab':    DeepLook_ACSCCDTAB,
    'acs_crrejtab':  DeepLook_Default,
    'acs_idctab':    DeepLook_Default,
    'acs_imphttab':  DeepLook_Default,
    'acs_mdriztab':  DeepLook_Default,
    'acs_mlintab':   DeepLook_ACSDetector,
    'acs_oscntab':   DeepLook_Default,
    'acs_pctetab':   DeepLook_Default,
    'acs_spottab':   DeepLook_Default,

    'wfc3_atodtab':  DeepLook_ACSCCDpars,
    'wfc3_bpixtab':  DeepLook_WFC3BPIXTAB,
    'wfc3_ccdtab':   DeepLook_ACSCCDTAB,
    'wfc3_crrejtab': DeepLook_Default,
    'wfc3_idctab':   DeepLook_Default,
    'wfc3_imphttab': DeepLook_Default,
    'wfc3_mdriztab': DeepLook_Default,
    'wfc3_oscntab':  DeepLook_Default,
}
