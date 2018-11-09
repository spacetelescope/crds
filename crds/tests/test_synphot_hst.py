"""This module tests the synphot pseudo-instrument support for HST."""

# ==============================================================

from crds.tests import test_config

# ==============================================================

def dt_synphot_naming():
    """
    >>> old_state = test_config.setup()

    TMC   rmap + reference
    TMG   rmap + reference
    TMT   rmap + reference
    COMP  rmap + reference

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
