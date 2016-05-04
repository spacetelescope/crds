
import sys

if sys.version_info >= (3,0,0):
    long = int
    string_types = (str,)

    import configparser
else:
    long = long
    string_types = (basestring,)

    import ConfigParser as configparser

__all__ = [
    "long",
    "string_types",
    
    "configparser",
    ]

