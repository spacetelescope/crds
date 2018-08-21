"""Module makes submit package run as a program using crds.submit"""
import sys

from . import submit

def main():
    sys.exit(submit.ReferenceSubmissionScript()())

if __name__ == "__main__":
    main()
