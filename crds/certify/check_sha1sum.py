"""This module contains functions for checking for identical existing files on
the CRDS server.
"""
import os.path

from crds import client
from crds.core import utils, log
from crds.core.exceptions import DuplicateSha1sumError

def check_sha1sums(filepaths, observatory=None):
    """Given a list of filepaths which nominally will be submitted
    to CRDS for project `observatory`,  check to see if any are
    bit-for-bit identical with existing files as determined by
    the CRDS server's catalog and sha1sum matching.

    filepaths  [str, ...]   paths of files to be checked for preexistence
    observartory   str    e.g. 'hst' or 'jwst'

    Returns    count of duplicate files
    """
    log.info("Checking local file sha1sums vs. CRDS server to identify files already in CRDS.")
    sha1sums = get_all_sha1sums(observatory)
    for filepath in filepaths:
        check_sha1sum(filepath, sha1sums, observatory)

def check_sha1sum(filepath, sha1sums=None, observatory=None):
    """Check to see if the sha1sum of `filepath` is identical to any
    of the files mentioned in `sha1sums`.

    Return 1   IFF `filepath` is a duplicate of an existing CRDS file.
    Otherwise   0
    """
    if sha1sums is None:
        sha1sums = get_all_sha1sums(observatory)
    sha1sum = utils.checksum(filepath)
    log.verbose("Checking file", repr(filepath), "with sha1sum", repr(sha1sum),
                "for duplication on CRDS server.")
    if sha1sum in sha1sums:
        raise DuplicateSha1sumError(
            "File", repr(os.path.basename(filepath)),
            "is identical to existing CRDS file", repr(sha1sums[sha1sum]))

def get_all_sha1sums(observatory=None):
    """Query the CRDS server for sha1sums for all existing files.

    Returns {sha1sum : name, ...}
    """
    if observatory is None:
        observatory = client.get_default_observatory()
    fileinfo = client.get_file_info_map(
        observatory, fields=["sha1sum"])
    sha1sums = { info["sha1sum"]: name
                 for name,info in fileinfo.items() }
    log.verbose("Retrieved", len(sha1sums), "sha1sums for existing CRDS files.")
    return sha1sums
