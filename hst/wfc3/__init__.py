import crds.log as log
import crds.rmap as rmap

# =======================================================================

"""
** See WFC3 TIR-2009-03, Changes to CDBS expansion and selection criteria
   for WFC3 UVIS bias reference files

DETECTOR = UVIS

For WFC3,  the aperture value listed in the reference file is expanded into
many CDBS records with replacement APERTUREs.  Best Reference matches the
APERTURE value in the dataset to the APERTURE value in CDBS records... not the
unexpanded APERTURE from the reference file header.

WFC3_EXPANDED_APERTURES as the form:

  {  (BINAXIS1, BINAXIS2, APERTURE)   :  [APERTURE_EXPANSIONS]  }

CRDS expands the reference file APERTURE at rmap creation time.

"""

header_substitutions = {
    "APERTURE" : {
        "FULLFRAME_4AMP" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER", "UVIS-QUAD","UVIS-QUAD-FIX","G280-REF",
        ),
        "QUAD_CORNER_SUBARRAYS" : (
            "UVIS-QUAD-SUB",
            "UVIS1-C512A-SUB", "UVIS1-C512B-SUB",
            "UVIS2-C512C-SUB", "UVIS2-C512D-SUB",
        ),
        "CHIP1_SUB_NOCORNERS" : (
            "UVIS1-2K4-SUB", "UVIS1-M512-SUB",
        ),
        "CHIP2_SUB_NOCORNERS" : (
            "UVIS2-2K4-SUB", "UVIS2-M512-SUB",
        ),
        "FULLFRAME_2AMP" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER",
        ),
        "CUSTOM_SUBARRAYS" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER", "UVIS-QUAD", "UVIS-QUAD-FIX", "G280-REF"
        ),
        "*" : (
            "UVIS", "UVIS-FIX", "UVIS1", "UVIS1-FIX", "UVIS2", "UVIS2-FIX",
            "UVIS-CENTER", "UVIS-QUAD", "UVIS-QUAD-FIX", "G280-REF"
        ),
    },
    'CCDAMP' : {
        'G280_AMPS' : ('ABCD','A','B','C','D','AC','AD','BC','BD'), 
    },
}

header_additions = [
    ("substitutions", header_substitutions),
]

def wfc3_biasfile_filter(kmap):
    log.write("Hacking WFC3 Biasfile  APERTURE macros.   Adding t6i1733ei_bia.fits special case.")
    kmap[('UVIS', 'G280_AMPS', '1.5', '1.0', '1.0', 'G280-REF', 'T')] = \
      [rmap.Filemap(date='1990-01-01 00:00:00', file='t6i1733ei_bia.fits',
              comment='Placeholder file. All values set to zero.--------------------------, 12047, Jun 18 2009 05:36PM')]
    return kmap, header_additions

