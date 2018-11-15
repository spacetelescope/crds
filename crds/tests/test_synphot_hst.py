"""This module tests the synphot pseudo-instrument support for HST."""

# ==============================================================
from crds.core import config, naming, timestamp
from crds.hst import locate as hst_locate

from crds.tests import test_config

# ==============================================================

def dt_synphot_naming():
    """
    >>> old_state = test_config.setup()

    >>> NOW = timestamp.parse_date("2018-11-14T00:00:00")
    
    THERMAL

    >>> config.is_crds_name("wfc3_ir_f098m_002_th.fits")
    False
    >>> config.is_cdbs_name("wfc3_ir_f098m_002_th.fits")
    True
    >>> config.is_reference("wfc3_ir_f098m_002_th.fits")
    True
    >>> config.is_mapping("wfc3_ir_f098m_002_th.fits")
    False
    >>> hst_locate.get_file_properties("wfc3_ir_f098m_002_th.fits")
    ('synphot', 'thermal')
    >>> hst_locate.ref_properties_from_cdbs_path("data/wfc3_ir_f098m_002_th.fits")
    ('data', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    >>> hst_locate.ref_properties_from_header("data/wfc3_ir_f098m_002_th.fits")
    ('data', 'hst', 'synphot', 'thermal', 'wfc3_ir_f098m_002_th', '.fits')
    >>> naming.generate_unique_name("wfc3_ir_f098m_002_th.fits", "hst", NOW)
    '2be00000m_th.fits'

    THRUPUT

    >>> config.is_crds_name("wfc3_uvis_f469nf2_003_syn.fits")
    False
    >>> config.is_cdbs_name("wfc3_uvis_f469nf2_003_syn.fits")
    True
    >>> config.is_reference("wfc3_uvis_f469nf2_003_syn.fits")
    True
    >>> config.is_mapping("wfc3_uvis_f469nf2_003_syn.fits")
    False
    >>> hst_locate.get_file_properties("wfc3_uvis_f469nf2_003_syn.fits")
    ('synphot', 'thruput')
    >>> hst_locate.ref_properties_from_cdbs_path("data/wfc3_uvis_f469nf2_003_syn.fits")
    ('data', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    >>> hst_locate.ref_properties_from_header("data/wfc3_uvis_f469nf2_003_syn.fits")
    ('data', 'hst', 'synphot', 'thruput', 'wfc3_uvis_f469nf2_003_syn', '.fits')
    >>> naming.generate_unique_name("wfc3_uvis_f469nf2_003_syn.fits", "hst", NOW)
    '2be00000m_syn.fits'

    TMGTAB

    >>> config.is_crds_name("2381905mm_tmg.fits")
    False
    >>> config.is_cdbs_name("2381905mm_tmg.fits")
    True
    >>> config.is_reference("2381905mm_tmg.fits")
    True
    >>> config.is_mapping("2381905mm_tmg.fits")
    False
    >>> hst_locate.get_file_properties("2381905mm_tmg.fits")
    ('synphot', 'tmgtab')
    >>> hst_locate.ref_properties_from_cdbs_path("data/2381905mm_tmg.fits")
    ('data', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    >>> hst_locate.ref_properties_from_header("data/2381905mm_tmg.fits")
    ('data', 'hst', 'synphot', 'tmgtab', '2381905mm_tmg', '.fits')
    >>> naming.generate_unique_name("2381905mm_tmg.fits", "hst", NOW)
    '2be00000m_tmg.fits'

    TMCTAB

    >>> config.is_crds_name("2b516556m_tmc.fits")
    False
    >>> config.is_cdbs_name("2b516556m_tmc.fits")
    True
    >>> config.is_reference("2b516556m_tmc.fits")
    True
    >>> config.is_mapping("2b516556m_tmc.fits")
    False
    >>> hst_locate.get_file_properties("2b516556m_tmc.fits")
    ('synphot', 'tmctab')
    >>> hst_locate.ref_properties_from_cdbs_path("data/2b516556m_tmc.fits")
    ('data', 'hst', 'synphot', 'tmctab', '2b516556m_tmc', '.fits')
    >>> hst_locate.ref_properties_from_header("data/2b516556m_tmc.fits")
    ('data', 'hst', 'synphot', 'tmctab', '2b516556m_tmc', '.fits')
    >>> naming.generate_unique_name("2b516556m_tmc.fits", "hst", NOW)
    '2be00000m_tmc.fits'
    
    TMTTAB

    >>> config.is_crds_name("tae17277m_tmt.fits")
    False
    >>> config.is_cdbs_name("tae17277m_tmt.fits")
    True
    >>> config.is_reference("tae17277m_tmt.fits")
    True
    >>> config.is_mapping("tae17277m_tmt.fits")
    False
    >>> hst_locate.get_file_properties("tae17277m_tmt.fits")
    ('synphot', 'tmttab')
    >>> hst_locate.ref_properties_from_header("data/tae17277m_tmt.fits")
    ('data', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    >>> hst_locate.ref_properties_from_cdbs_path("data/tae17277m_tmt.fits")
    ('data', 'hst', 'synphot', 'tmttab', 'tae17277m_tmt', '.fits')
    >>> naming.generate_unique_name("tae17277m_tmt.fits", "hst", NOW)
    '2be00000m_tmt.fits'

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_certify():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_checksum():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_refactor():
    """
    >>> old_state = test_config.setup()

    TMC   rmap
    TMG   rmap
    TMT   rmap
    COMP  rmap

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_newcontext():
    """
    >>> old_state = test_config.setup()

    TMC   rmap
    TMG   rmap
    TMT   rmap
    COMP  rmap

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_bestrefs():
    """
    >>> old_state = test_config.setup()
    >>> test_config.cleanup(old_state)
    """

def dt_synphot_sync():
    """
    >>> old_state = test_config.setup()
    >>> test_config.cleanup(old_state)
    """

def dt_synphot_diff():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_rowdiff():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_list():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_plugin():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_matches():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_datafile():
    """
    >>> old_state = test_config.setup()

    TMC   reference
    TMG   reference
    TMT   reference
    COMP  reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_uses():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

    >>> test_config.cleanup(old_state)
    """

def dt_synphot_sql():
    """
    >>> old_state = test_config.setup()
    >>> test_config.cleanup(old_state)
    """

# ==============================================================

def main():
    """Run module tests,  for now just doctests only.

    test_config.setup() and cleanup() are done inline above because bracketing
    the tests here does not get picked up by nose test discovery.  Combining
    tests into one giant docstring works but is hard to analyze and debug when
    things go wrong.
    """
    from crds.tests import test_synphot_hst, tstmod
    return tstmod(test_synphot_hst)

# ==============================================================

if __name__ == "__main__":
    print(main())
