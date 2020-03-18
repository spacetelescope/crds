"""
Special-purpose validators used only with HST synphot files.
"""
import re
import os

import numpy as np

import crds
from crds import data_file
from crds.core import log
from crds.misc.synphot import utils

from .core import Validator


class SynphotGraphValidator(Validator):
    """
    Custom validations for synphot graph table (tmgtab) files.
    """
    def check_header(self, filename, header):
        with data_file.fits_open(filename) as hdul:
            result = self._check_connectivity(hdul)
            result = self._check_direction(hdul) and result
            return result

    def _check_connectivity(self, hdul):
        """
        Confirm that all rows in the graph can be reached by following paths
        starting at innode = 1.
        """

        # This is inefficient, since the subpaths are often shared,
        # but graphs don't get certified regularly, and it seems worthwhile
        # to sacrifice a little speed to keep the code simple.
        def _get_visited_indexes(graph, innode=1, seen_nodes=None):
            if seen_nodes is None:
                seen_nodes = set()

            if innode in seen_nodes:
                # Cycles will result in an error in _check_direction, so
                # we don't need to log an error here.
                return set()

            seen_nodes = seen_nodes.union({innode})

            selected = graph["INNODE"] == innode

            visited = set(np.where(selected)[0])

            for outnode in np.unique(graph[selected]["OUTNODE"]):
                visited.update(_get_visited_indexes(graph, outnode, seen_nodes=seen_nodes))

            return visited

        graph = hdul[-1].data
        visited_indexes = _get_visited_indexes(graph)

        result = True
        if len(visited_indexes) < len(graph):
            missing_indexes = set(range(len(graph))) - visited_indexes
            log.error(
                "TMG contains disconnected rows at indexes:",
                ", ".join(str(i) for i in missing_indexes)
            )
            result = False

        return result

    def _check_direction(self, hdul):
        """
        Confirm that all rows in the graph point to higher INNODE values
        than themselves, which prevents cycles.
        """
        graph = hdul[-1].data
        result = True
        if not (graph["INNODE"] < graph["OUTNODE"]).all():
            log.error(
                "TMG contains rows with INNODE >= OUTNODE."
            )
            result = False

        return result


class SynphotLookupValidator(Validator):
    """
    Custom validations for synphot throughput component lookup
    table (tmctab) and thermal component lookup (tmctab) files.
    """
    def check_header(self, filename, header):
        with data_file.fits_open(filename) as hdul:
            return self._check_filenames(hdul)

    def _check_filenames(self, hdul):
        """
        Confirm that values in the FILENAME column are prefixed
        with a valid path variable, and are suffixed with the correct
        parametrization variable.
        """
        result = True
        for i, row in enumerate(hdul[-1].data):
            expected_path_prefix = utils.get_path_prefix(row["COMPNAME"])
            if row["FILENAME"].split("$")[0] + "$" != expected_path_prefix:
                log.error("Malformed FILENAME value at index", i, "(missing or invalid path prefix)")
                result = False

            param_keyword = utils.get_parametrization_keyword(row["COMPNAME"])
            if param_keyword is None and row["FILENAME"].endswith("]"):
                log.error("Malformed FILENAME value at index", i, "(should not be parametrized)")
                result = False
            elif param_keyword is not None and not row["FILENAME"].lower().endswith("[{}]".format(param_keyword)):
                log.error("Malformed FILENAME value at index", i, "(should be parametrized)")
                result = False

        return result


class SynphotThroughputValidator(Validator):
    """
    Custom validations for synphot component throughput table (thruput) files.
    """
    def check_header(self, filename, header):
        with data_file.fits_open(filename) as hdul:
            result = self._check_throughput_first_and_last(hdul)
            result = self._check_parametrization(hdul) and result
            result = _check_component_filename(
                self.context, utils.THROUGHPUT_REFTYPE, utils.THROUGHPUT_FILENAME_SUFFIX,
                filename, header
            ) and result
            return result

    def _check_throughput_first_and_last(self, hdul):
        """
        Confirm that the first and last values of THROUGHPUT and MJD# columns
        is zero.  Emit a warning only, since there are exceptions to this rule.
        """
        for column_name in hdul[-1].data.names:
            if column_name == "THROUGHPUT" or column_name.startswith("MJD#"):
                if not (hdul[-1].data[column_name][0] == 0.0):
                    log.warning("First value of column '{}' is not 0.0".format(column_name))
                if not (hdul[-1].data[column_name][-1] == 0.0):
                    log.warning("Last value of column '{}' is not 0.0".format(column_name))

        return True

    def _check_parametrization(self, hdul):
        """
        If the component table is parametrized, confirm that it has at least 2
        parametrized columns.
        """
        component = hdul[0].header["COMPNAME"]

        column_prefix = utils.get_parametrization_keyword(component)
        if column_prefix is not None:
            column_count = len([n for n in hdul[-1].data.names if n.lower().startswith(column_prefix)])
            if column_count < 2:
                template = "Table is parametrized by {}, but includes only {} columns with that prefix."
                log.error(template.format(column_prefix, column_count))
                return False

        return True


class SynphotThermalValidator(Validator):
    """
    Custom validations for synphot component thermal table (thermal) files.
    """
    def check_header(self, filename, header):
        return _check_component_filename(
            self.context, utils.THERMAL_REFTYPE, utils.THERMAL_FILENAME_SUFFIX,
            filename, header
        )


def _check_component_filename(context, reftype, suffix, filename, header):
    compname = header.get("COMPNAME", "").lower()
    if not compname:
        log.error("Header missing COMPNAME, unable to certify filename")
        return False

    pattern = re.compile(".*_([0-9]{3})_" + suffix + ".fits")

    match = pattern.match(os.path.basename(filename))
    if not match:
        log.error("Invalid filename: must end in _###_{}.fits".format(suffix))
        return False

    if context:
        new_version = int(match.group(1))

        original_filename = _get_synphot_filename(context, reftype, compname)
        if original_filename:
            match = pattern.match(os.path.basename(original_filename))
            if not match:
                log.warning(
                    "Previous filename '{}' does not end in _###_{}.fits, skipping version check".format(
                        original_filename, suffix
                    )
                )
                return True

            original_version = int(match.group(1))

            if new_version <= original_version:
                log.error(
                    "New filename version ({:03d}) must exceed previous version ({:03d})".format(
                        new_version, original_version
                    )
                )
                return False
        else:
            log.warning(
                "No previous file exists for COMPNAME '{}', skipping version check".format(compname)
            )

    return True


def _get_synphot_filename(context, reftype, compname):
    pmap = crds.get_pickled_mapping(context, ignore_checksum=True)
    rmap = pmap.get_imap(utils.SYNPHOT_INSTRUMENT).get_rmap(reftype)

    for key, filename in rmap.selector.todict()["selections"]:
        if key[0].lower() == compname:
            return filename

    return None
