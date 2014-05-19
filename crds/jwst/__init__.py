INSTRUMENTS = ["miri","nirspec","nircam","niriss", "fgs"]

EXTENSIONS = [".pmap", ".imap", ".rmap", ".fits", ]


# NOTE: text descriptions for web page.
# See also locate.py FILETYPE_TO_FILEKIND and FILEKIND_TO_FILETYPE

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

FILEKINDS = sorted(TEXT_DESCR.keys())

