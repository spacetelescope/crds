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

import crds
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

DEFAULT_SYSTEM_CRDSCFG_PATH = os.path.join(HERE, "jwst_system_crdscfg.yaml")

# --------------------------------------------------------------------------------------

def header_to_reftypes(context, header):
    """Given a dataset `header`,  extract the EXP_TYPE or META.EXPOSURE.TYPE keyword
    from and use it to look up the reftypes required to process it.

    Return a list of reftype names.
    """
    with log.warn_on_exception("Failed determining required reftypes from header", log.PP(header)):
        cal_ver = header.get("META.CALIBRATION_SOFTWARE_VERSION", header.get("CAL_VER"))
        exp_type = header.get("META.EXPOSURE.TYPE",  header.get("EXP_TYPE"))
        config_manager = get_config_manager(context, cal_ver)
        if config_manager is not None:
            return config_manager.exptype_to_reftypes(exp_type)
    return []

@utils.cached  # for caching,  pars must be immutable, ideally simple
def get_config_manager(context, cal_ver):
    """Construct a pipeline configuration manager appropriate for the given CRDS `context`
    and calibration s/w version `calver`.
    """
    import yaml
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
        refpath = rmapping.get_bestref(header)
        api.dump_references(context, [refpath])
    with open(refpath) as opened:
        crdscfg =  yaml.load(opened)
    return CrdsCfgManager(context, refpath, crdscfg)

class CrdsCfgManager(object):
    """The CrdsCfgManager handles find."""
    def __init__(self, context, refpath, crdscfg):
        self._context = context
        self._refpath = refpath
        self._crdscfg = crdscfg
        
    @utils.cached
    def exptype_to_reftypes(self, exp_type):
        """For a given EXP_TYPE string, return a list of reftypes needed to process that
        EXP_TYPE through the data levels appropriate for that EXP_TYPE.

        Return [reftypes... ]
        """
        level_2a_pipeline = self.get_level_pipeline("level2a", exp_type)
        level_2b_pipeline = self.get_level_pipeline("level2b", exp_type)
        level_2a_types = self.get_pipeline_types(level_2a_pipeline, exp_type)
        level_2b_types = self.get_pipeline_types(level_2b_pipeline, exp_type)
        combined = sorted(list(set(level_2a_types + level_2b_types)))
        return combined

    @utils.cached
    def get_level_pipeline(self, level, exp_type):
        """Interpret the level_pipeline_exptypes data structure relative to
        processing `level` and `exp_type` to determine a pipeline .cfg file.

        Return pipeline .cfg
        """
        pipeline_exptypes = self._crdscfg["level_pipeline_exptypes"][level]
        for mapping in pipeline_exptypes:
            for pipeline, exptypes in mapping.items():
                for exptype_pattern in exptypes:
                    if glob_match(exptype_pattern, exp_type):
                        log.verbose("Pipeline .cfg for", srepr(level), "and", 
                                    srepr(exp_type), "is:", srepr(pipeline))
                        return pipeline
        raise exceptions.CrdsPipelineCfgDeterminationError("Unhandled EXP_TYPE", srepr(exp_type))

    def get_pipeline_types(self, pipeline, exp_type):
        """Based on a pipeline .cfg filename and an EXP_TYPE,  look up
        the Steps corresponding to the .cfg and extrapolate those to the
        reftypes used by those Steps.   If there are exceptions to the
        reftypes assigned for a particular Step that depend on EXP_TYPE,
        return the revised types for that Step instead.
        
        Return [reftypes ...]
        """
        crdscfg = self._crdscfg
        steps = crdscfg["pipeline_cfgs_to_steps"][pipeline]
        exceptions = crdscfg["steps_to_reftypes_exceptions"]
        reftypes = []
        for step in steps:
            if step not in exceptions:
                reftypes.extend(crdscfg["steps_to_reftypes"][step])
            else:
                for case in exceptions[step]:
                    item = list(case.values())[0]
                    more_reftypes = item["reftypes"][:]
                    exptypes = item["exp_types"][:]
                    found = False
                    for exptype_pattern in exptypes:
                        if glob_match(exptype_pattern, exp_type):
                            log.verbose("Adding exceptional types", more_reftypes, 
                                        "for step", srepr(step), "case", srepr(exptype_pattern), 
                                        "based on exp_type", srepr(exp_type))
                            found = True
                            reftypes.extend(more_reftypes)
                            break
                    if found:
                        break
                else:
                    raise exceptions.CrdsPipelineTypeDeterminationError("Unhandled EXP_TYPE for exceptional Step", srepr(step))
        log.verbose("Reftypes for pipeline", srepr(pipeline), "and", srepr(exp_type), 
                    "are:", srepr(reftypes))
        return reftypes

def glob_match(expr, value):
    """Convert the given glob `expr` to a regex and match it to `value`."""
    re_str = fnmatch.translate(expr)
    return re.match(re_str, value)

def test():
    import doctest, crds.jwst.pipeline
    return doctest.testmod(crds.jwst.pipeline)

# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    print(test())
