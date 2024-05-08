"""Utilities around determinig staleness of the archive

Developer Notes
---------------
This is essentially alpha-level code to demonstrate how to determine
staleness for the JWST archive. Major work to be done is documented
in CCD-1257.

A side effect of this is that, as noted, all the potential doctest
lines are commented out.
"""
import os
import sys

from dataclasses import dataclass
import logging
from pathlib import Path
import re
from typing import Any

from numpy.ma.core import MaskedConstant

import asdf
import astropy
from astropy.table import Table, vstack
from astropy.time import Time, TimeDelta

from jwst.lib.suffix import remove_suffix

import crds.client.api as crds_api
from crds.core import cmdline, log
from crds.core.exceptions import ServiceError

# Configure logging
LOGGER = logging.getLogger(__name__)

try:
    from astroquery.mast import Mast
except ModuleNotFoundError:
    log.error('Module `astroquery` does not exist. This module will not function without it.')

# Default start search time is essentially start-of-mission
DEFAULT_START_TIME = '2022-01-01'

# First context active for the actual mission
FIRST_CONTEXT = 'jwst_0780.pmap'

# Default epilog text
EPILOG_PATH = Path(__file__).parent / 'stale_epilog.txt'


class StaleByClassScript(cmdline.Script, cmdline.UniqueErrorsMixin):
    """Command line script to determine stale datasets according to their context"""

    description = """
`stale` is the initial attempt at determining how current the calibration is for
products in the JWST archive. For this report, "staleness" is defined as those
dataset ids whose context is not current yet appear in affected dataset reports
for all operational context changes between the exposure's context and the
current context.
    """

    eplilog = """
.............................
crds.stalebycontext use cases
.............................

.......
Caching
.......
    """
    def __init__(self, *args, **argv):
        super().__init__(*args, **argv)

        ad_cache_path = None
        if self.args.cache_path:
            ad_cache_path =self.args.cache_path / 'affected_datasets_cache.asdf'
        self.ad = AffectedDatasets(cache_path=ad_cache_path)

        self.stale = StaleByContext(affected_datasets=self.ad, end_context=self.args.end_context,
                                    cache=self.args.cache_path, update_cache=self.args.update_cache)

        self.instruments = self.args.instruments
        self.start_time = self.args.start_time
        self.end_time = self.args.end_time

    def add_args(self):
        """Add command line arguments/options"""
        self.add_argument('--instruments', metavar='INSTRUMENTS',
                          help='Instruments to work on. If unspecified, all instruments are considered.',
                          nargs='+', default=None)
        self.add_argument('--end-context',
                          help='Final context to check.',
                          default=None)
        self.add_argument('--start-time',
                          help='Time of first exposure.',
                          default=DEFAULT_START_TIME, type=astropy.time.Time)
        self.add_argument('--end-time',
                          help='Time of last exposure.',
                          default=None, type=astropy.time.Time)
        self.add_argument('--cache-path',
                          help='Path to a folder to cache affected data and exposure information',
                          default=None, type=Path)
        self.add_argument('-update-cache',
                          help='Force updating of an existing cache',
                          action='store_true')
        self.add_argument('--epilog',
                          help='Epilog text to add to report (in markdown format)',
                          default=str(EPILOG_PATH), type=Path)

    def main(self):
        """Execute StaleByContext"""
        self.stale.archive_state(instruments=self.instruments,
                                 start_time=self.start_time, end_time=self.end_time)
        log.info(self.stale.report(epilog=self.args.epilog))

        return log.errors()


@dataclass
class StaleInfo:
    """Affected data for a given set of exposures"""
    exposures : Any              # Table of exposures examined.
    datasets : set               # Datasets examined.
    uncalibrated_datasets : set  # Uncalibrated datasets
    stale_contexts : set         # Contexts that have stale datasets
    stale_datasets : set                  # Stale datasets


