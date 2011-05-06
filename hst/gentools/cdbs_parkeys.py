import collections

import crds.hst.tpn as tpn

import crds.rmap as rmap
import crds.log as log

# =======================================================================

# MAPKEYS defines the key values which are added to the secondary lookup list.
MAPKEYS     = ('use_after','file')

# COMMENTKEYS defines the row items which are appended as a comment to each rmap mapping.
COMMENTKEYS = ('comments', 'delivery_#', 'delivery_date')

"""
KIND_KEYS maps different file kinds for each instrument onto a selection of the table columns which
are used to do the first stage lookup of a best reference.   Note that the names shown here correspond to HTML tables
and must be translated into equivalent FITS header keywords.
"""
KIND_KEYS = {

    # *-vars are optional and default to "*"
    # %-vars, or their FITS equivalent, are fetched from within the reference header if possible,  otherwise set to *
    # At lookup time,   a * will match any value or no value.

# kind_key comments were stripped directly from table XML using tlist.py.   The actual mapping information was
# human generated based on what looked important in the comments.

#../hst/acs/sources/acs_atodtab_0.xml --> ('amp', 'ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_biasfile_0.xml --> ('amp', 'ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after', 'x_size', 'y_size')
#../hst/acs/sources/acs_biasfile_0.xml --> ('amp', 'ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_biasfile_0.xml --> ('ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_biasfile_1.xml --> ('amp', 'ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_biasfile_1.xml --> ('ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_bpixtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_ccdtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_cfltfile_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_1', 'filter_2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_crrejtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after_date')
#../hst/acs/sources/acs_darkfile_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_darkfile_0.xml --> ('file',)
#../hst/acs/sources/acs_darkfile_1.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_darkfile_1.xml --> ('file',)
#../hst/acs/sources/acs_darkfile_2.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_dgeofile_0.xml --> ('availability', 'comments', 'delivery_#', 'detector', 'file', 'filter_1', 'filter_2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_idctab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_mdriztab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_mlintab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_oscntab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_1', 'filter_2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_1.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_1', 'filter_2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_1.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_2.xml --> ('availability', 'comments', 'delivery_#', 'detector', 'file', 'filter1', 'filter2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_3.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_1', 'filter_2', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_4.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_1', 'filter_2', 'otfr_start_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_pfltfile_5.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter_1', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/acs/sources/acs_spottab_0.xml --> ('availability', 'comments', 'delivery_#', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
   "acs" : {
             "biasfile" : ('detector','*ccd_gain','*amp','*x_size','*y_size',"%ltv1","%ltv2"),   #
             "atodtab" : ('detector','ccd_gain','amp'),
             "bpixtab" : ('detector',),
             "ccdtab" :  ('detector',),
             "cfltfile": ('detector','filter_1','filter_2'),
             "crrejtab" :  ('detector',),
             "darkfile" :  ('detector',),
             "dgeofile": ('detector','filter_1','filter_2'),
             "idctab" :  ('detector',),
             "mdriztab" :  ('detector',),
             "mlintab" :  ('%detector',),
             "oscntab" :  ('detector',),
             "pfltfile": ('detector',"%amp",'!filter_1','%filter_2','%obstype','!fw1offst=0.0','!fw2offst=0.0','!fwsoffst=0.0',),
             "spottab" :  ('detector',),
    },

#../hst/cos/cos_badttab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obsmode', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_bpixtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_brftab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_brsttab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obsmode', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_deadtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_disptab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_flatfile_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_geofile_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_lamptab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_phatab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_phottab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_tdstab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_wcptab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/cos/cos_xtractab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'otfr_start_use_date', 'use_after')
   "cos": {
            "badttab" : ('detector', 'obsmode'),
            "bpixtab" : ('detector',),
            "brftab" : ('detector',),
            "brsttab" : ('detector', 'obsmode'),
            "deadtab" : ('detector',),
            "disptab" : ('detector', 'obstype'),
            "flatfile" : ('detector', 'obstype'),
            "geofile" : ('detector',),
            "lamptab" : ('detector', 'obstype'),
            "phatab" : ('detector',),
            "phottab" : ('detector', 'obstype'),
            "tdstab" : ('detector',),
            "wcptab" : ('detector', 'obstype'),
            "xtractab" : ('detector', 'obstype'),
    },

#../hst/stis/sources/stis_apdstab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_apertab_0.xml  --> ('aperture', 'comments', 'delivery_#', 'delivery_date', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_biasfile_0.xml --> ('amp', 'binaxis1', 'binaxis2', 'ccd_gain', 'ccd_offset', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_bpixtab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_ccdtab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_cdstab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_crrejtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_darkfile_0.xml --> ('amp', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'gain', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_darkfile_1.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_disptab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_echsctab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_exstab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_halotab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_idctab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_inangtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_lamptab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_lfltfile_0.xml --> ('aperture', 'cen._wave.', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'opt._element', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_mlintab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_mofftab_0.xml  --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_pctab_0.xml    --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'opt._element', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_pfltfile_0.xml --> ('aperture', 'cen._wave.', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'opt._element', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_phottab_0.xml  --> ('cen._wave.', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'obstype', 'opt._element', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_riptab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_sdctab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_sptrctab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_srwtab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_tdctab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_tdstab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_wcptab_0.xml   --> ('comments', 'delivery_#', 'delivery_date', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/stis/sources/stis_xtractab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
    "stis": {
            "apdstab"  : (),  # 'pedigree'),
            "apertab"  : ('aperture',),
            "biasfile" : ('detector','ccd_gain','amp','ccd_offset','binaxis1','binaxis2',),   # ('detector', 'amp','binaxis1','binaxis2','ccd_gain','ccd_offset'),
            "bpixtab"  : ('detector',),
            "ccdtab"   : ('detector',),
            "cdstab"   : ('detector',),
            "crrejtab" : ('detector',),
            "darkfile" : ('*detector','*amp', '*gain'),
            "disptab"  : ('detector',),
            "echsctab" : ('detector',),
            "exstab"   : ('detector',),
            "halotab"  : ('detector',),
            "idctab"   : ('detector',),
            "inangtab" : ('detector',),
            "lamptab"  : (),
            "lfltfile" : ('detector','obstype','opt._element','*aperture','*cen._wave.',),
            "mlintab"  : ('detector',),
            "mofftab"  : ('detector',),
            "pctab"    : ('detector','obstype','opt._element',),
            "pfltfile" : ('detector','obstype','opt._element','aperture','*cen._wave.'),
            "phottab"  : ('detector','obstype','opt._element','*cen._wave.'),
            "riptab"   : ('detector',),
            "sdctab"   : ('detector',),
            "sptrctab" : ('detector',),
            "srwtab"   : ('detector',),
            "tdctab"   : ('detector',),
            "tdstab"   : ('detector',),
            "wcptab"   : (),
            "xtractab" : ('detector',),
   },


#../hst/wfc3/sources/wfc3_biasfile_0.xml --> ('amp', 'binaxis1', 'binaxis2', 'ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_bpixtab_0.xml --> ('amp', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_ccdtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_crrejtab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_darkfile_0.xml --> ('amp', 'binaxis1', 'binaxis2', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_darkfile_1.xml --> ('amp', 'ccd_gain', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'samp-seq', 'subtype', 'use_after')
#../hst/wfc3/sources/wfc3_dfltfile_0.xml --> ('file',)
#../hst/wfc3/sources/wfc3_dfltfile_1.xml --> ('file',)
#../hst/wfc3/sources/wfc3_dgeofile_0.xml --> ('file',)
#../hst/wfc3/sources/wfc3_idctab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_lfltfile_0.xml --> ('file',)
#../hst/wfc3/sources/wfc3_lfltfile_1.xml --> ('file',)
#../hst/wfc3/sources/wfc3_mdriztab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_nlinfile_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_oscntab_0.xml --> ('comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_pfltfile_0.xml --> ('amp', 'binaxis1', 'binaxis2', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_pfltfile_1.xml --> ('amp', 'binaxis1', 'binaxis2', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_pfltfile_2.xml --> ('amp', 'binaxis1', 'binaxis2', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_pfltfile_3.xml --> ('amp', 'comments', 'delivery_#', 'delivery_date', 'detector', 'file', 'filter', 'otfr_start_use_date', 'pedigree', 'use_after')
#../hst/wfc3/sources/wfc3_shadfile_0.xml --> ('file',)

    "wfc3" : {
                # biasfile keyorder is *fixed* by a hack function in gen_file_rmap.py
                "biasfile" : ('detector', 'amp', 'ccd_gain','binaxis1', 'binaxis2','!aperture','%subarray'),
                "bpixtab" : ('detector',),
                "ccdtab" : ('detector',),
                "crrejtab" : ('detector',),
                "darkfile" : ('detector', '*amp', '*ccd_gain', '*samp-seq', '*subtype', '*binaxis1=1.0', '*binaxis2=1.0',),
                "idctab" : ('detector',),
                "mdriztab" : ('detector',),
                "nlinfile" : ('detector',),
                "oscntab" : ('detector',),
                "pfltfile" : ('detector', 'filter', '*binaxis1', '*binaxis2',),  # , "amp"),
    },
}

