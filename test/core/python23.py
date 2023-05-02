import sys

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

__all__ = [
    "long",
    "string_types",

    "urlopen",
    "unescape",
    "configparser",
    "pickle",
    "StringIO",
    "unicode_to_str",
    "builtins",
]
