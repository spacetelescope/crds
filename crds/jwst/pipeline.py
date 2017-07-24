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

import fnmatch
import re

# import yaml

import crds
from crds.core import exceptions, log, utils, python23
from crds.core.log import srepr

# from jwst.stpipe import cmdline

def test_header(calver, exp_type):
    header = {
        "META.INSTRUMENT.NAME" : "SYSTEM",
        "REFTYPE" : "CRDSCFG",
        "META.CALIBRATION_SOFTWARE_VERSION" : calver,
        "META.EXPOSURE.TYPE" : exp_type,
        }
    return header

'''
DARK, (LED, LAMP, FLAT)  all level2a only
DARK has special calwebb_dark

All otheres go through both level2a and level2b
'''

HEADER_YAML = """
author: CRDS
descrip: "Reference used to determine pipeline configuration from dataset parameters."
history: "First version generated from calcode .cfg files and EXP_TYPE/LEVEL mapping."
instrument: SYSTEM
pedigree: DUMMY
reftype: CRDSCFG
telescope: JWST
useafter: 1900-01-01T00:00:00
"""

# Input manually
# Order is important since the first pattern matching an exp_type in any given level wins.
PIPELINE_CFGS_YAML = """
pipeline_cfgs: [calwebb_dark.cfg, calwebb_sloper.cfg, calwebb_spec2.cfg, calniriss_soss2.cfg,
  calwebb_image2.cfg]
"""

# Input manually
LEVEL_PIPELINE_EXPTYPE_YAML = """
level_pipeline_exptypes:
    level2a:
        - calwebb_dark.cfg: [FGS_DARK, MIR_DARK, NRC_DARK, NIS_DARK, NRS_DARK]

        - calwebb_sloper.cfg: ["*"]

    level2b:
        - calwebb_spec2.cfg: [MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS, MIR_MRS, NRS_FIXEDSLIT, 
                             NRS_MSASPEC, NRS_IFU, NRS_BRIGHTOBJ, NRS_AUTOWAVE]

        - calniriss_soss2.cfg: [NIS_SOSS]

        - calwebb_image2.cfg: [NRC_IMAGE, NRC_TACQ, NRC_CORON, NRC_FOCUS, 
                             MIR_IMAGE, MIR_TACQ, MIR_LYOT, MIR_4QPM, MIR_CORONCAL,
                             NIS_IMAGE, NIS_AMI, NIS_TACQ,
                             NRS_IMAGE, NRS_FOCUS, NRS_MIMF, NRS_BOTA, NRS_TACQ, NRS_TASLIT, NRS_TACONFIRM, NRS_CONFIRM,
                             FGS_IMAGE, FGS_FOCUS]

        - skip_2b.cfg: ["*DARK*", "*FLAT*", "*LED*", "*LAMP*", NIS_FOCUS, NIS_WFSS, NRS_AUTOWAVE]
"""

STEPS_TO_REFTYPE_EXCEPTIONS_YAML = """
steps_to_reftypes_exceptions:
    flat_field:
        - case1:
            exp_types: [NRS_FIXEDSLIT, NRS_IFU, NRS_MSASPEC]
            reftypes: [dflat, fflat, sflat]
        - case2:
            exp_types: ["NRS_*"]
            reftypes: []
        - case3:
            exp_types: ["*"]
            reftypes: [flat]
"""

# --------------------------------------------------------------------------------------

def generate_crdscfg_yaml():
    """Generate the SYSTEM CRDSCFG reference YAML."""
    import yaml
    pipeline_cfgs = yaml.load(PIPELINE_CFGS_YAML)["pipeline_cfgs"]
    pipeline_cfgs_to_steps, all_steps_to_reftypes = generate_pipeline_info(pipeline_cfgs)
    crdscfg = HEADER_YAML + PIPELINE_CFGS_YAML + LEVEL_PIPELINE_EXPTYPE_YAML + "\n"
    crdscfg += yaml.dump({"pipeline_cfgs_to_steps" : pipeline_cfgs_to_steps}) + "\n"
    crdscfg += yaml.dump({"steps_to_reftypes" : all_steps_to_reftypes})
    crdscfg += STEPS_TO_REFTYPE_EXCEPTIONS_YAML
    return crdscfg
    
def generate_pipeline_info(pipeline_cfgs):
    from jwst.stpipe import cmdline
    pipeline_cfgs_to_steps = {}
    all_steps_to_reftypes = {}
    pipeline_cfgs_to_steps["skip_2b.cfg"] = []
    for pipeline_cfg in pipeline_cfgs:
        steps_to_reftypes = cmdline.steps_to_reftypes_from_config(pipeline_cfg)
        pipeline_cfgs_to_steps[pipeline_cfg] = sorted(list(steps_to_reftypes.keys()))
        all_steps_to_reftypes.update(steps_to_reftypes)
    return pipeline_cfgs_to_steps, all_steps_to_reftypes