# ===================================================================

"""

The following dumps out the mapping from CDBS HTML parkeys to FITS header keywords:

ACS:

[keymatch(header_keyword='idctab', rmap_keys=('detector', 'use_after'), tpn_keys=['DETCHIP', 'DETECTOR', 'DIRECTION', 'FILETYPE', 'FILTER1', 'FILTER2', 'INSTRUME', 'NORDER', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='atodtab', rmap_keys=('detector', 'ccd_gain', 'amp', 'use_after'), tpn_keys=['CCDAMP', 'CCDCHIP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='cfltfile', rmap_keys=('detector', 'filter_1', 'filter_2', 'use_after'), tpn_keys=['DETECTOR', 'FILETYPE', 'FILTER1', 'FILTER2', 'INSTRUME', 'OBSTYPE', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='spottab', rmap_keys=('detector', 'use_after'), tpn_keys=['DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='dgeofile', rmap_keys=('detector', 'filter_1', 'filter_2', 'use_after'), tpn_keys=['DETECTOR', 'FILETYPE', 'FILTER1', 'FILTER2', 'INSTRUME', 'OBSTYPE', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='bpixtab', rmap_keys=('detector', 'use_after'), tpn_keys=['CCDAMP', 'CCDCHIP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='crrejtab', rmap_keys=('detector', 'use_after'), tpn_keys=['CCDCHIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='pfltfile', rmap_keys=('detector', '*filter_1', '*filter_2', 'use_after'), tpn_keys=['CCDAMP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'FILTER1', 'FILTER2', 'FW1OFFST', 'FW2OFFST', 'FWSOFFST', 'INSTRUME', 'OBSTYPE', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='mdriztab', rmap_keys=('detector', 'use_after'), tpn_keys=['DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='darkfile', rmap_keys=('detector', 'use_after'), tpn_keys=['CCDAMP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='ccdtab', rmap_keys=('detector', 'use_after'), tpn_keys=['CCDAMP', 'CCDCHIP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='mlintab', rmap_keys=('detector', 'use_after'), tpn_keys=['DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='oscntab', rmap_keys=('detector', 'use_after'), tpn_keys=['CCDAMP', 'CCDCHIP', 'DETECTOR', 'FILETYPE', 'INSTRUME']),
 keymatch(header_keyword='biasfile', rmap_keys=('detector', 'ccd_gain', '*amp', '*x_size', '*y_size', 'use_after'), tpn_keys=['CCDAMP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER'])]

COS:

[keymatch(header_keyword='badttab', rmap_keys=('detector', 'obsmode', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSMODE', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='xtractab', rmap_keys=('detector', 'obstype', 'use_after'), tpn_keys=['APERTURE', 'CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='brftab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='lamptab', rmap_keys=('detector', 'obstype', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='geofile', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='bpixtab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='tdstab', rmap_keys=('detector', 'use_after'), tpn_keys="[Errno 2] No such file or directory: '../hst/cdbs_data/cos_tds.tpn'"),
 keymatch(header_keyword='phatab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='wcptab', rmap_keys=('detector', 'obstype', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='flatfile', rmap_keys=('detector', 'obstype', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='brsttab', rmap_keys=('detector', 'obsmode', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSMODE', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='phottab', rmap_keys=('detector', 'obstype', 'use_after'), tpn_keys=['APERTURE', 'CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='deadtab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS']),
 keymatch(header_keyword='disptab', rmap_keys=('detector', 'obstype', 'use_after'), tpn_keys=['APERTURE', 'CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'SEGMENT', 'USEAFTER', 'VCALCOS'])]

STIS:

[keymatch(header_keyword='lfltfile', rmap_keys=('detector', 'obstype', 'opt._element', 'aperture', 'cen._wave.', 'use_after'), tpn_keys="[Errno 2] No such file or directory: '../hst/cdbs_data/stis_lfl.tpn'"),
 keymatch(header_keyword='mofftab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='halotab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='riptab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='lamptab', rmap_keys=('*detector', 'use_after'), tpn_keys=['DESCRIP', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='tdstab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='cdstab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='pctab', rmap_keys=('detector', 'obstype', 'opt._element', 'use_after'), tpn_keys=['APERTURE', 'CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='crrejtab', rmap_keys=('detector', 'use_after'), tpn_keys=['CRSPLIT', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'MEANEXP', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='pfltfile', rmap_keys=('detector', 'obstype', 'opt._element', 'aperture', 'cen._wave.', 'use_after'), tpn_keys="[Errno 2] No such file or directory: '../hst/cdbs_data/stis_pfl.tpn'"),
 keymatch(header_keyword='apdstab', rmap_keys=('*detector', 'use_after'), tpn_keys=['APERTURE', 'DESCRIP', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='inangtab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='wcptab', rmap_keys=('*detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='darkfile', rmap_keys=('*detector', '*amp', '*gain', 'use_after'), tpn_keys=['CCDAMP', 'CCDGAIN', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='biasfile', rmap_keys=('detector', 'ccd_gain', 'amp', 'ccd_offset', 'binaxis1', 'binaxis2', 'use_after'), tpn_keys=['CCDAMP', 'CCDGAIN', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='mlintab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='echsctab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='disptab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='idctab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'FILTER', 'INSTRUME', 'NORDER', 'PARITY', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='xtractab', rmap_keys=('detector', 'use_after'), tpn_keys=['APERTURE', 'CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='phottab', rmap_keys=('detector', 'obstype', 'opt._element', 'cen._wave.', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OBSTYPE', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='sptrctab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='exstab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='sdctab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='bpixtab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='srwtab', rmap_keys=('detector', 'use_after'), tpn_keys=['CENWAVE', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'OPT_ELEM', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='ccdtab', rmap_keys=('detector', 'use_after'), tpn_keys=['BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'CCDOFFST', 'DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='apertab', rmap_keys=('aperture', 'use_after'), tpn_keys=['APERTURE', 'DESCRIP', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='tdctab', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER'])]

WFC3:

WARNING[52]: Can't get rmap for: ('wfc3', 'lfltfile')
WARNING[53]: Can't get rmap for: ('wfc3', 'dgeofile')
WARNING[54]: Can't get tpn for: ('wfc3', 'dgeofile')
WARNING[55]: Can't get rmap for: ('wfc3', 'dfltfile')
WARNING[56]: Can't get rmap for: ('wfc3', 'shadfile')
Out[37]:
[keymatch(header_keyword='lfltfile', extension='LFL', rmap_keys="Can't load rmap file: '../hst/wfc3/rmaps/wfc3_lfltfile.rmap'", tpn_keys=['CCDAMP', 'DETECTOR', 'FILETYPE', 'FILTER', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='idctab', extension='IDC', rmap_keys=('detector', 'use_after'), tpn_keys=['DETCHIP', 'DETECTOR', 'DIRECTION', 'FILETYPE', 'INSTRUME', 'NORDER', 'PARITY', 'PEDIGREE', 'USEAFTER', 'WAVELENGTH']),
 keymatch(header_keyword='dgeofile', extension='DXY', rmap_keys="Can't load rmap file: '../hst/wfc3/rmaps/wfc3_dgeofile.rmap'", tpn_keys="[Errno 2] No such file or directory: '../hst/cdbs_data/wfc3_DXY.tpn'"),
 keymatch(header_keyword='bpixtab', extension='BPX', rmap_keys=('detector', 'amp', 'use_after'), tpn_keys=['CCDCHIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='crrejtab', extension='CRR', rmap_keys=('detector', 'use_after'), tpn_keys=['CRSPLIT', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='pfltfile', extension='PFL', rmap_keys=('detector', 'amp', 'filter', '*binaxis1', '*binaxis2', 'use_after'), tpn_keys=['CCDAMP', 'DETECTOR', 'FILETYPE', 'FILTER', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='mdriztab', extension='MDZ', rmap_keys=('detector', 'use_after'), tpn_keys=['DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='nlinfile', extension='LIN', rmap_keys=('detector', 'use_after'), tpn_keys=['DESCRIP', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='darkfile', extension='DRK', rmap_keys=('detector', 'amp', '*ccd_gain', '*samp-seq', '*subtype', '*binaxis1', '*binaxis2', 'use_after'), tpn_keys=['CCDAMP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'SUBTYPE', 'USEAFTER']),
 keymatch(header_keyword='dfltfile', extension='DFL', rmap_keys="Can't load rmap file: '../hst/wfc3/rmaps/wfc3_dfltfile.rmap'", tpn_keys=['CCDAMP', 'DETECTOR', 'FILETYPE', 'FILTER', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='biasfile', extension='BIA', rmap_keys=('detector', 'amp', 'ccd_gain', 'binaxis1', 'binaxis2', 'use_after'), tpn_keys=['BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='oscntab', extension='OSC', rmap_keys=('detector', 'use_after'), tpn_keys=['BINX', 'BINY', 'CCDAMP', 'CCDCHIP', 'DETECTOR', 'FILETYPE', 'INSTRUME']),
 keymatch(header_keyword='ccdtab', extension='CCD', rmap_keys=('detector', 'use_after'), tpn_keys=['BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDCHIP', 'CCDGAIN', 'CCDOFSTA', 'CCDOFSTB', 'CCDOFSTC', 'CCDOFSTD', 'DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER']),
 keymatch(header_keyword='shadfile', extension='SHD', rmap_keys="Can't load rmap file: '../hst/wfc3/rmaps/wfc3_shadfile.rmap'", tpn_keys=['DETECTOR', 'FILETYPE', 'INSTRUME', 'PEDIGREE', 'USEAFTER'])]
"""

