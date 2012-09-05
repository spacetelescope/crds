INSTRUMENTS = ["miri","nirspec","nircam","niriss"]

EXTENSIONS = [".pmap", ".imap", ".rmap", ".fits", ]

TEXT_DESCR = {
    "flat" : "Flat Field",
    "photom" : "Absolute Calibration",
    "dark" : "Dark Frame",
    "linearity" : "Detector Linearity Correction Coefficients",
    "mask" : "Bad Pixel Mask",
    "amplifier" : "Detector Amplifier Readout Parameters",
    "dqi" : "Data Quality Initialization",
}

FILEKINDS = sorted(TEXT_DESCR.keys())

