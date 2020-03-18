"""This module defines replacement functionality for the CDBS "certify" program
used to check parameter values in .fits reference files.   It verifies that FITS
files define required parameters and that they have legal values.
"""
from crds.core import log, utils
from . import core as core_validators
from . import synphot as synphot_validators


__all__ = [
    "validator",
    "get_validators",
]


_VALIDATOR_MODULES = [
    core_validators,
    synphot_validators
]


def validator(info, context=None):
    """Given TpnInfo object `info`, construct and return a Validator for it."""
    if len(info.values) == 1 and info.values[0].startswith("&"):
        # This block handles &-types like &PEDIGREE and &SYBDATE
        # only called on static TPN infos.
        class_name = "".join([v.capitalize() for v in info.values[0][1:].split("_")]) + "Validator"
        module = next((m for m in _VALIDATOR_MODULES if hasattr(m, class_name)), None)
        if module is None:
            raise ValueError("Unrecognized validator {}, expected class {}".format(info.values[0], class_name))
        rval = getattr(module, class_name)(info, context=context)
    elif info.datatype == "C":
        rval = core_validators.CharacterValidator(info, context=context)
    elif info.datatype == "R":
        rval = core_validators.RealValidator(info, context=context)
    elif info.datatype == "D":
        rval = core_validators.DoubleValidator(info, context=context)
    elif info.datatype == "I":
        rval = core_validators.IntValidator(info, context=context)
    elif info.datatype == "L":
        rval = core_validators.LogicalValidator(info, context=context)
    elif info.datatype == "X":
        if info.keytype == "C":
            rval = core_validators.ColumnExpressionValidator(info, context=context)
        else:
            rval = core_validators.ExpressionValidator(info, context=context)
    else:
        raise ValueError("Unimplemented datatype " + repr(info.datatype))
    return rval


def get_validators(observatory, refpath, context=None):
    """Given `observatory` and a path to a reference file `refpath`,  load the
    corresponding validators that define individual constraints that reference
    should satisfy.
    """
    tpns = _get_reffile_tpninfos(observatory, refpath)
    checkers = [validator(x, context=context) for x in tpns]
    log.verbose("Validators for", repr(refpath), "("+str(len(checkers))+"):\n", log.PP(checkers), verbosity=65)
    return checkers


def _get_reffile_tpninfos(observatory, refpath):
    """Load just the TpnInfo objects for `observatory` and the given `refpath`.
    This entails both "class" TpnInfo's from CDBS as well as TpnInfo objects
    derived from the JWST data models.
    """
    locator = utils.get_locator_module(observatory)
    instrument, filekind = locator.get_file_properties(refpath)
    tpns = list(locator.get_all_tpninfos(instrument, filekind, "tpn"))
    tpns.extend(locator.get_extra_tpninfos(refpath))
    return tpns
