"""This module defines text descriptions for each HST file kind,  which I think
are similar to but distinct from the actual REFTYPE keyword values.

This data was manually cut-and-pasted from links like this:

https://blogs.stsci.edu/cdbs/sql-tables/acs-acs-ref-data-table-reference-file-identifier/

based on limited e-mail direction from Rossy.
"""

import cStringIO

from crds import log
from crds.hst import tpn

RAW_WEB_CUTS = {
"acs" : """
acr_best_biasfile   BIAS Frame  BIA
acr_best_cfltfile   CORONAGRAPHIC SPOT FLAT IMAGE   CFL
acr_best_darkfile   DARK Frame  DRK
acr_best_dfltfile   DELTA FLAT Field IMAGE    DFL
acr_best_dgeofile   Geometric Distortion Correction File DXY
acr_best_flshfile   POST-FLASH IMAGE    FLS
acr_best_lfltfile   Low-order Flat Field Image   LFL
acr_best_pfltfile   Pixel To Pixel Flat Field Image PFL
acr_best_shadfile   Shutter Shading Correction Image   SHD
acr_best_atodtab    Analog To Digital Lookup Table A2D
acr_best_bpixtab    Data Quality (Bad Pixel) Initialization Tables  BPX
acr_best_ccdtab CCD Parameters Table    CCD
acr_best_comptab    Master Component Table (py/synphot)  TMC
acr_best_crrejtab   Cosmic Ray Rejection Parameter Table    CRR
acr_best_graphtab   Master Graph Table (py/synphot) TMG
acr_best_idctab     Image Distortion Correction File IDC
acr_best_mdriztab   MULTIDRIZZLE PARAMETER TABLE    MDZ
acr_best_mlintab    MAMA LINEARITY TABLE    LIN
acr_best_oscntab    CCD OVERSCAN REGION TABLE   OSC
acr_best_phottab    Phototmetric Calibration Table PHT
acr_best_spottab    SPOT POSITION TABLE CSP
acr_best_drkcfile   CTE corrected dark  DKC
acr_best_pctetab    CTE CORRECTION TABLE    PCTE
acr_best_imphttab   PHOTOMETRY KEYWORD TABLE    IMP
""", 

"cos" : """
csr_best_geofile    Geometric Distortion Correction     GEO
csr_best_flatfile   Flat Field  FLT
csr_best_badttab    Bad Time Interval Table     BADT
csr_best_bpixtab    Data Quality (Bad Pixel) Initialization Tables BPIX
csr_best_brftab     Baseline Reference Frame Table  BRF
csr_best_brsttab    Burst Parameters Tables     BURST
csr_best_deadtab    Deadtime Reference Table    DEAD
csr_best_disptab    Dispersion Relation Tables DISP
csr_best_fluxtab    Sensitivity Reference Files     PHOT
csr_best_lamptab    Template Calibration Lamp Spectra Tables   LAMP
csr_best_phatab     Pulse Height Parameters Tables  PHA
csr_best_tdstab     Time Dependent Sensitivity Table   TDS
csr_best_wcptab     Wavecal Parameters Reference Table  WCP
csr_best_xtractab   1-D Extraction Parameters Tables    1DX
""",

"nicmos" : """
nsr_best_darkfile   Dark Frame   DRK
nsr_best_flatfile   Flat Field  FLT
nsr_best_illmfile   Illumination Pattern File   ILM
nsr_best_maskfile   Static Mask File  XXX  
nsr_best_nlinfile   Detector Linearity Correction File     LIN
nsr_best_noisfile   Detector Read-Noise File    NOI
nsr_best_saadfile   Post SAA Dark Assoc.    Name
nsr_best_tempfile   Temperature-dependent dark reference file   TDD
nsr_best_backtab    Background Model Table  -
nsr_best_phottab    Phototmetric Calibration Table PHT
nsr_best_idctab     Image Distortion Correction File  IDC
""",

"stis" : """
ssr_best_biasfile   Bias Frame    BIA
ssr_best_darkfile   Dark Frame    DRK
ssr_best_pfltfile   Pixel To Pixel Flat Field Image   PFL
ssr_best_dfltfile   Delta flat field image  DFL
ssr_best_lfltfile   Low-order Flat Field Image  LFL
ssr_best_shadfile   Shutter Shading Correction Image SSC
ssr_best_sdstfile   Small scale distortion image files  SSD
ssr_best_atodtab    Analog To Digital Lookup Table A2D
ssr_best_apdstab    Aperture Description Tables     APD
ssr_best_apertab    Aperture Throughput Tables  APT
ssr_best_bpixtab    Data Quality (Bad Pixel) Initialization Tables    BPX
ssr_best_ccdtab     CCD Parameters Table   CCD
ssr_best_crrejtab   Cosmic Ray Rejection Parameter Table  CRR
ssr_best_disptab    Dispersion Relation Tables  DSP
ssr_best_inangtab   Incidence Angle Correction Tables   IAC
ssr_best_idctab     Image Distortion Correction File  IDC
ssr_best_mlintab    MAMA Linearity Table  LIN
ssr_best_lamptab    Template Calibration Lamp Spectra Tables     LMP
ssr_best_mofftab    MAMA Offset Correction Tables   MOC
ssr_best_pctab  Photometric Correction Tables   PCT
ssr_best_phottab    Phototmetric Calibration Table PHOT
ssr_best_sdctab     2-D Spectrum Distortion Corrections     SDC
ssr_best_cdstab     Cross-Disperser Scattering Tables   CDS
ssr_best_echsctab   Echelle Scattering Tables   ECH
ssr_best_ecstab     Echelle Cross-Dispersion Scattering Tables  EXS
ssr_best_halotab    Detectore Halo tables   HAL
ssr_best_riptab     Echelle Ripple Tables   RIP
ssr_best_srwtab     Scattering reference Wavelength Tables  SRW
ssr_best_psftab     Telescope Point Spread Function Tables  TEL
ssr_best_tdctab     NUV Dark Correction Tables  TDC
ssr_best_tdstab     Time Dependent Sensitivity Table   TDS
ssr_best_wcptab     Wavecal Parameters Reference Table  WCP
ssr_best_sptrctab   1-D Spectrum Trace Tables   1DT
ssr_best_xtractab   1-D Extraction Parameters Tables    1DX 
""",

"wfc3" : """
w3r_best_atodtab    Analog To Digital Lookup Table    A2D
w3r_best_biasfile   Bias Frame  BIA
w3r_best_darkfile   Dark Frame  DRK
w3r_best_dfltfile   Delta Flat Field Image   DFL
w3r_best_lfltfile   Low-order Flat Field Image    LFL
w3r_best_pfltfile   Pixel To Pixel Flat Field Image  PFL
w3r_best_dgeofile   Geometric Distortion Correction File   DXY
w3r_best_flshfile   Post-Flash Image   FLS
w3r_best_nlinfile   Detector Linearity Correction File   LIN
w3r_best_shadfile   Shutter Shading Correction Image  SHD
w3r_best_bpixtab    Bad Pixel Table    BPX
w3r_best_ccdtab     CCD Parameters Table CCD
w3r_best_comptab    Master Component Table (py/synphot)  TMC
w3r_best_graphtab   Master Graph Table (py/synphot)    TMG
w3r_best_idctab     Image Distortion Correction File  IDC
w3r_best_crrejtab   Cosmic Ray Rejection Parameter Table CRR
w3r_best_mdriztab   Multidrizzle Parameter Table   MDZ
w3r_best_oscntab    Overscan Region Tables  OSC
""",

"wfpc2" : """
w2r_best_atodfile   Analog to Digital Converter Lookup Table    R1?
w2r_best_biasfile   Bias Frame  R2?
w2r_best_darkfile   Dark Frame  R3?
w2r_best_flatfile   Flat Field R4?
w2r_best_maskfile   Static Mask File    R0?
w2r_best_shadfile   Shutter Shading Correction Image  R5?
w2r_best_comptab    Master Component Table (py/synphot)  TMC.FITS
w2r_best_graphtab   Master Graph Table (py/synphot)    TMG.FITS
w2r_best_idctab     Image Distortion Correction File  IDC.FITS
w2r_best_offtab not used    &bsp;/TD>
""",

}

