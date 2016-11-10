"""This module provides functions that interface with the JWST calibration code to determine
things like "reference types used by a pipeline."
"""
import yaml

from crds import log

from jwst.stpipe import cmdline

PIPELINES = [
    "calwebb_dark.cfg",
    "calwebb_sloper.cfg",
    "calwebb_spec2.cfg",
    "calniriss_soss2.cfg",
    "calwebb_image2.cfg",
]

def print_types():
    for pipeline in PIPELINES:
        print(pipeline, "::", " ".join(cmdline.reference_types_from_config(pipeline)))

CFGMAP_YAML = """
level2a:
        calwebb_dark.cfg: [FGS_DARK, MIR_DARK, NRC_DARK, NIS_DARK, NRS_DARK]
        calwebb_sloper.cfg: [default]

level2b:
        calwebb_spec2.cfg: [MIR_LRS-FIXEDSLIT, MIR_LRS-SLITLESS, MIR_MRS, NRS_FIXEDSLIT, NRS_MSASPEC, NRS_IFU]

        calniriss_soss2.cfg: [NIS_SOSS]

        calwebb_image2.cfg: [NRC_IMAGE, NRC_TACQ, NRC_CORN, NRC_FOCUS, 
                             MIR_IMAGE, MIR_TACQ, MIR_LYOT, MIR_4QPM, MIR_CORONCAL,
                             NIS_IMAGE, NIS_AMI, 
                             NRS_IMAGE, NRS_FOCUS, NRS_MIMF, NRS_BOTA, NRS_TACQ, NRS_TASLIT, NRS_TACONFIRM]
"""

import yaml

from jwst.stpipe import cmdline

PIPELINE_TO_REFTYPES = {}
MODE_TO_CONFIG  = {}
MODE_TO_REFTYPES = {}

def setup_cfgmap():
    CFGMAP = yaml.load(CFGMAP_YAML)
    for level in CFGMAP:
        for pipeline in CFGMAP[level]:
            for exp_type in CFGMAP[level][pipeline]:
                MODE_TO_CONFIG[exp_type] = pipeline
                if pipeline not in PIPELINE_TO_REFTYPES:
                    PIPELINE_TO_REFTYPES[pipeline] = cmdline.reference_types_from_config(pipeline)
                MODE_TO_REFTYPES[exp_type] = [pipeline, PIPELINE_TO_REFTYPES[pipeline][:]]
    print(yaml.dump(MODE_TO_REFTYPES))


MODE_TO_REFTYPES_STR = '''
FGS_DARK:
- calwebb_dark.cfg
- [ipc, linearity, mask, refpix, rscd, saturation, superbias]
MIR_4QPM:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
MIR_CORONCAL:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
MIR_DARK:
- calwebb_dark.cfg
- [ipc, linearity, mask, refpix, rscd, saturation, superbias]
MIR_IMAGE:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
MIR_LRS-FIXEDSLIT:
- calwebb_spec2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
MIR_LRS-SLITLESS:
- calwebb_spec2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
MIR_LYOT:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
MIR_MRS:
- calwebb_spec2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
MIR_TACQ:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NIS_AMI:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NIS_DARK:
- calwebb_dark.cfg
- [ipc, linearity, mask, refpix, rscd, saturation, superbias]
NIS_IMAGE:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NIS_SOSS:
- calniriss_soss2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
NRC_CORN:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRC_DARK:
- calwebb_dark.cfg
- [ipc, linearity, mask, refpix, rscd, saturation, superbias]
NRC_FOCUS:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRC_IMAGE:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRC_TACQ:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_BOTA:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_DARK:
- calwebb_dark.cfg
- [ipc, linearity, mask, refpix, rscd, saturation, superbias]
NRS_FIXEDSLIT:
- calwebb_spec2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
NRS_FOCUS:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_IFU:
- calwebb_spec2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
NRS_IMAGE:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_MIMF:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_MSASPEC:
- calwebb_spec2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, fringe,
  ifufore, ifupost, ifuslicer, msa, ote, photom, regions, specwcs, straymask, v2v3,
  wavelengthrange]
NRS_TACONFIRM:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_TACQ:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
NRS_TASLIT:
- calwebb_image2.cfg
- [area, camera, collimator, disperser, distortion, filteroffset, fore, fpa, ifufore,
  ifupost, ifuslicer, msa, ote, photom, regions, specwcs, v2v3, wavelengthrange]
default:
- calwebb_sloper.cfg
- [dark, gain, ipc, linearity, mask, readnoise, refpix, rscd, saturation, superbias]
'''

MODE_TO_REFTYPES = yaml.load(MODE_TO_REFTYPES_STR)

def header_to_reftypes(header):
    try:
        return MODE_TO_REFTYPES[header.get("META.EXPOSURE.TYPE", header.get("EXP_TYPE"))][1]
    except Exception:
        log.verbose_warning("No EXP_TYPE defined in header:\n", log.PP(header))
        return []

if __name__ == "__main__":
    print_types()

