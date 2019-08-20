import sys

from .certify import CertifyScript

def main():
    """Construct and run the Certify script,  return 1 if errors occurred, 0 otherwise."""
    errors = CertifyScript()()
    exit_status = int(errors > 0)  # no errors = 0,  errors = 1
    return exit_status

if __name__ == "__main__":
    sys.exit(CertifyScript()())
