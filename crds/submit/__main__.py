"""Module makes submit package run as a program using crds.submit"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys

from . import submit

def main():
    sys.exit(submit.ReferenceSubmissionScript()())

if __name__ == "__main__":
    main()
