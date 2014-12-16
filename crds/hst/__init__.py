# To avoid circular imports,  limit this file to inline definitions,  not imports

from crds.hst import reftypes

TYPES = reftypes.from_package_file(__file__)

INSTRUMENTS = TYPES.instruments
EXTENSIONS = TYPES.extensions
TEXT_DESCR = TYPES.text_descr
FILEKINDS = TYPES.filekinds

"""
INSTRUMENTS = ["acs","cos","nicmos","stis","wfc3","wfpc2"]

EXTENSIONS = [
              ".pmap",
              ".imap",
              ".rmap",

              ".fits",

              ".r0h",
              ".r0d",
              ".r1h",
              ".r1d",
              ".r2h",
              ".r2d",
              ".r3h",
              ".r3d",
              ".r4h",
              ".r4d",
              ".r5h",
              ".r5d",
              ".r6h",
              ".r6d",
              ".r7h",
              ".r7d",
              ".r8h",
              ".r8d",
              ".r9h",
              ".r9d",
                ]

# from .text_descr import TEXT_DESCR
TEXT_DESCR = {
    'apdestab': 'Aperture Description Table',
    'apertab': 'Aperture Throughput Table',
    'atodfile': 'Analog To Digital Converter Lookup Table',
    'atodtab': 'Analog To Digital Lookup Table',
    'backtab': 'Background Model Table',
    'badttab': 'Bad Time Interval Table',
    'biasfile': 'Bias Frame',
    'biacfile': 'CTE Bias Frame',
    'bpixtab': 'Data Quality (Bad Pixel) Initialization Table',
    'brftab': 'Baseline Reference Frame Table',
    'brsttab': 'Burst Parameters Table',
    'ccdtab': 'Ccd Parameters Table',
    'cdstab': 'Cross-disperser Scattering Table',
    'cfltfile': 'Coronagraphic Spot Flat Image',
    'comptab': 'Master Component Table (py/synphot)',
    'crrejtab': 'Cosmic Ray Rejection Parameter Table',
    'd2imfile': 'Column Correction File',
    'darkfile': 'Dark Frame',
    'drkcfile': 'CTE Dark Current Frame',
    'deadtab': 'Deadtime Reference Table',
    'dfltfile': 'Delta Flat Field Image',
    'dgeofile': 'Geometric Distortion Correction File',
    'disptab': 'Dispersion Relation Table',
    'drkcfile': 'Cte Corrected Dark',
    'echsctab': 'Echelle Scattering Table',
    'exstab': 'Echelle Cross-Dispersion Scattering Table',
    'flatfile': 'Flat Field',
    'flshfile': 'Post-flash Image',
    'fluxtab': 'Sensitivity Reference Files',
    'gactab': 'Grating-Aperture Correction Table',
    'geofile': 'Geometric Distortion Correction',
    'graphtab': 'Master Graph Table (py/synphot)',
    'gsagtab': 'Gain Sag Reference Table',
    'halotab': 'Detectore Halo Table',
    'hvtab': 'High Voltage Reference Table',
    'idctab': 'Image Distortion Correction File',
    'illmfile': 'Illumination Pattern File',
    'imphttab': 'Photometry Keyword Table',
    'inangtab': 'Incidence Angle Correction Table',
    'lamptab': 'Template Calibration Lamp Spectra Table',
    'lfltfile': 'Low-order Flat Field Image',
    'maskfile': 'Static Mask File',
    'mdriztab': 'Multidrizzle Parameter Table',
    'mlintab': 'Mama Linearity Table',
    'mofftab': 'Mama Offset Correction Table',
    'nlinfile': 'Detector Linearity Correction File',
    'noisfile': 'Detector Read-noise File',
    'npolfile': 'Non-polynomial Offset',
    'offtab': 'Inter-chip Offsets Table',
    'oscntab': 'Overscan Region Table',
    'pctab': 'Photometric Correction Table',
    'pctetab': 'Pixel CTE Correction Table',
    'pedsbtab': 'pedsbtab',
    'pfltfile': 'Pixel To Pixel Flat Field Image',
    'phatab': 'Pulse Height Parameters Table',
    'phottab': 'Phototmetric Calibration Table',
    'pmodfile': 'Persistence Model Files',
    'pmskfile': 'Persistence Mask Files',
    'proftab': '2D Spectrum Profile Table',
    'riptab': 'Echelle Ripple Table',
    'rnlcortb': 'Nonlinearity Power Law Table',
    'saacntab': 'SAACLEAN Task Parameters',
    'saadfile': 'Post Saa Dark Assoc.',
    'sdctab': '2-d Spectrum Distortion Corrections',
    'sdstfile': 'Small Scale Distortion Image Files',
    'shadfile': 'Shutter Shading Correction Image',
    'snkcfile': 'Sink Pixel Correction Image',
    'spottab': 'Spot Position Table',
    'sptrctab': '1-d Spectrum Trace Table',
    'spwcstab': 'Spectroscopic WCS Parameters Table',
    'srwtab': 'Scattering Reference Wavelength Table',
    'tdctab': 'Nuv Dark Correction Table',
    'tdffile': 'Temperature Dependent Flat Fields',
    'tdstab': 'Time Dependent Sensitivity Table',
    'teltab': 'Telescope Point Spread Function Table',
    'tracetab': '1D Spectral Trace Table',
    'twozxtab': 'Two-Zone Spectral Extraction Parameters Table',
    'tempfile': 'Temperature-dependent Dark Reference File',
    'walktab': 'Walk Correction Reference Table',
    'wcptab': 'Wavecal Parameters Reference Table',
    'wf4tfile': 'WF4 Correction Table',
    'xtractab': '1-d Extraction Parameters Table',
    'zprattab': 'Nonlincor Zeropoint Scaling Table'
}

FILEKINDS = sorted(TEXT_DESCR.keys())
"""

# from crds.hst.reftypes import INSTRUMENTS, EXTENSIONS, TEXT_DESCR, FILEKINDS

