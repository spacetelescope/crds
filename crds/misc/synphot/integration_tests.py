import os
import shutil
from contextlib import contextmanager
import warnings
from multiprocessing import Pool

from astropy.io import fits

from crds.core import rmap, log
from crds import config
from . import utils


class SynphotIntegrationTestBase:
    """
    Base class for synphot integration tests.
    """
    def __init__(
        self,
        context,
        graph_file=None,
        throughput_lookup_file=None,
        thermal_lookup_file=None,
        delivered_throughput_files=None,
        delivered_thermal_files=None
    ):
        self.context = context

        if graph_file is None:
            self.graph_file = utils.get_cache_path(context, utils.GRAPH_REFTYPE)
        else:
            self.graph_file = graph_file

        if throughput_lookup_file is None:
            self.throughput_lookup_file = utils.get_cache_path(context, utils.THROUGHPUT_LOOKUP_REFTYPE)
        else:
            self.throughput_lookup_file = throughput_lookup_file

        if thermal_lookup_file is None:
            self.thermal_lookup_file = utils.get_cache_path(context, utils.THERMAL_LOOKUP_REFTYPE)
        else:
            self.thermal_lookup_file = thermal_lookup_file

        if delivered_throughput_files is None:
            self.delivered_throughput_files = []
        else:
            self.delivered_throughput_files = delivered_throughput_files

        if delivered_thermal_files is None:
            self.delivered_thermal_files = []
        else:
            self.delivered_thermal_files = delivered_thermal_files

        self.imap = rmap.asmapping(context).get_imap(utils.SYNPHOT_INSTRUMENT)

        self.throughput_compname_to_path = self._build_compname_to_path(
            utils.THROUGHPUT_REFTYPE,
            self.delivered_throughput_files
        )

        self.thermal_compname_to_path = self._build_compname_to_path(
            utils.THERMAL_REFTYPE,
            self.delivered_thermal_files
        )

    def _build_compname_to_path(self, reftype, delivered_files):
        """
        Build a map of component names to filesystem paths, using freshly
        delivered files by preference.
        """
        result = {}
        for file in delivered_files:
            with fits.open(file) as hdul:
                # A significant minority of existing files have uppercase COMPNAME,
                # enough that it's not worthwhile to redeliver them all.
                result[hdul[0].header["COMPNAME"].lower()] = file

        mapping = self.imap.get_rmap(reftype)
        # This is a tad brittle, in that it assumes that the COMPNAME parkey
        # will occupy the first position.
        for key, filename in mapping.selector.todict()["selections"]:
            compname = key[0].lower()
            if not compname in result:
                result[compname] = config.locate_file(filename, "hst")

        return result


@contextmanager
def _configured_stsynphot(synphot_root):
    # stsynphot will complain that its Vega spectrum file is missing
    with warnings.catch_warnings():
        try:
            import stsynphot
        except ImportError:
            raise ImportError("Missing stsynphot package.  Install the 'synphot' extras and try again.")

    original_rootdir = stsynphot.conf.rootdir
    try:
        stsynphot.conf.rootdir = synphot_root
        yield stsynphot
    finally:
        stsynphot.conf.rootdir = original_rootdir


def _test_stsynphot_mode(synphot_root, obsmode):
    result = True
    errors = []
    warns = []
    with _configured_stsynphot(synphot_root) as sts:
        try:
            with warnings.catch_warnings(record=True) as warning_list:
                sts.band(obsmode)
                for warning in warning_list:
                    warns.append("Warning from stsynphot with obsmode '{}': {}".format(obsmode, warning.message))
        except Exception as e:
            errors.append("Exception from stsynphot with obsmode '{}': {}".format(obsmode, repr(e)))
            result = False

    return result, errors, warns