class AffectedDatasets(dict):
    """Collecting and managing the affected dataset lists

    Basic implementation is a dict where the key is initial
    "from" context and the value is a set of all the affected datasets
    when starting from the `key` context.

    The affected datasets are retrieved from the CRDS server using
    `crds.client.api.get_affected_datasets`. The data is then simply
    re-arranged to make the dataset search easier.

    Parameters
    ----------
    cache_path : File-like or None
        Name of the ASDF file store cache all information locally.

    Attributes
    ----------
    self : dict
        The list of affected datasets by starting context.

    contexts : [str[,...]]
        Ordered lists of starting contexts

    context_history : [str[,...]]
        Ordered list of the server's context history with contexts
        that have been rolled back removed.
    """
    def __init__(self, *args, **kwargs):
        self._cache_path = kwargs.pop('cache_path', None)

        super().__init__(*args, **kwargs)
        self._context_history = None
        self._bad_contexts = []

        if self._cache_path:
            try:
                with asdf.open(self._cache_path) as af:
                    self.from_asdf(af)
            except IOError as exception:
                log.debug('Cannot access cache file', self._cache_path, 'because', exception)
                log.debug('Creating', self._cache_path)

    @property
    def contexts(self):
        """Retrieve the ordered set of context that have been ingested"""
        contexts = list(self.keys())
        contexts.sort()
        return contexts

    @property
    def context_history(self):
        """The context history from the CRDS server

        This is not simply the whole history. When operational contexts
        are rolled-back, the context order is interrupted. For affected
        dataset checking, the contexts that have been rolled back
        should not be included.

        Examples
        --------
        >>> ad = AffectedDatasets()  # doctest: +SKIP
        >>> ad.context_history[90:100]  # doctest: +SKIP
        ['jwst_0348.pmap', 'jwst_0352.pmap', 'jwst_0361.pmap', 'jwst_0391.pmap', 'jwst_0401.pmap', 'jwst_0406.pmap', 'jwst_0410.pmap', 'jwst_0414.pmap', 'jwst_0419.pmap', 'jwst_0422.pmap']

        Notes
        -----
        The context history is limited to contexts that have been active only during the
        mission. The initial context for JWST was jwst_0780.pmap
        """
        if self._context_history is None:
            history = crds_api.get_context_history('jwst')
            rolled_back = []
            for entry in history:
                context = entry[1]
                if context < FIRST_CONTEXT:
                    continue
                try:
                    last_entry = rolled_back.pop()
                except IndexError:
                    rolled_back.append(context)
                    continue
                while last_entry > context:
                    last_entry = rolled_back.pop()
                rolled_back.append(last_entry)  # Re-add the last good context
                rolled_back.append(context)
            self._context_history = rolled_back
            self.update_cache()

        return self._context_history

    def is_affected(self, datasets, start_context, end_context=None):
        """Determine if any datasets are in an affected dataset list starting from context

        Parameters
        ----------
        datasets : [str[,...]]
            List of dataset ids to check for.

        start_context : str or None
            CRDS context to start with of the form "jwst_XXXX.pmap".

        end_context : str or None
            CRDS final context of the form "jwst_XXXX.pmap".
            If None, the CRDS operational context is used.

        Returns
        -------
        is_affected : [str[,...]]
            Dataset ids that were actually affected

        Examples
        --------
        >>> ad = AffectedDatasets()  # doctest: +SKIP
        >>> ad.is_affected(['junk', 'jw01243006004_02103_00008.nrcblong'], 'jwst_1039.pmap', 'jwst_1041.pmap')  # doctest: +SKIP
        {'jw01243006004_02103_00008.nrcblong'}
        """
        if end_context is None:
            end_context = crds_api.get_default_context()
        self.retrieve(start_context, end_context=end_context)
        start_idx = self.contexts.index(start_context)
        try:
            end_idx = self.contexts.index(end_context)
        except ValueError:
            end_idx = len(self)

        log.debug('Searching contexts', start_context, '[', start_idx, ']:', end_context, '[', end_idx, ']')
        affected = set()
        for context in self.contexts[start_idx:end_idx]:
            affected.update(self[context] & set(datasets))

        return affected

    def retrieve(self, from_context, end_context=None):
        """Read in all the affected dataset info from the CRDS service.

        from_context : str or None
            CRDS context to start with of the form "jwst_XXXX.pmap".

        end_context : str or None
            CRDS final context of the form "jwst_XXXX.pmap".
            If None, the CRDS operational context is used.

        Examples
        --------
        >>> ad = AffectedDatasets()  # doctest: +SKIP
        >>> ad.retrieve('jwst_1039.pmap', 'jwst_1041.pmap')  # doctest: +SKIP
        >>> ad.contexts  # doctest: +SKIP
        ['jwst_1039.pmap', 'jwst_1040.pmap']
        >>> len(ad['jwst_1039.pmap'])  # doctest: +SKIP
        41456
        >>> len(ad['jwst_1040.pmap'])  # doctest: +SKIP
        1735
        """
        update_cache = False
        if end_context is None:
            end_context = crds_api.get_default_context()
        current_idx = self.context_history.index(from_context)
        while from_context < end_context:
            if (from_context not in self.contexts) and (from_context not in self._bad_contexts):
                try:
                    data = crds_api.get_affected_datasets('jwst', from_context)
                except ServiceError as exception:
                    log.warning('No affected dataset information for context', from_context)
                    log.warning('Affected dataset information will be incomplete.')
                    log.debug('Reason: ', exception)
                    self._bad_contexts.append(from_context)
                    update_cache = True
                else:
                    log.debug('Data read for', data['old_context'], 'to', data['new_context'])
                    self[from_context] = set(data['affected_ids'])
                    update_cache = True
            current_idx += 1
            from_context = self.context_history[current_idx]
        if update_cache:
            self.update_cache()

    def to_asdf(self):
        """Serialize to an ASDF structure

        Returns
        -------
        asdf_file : asdf.AsdfFile
        """
        tree = {'context_history': self.context_history,
                'data': dict(self),
                'bad_contexts': self._bad_contexts}
        asdf_file = asdf.AsdfFile(tree)
        return asdf_file

    def from_asdf(self, asdf_file):
        """Restore from an AsdfFile object

        Parameters
        ----------
        asdf_file : asdf.AsdfFile
        """
        self._context_history = asdf_file['context_history']
        self.update(asdf_file['data'])
        self._bad_contexts = getattr(asdf_file, 'bad_contexts', list())

    def update_cache(self):
        """If a cache is defined, update it"""
        if self._cache_path:
            af = self.to_asdf()
            af.write_to(self._cache_path)


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
    >>> mast_nircam = MastCrdsCtx('NIRCam', start_time='2023-01-01', end_time='2023-01-15')  # doctest: +SKIP
    >>> mast_nircam.instrument  # doctest: +SKIP
    'nircam'
    >>> mast_nircam.start_time  # doctest: +SKIP
    <Time object: scale='utc' format='iso' value=2023-01-01 00:00:00.000>
    >>> mast_nircam.end_time  # doctest: +SKIP
    <Time object: scale='utc' format='iso' value=2023-01-15 00:00:00.000>
    >>> mast_nircam.retrieve_by_chunk()  # doctest: +SKIP
    >>> len(mast_nircam.contexts)  # doctest: +SKIP
    13212
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
        self.start_time = make_time(start_time)
        if end_time is None:
            end_time = Time.now()
        self.end_time = make_time(end_time)
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

        Returns
        -------
        exposures : `astropy.table.Table`
            Table of exposures and all archived parameters

        Examples
        -------
        >>> nircam_ctxs = MastCrdsCtx.retrieve('nircam', start_time='2023-01-01', end_time='2023-01-15')  # doctest: +SKIP
        >>> len(nircam_ctxs)  # doctest: +SKIP
        13212
        """
        log.info('Retrieving keywords from MAST for instrument',
                 instrument, 'over period', start_time, '->', end_time)
        mcc = MastCrdsCtx(instrument, start_time=start_time, end_time=end_time)
        mcc.retrieve_by_chunk()
        log.info('\t# exposures retrieved:', len(mcc.contexts))
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
            log.debug('MAST query', self.service, period, '-', period_end)
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

    Parameters
    ----------
    affected_datasets : AffectedDatasets
        The affected datasets information as generated by the CRDS server.

    end_context : str or None
        CRDS final context of the form "jwst_XXXX.pmap".
        If None, the CRDS operational context is used.

    cache : file-like path or None
        Path to the folder where downloaded information from a CRDS server
        and the archive service is stored. If None, information will be downloaded.
        If specified and `update_cache` is False, information will be pulled
        from the servers. If `update_cache` is True, information will be pulled
        from the servers and the cache refreshed with the new data.

    update_cache : boolean
        Update the local cache.

    Attributes
    ----------
    affected_datasets : AffectedDatasets
        As documented under Parameters.

    end_context : str or None
        As documented under Parameters.

    cache : file-like path or None
        As documented under Parameters.

    stale_info : {str: StaleInfo[,...]}
        Dictionary, by instrument, of the stale dataset information

    stale_info_accumulated : StaleInfo
        Combined stale info for all instruments.

    update_cache : boolean
        As documented under Parameters.
    """

    def __init__(self, affected_datasets=None, end_context=None, cache=None, update_cache=False):
        self.affected_datasets = affected_datasets
        self.end_context = end_context
        if cache is not None:
            self.cache = Path(cache)
        else:
            self.cache = None
        self.update_cache = update_cache

        if self.cache and not self.cache.exists():
            log.info('Cache folder', self.cache ,'does not exist. Attempting to create...')
            self.cache.mkdir(parents=True, exist_ok=True)

        self.stale_info = dict()
        self.stale_info_accumulated = None
        self.start_time = None
        self.end_time = None

    @property
    def affected_datasets(self):
        if self._ad is None:
            self._ad = AffectedDatasets()
        return self._ad

    @affected_datasets.setter
    def affected_datasets(self, affected_datasets):
        self._ad = affected_datasets

    @property
    def end_context(self):
        if self._endctx is None:
            self._endctx = crds_api.get_default_context()
        return self._endctx

    @end_context.setter
    def end_context(self, end_context):
        self._endctx = end_context

    def accumulate(self):
        """Accumulate the individual instrument data into a single set of data.

        Attributes
        ----------
        stale_info_all : StaleInfo
           Updated to have the combined stale info for all instruments.
        """
        exposures = list()
        datasets = set()
        uncalibrated_datasets = set()
        stale_contexts = set()
        stale_datasets = set()
        for stale_info in self.stale_info.values():
            exposures.append(stale_info.exposures)
            datasets.update(stale_info.datasets)
            uncalibrated_datasets.update(stale_info.uncalibrated_datasets)
            stale_contexts.update(stale_info.stale_contexts)
            stale_datasets.update(stale_info.stale_datasets)
        exposures = vstack(exposures)
        self.stale_info_accumulated = StaleInfo(
            exposures=exposures,
            datasets=datasets,
            uncalibrated_datasets=uncalibrated_datasets,
            stale_contexts=stale_contexts,
            stale_datasets=stale_datasets
        )

    def archive_state(self, instruments=None, start_time=DEFAULT_START_TIME, end_time=None):
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

        start_time, end_time : Time-like, or None
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
        self.start_time = make_time(start_time)
        self.end_time = make_time(end_time)

        if instruments is None:
            instruments = ['fgs', 'miri', 'nircam', 'niriss', 'nirspec']

        for instrument in instruments:
            self.stale_info.update({instrument: self.archive_state_instrument(instrument, start_time, end_time)})

        self.accumulate()
        # report = self.report()

        # log.info(report)

    def archive_state_instrument(self, instrument, start_time, end_time):
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

        start_time, end_time : Time-like
            Time period to examine. `start_time` cannot be None.
            `end_time`, if None, will be the current date.

        Returns
        -------
        stale_info : StaleInfo
            Information about stale datasets and the related contexts.
        """
        log.info('Working instrument', instrument ,'over period of', start_time ,'->', end_time)
        exposures = self.get_exposure_pars(instrument, start_time, end_time)
        stale_info = self.archive_state_exposures(exposures)
        return stale_info

    def archive_state_exposures(self, exposures):
        """Determine staleness by instrument

        Parameters
        ----------
        exposures : astropy.table.Table
            Table of exposures to examine.

        Returns
        -------
        stale_info : StaleInfo
            Information about stale datasets and the related contexts.
        """
        log.info('# exposures to be examined:', len(exposures))

        # First result: List of uncalibrated exposures.
        uncalibrated_datasets = {filename_to_datasetid(exposure)
                                 for exposure, context in exposures['filename', 'crds_ctx']
                                 if isinstance(context, MaskedConstant)}
        log.info('\t# uncalibrated datasets:', len(uncalibrated_datasets))

        # Start filtering down to find the stale exposures.
        old_exposures_mask = exposures['crds_ctx'] < self.end_context
        old_exposures = exposures[old_exposures_mask]
        stale_contexts = {context for context in old_exposures['crds_ctx'] if not isinstance(context, MaskedConstant)}
        log.info('\tStale contexts:', stale_contexts)

        # Determine whether any stale exposures are in an affected dataset report. If so,
        # mark as truly stale.
        is_affected = set()
        datasets = set()
        for context in stale_contexts:
            context_mask = old_exposures['crds_ctx'] == context
            current_exposures = old_exposures[context_mask]

            # Create list of formal dataset ids.
            new_datasets = {filename_to_datasetid(filename) for filename in current_exposures['filename']}
            datasets.update(new_datasets)

            # Check against affected datasets
            try:
                affected = self.affected_datasets.is_affected(new_datasets, context, self.end_context)
                is_affected.update((dataset, context) for dataset in affected)
            except ValueError as exception:
                log.warning('Context range', context, '-', self.end_context,'is not available in the affected datasets archive')
                log.debug('Reason: ', exception)
                continue

        # That's all folks.
        stale_info = StaleInfo(
            exposures=exposures,
            datasets=datasets,
            uncalibrated_datasets=uncalibrated_datasets,
            stale_contexts=stale_contexts,
            stale_datasets=is_affected
        )
        log.info('\tStale datasets', len(is_affected), 'out of', len(datasets), 'total datasets')
        return stale_info

    def cache_table(self, *args, table=None, format='ecsv'):
        """Write out an astropy table to the cache

        Parameters
        ----------
        args : [str[,...]]
            List of strings defining the cache name of the file.

        table : `astropy.table.Table`
            The table to be written

        format : str
            Format of table to write.
        """
        name = cache_name(*args, format=format)
        path = self.cache / name
        table.write(path, format='ascii.' + format, overwrite=True)

    def get_exposure_pars(self, instrument, start_time=DEFAULT_START_TIME, end_time=None):
        """Get exposure parameters

        Exposure parameters are retrieved from MAST.

        If `self.cache` is defined and `self.update_cache` is False, data is
        retrieved from the cache. If `self.update_cache` is True, MAST is queried and
        the results are cached.

        Parameters
        ----------
        instrument : str
            The instrument being searched for.

        start_time, end_time : Time-like objects
            The time range being searched.

        Returns
        -------
        exposures : Time-like object
            Table of exposures and all archived parameters
        """
        self.start_time = make_time(start_time)
        self.end_time = make_time(end_time)
        update_cache = self.update_cache
        if self.cache:
            if not self.update_cache:
                try:
                    exposures = self.get_exposure_pars_cache(instrument, start_time=self.start_time, end_time=self.end_time)
                except OSError as exception:
                    log.debug('Cannot read from cache:', exception)
                    log.debug('Forcing cache updating.')
                    update_cache = True
                else:
                    return exposures

        exposures = MastCrdsCtx.retrieve(instrument, self.start_time, self.end_time)
        if self.cache and update_cache:
            self.cache_table("exposure_pars", instrument, table=exposures)
        return exposures

    def get_exposure_pars_cache(self, instrument, start_time=DEFAULT_START_TIME, end_time=None):
        """Get exposure parameters from the cache

        Parameters
        ----------
        instrument : str
            The instrument being searched for.

        start_time, end_time : Time-like objects
            The time range being searched.

        Returns
        -------
        exposures : `astropy.table.Table`
            Table of exposures and all archived parameters

        Raises
        ------
        IOError
            Usually due to missing cache file. Will also be raised if the cache,
            after filtering for the specified time range, produces zero results.
        """
        name = cache_name('exposure_pars', instrument, format='ecsv')
        path = self.cache / name
        pars = Table.read(path)
        mask = (pars['date_obs_mjd'] >= start_time.mjd) & (pars['date_obs_mjd'] <= end_time.mjd)
        filtered = pars[mask]
        if not len(filtered):
            raise IOError('Cache filtered on time range produces zero results')
        return filtered

    def report(self, epilog=EPILOG_PATH):
        """Generate Report

        Parameters
        ----------
        epilog : Path-like or None
            File containing markdown text to add to the end of the report.

        Returns
        -------
        report : str
            A Markup-based report found in the summary of a report
        """

        # Do some math before reporting.
        accumulated = self.stale_info_accumulated
        stale_dataset_percentage = len(accumulated.stale_datasets) / len(accumulated.datasets) * 100.
        oldest_stale_context = sorted(accumulated.stale_contexts)[0]
        stale_context_percentage = len(accumulated.stale_contexts) / len(self.affected_datasets.contexts) * 100.
        all_programs = set(filename[2:7]
                           for filename in accumulated.exposures['filename'])
        stale_programs = set(filename[2:7]
                             for filename, _ in accumulated.stale_datasets)
        stale_program_percentage = len(stale_programs) / len(all_programs) * 100.

        # Generate report.
        text = (
            f'Stale Report: Up to context {self.end_context}'
            '\n=========================================='
            f'\nGenerated: {Time.now}'
            '\n'
            '\nAbstract'
            '\n---------\n'
            '\nAn updated stale report has been generated during the process of finalizing the'
            '\nstale tool for operations. The original abstract is as follows:'
            '\n'
            '\n> This is the initial attempt at determining how current the calibration is for'
            '\n> products in the JWST archive. For this report, "staleness" is defined as those'
            '\n> dataset ids whose context is not current yet appear in affected dataset reports'
            '\n> for all operational context changes between the exposure\'s context and the'
            '\n> current context. Issues will be discussed and other measures of staleness will'
            '\n> be presented, though not explored.'
            '\n'
            '\nSummary'
            '\n--------\n'
            f'This report covers all exposures taken during the period of {self.start_time} through'
            f'\nto {self.end_time}. The end context is {self.end_context}. The results are as follows:'
            '\n'
            f'\n- Total exposures examined: {len(accumulated.exposures)}'
            f'\n- Total datasets examined: {len(accumulated.datasets)}'
            f'\n- Total stale datasets: {len(accumulated.stale_datasets)}'
            f'\n- Percentage stale datasets: {stale_dataset_percentage:.0f}%'
            '\n'
            f'\nA "stale" dataset is a dataset that has a context before {self.end_context} and appears in one'
            f'\nor more affected dataset lists between the dataset\'s context and {self.end_context}.'
            '\n'
            f'\nThe oldest stale context found is {oldest_stale_context}. About {stale_context_percentage:.0f}% of all operational contexts'
            '\nhave stale datasets.'
            '\n'
            f'\n{len(stale_programs)}, or {stale_program_percentage:.0f}% of all programs, have stale datasets.'
            '\n'
            '\nStale programs:'
            f'\n{stale_programs}'
            '\n'
            '\nStale datasets per instrument:'
        )

        for instrument, stale_info in self.stale_info.items():
            n_stale_datasets = len(stale_info.stale_datasets)
            n_datasets = len(stale_info.datasets)
            percentage = n_stale_datasets / n_datasets * 100.
            text += f'\n- {instrument}: {n_stale_datasets} stale datasets out of {n_datasets} ({percentage:.0f}%)'

        if epilog:
            with open(epilog, 'r') as fh:
                text +='\n\n'
                text += fh.read()

        return text


# #########
# Utilities
# #########
def cache_name(*args, format='ecsv'):
    """Create a cache name based on arguments

    Parameters
    ----------
    args : [str[,]]
        List of strings that will be used to create the file name

    format : str
        Format of file intended. This is the ".<format>" field of the file name.

    Returns
    -------
    name : str
       The file name
    """
    name = '_'.join(args)
    name = name + '.' + format
    return name


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
    >>> env_override('StalePytestVar', 'myvalue')  # doctest: +SKIP
    'myvalue'
    >>> import os  # doctest: +SKIP
    >>> os.environ['StalePytestVar'] = 'env value'  # doctest: +SKIP
    >>> env_override('StalePytestVar', 'myvalue')  # doctest: +SKIP
    'myvalue'
    >>> env_override('StalePytestVar')  # doctest: +SKIP
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
    >>> filename_to_datasetid('jw02738006001_04101_00004_nrca1_i2d.fits')  # doctest: +SKIP
    'jw02738006001_04101_00004.nrca1'
    >>> filename_to_datasetid('jw02738-o006_t002_nircam_clear-f444w_segm.fits')  # doctest: +SKIP
    'jw02738-o006_t002_nircam'
    >>> filename_to_datasetid('hello')  # doctest: +SKIP
    ValueError('Name base "hello" does not match a Level2 or Level3 name pattern')
    """
    l2pattern = r'(jw.{11}_.{5}_.+)_(.+)'
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
    msg = f'Name base "{base}" does not match a Level2 or Level3 name pattern'
    log.debug(msg)
    return ValueError(msg)

def make_time(obj=None):
    """Coerce object to an astropy.time.Time object

    Parameters
    ----------
    obj : object
        The object to coerce.

    Returns
    -------
    time : astropy.time.Time
        The object as a Time object
    """
    if obj is None:
        return Time.now()
    if not isinstance(obj, Time):
        return Time(obj)
    return obj


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


# #######################
# Command-line executable
# #######################
def main():
    """Construct and run the script,  return 1 if errors occurred, 0 otherwise."""
    errors = StaleByClassScript()()
    exit_status = int(errors > 0)  # no errors = 0,  errors = 1
    return exit_status


if __name__ == "__main__":
    sys.exit(main())