# --------------------------------------------------------------------------------------
CRDSCFG_REFERENCE_YAML = '''
author: CRDS
descrip: "Reference used to determine pipeline configuration from dataset parameters."
history: "First version generated from calcode .cfg files and EXP_TYPE/LEVEL mapping."
instrument: SYSTEM
pedigree: DUMMY
reftype: CRDSCFG
telescope: JWST
useafter: 1900-01-01T00:00:00

pipeline_cfgs: [calwebb_dark.cfg, calwebb_sloper.cfg, calwebb_spec2.cfg, calniriss_soss2.cfg,
  calwebb_image2.cfg]

level_pipeline_exptypes:
    level2a:
        - calwebb_dark.cfg: [FGS_DARK, MIR_DARK, NRC_DARK, NIS_DARK, NRS_DARK]

        - calwebb_sloper.cfg: ["*"]

    level2b:
        - calwebb_spec2.cfg: [MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS, MIR_MRS, NRS_FIXEDSLIT, 
                             NRS_MSASPEC, NRS_IFU, NRS_BRIGHTOBJ, NRS_AUTOWAVE]

        - calniriss_soss2.cfg: [NIS_SOSS]

        - calwebb_image2.cfg: [NRC_IMAGE, NRC_TACQ, NRC_CORON, NRC_FOCUS, 
                             MIR_IMAGE, MIR_TACQ, MIR_LYOT, MIR_4QPM, MIR_CORONCAL,
                             NIS_IMAGE, NIS_AMI, NIS_TACQ,
                             NRS_IMAGE, NRS_FOCUS, NRS_MIMF, NRS_BOTA, NRS_TACQ, NRS_TASLIT, NRS_TACONFIRM, NRS_CONFIRM,
                             FGS_IMAGE, FGS_FOCUS]

        - skip_2b.cfg: ["*DARK*", "*FLAT*", "*LED*", "*LAMP*", NIS_FOCUS, NIS_WFSS, NRS_AUTOWAVE]

pipeline_cfgs_to_steps:
  calniriss_soss2.cfg: [assign_wcs, bkg_subtract, cube_build, extract_1d, extract_2d,
    flat_field, fringe, imprint_subtract, pathloss, photom, resample_spec, srctype,
    straylight]
  calwebb_dark.cfg: [dq_init, ipc, lastframe, linearity, refpix, rscd, saturation,
    superbias]
  calwebb_image2.cfg: [assign_wcs, flat_field, photom]
  calwebb_sloper.cfg: [dark_current, dq_init, ipc, jump, lastframe, linearity, persistence,
    ramp_fit, refpix, rscd, saturation, superbias]
  calwebb_spec2.cfg: [assign_wcs, bkg_subtract, cube_build, extract_1d, extract_2d,
    flat_field, fringe, imprint_subtract, pathloss, photom, resample_spec, srctype,
    straylight]
  skip_2b.cfg: []

steps_to_reftypes:
  assign_wcs: [camera, collimator, disperser, distortion, filteroffset, fore, fpa,
    ifufore, ifupost, ifuslicer, msa, ote, regions, specwcs, v2v3, wavelengthrange]
  bkg_subtract: []
  cube_build: []
  dark_current: [dark]
  dq_init: [mask]
  extract_1d: [extract1d]
  extract_2d: []
  flat_field: []
  fringe: [fringe]
  imprint_subtract: []
  ipc: [ipc]
  jump: [gain, readnoise]
  lastframe: []
  linearity: [linearity]
  pathloss: [pathloss]
  persistence: []
  photom: [area, photom]
  ramp_fit: [gain, readnoise]
  refpix: [refpix]
  resample_spec: [drizpars]
  rscd: [rscd]
  saturation: [saturation]
  srctype: []
  straylight: [straymask]
  superbias: [superbias]

steps_to_reftypes_exceptions:
    flat_field:
        - case1:
            exp_types: [NRS_FIXEDSLIT, NRS_IFU, NRS_MSASPEC]
            reftypes: [dflat, fflat, sflat]
        - case2:
            exp_types: ["NRS_*"]
            reftypes: []
        - case3:
            exp_types: ["*"]
            reftypes: [flat]
'''

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
    with log.verbose_warning_on_exception(
            "Failed to load SYSTEM CRDSCFG for determining required reftypes.   Using build-7 default."):
        header = {
            "META.INSTRUMENT.NAME" : "SYSTEM", 
            "META.CALIBRATION_SOFTWARE_VERSION": cal_ver 
        }
        pmap = crds.get_symbolic_mapping(context)
        imap = pmap.get_imap("system")
        rmapping = imap.get_rmap("crdscfg")
        refpath = rmapping.get_bestref(header)
        with open(refpath) as opened:
            crdscfg =  yaml.load(opened)
        return CrdsCfgManager(context, refpath, crdscfg)
    crdscfg = yaml.load(python23.StringIO(CRDSCFG_REFERENCE_YAML))
    return CrdsCfgManager(context, "no_system_crdscfg_reference_found", crdscfg)

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
    print(generate_crdscfg_yaml())
