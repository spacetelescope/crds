"""This module provides functions that interface with the JWST calibration code to determine
things like "reference types used by a pipeline."
"""
import fnmatch
import re

import yaml

from crds import log

# from jwst.stpipe import cmdline

PIPELINES = [
    "calwebb_dark.cfg",
    "calwebb_sloper.cfg",

    "calwebb_spec2.cfg",
    "calniriss_soss2.cfg",
    "calwebb_image2.cfg",
]

def print_types():
    from jwst.stpipe import cmdline
    for pipeline in PIPELINES:
        print(pipeline, "::", " ".join(cmdline.reference_types_from_config(pipeline)))


'''
DARK, (LED, LAMP, FLAT)  all level2a only
DARK has special calwebb_dark

All otheres go through both level2a and level2b
'''


CFGMAP_YAML = """
level2a:
        calwebb_dark.cfg: [FGS_DARK, MIR_DARK, NRC_DARK, NIS_DARK, NRS_DARK]
        calwebb_sloper.cfg: ["*"]

level2b:
        calwebb_spec2.cfg: [MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS, MIR_MRS, NRS_FIXEDSLIT, NRS_MSASPEC, NRS_IFU]

        calniriss_soss2.cfg: [NIS_SOSS]

        calwebb_image2.cfg: [NRC_IMAGE, NRC_TACQ, NRC_CORN, NRC_FOCUS, 
                             MIR_IMAGE, MIR_TACQ, MIR_LYOT, MIR_4QPM, MIR_CORONCAL,
                             NIS_IMAGE, NIS_AMI, 
                             NRS_IMAGE, NRS_FOCUS, NRS_MIMF, NRS_BOTA, NRS_TACQ, NRS_TASLIT, NRS_TACONFIRM]

        skip_2b.cfg: ["*DARK*", "*FLAT*", "*LED*", "*WSS*", "*LAMP*", NIS_FOCUS, NIS_WFSS, NRS_AUTOWAVE]
"""

PIPELINE_TO_REFTYPES = {
    'calniriss_soss2.cfg': [
        'area',
        'camera',
        'collimator',
        'disperser',
        'distortion',
        'filteroffset',
        'fore',
        'fpa',
        'fringe',
        'ifufore',
        'ifupost',
        'ifuslicer',
        'msa',
        'ote',
        'photom',
        'regions',
        'specwcs',
        'straymask',
        'v2v3',
        'wavelengthrange',
        ],
    'calwebb_dark.cfg': [
        'ipc',
        'linearity',
        'mask',
        'refpix',
        'rscd',
        'saturation',
        'superbias',
        ],
    'calwebb_image2.cfg': [
        'area',
        'camera',
        'collimator',
        'disperser',
        'distortion',
        'filteroffset',
        'fore',
        'fpa',
        'ifufore',
        'ifupost',
        'ifuslicer',
        'msa',
        'ote',
        'photom',
        'regions',
        'specwcs',
        'v2v3',
        'wavelengthrange',
        ],
    'calwebb_sloper.cfg': [
        'dark',
        'gain',
        'ipc',
        'linearity',
        'mask',
        'readnoise',
        'refpix',
        'rscd',
        'saturation',
        'superbias',
        ],
    'calwebb_spec2.cfg': [
        'area',
        'camera',
        'collimator',
        'disperser',
        'distortion',
        'filteroffset',
        'fore',
        'fpa',
        'fringe',
        'ifufore',
        'ifupost',
        'ifuslicer',
        'msa',
        'ote',
        'photom',
        'regions',
        'specwcs',
        'straymask',
        'v2v3',
        'wavelengthrange',
        ],
 'skip_2b.cfg': []}

