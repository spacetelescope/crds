"""Utilities around determinig staleness of the archive"""
import os

import logging
import gzip
from pathlib import Path
import re

from numpy.ma.core import MaskedConstant

from astropy.table import vstack
from astropy.time import Time, TimeDelta
from astroquery.mast import Mast
from crds.list import ListScript
from jwst.lib.file_utils import pushdir
from jwst.lib.suffix import remove_suffix

# Configure logging
logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)
logger.addHandler(logging.NullHandler())

# Default start search time is essentially start-of-mission
DEFAULT_START_TIME = '2022-01-01'


class AffectedDatasets(dict):
    """Collecting and managing the affected dataset lists

    Basic implementation is a dict where the key is initial
    "from" context and the value is a set of all the affected datasets
    when starting from the `key` context.

    The reprocessing folder has the following structure. It contains folders with
    the naming convention

    yyyy-mm-dd:hh:mm:ss_fromctx_toctx

    where `fromctx` and `toctx` are the from and to contexts used to created the
    affected dataset list. Within each folder are four files

    - affected_ids.txt.gz
    - bestrefs.status
    - bestrefs_err.txt.gz
    - bestrefs_err_truncated.txt.gz

    The 'bestrefs*' files contain the status and logs of the `crds bestrefs` execution.
    The 'afffected_ids.txt.gz' contains the list of affected dataset ids.

    Attributes
    ----------
    self : dict
        The list of affected datasets by starting context.

    contexts : [str[,...]]
        Ordered lists of starting contexts
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.contexts = None

    def is_affected(self, datasets, start_context, end_context):
        """Determine if any datasets are in an affected dataset list starting from context

        Parameters
        ----------
        datasets : [str[,...]]
            List of dataset ids to check for.

        start_context : str
            CRDS context to start with. Can have the full string such as 'jwst_0123.pmap'
            or just the number, '0123'.

        end_context : str
            CRDS final context. Can have the full string such as 'jwst_0123.pmap'
            or just the number, '0123'.

        Returns
        -------
        is_affected : [str[,...]]
            Dataset ids that were actually affected
        """
        regex = re.compile(r'(jwst_)*(\d+)(\..+)*')
        start_context = regex.fullmatch(start_context).group(2)
        end_context = regex.fullmatch(end_context).group(2)
        start_idx = self.contexts.index(start_context)
        try:
            end_idx = self.contexts.index(end_context)
        except ValueError:
            end_idx = len(self)

        affected = set()
        for context in self.contexts[start_idx:end_idx]:
            affected.update(self[context] & datasets)

        return affected

    def read(self, reprocessing_path=None):
        """Read in all the affected dataset info from a CRDS reprocessing folder

        Parameters
        ----------
        reprocessing_path : str, pathlib.Path, None
            The path to the folder where the affected datasets reprocessing reports
            are located. If None, the environment variable CRDS_REPROCESSING
            is used.
        """
        reprocessing_path = env_override('CRDS_REPROCESSING', reprocessing_path)
        with pushdir(reprocessing_path) as rp_path:
            for path in rp_path.iterdir():
                logger.debug('Path: %s', path)
                if not path.is_dir():
                    logger.debug('Path is not a dir')
                    continue
                try:
                    _, from_ctx, to_ctx  = path.stem.split('_')
                except ValueError:
                    logger.debug('Cannot get contexts')
                    continue
                try:
                    with gzip.open(path / 'affected_ids.txt.gz', 'rb') as ids_file:
                        try:
                            ids = ids_file.read().decode('utf-8').replace('\n', ' ')
                        except TypeError:
                            logger.debug('Cannot read "affected_ids.txt.gz')
                            continue
                except FileNotFoundError:
                    logger.debug('No "affected_ids.txt.gz" found')
                    continue
                self[f'{int(from_ctx):0>4}'] = set(ids.split(' '))
        self.contexts = list(self.keys())
        self.contexts.sort()


class MastCrdsCtx:
    """Retrieve the CRDS context for all exposures in a given timeframe

    Parameters
    ----------
    instrument : str
        The instrument being searched for.

    start_time, end_time : astropy.time.Time
        The time range being searched.

    time_chunk : astropy.time.TimeDelta
        The periods over which the queries to MAST are made.
        Default is 30 days.

    Attributes
    ----------
    Same as the Parameters with the following additions.

    contexts : astropy.table.Table
        The table of exposures and their CRDS_CTX header values

    service : Mast.Jwst.Filtered.*
        The MAST service in use.

    Examples
    --------
    >>> mast_nircam = MastCrdsCtx('NIRCam', start_time='2023-01-01', end_time='2023-01-15')
    >>> mast_nircam.instrument
    'nircam'
    >>> mast_nircam.start_time
    <Time object: scale='utc' format='iso' value=2023-01-01 00:00:00.000>
    >>> mast_nircam.end_time
    <Time object: scale='utc' format='iso' value=2023-01-15 00:00:00.000>
    >>> mast_nircam.retrieve_by_chunk()
    >>> len(mast_nircam.contexts)
    13215
    """

    # Columns from MAST to retrieve
    COLUMNS = '*'

    # List of MAST services by instrument
    SERVICE = {
        'fgs': 'Mast.Jwst.Filtered.Fgs',
        'miri': 'Mast.Jwst.Filtered.Miri',
        'nircam': 'Mast.Jwst.Filtered.Nircam',
        'niriss': 'Mast.Jwst.Filtered.Niriss',
        'nirspec': 'Mast.Jwst.Filtered.Nirspec',
    }

    def __init__(self, instrument, start_time=DEFAULT_START_TIME, end_time=None, time_chunk=TimeDelta(30, format='jd')):
        self.instrument = instrument.lower()
        if not isinstance(start_time, Time):
            start_time = Time(start_time)
        if end_time is None:
            end_time = Time.now()
        if not isinstance(end_time, Time):
            end_time = Time(end_time)
        self.start_time = start_time
        self.end_time = end_time
        self.time_chunck = time_chunk

        self.service = self.SERVICE[instrument.lower()]
        self.contexts = None

    @staticmethod
    def retrieve(instrument, start_time=DEFAULT_START_TIME, end_time=None):
        """Retrieve the context table for an instrument over a time range

        Parameters
        ----------
        instrument : str
            The instrument being searched for.

        start_time, end_time : astropy.time.Time
            The time range being searched.

        Examples
        -------
        >>> nircam_ctxs = MastCrdsCtx.retrieve('nircam', start_time='2023-01-01', end_time='2023-01-15')
        >>> len(nircam_ctxs)
        13215
        """
        mcc = MastCrdsCtx(instrument, start_time=start_time, end_time=end_time)
        mcc.retrieve_by_chunk()
        return mcc.contexts

    def retrieve_by_chunk(self):
        """Retrieve the exposure/crds context table from MAST

        Attributes Modified
        -------------------
        contexts : astropy.table.Table
            The table of exposures and their CRDS_CTX header values
        """
        date_filter = {'date_obs_mjd': None}
        params = {'columns': self.COLUMNS, 'filters': date_filter}

        period = self.start_time
        results = []
        while period < self.end_time:
            period_end = period + self.time_chunck
            if period_end > self.end_time:
                period_end = self.end_time
            logger.debug('MAST query %s %s-%s', self.service, period, period_end)
            date_filter['date_obs_mjd'] = [set_mjd_range(period, period_end)]
            params['filters'] = set_params(date_filter)
            results.append(Mast.service_request(self.service, params))
            period = period_end
        self.contexts = vstack(results)


class StaleByContext:
    """Determine staleness of exposures by exposure CRDS context

    The one CRDS-related piece of information that is available in
    the MAST JWST keyword search is 'CRDS_CTX'. Hence, the staleness
    will be determined solely on context comparison. If an exposure's
    context is not current, a search of all the affected dataset reports
    starting with the exposure's context, will be made to see if the
    exposure dataset id had been identified as affected. If it does
    appear, that exposure will be marked stale.

    Notes
    -----
    The existing affected dataset reports are being used for efficiency
    reasons. If not available, the `crds.bestrefs` function can be
    called directly to get the information. However, making the calls
    can take a long time.

    Attributes
    ----------
    affected_datasets : AffectedDatasets
        The affected datasets information as generated by the CRDS server.

    end_context : str or None
        The defined final context to be compared to. If None, this will
        get the current operational context.

    is_affected : set(str(,...))
        Set of datasets that are in the affected dataset lists.
        Populated by methods `archive_state` and `archive_state_instrument`.

    stale_contexts : set(str(,...))
        Set of stale contexts found.
        Populated by methods `archive_state` and `archive_state_instrument`.

    total_exposures : int
        Total exposures examined.
        Populated by methods `archive_state` and `archive_state_instrument`.

    uncalibrated_datasets : set(str(,...))
        List of datasets that have no CRDS context.
        Populated by methods `archive_state` and `archive_state_instrument`.
    """

    def __init__(self, affected_datasets=None, end_context=None):
        self.affected_datasets = affected_datasets
        self.end_context = end_context

        self.reset()

    @property
    def affected_datasets(self):
        if self._ad is None:
            self._ad = AffectedDatasets()
            self._ad.read()
        return self._ad

    @affected_datasets.setter
    def affected_datasets(self, affected_datasets):
        self._ad = affected_datasets

    @property
    def end_context(self):
        if self._endctx is None:
            cmd = ['crds.list', '--status']
            script = ListScript(cmd)
            script()
            self._endctx = script.default_context
        return self._endctx

    @end_context.setter
    def end_context(self, end_context):
        self._endctx = end_context

    def archive_state(self, instruments=None, start_time=DEFAULT_START_TIME, end_time=None, reset=True):
        """Determine state of archive

        Given a list of instruments and time range to examine, determine
        the state of all exposures with respect to possible staleness.

        Parameters
        ----------
        instruments : [str[,...]] or None
            List of instruments to look for. List can contain any of following strings.
            Case is not significant. If None, all instruments are examined.
            - fgs
            - miri
            - nircam
            - niriss
            - nirspec

        start_time, end_time : str, astropy.Time, or None
            Time period to examine. `start_time` cannot be None.
            `end_time`, if None, will be the current date.

        reset : bool
            Reset the result attributes.

        Attributes Modified
        -------------------
        is_affected : set(str(,...))
            Set of datasets that are in the affected dataset lists.

        stale_contexts : set(str(,...))
            Set of stale contexts found.

        uncalibrated_datasets : set(str(,...))
            List of datasets that have no CRDS context.
        """
        if reset:
            self.reset()

        if instruments is None:
            instruments = ['fgs', 'miri', 'nircam', 'niriss', 'nirspec']

        for instrument in instruments:
            self.archive_state_instrument(instrument, start_time, end_time)

    def archive_state_instrument(self, instrument, start_time, end_time, reset=False):
        """Determine staleness by instrument

        Parameters
        ----------
        instrument : str
            The instrument to look for. The following are allowed:
            - fgs
            - miri
            - nircam
            - niriss
            - nirspec

        start_time, end_time : astropy.Time
            Time period to examine. `start_time` cannot be None.
            `end_time`, if None, will be the current date.

        reset : bool
            Reset the result attributes.

        Attributes Modified
        -------------------
        is_affected : set(str(,...))
            Set of datasets that are in the affected dataset lists.

        stale_contexts : set(str(,...))
            Set of stale contexts found.

        uncalibrated_datasets : set(str(,...))
            List of datasets that have no CRDS context.
        """
        logger.info('Working instrument %s over period of %s-%s', instrument, start_time, end_time)
        if reset:
            self.reset()

        exposures = MastCrdsCtx.retrieve(instrument, start_time, end_time)
        self.total_exposures += len(exposures)

        # First result: List of uncalibrated exposures.
        uncalibrated_datasets = {filename_to_datasetid(exposure)
                                 for exposure, context in exposures['filename', 'crds_ctx']
                                 if isinstance(context, MaskedConstant)}

        # Start filtering down to find the stale exposures.
        old_exposures_mask = exposures['crds_ctx'] < self.end_context
        old_exposures = exposures[old_exposures_mask]
        stale_contexts = {context for context in old_exposures['crds_ctx'] if not isinstance(context, MaskedConstant)}

        # Determine whether any stale exposures are in an affected dataset report. If so,
        # mark as truly stale.
        is_affected = set()
        for context in stale_contexts:
            context_mask = old_exposures['crds_ctx'] == context
            current_exposures = old_exposures[context_mask]

            # Create list of formal dataset ids.
            datasets = {filename_to_datasetid(filename) for filename in current_exposures['filename']}

            # Check against affected datasets
            try:
                is_affected.update(self.affected_datasets.is_affected(datasets, context, self.end_context))
            except ValueError as exception:
                logger.warning('Context range %s-%s is not available in the affected datasets archive', context, self.end_context)
                logger.debug('Reason: ', exc_info=exception)
                continue

        # Update results
        self.uncalibrated_datasets.update(uncalibrated_datasets)
        self.stale_contexts.update(stale_contexts)
        self.is_affected.update(is_affected)

    def reset(self):
        """Reset the result attributes

        Attributes Modified
        -------------------

        is_affected : set(str(,...))
            Set of datasets that are in the affected dataset lists.
            Populated by methods `archive_state` and `archive_state_instrument`.

        stale_contexts : set(str(,...))
            Set of stale contexts found.
            Populated by methods `archive_state` and `archive_state_instrument`.

        uncalibrated_datasets : set(str(,...))
            List of datasets that have no CRDS context.
            Populated by methods `archive_state` and `archive_state_instrument`.
        """
        self.is_affected = set()
        self.stale_contexts = set()
        self.total_exposures = 0
        self.uncalibrated_datasets = set()


# #########
# Utilities
# #########
def env_override(envvar, override=None):
    """Use environment variable unless override is specified

    Parameters
    ----------
    envvar : str
        Environment variable to use

    override : obj
        If specified, the value to use

    Returns
    -------
    value : obj or None
        Either `override`, the value of the environment variable `envvar`, or None

    Examples
    --------
    >>> env_override('StalePytestVar', 'myvalue')
    'myvalue'
    >>> import os
    >>> os.environ['StalePytestVar'] = 'env value'
    >>> env_override('StalePytestVar', 'myvalue')
    'myvalue'
    >>> env_override('StalePytestVar')
    'env value'
    """
    value = override
    if value is None:
        value = os.environ.get(envvar, None)

    return value

def filename_to_datasetid(name):
    """Convert a exposure filename to its dataset id

    Names such as

        jw01933001004_02101_00010_nrcalong_rate.fits

    have the dataset id of

        jw01933001004_02101_00010.nrcalong

    Parameters
    ----------
    name : str
        Filename

    Returns
    -------
    datasetid : str
        The datasetid

    Examples
    --------
    >>> filename_to_datasetid('jw02738006001_04101_00004_nrca1_i2d.fits')
    'jw02738006001_04101_00004.nrca1'
    >>> filename_to_datasetid('jw02738-o006_t002_nircam_clear-f444w_segm.fits')
    'jw02738-o006_t002_nircam'
    >>> filename_to_datasetid('hello')
    ValueError('Name base "hello" does not match a Level2 or Level3 name pattern')
    """
    l2pattern = r'(jw.{11}_.{5}_.{5})_(.+)'
    l3pattern = r'(jw.{5}-[aco].{3,4}_.+?_.+?)_.+'

    base = Path(name).stem
    base = remove_suffix(base)[0]
    match = re.fullmatch(l2pattern, base)
    if match:
        id = match.group(1) + '.' + match.group(2)
        return id
    match = re.fullmatch(l3pattern, base)
    if match:
        return match.group(1)
    return ValueError(f'Name base "{base}" does not match a Level2 or Level3 name pattern')


def set_mjd_range(min, max):
    """Set time range in MJD given limits

    Parameters
    ----------
    min, max: astropy.time.Time
        The time range to define.
    """
    return {
        "min": min.mjd,
        "max": max.mjd
    }


def set_params(parameters):
    return [{"paramName" : p, "values" : v} for p, v in parameters.items()]