class SynphotObsmodeIntegrationTest(SynphotIntegrationTestBase):
    """
    Test synphot files by constructing stsynphot objects from the
    observation mode strings in the obsmode reference file.  Requires
    that stsynphot be installed.
    """
    def __init__(
        self,
        context,
        synphot_root,
        obsmodes_file=None,
        link=False,
        processes=1,
        batch_size=100,
        **kwargs
    ):
        super().__init__(context, **kwargs)

        self.synphot_root = synphot_root

        if obsmodes_file is None:
            self.obsmodes_file = utils.get_cache_path(self.context, utils.OBSMODES_REFTYPE)
        else:
            self.obsmodes_file = obsmodes_file

        self.link = link
        self.processes = processes
        self.batch_size = 100

    def populate_synphot_root(self):
        """
        Copy or link the full set of synphot files to synphot_root, with
        newly delivered files overlaid.
        """
        os.makedirs(self.synphot_root, exist_ok=True)
        os.makedirs(utils.get_mtab_path(self.synphot_root), exist_ok=True)
        for instrument in utils.ALL_INSTRUMENTS:
            os.makedirs(utils.get_instrument_path(self.synphot_root, instrument), exist_ok=True)

        self.link_or_copy_table(utils.GRAPH_REFTYPE, self.graph_file)
        self.link_or_copy_table(utils.THROUGHPUT_LOOKUP_REFTYPE, self.throughput_lookup_file)
        self.link_or_copy_table(utils.THERMAL_LOOKUP_REFTYPE, self.thermal_lookup_file)

        for component, path in self.throughput_compname_to_path.items():
            self.link_or_copy_component(component, path)

        for component, path in self.thermal_compname_to_path.items():
            self.link_or_copy_component(component, path)

    def run(self, progress_callback=None):
        """
        Create stsynphot bandpass objects from the observation modes in the obsmodes file.
        Emits appropriate log messages and returns True if validations succeed,
        False if there's an error.
        """

        failed = 0
        with fits.open(self.obsmodes_file) as hdul:
            total_modes = len(hdul[-1].data)
            log.info("Creating bandpass objects from {} observation modes".format(total_modes))

            if self.processes > 1:
                with Pool(processes=self.processes) as pool:
                    for start_index in range(0, total_modes, self.batch_size):
                        end_index = start_index + self.batch_size
                        results = pool.starmap(
                            _test_stsynphot_mode,
                            [(self.synphot_root, m) for m in hdul[-1].data["OBSMODE"][start_index:end_index]]
                        )
                        for i, (result, errors, warns) in enumerate(results):
                            if not result:
                                failed += 1
                            for warning in warns:
                                log.warning(warning)
                            for error in errors:
                                log.error(error)

                            if progress_callback:
                                progress_callback(start_index + i + 1, total_modes)
            else:
                for i, obsmode in enumerate(hdul[-1].data["OBSMODE"]):
                    result, errors, warns = _test_stsynphot_mode(self.synphot_root, obsmode)
                    if not result:
                        failed += 1
                    for warning in warns:
                        log.warning(warning)
                    for error in errors:
                        log.error(error)

                    if progress_callback:
                        progress_callback(i + 1, total_modes)

        if failed > 0:
            log.info("{} / {} observation modes failed".format(failed, total_modes))
        else:
            log.info("Congratulations, all observation modes succeeded!")

        return failed == 0

    def link_or_copy_component(self, component, source):
        source_basename = os.path.basename(source)
        instrument = utils.get_instrument(component)
        dest = os.path.join(utils.get_instrument_path(self.synphot_root, instrument), source_basename)
        self.link_or_copy(source, dest)

    def link_or_copy_table(self, reftype, source):
        # Don't use the original filename here, in case a replacement
        # graph or lookup was uploaded with an unusual name.
        if reftype == utils.GRAPH_REFTYPE:
            basename = "test_tmg.fits"
        elif reftype == utils.THROUGHPUT_LOOKUP_REFTYPE:
            basename = "test_tmc.fits"
        else:
            basename = "test_tmt.fits"
        dest = os.path.join(utils.get_mtab_path(self.synphot_root), basename)
        self.link_or_copy(source, dest)

    def link_or_copy(self, source, dest):
        if os.path.exists(dest):
            return

        if self.link:
            os.link(source, dest)
        else:
            shutil.copy(source, dest)


