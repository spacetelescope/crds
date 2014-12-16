{
    'description': '''

PR: 79700, 79701
Keyword: BIACFILE

CTE Bias Image File (BIC): <uniquename>_bic.fits

Description: The bias reference image consists of a real*4 two-dimensional
image of the bias level for use with the CTE-corrected data.
Note: this file is only for use by the CTE-correction branch of calwf3; it is
not used for calibrating non-CTE corrected data.

Format: Bias reference images are zero exposure time, full-frame images,
including serial and parallel overscan regions. Thus the bic image size is
2070 x 4206 pixel image for unbinned images. There are no
plans to provide a pixel-based CTE correction for binned images or subarray
images, though we hope to include subarrays at some time in the future.
The CTE bias reference images for each of the 2 CCDs that
make up the full UVIS detector array are stored separately in 2 imsets in the
dark file, identical to the UVIS science data format. There is no IR equivalent
of this file.

Selection criteria: The appropriate CTE bias reference file is selected by the
keywords DETECTOR, APERTURE, CCDAMP, CCDGAIN, BINAXIS1, and BINAXIS2.

Restrictions: none

Required additional keywords: FILETYPE = 'CTEBIAS'
 
''',
    'extra_keys': ('SUBARRAY',),
    'file_ext': '.fits',
    'filetype': 'CTEBIAS',
    'ld_tpn': 'wfc3_bic_ld.tpn',
    'parkey': ('DETECTOR', 'APERTURE', 'CCDAMP', 'CCDGAIN', 'BINAXIS1', 'BINAXIS2'),
    'parkey_relevance': {},
    'reffile_format': 'IMAGE',
    'reffile_required': 'YES',
    'reffile_switch': 'PCTECORR',
    'rmap_relevance': '((DETECTOR == "UVIS") and (SUBARRAY == "FALSE"))',
    'suffix': 'bic',
    'text_descr': 'CTE Bias Frame',
    'tpn': 'wfc3_bic.tpn',
    'unique_rowkeys': None,
}
