"""Generate .spec files from existing JWST mappings and original hard coded
enumerations.
"""

import os.path

INSTRUMENTS = ["miri","nirspec","nircam","niriss", "fgs"]

EXTENSIONS = [".pmap", ".imap", ".rmap", ".fits", ]


# Text descriptions for web page.   { filekind : text_descr }
TEXT_DESCR = {
    "flat" : "Flat Field",
    "photom" : "Absolute Calibration",
    "dark" : "Dark Frame",
    "fringe" : "Spectral Fringing Correction Factors",
    "linearity" : "Detector Linearity Correction Coefficients",
    "mask" : "Bad Pixel Mask",
    "amplifier" : "Detector Amplifier Readout Parameters",
    "readnoise" : "Read Noise",
    "gain" : "Gain",
    "saturation" : "Saturation",
    "ipc" : "Interpixel Capacitance",
    "drizpars" : "Drizzle Parameters used in Image Distortion Correction and Combination",
    "reset" : "Reset Correction",
    "lastframe" : "Last Frame",
    "straymask" : "Stray Light Mask",
    "distortion" : "Distortion",
    "regions" : "Regions",
    "specwcs" : "Spectroscopic World Coordinate System",
    "wcsregions" : "World Coordinate System Regions",
    
    

}

# Type names in rmaps, written down as REFTYPE in FITS
FILEKINDS = sorted(TEXT_DESCR.keys())

# Type name conversion,  { long form : short form },  default to short form if not mentioned.
FILETYPE_TO_FILEKIND = {
    "DETECTOR PARAMETERS" : "AMPLIFIER",
    "PIXEL-TO-PIXEL FLAT" : "FLAT",
    "PHOTOMETRIC CALIBRATION" : "PHOTOM",
    "INTERPIXEL CAPACITANCE" : "IPC",
    "SPECTRAL FRINGING CORRECTION FACTORS" : "FRINGE",
}

# Type name conversion  { short form : long form }
FILEKIND_TO_FILETYPE = { val:key for (key, val) in FILETYPE_TO_FILEKIND.items() }

# ===========================================================

HERE = os.path.dirname(__file__) or "."

def gen_specs(context):
    """"""
    import crds, crds.reftypes
    p = crds.get_cached_mapping(context)
    for mapping in p.mapping_names():
        if mapping.endswith(".rmap"):
            r = crds.get_cached_mapping(mapping)
            specname = r.instrument + "_" + r.filekind + ".spec"
            specpath = os.path.join(HERE, "specs", specname)
            spec = dict(r.header)
            spec["filetype"] = FILEKIND_TO_FILETYPE.get(
                r.filekind.upper(), r.filekind.upper())
            spec["file_ext"] = os.path.splitext(r.reference_names()[0])[-1]
            spec["text_descr"] = TEXT_DESCR[r.filekind]
            crds.reftypes.write_spec(specpath, spec)