class SynphotCoreIntegrationTest(SynphotIntegrationTestBase):
    """
    Perform additional validations on the full ensemble of synphot files.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        """
        Combine newly delivered files with existing synphot files and validate
        the group for consistency.  Emits appropriate log messages and returns
        True if validations succeed, False if there's an error.
        """
        graph = fits.open(self.graph_file)[-1].data
        graph_throughput_compnames = set(graph["COMPNAME"])
        graph_thermal_compnames = set(graph["THCOMPNAME"])

        throughput_lookup = fits.open(self.throughput_lookup_file)[-1].data
        throughput_lookup_compnames = set(throughput_lookup["COMPNAME"])

        thermal_lookup = fits.open(self.thermal_lookup_file)[-1].data
        thermal_lookup_compnames = set(thermal_lookup["COMPNAME"])

        result = self.check_compname_agreement(
            "TMG COMPNAME",
            graph_throughput_compnames,
            set(),
            "TMC COMPNAME",
            throughput_lookup_compnames,
            set()
        )

        result = self.check_compname_agreement(
            "TMG THCOMPNAME",
            graph_thermal_compnames,
            utils.KNOWN_MISSING_GRAPH_THERMAL_COMPONENTS,
            "TMT COMPNAME",
            thermal_lookup_compnames,
            utils.KNOWN_MISSING_THERMAL_LOOKUP_COMPONENTS
        ) and result

        result = self.check_compname_agreement(
            "TMG COMPNAME",
            graph_throughput_compnames,
            set(),
            "throughput table COMPNAME",
            set(self.throughput_compname_to_path.keys()),
            utils.KNOWN_MISSING_THROUGHPUT_COMPONENTS
        ) and result

        result = self.check_compname_agreement(
            "TMG THCOMPNAME",
            graph_thermal_compnames,
            utils.KNOWN_MISSING_GRAPH_THERMAL_COMPONENTS,
            "thermal table COMPNAME",
            set(self.thermal_compname_to_path.keys()),
            utils.KNOWN_MISSING_THERMAL_COMPONENTS.union(utils.KNOWN_MISSING_THERMAL_LOOKUP_COMPONENTS)
        ) and result

        result = self.check_filenames(
            "TMC",
            throughput_lookup,
            self.throughput_compname_to_path
        ) and result

        result = self.check_filenames(
            "TMT",
            thermal_lookup,
            self.thermal_compname_to_path
        ) and result

        return result

    def check_compname_agreement(
        self,
        description_a,
        compnames_a,
        known_missing_a,
        description_b,
        compnames_b,
        known_missing_b,
    ):
        """
        Check and report any differences between two sets of component names.
        """
        result = True

        log.info("Checking for components present in {} but missing from {}".format(
            description_a, description_b
        ))
        missing_from_b = (compnames_a - compnames_b) - known_missing_b
        if len(missing_from_b) > 0:
            missing_compnames = ", ".join(missing_from_b)
            message = "Components present in {} but missing from {}: {}".format(
                description_a, description_b, missing_compnames
            )
            log.error(message)
            result = False

        log.info("Checking for components present in {} but missing from {}".format(
            description_b, description_a
        ))
        missing_from_a = (compnames_b - compnames_a) - known_missing_a
        if len(missing_from_a) > 0:
            missing_compnames = ", ".join(missing_from_a)
            message = "Components present in {} but missing from {}: {}".format(
                description_b, description_a, missing_compnames
            )
            log.error(message)
            result = False

        return result

    def check_filenames(self, description, lookup, compname_to_path):
        """
        Check that lookup filenames are correct.
        """
        result = True

        log.info("Confirming correctly formed {} filenames".format(description))
        for row in lookup:
            lookup_filename = utils.get_lookup_filename(
                row["COMPNAME"],
                os.path.basename(compname_to_path[row["COMPNAME"]])
            )
            if lookup_filename != row["FILENAME"]:
                log.error(
                    "Malformed {} filename, expected '{}', found '{}'".format(
                        description, lookup_filename, row["FILENAME"]
                    )
                )
                result = False

        return result