"""
The CDBS table column headers are similar to but sometimes not exactly the same as
corresponding FITS header keywords.   This table establishes the correspondence for
the HST instruments
"""

CDBS_PARKEYS_TO_FITS = {

    "filter_1" : "FILTER1",
    "filter_2" : "FILTER2",
    "ccd_gain" : "CCDGAIN",
    "amp"      : "CCDAMP",
    "ccd_offset" : "CCDOFFST",
    "samp_seq" : "SAMP_SEQ",

    "use_after" : "USEAFTER",

    "acs" : {
             "x_size" : "NAXIS1",
             "y_size" : "NAXIS2",
    },

    "cos" : {
    },

    "stis" : {
        "opt._element" : "OPT_ELEM",
        "cen._wave." : "CENWAVE",
        "gain"     : "CCDGAIN",
    },

    "wfc3" : {
        "samp-seq" : "SAMP_SEQ"
    },
}

def to_fitskey(instrument, var):
    """Translate a parkey name into a FITS header keyword."""
    try:
        fits_key = CDBS_PARKEYS_TO_FITS[instrument][var]
    except KeyError:
        try:
            fits_key = CDBS_PARKEYS_TO_FITS[var]
        except KeyError:
            fits_key = var.upper()
    return fits_key

# =======================================================================

