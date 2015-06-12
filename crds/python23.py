
import sys

if sys.version_info >= (3,0,0):
    long = int
    string_types = (str,)
else:
    long = long
    string_types = (basestring,)

__all__ = [
    "long",
    "string_types",
    ]

