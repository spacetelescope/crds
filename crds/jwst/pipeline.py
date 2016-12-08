"""This module provides functions that interface with the JWST calibration code to determine
things like "reference types used by a pipeline."
"""
import fnmatch
import re

# import yaml

from crds import config, log, utils
from crds.log import srepr
from crds import exceptions

# from jwst.stpipe import cmdline

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
reftype: CALCFG
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

def generate_calcfg_yaml():
    """Generate the SYSTEM CALCFG reference YAML."""
    import yaml
    pipeline_cfgs = yaml.load(PIPELINE_CFGS_YAML)["pipeline_cfgs"]
    pipeline_cfgs_to_steps, all_steps_to_reftypes = generate_pipeline_info(pipeline_cfgs)
    calcfg = HEADER_YAML + PIPELINE_CFGS_YAML + LEVEL_PIPELINE_EXPTYPE_YAML + "\n"
    calcfg += yaml.dump({"pipeline_cfgs_to_steps" : pipeline_cfgs_to_steps}) + "\n"
    calcfg += yaml.dump({"steps_to_reftypes" : all_steps_to_reftypes})
    calcfg += STEPS_TO_REFTYPE_EXCEPTIONS_YAML
    return calcfg
    
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
CALCFG_REFERENCE_YAML = '''
author: CRDS
descrip: "Reference used to determine pipeline configuration from dataset parameters."
history: "First version generated from calcode .cfg files and EXP_TYPE/LEVEL mapping."
instrument: SYSTEM
pedigree: DUMMY
reftype: CALCFG
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

def header_to_reftypes(header):
    """Given a dataset `header`,  extract the EXP_TYPE or META.EXPOSURE.TYPE keyword
    from and use it to look up the reftypes required to process it.

    Return a list of reftype names.
    """
    with log.warn_on_exception("Failed determining required reftypes from header", log.PP(header)):
        exp_type = header.get("META.EXPOSURE.TYPE")
        if not exp_type:
            exp_type = header["EXP_TYPE"]
        return exptype_to_reftypes(exp_type)
    return []

@utils.cached
def exptype_to_reftypes(exp_type):
    """For a given EXP_TYPE string, return a list of reftypes needed to process that
    EXP_TYPE through the data levels appropriate for that EXP_TYPE.

    Return [reftypes... ]
    """
    level_2a_pipeline = get_level_pipeline("level2a", exp_type)
    level_2b_pipeline = get_level_pipeline("level2b", exp_type)
    level_2a_types = get_pipeline_types(level_2a_pipeline, exp_type)
    level_2b_types = get_pipeline_types(level_2b_pipeline, exp_type)
    combined = sorted(list(set(level_2a_types + level_2b_types)))
    return combined

@utils.cached
def load_calcfg_reference():
    """Load the CALCFG reference info into a Python data structure and
    return it.  Set global CALCFG.
    """
    import yaml
    return yaml.load(CALCFG_REFERENCE_YAML)
    
def get_level_pipeline(level, exp_type):
    """Interpret the level_pipeline_exptypes data structure relative to
    processing `level` and `exp_type` to determine a pipeline .cfg file.

    Return pipeline .cfg
    """
    CALCFG = load_calcfg_reference()
    pipeline_exptypes = CALCFG["level_pipeline_exptypes"][level]
    for mapping in pipeline_exptypes:
        for pipeline, exptypes in mapping.items():
            for exptype_pattern in exptypes:
                if glob_match(exptype_pattern, exp_type):
                    log.verbose("Pipeline .cfg for", srepr(level), "and", 
                                srepr(exp_type), "is:", srepr(pipeline))
                    return pipeline
    raise exceptions.CrdsPipelineCfgDeterminationError("Unhandled EXP_TYPE", srepr(exp_type))

def get_pipeline_types(pipeline, exp_type):
    """Based on a pipeline .cfg filename and an EXP_TYPE,  look up
    the Steps corresponding to the .cfg and extrapolate those to the
    reftypes used by those Steps.   If there are exceptions to the
    reftypes assigned for a particular Step that depend on EXP_TYPE,
    return the revised types for that Step instead.
    
    Return [reftypes ...]
    """
    CALCFG = load_calcfg_reference()
    steps = CALCFG["pipeline_cfgs_to_steps"][pipeline]
    exceptions = CALCFG["steps_to_reftypes_exceptions"]
    reftypes = []
    for step in steps:
        if step not in exceptions:
            reftypes.extend(CALCFG["steps_to_reftypes"][step])
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

# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    print(generate_calcfg_yaml())
