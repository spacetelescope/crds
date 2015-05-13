
import sys

if sys.version_info >= (3,0,0):
    long = int

    __all__ = [
        "long",
        ]
else:
    __all__ = [
        ]

