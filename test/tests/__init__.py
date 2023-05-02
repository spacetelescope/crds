def tstmod(module):
    """Wrap test_config.tstmod to configure standard options throughout CRDS test_config."""
    import doctest
    # doctest.ELLIPSIS_MARKER = '-etc-'
    return doctest.testmod(module, optionflags=doctest.ELLIPSIS)
