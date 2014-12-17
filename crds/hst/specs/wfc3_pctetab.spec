{
    'description' : '''
PR #79700, 79701

Keyword: PCTETAB

Pixel-by-pixel CTE correction table (PCTE): <uniquename>_cte.fits

Description: The CTE table contains the parameters necessary for determining
and applying the appropriate CTE correction.

Format: This file departs from the standard format of SCI, ERR, and DQ image
extensions. The parameters for controlling the CTE correction are stored in
two floating-point FITS file binary tables and two small images, each in its
own file extension. Table 2 below summarizes the contents of each of the
extension.

The first extension lists the charge-trap levels; the columns are
W, QLEV_W, and DPDE_W, respectively the trap number, the charge-packet size
it applies to (in electrons), and the size of the trap (also in electrons).
The second extension contains the CTE scalings as a function of column number.
This table consists of 5 columns, each with 8412 elements. The first column
contains the integer column number in the wide 'raz' file format. Columns 2-6
contain the real*4 CTE scaling appropriate for that column at the 512th row,
1024th row, 1536th row, and 2048th row respectively. Column names are IZ,
SENS_0512, SENS_1024, SENS_1536, and SENS_2048. The third extension contains
the differential CTE trail profile as a function of charge level, presented as
a small image. Finally, the fourth extension contains the cumulative CTE trail
profile as function of charge level, also in the form of an image.

Selection criteria: The appropriate CTE-correction reference file is selected
based on the keywords DETECTOR, BINAXIS1, and BINAXIS2.

Restrictions: none

Required additional keywords: FILETYPE = 'PIXCTE'
''',
    'extra_keys': (),
    'file_ext': '.fits',
    'filetype': 'pixcte',
    'ld_tpn': 'wfc3_cte_ld.tpn',
    'parkey': ('DETECTOR', 'BINAXIS1', 'BINAXIS2'),
    'reffile_format': 'TABLE',
    'reffile_required': 'none',
    'reffile_switch': 'PCTECORR',
    'rmap_relevance': '((DETECTOR == "UVIS") and (SUBARRAY == "FALSE"))',
    'suffix': 'cte',
    'text_descr': 'Pixel CTE Correction Table',
    'tpn': 'wfc3_cte.tpn',
    'unique_rowkeys': None,
}
