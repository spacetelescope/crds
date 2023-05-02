"""
This module supports running crds.bestrefs from the command line using -m syntax:

% crds bestrefs ...

"""
import sys

from crds.bestrefs import bestrefs

def main():
    """Construct and run the bestrefs script,  return 1 if errors occurred, 0 otherwise."""
    errors = bestrefs.BestrefsScript()()
    exit_status = int(errors > 0)  # no errors = 0,  errors = 1
    return exit_status

if __name__ == "__main__":
    sys.exit(main())