CFGMAP = {
    'level2a': {
        'calwebb_dark.cfg': [
            'FGS_DARK',
            'MIR_DARK',
            'NRC_DARK',
            'NIS_DARK',
            'NRS_DARK'
            ],
        'calwebb_sloper.cfg': [
            '*',
            ]
        },
    'level2b': {
        'calniriss_soss2.cfg': [
            'NIS_SOSS',
            ],
        'calwebb_image2.cfg': [
            'NRC_IMAGE',
            'NRC_TACQ',
            'NRC_CORN',
            'NRC_FOCUS',
            'MIR_IMAGE',
            'MIR_TACQ',
            'MIR_LYOT',
            'MIR_4QPM',
            'MIR_CORONCAL',
            'NIS_IMAGE',
            'NIS_AMI',
            'NRS_IMAGE',
            'NRS_FOCUS',
            'NRS_MIMF',
            'NRS_BOTA',
            'NRS_TACQ',
            'NRS_TASLIT',
            'NRS_TACONFIRM'
            ],
        'calwebb_spec2.cfg': [
            'MIR_LRS-FIXEDSLIT',
            'MIR_LRS-SLITLESS',
            'MIR_MRS',
            'NRS_FIXEDSLIT',
            'NRS_MSASPEC',
            'NRS_IFU',
            ],
        'skip_2b.cfg': [
            '*DARK*',
            '*FLAT*',
            '*LED*',
            '*WSS*',
            '*LAMP*',
            'NIS_FOCUS',
            'NIS_WFSS',
            'NRS_AUTOWAVE',
            ]
        }
    }

def get_pipeline_reftypes():
    """Return a global mapping from JWST cal code top level pipeline .cfg files
    to the reftypes required to process each sub-Step as a Python dict.
    """
    from jwst.stpipe import cmdline
    pipeline_to_reftypes = {}
    for pipeline in PIPELINES:
        pipeline_to_reftypes[pipeline] = cmdline.reference_types_from_config(pipeline)
    pipeline_to_reftypes["skip_2b.cfg"] = []
    # print(yaml.dump(pipeline_to_reftypes))
    return pipeline_to_reftypes

def header_to_reftypes(header):
    """Given a dataset `header`,  extract the EXP_TYPE or META.EXPOSURE.TYPE keyword
    from and use it to look up the reftypes required to process it.

    Return a list of reftype names.
    """
    with log.augment_exception("Can't find EXP_TYPE for:\n", log.PP(header)):
        exp_type = header.get("META.EXPOSURE.TYPE", header.get("EXP_TYPE"))
    return exptype_to_reftypes(exp_type)

def exptype_to_reftypes(exp_type):
    """For a given EXP_TYPE string, return a list of reftypes needed to process that
    EXP_TYPE through the data levels appropriate for that EXP_TYPE.

    Return [reftypes... ]
    """
    level_2a_types = get_level_reftypes(CFGMAP["level2a"], exp_type)
    level_2b_types = get_level_reftypes(CFGMAP["level2b"], exp_type)
    return level_2a_types + level_2b_types

def get_level_reftypes(pipelines, exp_type):
    """Given a dictionary `pipelines` mapping cal code .cfg files to EXP_TYPE
    glob patterns,  determine the pipeline .

    Return [reftypes... to process exp_type]
    """
    pipeline_cfg = get_level_pipeline(pipelines, exp_type)
    return PIPELINE_TO_REFTYPES[pipeline_cfg]

def get_level_pipeline(pipelines, exp_type):
    """Given a dictionary `pipelines` mapping cal code .cfg files to EXP_TYPE
    glob patterns,  determine the pipeline name for which some pattern matches.

    Return pipeline .cfg name
    """
    for pipeline in pipelines:
        for exp_type_expr in pipelines[pipeline]:
            if glob_match(exp_type_expr, exp_type):
                return pipeline
    raise RuntimeError("Unhandled EXP_TYPE " + repr(exp_type))

def glob_match(expr, value):
    """Convert the given glob `expr` to a regex and match it to `value`."""
    re_str = fnmatch.translate(expr)
    return re.match(re_str, value)

if __name__ == "__main__":
    print_types()

