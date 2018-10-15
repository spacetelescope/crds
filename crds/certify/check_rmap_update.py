"""
This module performs trial rmap updates in the same manner the server will
do them for the purpose of revealing problems with files as they relate to
the rmap and each other.
"""

from collections import defaultdict

import crds
from crds.core import config, utils
from crds.refactoring import refactor

def organize_files(observatory, filepaths):
    """Group list of reference file paths `files` by (instrument,filekind) so 
    that hey can be inserted into the appopriate rmaps.

    Returns { (instrument, filekind) : [ reference, ...], ... }
    """
    organized = defaultdict(list)
    for file in filepaths:
        if config.is_reference(file):
            instr, filekind = utils.get_file_properties(observatory, file)
            organized[(instr, filekind)].append(file)
    return organized

def check_rmap_updates(observatory, context, filepaths):
    """Do a test insertion of list of reference file paths `filepaths` into 
    the appropriate rmaps under CRDS `context` for the purpose of detecting
    problems with adding the filepaths to context as a group.

    The primary problem detected by the test insertion will be overlapping
    match cases which can happen within `filepaths` or between a new reference
    and an existing reference in the rmap.

    These really come in two forms:

    1. In the extreme, a perfectly overlapping case will result in only one of
    two equivalent references being added to the rmap.   The first of the two
    added references is replaced by the second.

    2. A more pernicious case occurs when two categories overlap,  but one is
    a proper subset of the other.  In this instance,  because the categories
    are different,  a replacement does not occur,  but at runtime whenever a
    dataset satisfying the more restrictive category occurs,  both categories
    match with equal weight;  this results in an undesirable search ambiguity.
    """
    organized = organize_files(observatory, filepaths)
    pmap = crds.get_cached_mapping(context)
    for instrument, filekind in organized:
        for filepaths2 in organized[instrument, filekind]:
            old_rmap = pmap.get_imap(instrument).get_rmap(filekind)
            new_rmap = "/tmp/" + old_rmap
            refactor.rmap_insert_references(old_rmap, new_rmap, filepaths2)
