
import sys

if sys.version_info >= (3,0,0):
    long = int
    string_types = (str,)

    from urllib.request import urlopen
    from html import unescape
    import configparser

else:
    long = long
    string_types = (basestring,)

    import HTMLParser as _parser_mod
    from urllib2 import urlopen
    unescape = _parser_mod.HTMLParser().unescape

    import ConfigParser as configparser

__all__ = [
    "long",
    "string_types",

    "urlopen",
    "unescape",
    "configparser",

    ]