TEXT_DESCR = {}

def logger(*args):
    pass

def make_text_descr():
    """Initialize mapping { filekind : "text description" }"""
    
    instruments = {}
    
    for instr, data in RAW_WEB_CUTS.items():
        # TEXT_DESCR[instr] = {}
        for line in cStringIO.StringIO(data):
            words = line.split()
            if len(words) < 3:
                continue
            filekind = words[0].split("_")[2]
            descr_words = [w.capitalize() for w in words[1:-1]]
            description = " ".join(descr_words)
            if filekind not in TEXT_DESCR:
                TEXT_DESCR[filekind] = description
            elif TEXT_DESCR[filekind] != description:
                logger("Different descriptions of", repr(filekind),
                            repr(TEXT_DESCR[filekind]), 
                            "versus", repr(description))
            if filekind not in instruments:
                instruments[filekind] = set()
            instruments[filekind] = instruments[filekind].union(set([instr]))
    for fkind in tpn.FILEKINDS:
        if fkind not in TEXT_DESCR:
            logger("No text description for filekind",repr(fkind))
            TEXT_DESCR[fkind] = fkind
    for fkind in TEXT_DESCR.keys():
        if fkind not in tpn.FILEKINDS:
            logger("Removing extraneous text description for", repr(fkind),
                   "of instruments", repr(sorted(instruments[fkind])))
            del TEXT_DESCR[fkind]

if __name__ == "__main__":
    import pprint
    import crds.log as log
    logger = log.warning
    make_text_descr()
    pprint.pprint(TEXT_DESCR)
else:
    make_text_descr()

