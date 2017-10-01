from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

if sys.version_info >= (3,0,0):
    long = int
    string_types = (str,)

    from urllib.request import urlopen
    from html import unescape
    import configparser
    import pickle
    from io import StringIO

    def unicode_to_str(input):
        """Recursively convert .json inputs with unicode to simple Python strings."""
        return input
    import builtins
else:
    long = long
    string_types = (basestring,)

    import HTMLParser as _parser_mod
    from urllib2 import urlopen
    unescape = _parser_mod.HTMLParser().unescape

    import ConfigParser as configparser
    import cPickle as pickle
    from StringIO import StringIO
    import __builtin__ as builtins

    def unicode_to_str(input):
        """Recursively convert .json inputs with unicode to simple Python strings."""
        if isinstance(input, dict):
            return {unicode_to_str(key): unicode_to_str(value)
                    for key, value in input.iteritems()}
        elif isinstance(input, (list, tuple)):
            return [unicode_to_str(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

__all__ = [
    "long",
    "string_types",

    "urlopen",
    "unescape",
    "configparser",
    "pickle",
    ]

