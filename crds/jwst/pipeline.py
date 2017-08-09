"""This module provides functions that interface with the JWST calibration code to determine
things like "reference types used by a pipeline."

>>> header_to_reftypes("jwst-operational", test_header("0.7.0", "FGS_DARK"))
['ipc', 'linearity', 'mask', 'refpix', 'rscd', 'saturation', 'superbias']

>>> header_to_reftypes("jwst-operational", test_header("0.7.0", "NRS_BRIGHTOBJ"))
['area', 'camera', 'collimator', 'dark', 'disperser', 'distortion', 'drizpars', 'extract1d', 'filteroffset', 'fore', 'fpa', 'fringe', 'gain', 'ifufore', 'ifupost', 'ifuslicer', 'ipc', 'linearity', 'mask', 'msa', 'ote', 'pathloss', 'photom', 'readnoise', 'refpix', 'regions', 'rscd', 'saturation', 'specwcs', 'straymask', 'superbias', 'v2v3', 'wavelengthrange']

>>> header_to_reftypes("jwst-operational", test_header("0.7.0", "MIR_IMAGE"))
['area', 'camera', 'collimator', 'dark', 'disperser', 'distortion', 'filteroffset', 'flat', 'fore', 'fpa', 'gain', 'ifufore', 'ifupost', 'ifuslicer', 'ipc', 'linearity', 'mask', 'msa', 'ote', 'photom', 'readnoise', 'refpix', 'regions', 'rscd', 'saturation', 'specwcs', 'superbias', 'v2v3', 'wavelengthrange']

>>> header_to_reftypes("jwst-operational", test_header("0.7.0", "MIR_LRS-FIXEDSLIT"))
['area', 'camera', 'collimator', 'dark', 'disperser', 'distortion', 'drizpars', 'extract1d', 'filteroffset', 'flat', 'fore', 'fpa', 'fringe', 'gain', 'ifufore', 'ifupost', 'ifuslicer', 'ipc', 'linearity', 'mask', 'msa', 'ote', 'pathloss', 'photom', 'readnoise', 'refpix', 'regions', 'rscd', 'saturation', 'specwcs', 'straymask', 'superbias', 'v2v3', 'wavelengthrange']

"""

# --------------------------------------------------------------------------------------

import os.path
import fnmatch
import re

# import yaml

# --------------------------------------------------------------------------------------

import crds, crds.core
from crds.core import exceptions, log, utils
from crds.core.log import srepr
from crds.client import api

# --------------------------------------------------------------------------------------

def test_header(calver, exp_type):
    header = {
        "META.INSTRUMENT.NAME" : "SYSTEM",
        "REFTYPE" : "CRDSCFG",
        "META.CALIBRATION_SOFTWARE_VERSION" : calver,
        "META.EXPOSURE.TYPE" : exp_type,
        }
    return header

# --------------------------------------------------------------------------------------

HERE = os.path.dirname(__file__) or "."

DEFAULT_SYSTEM_CRDSCFG_PATH = os.path.join(HERE, "jwst_system_crdscfg_b7.yaml")

# --------------------------------------------------------------------------------------

def header_to_reftypes(context, header):
    """Given a dataset `header`,  extract the EXP_TYPE or META.EXPOSURE.TYPE keyword
    from and use it to look up the reftypes required to process it.

    Return a list of reftype names.
    """
    with log.warn_on_exception("Failed determining required reftypes from header", log.PP(header)):
        cal_ver = header.get("META.CALIBRATION_SOFTWARE_VERSION", header.get("CAL_VER"))
        if cal_ver is None:
            from jwst import version
            cal_ver = version.__version__
        exp_type = header.get("META.EXPOSURE.TYPE",  header.get("EXP_TYPE"))
        config_manager = get_config_manager(context, cal_ver)
        if config_manager is not None:
            return config_manager.exptype_to_reftypes(exp_type)
    return []

@utils.cached  # for caching,  pars must be immutable, ideally simple
def get_config_manager(context, cal_ver):
    """Given `context` and calibration s/w version `cal_ver`,  identify the appropriate
    SYSTEM CRDSCFG reference file and create a CrdsCfgManager from it.
    """
    refpath = get_config_refpath(context, cal_ver)
    return load_refpath(context, refpath)

def load_refpath(context, refpath):
    """Given `context` and SYSTEM CRDSCFG reference at `refpath`,  construct a CrdsCfgManager."""
    import yaml
    with open(refpath) as opened:
        crdscfg =  yaml.load(opened)
    return CrdsCfgManager(context, refpath, crdscfg)

def get_config_refpath(context, cal_ver):
    """Given CRDS `context` and calibration s/w version `cal_ver`,  identify the applicable
    SYSTEM CRDSCFG reference file, cache it, and return the file path.
    """
    # default enables running on contexts that have no system crdscfg 
    # reference, B7 and earlier.
    refpath = DEFAULT_SYSTEM_CRDSCFG_PATH
    with log.verbose_warning_on_exception(
            "Failed locating SYSTEM CRDSCFG reference",
            "under context", repr(context),
            "and cal_ver", repr(cal_ver) + ".",
            "Using build-7 default."):
        header = {
            "META.INSTRUMENT.NAME" : "SYSTEM", 
            "META.CALIBRATION_SOFTWARE_VERSION": cal_ver 
        }
        pmap = crds.get_symbolic_mapping(context)
        imap = pmap.get_imap("system")
        rmapping = imap.get_rmap("crdscfg")
        ref = rmapping.get_best_ref(header)
        refpath = rmapping.locate_file(ref)
        api.dump_references(context, [ref])
    return refpath

class CrdsCfgManager(object):
    """The CrdsCfgManager handles using SYSTEM CRDSCFG information to compute things."""
    def __init__(self, context, refpath, crdscfg):
        self._context = context
        self._refpath = refpath
        self._crdscfg = utils.Struct(crdscfg)
        
    def exptype_to_reftypes(self, exp_type):
        """For a given EXP_TYPE string, return a list of reftypes needed to process that
        EXP_TYPE through the data levels appropriate for that EXP_TYPE.

        Return [reftypes, ... ]
        """
        reftypes = self._crdscfg.exptypes_to_reftypes[exp_type]
        log.verbose("Applicable reftypes for", srepr(exp_type), 
                    "determined by", srepr(os.path.basename(self._refpath)),
                    "are", srepr(reftypes))
        return reftypes

    def exptypes_to_pipelines(self, exp_type):
        """For a given EXP_TYPE string, return a list of pipeline .cfg's needed to 
        process that EXP_TYPE through the appropriate data levels.

        Return [.cfg's, ... ]
        """
        pipelines = self._crdscfg.exptypes_to_pipelines[exp_type]
        log.verbose("Applicable pipelines for", srepr(exp_type), 
                    "determined by", srepr(os.path.basename(self._refpath)),
                    "are", srepr(pipelines))
        return pipelines

def test():
    import doctest, crds.jwst.pipeline
    return doctest.testmod(crds.jwst.pipeline)

# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    print(test())
