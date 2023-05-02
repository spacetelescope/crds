"""This module is used to profile getrecommendations() and bestreds.BestrefsScript()."""

import pickle

import crds

from crds.tests.test_config import run_and_profile
from crds import data_file

def pickle_unpickle(context, data):
    p = crds.get_cached_mapping(context)
    p.get_required_parkeys()
    header = data_file.get_header(data)
    prefs = p.get_best_references(header)
    q = pickle.dumps(p)
    r = pickle.loads(q)
    rrefs = r.get_best_references(header)
    diffs = p.difference(r, include_header_diffs=True, recurse_added_deleted=True)
    assert prefs == rrefs
    assert str(p) == str(r)
    return {
        "refs": prefs == rrefs,
        "strs" : str(p) == str(r),
        "equal": p == r,
        "diffs": diffs,
        }

if __name__ == "__main__":
    run_and_profile("HST pickle/unpickle",  "pickle_unpickle('hst.pmap', 'data/j8bt06o6q_raw.fits')", globals())