"""
The following classes are emitted at rmap generation time to define the
code which will operate on the rmap at runtime,  enabling customization
of the selectors by instrument and reftype.
"""

SELECTOR_CLASSES = {
#    "acs" : {
#        "biasfile" : "crds.hst.acs.AcsBiasfileSelector",
#        "pfltfile" : "crds.hst.acs.AcsPfltfileSelector",
#    },
#    "wfc3" : {
#        "biasfile" : "crds.hst.wfc3.Wfc3BiasfileSelector",
#    },
}

def get_selector_class(instrument, reftype):
    try:
        return SELECTOR_CLASSES[instrument][reftype]
    except KeyError:
        return None


# =======================================================================
keymatch = collections.namedtuple("keymatch","header_keyword,extension,rmap_keys,tpn_keys")

def get_parameters(instrument):
    """Given an `instrument`,  get_parameters() will dump the rmap and tpn parameter lists
    so that a correspondence can be defined between FITS header keywords and CDBS HTML table
    column names.
    """
    header, data = rmap.load_mapping(instrument)
    components = []
    for reftype, (extension, map) in data.items():
        try:
            rmap_keys = rmap.get_rmap(instrument, reftype).header["parkey"]
        except Exception, e:
            rmap_keys = str(e)
            log.warning("Can't get rmap for:", repr((instrument, reftype)), str(e))
        try:
            tpn_keys = tuple(sorted(tpn.get_tpn(instrument, extension).keys()))
        except Exception, e:
            tpn_keys = str(e)
            log.warning("Can't get tpn for:", repr((instrument, reftype)), str(e))
        comp = keymatch(reftype, extension, rmap_keys, tpn_keys)
        components.append(comp)
    return components

