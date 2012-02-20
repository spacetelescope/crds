"""This module defines text descriptions for each HST file kind,  which I think
are similar to but distinct from the actual REFTYPE keyword values.

This data was manually cut-and-pasted from links like this:

https://blogs.stsci.edu/cdbs/sql-tables/acs-acs-ref-data-table-reference-file-identifier/

based on limited e-mail direction from Rossy.
"""

import cStringIO

RAW_WEB_CUTS = {
"acs" : """
acr_best_biasfile   BIAS IMAGE  BIA
acr_best_cfltfile   CORONAGRAPHIC SPOT FLAT IMAGE   CFL
acr_best_darkfile   DARK IMAGE  DRK
acr_best_dfltfile   DELTA FLAT IMAGE    DFL
acr_best_dgeofile   GEOMETRIC DELTA IMAGE (DISTORTION)  DXY
acr_best_flshfile   POST FLASH IMAGE    FLS
acr_best_lfltfile   LOW ORDER FLAT IMAGE    LFL
acr_best_pfltfile   PIXEL TO PIXEL FLAT FIELD IMAGE PFL
acr_best_shadfile   SHUTTER SHADING IMAGE   SHD
acr_best_atodtab    ANALOG-TO-DIGITAL TABLE A2D
acr_best_bpixtab    BAD PIXEL TABLE BPX
acr_best_ccdtab CCD PARAMETERS TABLE    CCD
acr_best_comptab    THE HST MASTER COMPONENT TABLE  TMC
acr_best_crrejtab   COSMIC RAY REJECTION PARAMETER TABLE    CRR
acr_best_graphtab   THE HST GRAPH TABLE TMG
acr_best_idctabtab  DISTORTION COEFFICIENTS TABLE   IDC
acr_best_mdriztabtab    MULTIDRIZZLE PARAMETER TABLE    MDZ
acr_best_mlintabtab MAMA LINEARITY TABLE    LIN
acr_best_oscntabtab CCD OVERSCAN REGION TABLE   OSC
acr_best_phottabtab PHOTOMETRY and THROUGHPUT TABLE PHT
acr_best_spottabtab SPOT POSITION TABLE CSP
acr_best_drkcfile   CTE corrected dark  DKC
acr_best_pctetab    CTE CORRECTION TABLE    PCTE
acr_best_imphttab   PHOTOMETRY KEYWORD TABLE    IMP
""", 

"cos" : """
csr_best_geofile    Geometric Distortion Correction     GEO
csr_best_flatfile   Flat Field  FLT
csr_best_badttab    Bad Time Interval Table     BADT
csr_best_bpixtab    Data Quality Initialization Tables  BPIX
csr_best_brftab     Baseline Reference Frame Table  BRF
csr_best_brsttab    Burst Parameters Tables     BURST
csr_best_deadtab    Deadtime Reference Table    DEAD
csr_best_disptab    Dispersion Relation Tables  DISP
csr_best_fluxtab    Sensitivity Reference Files     PHOT
csr_best_lamptab    Template Cal Lamp Spectra Tables    LAMP
csr_best_phatab     Pulse Height Parameters Tables  PHA
csr_best_tdstab     Time Dependent Sensitivity Table    TDS
csr_best_wcptab     Wavecal Parameters Reference Table  WCP
csr_best_xtractab   1-D Extraction Parameters Tables    1DX
""",

"nicmos" : """
nsr_best_darkfile   Dark Current File   DRK
nsr_best_flatfile   Flat Field  FLT
nsr_best_illmfile   Illumination Pattern File   ILM
nsr_best_maskfile   On-Orbit MASK for NCS data  
nsr_best_nlinfile   Detector Linearity File     LIN
nsr_best_noisfile   Detector Read-Noise File    NOI
nsr_best_saadfile   Post SAA Dark Assoc.    Name
nsr_best_tempfile   Temperature-dependent dark reference file   TDD
nsr_best_backtab    Background Model Table  -
nsr_best_phottab    Phototmetric Calibration Table  PHT
nsr_best_idctab     Image Distortion Coefficients File  IDC
""",

"stis" : """
ssr_best_biasfile   Bias image file     BIA
ssr_best_darkfile   Dark image files    DRK
ssr_best_pfltfile   Pixel-to-pixel flat files   PFL
ssr_best_dfltfile   Delta flat image files  DFL
ssr_best_lfltfile   Low-order flat image files  LFL
ssr_best_shadfile   Shutter shading correction image files  SSC
ssr_best_sdstfile   Small scale distortion image files  SSD
ssr_best_atodtab    A2D Correction Tables   A2D
ssr_best_apdstab    Aperture Description Tables     APD
ssr_best_apertab    Aperture Throughput Tables  APT
ssr_best_bpixtab    Bad Pixel Tables    BPX
ssr_best_ccdtab     CCD Parameters Tables   CCD
ssr_best_crrejtab   Cosmic Ray Rejection Parameters Tables  CRR
ssr_best_disptab    Dispersion Coefficients Tables  DSP
ssr_best_inangtab   Incidence Angle Correction Tables   IAC
ssr_best_idctab     Image Distortion Correction Tables  IDC
ssr_best_mlintab    MAMA Linearity Tables   LIN
ssr_best_lamptab    Calibration Lamp Tables     LMP
ssr_best_mofftab    MAMA Offset Correction Tables   MOC
ssr_best_pctab  Photometric Correction Tables   PCT
ssr_best_phottab    Photometric Conversion Tables   PHOT
ssr_best_sdctab     2-D Spectrum Distortion Corrections     SDC
ssr_best_cdstab     Cross-Disperser Scattering Tables   CDS
ssr_best_echsctab   Echelle Scattering Tables   ECH
ssr_best_ecstab     Echelle Cross-Dispersion Scattering Tables  EXS
ssr_best_halotab    Detectore Halo tables   HAL
ssr_best_riptab     Echelle Ripple Tables   RIP
ssr_best_srwtab     Scattering reference Wavelength Tables  SRW
ssr_best_psftab     Telescope Point Spread Function Tables  TEL
ssr_best_tdctab     NUV Dark Correction Tables  TDC
ssr_best_tdstab     Time Dependent Sensitivity Tables   TDS
ssr_best_wcptab     Wavecal Parameters Tables   WCP
ssr_best_sptrctab   1-D Spectrum Trace Tables   1DT
ssr_best_xtractab   1-D Extraction Parameters Tables    1DX 
""",

"wfc3" : """
w3r_best_atodtab    Analog to Digital Converter Lookup Table    A2D
w3r_best_biasfile   Bias Frame  BIA
w3r_best_darkfile   Dark Frame  DRK
w3r_best_dfltfile   Delta Flat Field File   DFL
w3r_best_lfltfile   Low-Order Flat Field    LFL
w3r_best_pfltfile   Pixel-to-Pixel Flat Field   PFL
w3r_best_dgeofile   Geometric Distortion    DXY
w3r_best_flshfile   Post-Flash Image File   FLS
w3r_best_nlinfile   Linearity Correction file   LIN
w3r_best_shadfile   Shutter Shading Correction  SHD
w3r_best_bpixtab    Bad Pixel Tables    BPX
w3r_best_ccdtab     Detector Characteristics Tables CCD
w3r_best_comptab    Master Component Table  TMC
w3r_best_graphtab   The Master Graph Table (SYNPHOT)    TMG
w3r_best_idctab     Image Distortion Coefficients File  IDC
w3r_best_crrejtab   Cosmic Ray Rejection Tables CRR
w3r_best_mdriztab   Multidrizzle Parameter Tables   MDZ
w3r_best_oscntab    Overscan Region Tables  OSC
""",

"wfpc2" : """
w2r_best_atodfile   Analog to Digital Converter Lookup Table    R1?
w2r_best_biasfile   Bias Frame  R2?
w2r_best_darkfile   Dark Frame  R3?
w2r_best_flatfile   Flat Field File R4?
w2r_best_maskfile   Static Mask File    R0?
w2r_best_shadfile   Shutter Shading Correction  R5?
w2r_best_comptab    Master Component Table  TMC.FITS
w2r_best_graphtab   The Master Graph Table (SYNPHOT)    TMG.FITS
w2r_best_idctab     Image Distortion Coefficients File  IDC.FITS
w2r_best_offtab not used    &bsp;/TD>
""",

}

TEXT_DESCR = {}

def make_text_descr():
    """Initialize nested mapping { [instr][filekind] : "text description" }"""
    for instr, data in RAW_WEB_CUTS.items():
        TEXT_DESCR[instr] = {}
        for line in cStringIO.StringIO(data):
            words = line.split()
            if len(words) < 3:
                continue
            filekind = words[0].split("_")[2]
            descr_words = [w.capitalize() for w in words[1:-1]]
            TEXT_DESCR[instr][filekind] = " ".join(descr_words)

make_text_descr()

