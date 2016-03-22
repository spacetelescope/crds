"""This module defines CRDS specific exceptions."""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

class CrdsError(Exception):
    """Baseclass for all client exceptions."""
    def __init__(self, *args, **keys):
        super(CrdsError, self).__init__(" ".join(str(arg) for arg in args), **keys)

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(str(self)) + ")"

# -------------------------------------------------------------------------------------------

class ServiceError(CrdsError):
    """The service call failed for some reason."""
    
class CrdsDownloadError(CrdsError):
    """Error downloading data for a reference or mapping file."""

# -------------------------------------------------------------------------------------------

class CrdsBadRulesError(CrdsError):
    """Attempt to use a bad CRDS rule or context containing a bad rule to determine best references."""

class CrdsBadReferenceError(CrdsError):
    """Attempt to recommend a bad CRDS reference file."""

# -------------------------------------------------------------------------------------------

class CrdsNetworkError(CrdsError):
    """First network service call failed, nominally connection refused."""
    
class CrdsLookupError(CrdsError, LookupError):
    """Filekind NOT FOUND for some reason defined in the exception string."""
    
# -------------------------------------------------------------------------------------------

class CrdsUnknownInstrumentError(CrdsError):
    """Reference to an instrument which does not exist in a context."""

class CrdsUnknownReftypeError(CrdsError):
    """Reference to a filekind which does not exist in a context."""

class MappingError(CrdsError):
    """Exception in load_rmap."""

class MappingFormatError(MappingError):
    "Something wrong with context or rmap file format."

class ChecksumError(MappingError):
    "There's a problem with the mapping's checksum."

class MissingHeaderKeyError(MappingError):
    """A required key was not in the mapping header."""

class InconsistentParkeyError(MappingError):
    """The parkey tuple was inconsistent with the rest of the .rmap in some way."""

# -------------------------------------------------------------------------------------------

class ValidationError(CrdsError):
    """Some Selector key did not match the set of legal values."""

class AmbiguousMatchError(CrdsError):
    """Represents a MatchSelector which matched more than one equivalently 
    weighted choice.   Ambiguous matches represents a problem in the RMAP 
    for projects which don't allow these or Selectors which don't support 
    them.   NOTE: allowing ambiguous matches is important to HST and the 
    canonical HST Match -> UseAfter pattern can support them under many
    circumstances.  The semantics for these are shaky since it's possible
    to have merge collisions which work out badly.
    """

class MissingParameterError(CrdsError):
    """A required parameter for a matching selector did not appear
    in the parameter dictionary.
    """

class BadValueError(CrdsError):
    """A required parameter for a matching selector did not have
    any of the valid values.
    """

class ModificationError(CrdsError):
    """Failed attempt to modify rmap, e.g. replacement vs. addition."""

class MatchingError(CrdsLookupError):
    """Represents a MatchSelector lookup which failed."""

class UseAfterError(CrdsLookupError):
    """None of the dates in the selector precedes the processing date."""

# -------------------------------------------------------------------------------------------

class InvalidUseAfterFormat(CrdsError):
    """CRDS was unable to parse the value from a USEAFTER keyword or equivalent."""

# -------------------------------------------------------------------------------------------

class IrrelevantReferenceTypeError(LookupError):
    """The reference determined by this rmap does not apply to the instrument
    mode specified by the dataset header.
    
    Based on the "rmap_relevance" rmap header expression.
    """

class OmitReferenceTypeError(LookupError):
    """The reference determined by this rmap does not apply to the instrument
    mode specified by the dataset header,  and should be completely omitted from
    the bestrefs results dictionary.
    
    Based on the "rmap_omit" rmap header expression.
    """

# -------------------------------------------------------------------------------------------

class UnsupportedUpdateModeError(CrdsError):
    """Database modes don't support updating best references recommendations on the server."""

# -------------------------------------------------------------------------------------------

class CertifyError(CrdsError):
    """Certify exception baseclass."""
    
class MissingKeywordError(CertifyError):
    """A required keyword was not defined."""

class IllegalKeywordError(CertifyError):
    """A keyword which should not be defined was present."""

class InvalidFormatError(CertifyError):
    """The given file was not loadable."""

class TypeSetupError(CertifyError):
    """An error occured while trying to locate file constraints and row mode variables."""
    
class MissingReferenceError(CertifyError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

# -------------------------------------------------------------------------------------------

class NameComparisonError(CrdsError):
    """Failed to determine the time order of two names."""

# -------------------------------------------------------------------------------------------

_exception_names = [ name for name in dir() if name.endswith("Error") ]

__all__ = _exception_names

