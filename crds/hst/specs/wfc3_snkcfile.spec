{
    'description' : '''
PR #79700,79701

Keyword: SNKCFILE

Sink pixel correction image (SNK): <uniquename>_snk.fits

Description: The sink-pixel reference file provides a map of sink-pixel
locations, including the dates at which the sinks first appeared and details
for flagging preceding and trailing neighboring pixel(s) impacted by the sinks.

Format: The file is a two-dimensional fits extension file but does not contain
ERR or DQ image extensions. There are two image SCI extensions, chip 2 in [1]
and chip 1 in [2], in raw full-frame unbinned size of 2070 x 4206.

Science pixels affected by sink pixels and their likely-contaminated neighbors
will now be flagged by calwf3 in the science image data quality file with
bitmask of 1024, the value for a charge trap.

Selection criteria: The appropriate sink pixel map file is selected by the
keywords DETECTOR, BINAXIS1, and BINAXIS2.

Restrictions: none

Required additional keywords: FILETYPE = 'SINK PIXELS'
''',
    'extra_keys': (),
    'file_ext': '.fits',
    'filetype': 'SINK PIXELS',
    'ld_tpn': 'wfc3_snk_ld.tpn',
    'parkey': ('DETECTOR', 'BINAXIS1', 'BINAXIS2'),
    'parkey_relevance': {},
    'reffile_format': 'IMAGE',
    'reffile_required': 'YES',
    'reffile_switch': 'PCTECORR',
    'rmap_relevance': '(PCTECORR != "OMIT")',
    'suffix': 'snk',
    'text_descr': 'Sink Pixel Correction Image',
    'tpn': 'wfc3_snk.tpn',
    'unique_rowkeys': None,
}
