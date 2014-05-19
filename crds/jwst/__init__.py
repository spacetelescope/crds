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

