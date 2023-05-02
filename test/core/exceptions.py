"""This module defines CRDS specific exceptions."""

class CrdsError(Exception):
    """Baseclass for all client exceptions."""
    def __init__(self, *args, **keys):
        super(CrdsError, self).__init__(" ".join(str(arg) for arg in args), **keys)

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(str(self)) + ")"

# -------------------------------------------------------------------------------------------

class ServiceError(CrdsError):
    """The service call failed for some reason."""

class StatusChannelNotFoundError(ServiceError):
    """Requested status channel does not exist.  Typo or deleted."""

class OwningProcessAbortedError(ServiceError):
    """An abort request was recieved on the specified channel."""

# -------------------------------------------------------------------------------------------

class CrdsConfigError(CrdsError):
    """An inconsistency has been detected between CRDS configuration and operating status or data."""

# -------------------------------------------------------------------------------------------

class CrdsWebError(CrdsError):
    """The id='error_message' <div> of a CRDS_server responsae page was present and not empty.
    Generic 'caught' web error with error message.
    """

class CrdsWebAuthenticationError(CrdsWebError):
    """The id='error_login' <div> of a CRDS server login response was present and not empty.
    Login to the website failed due to username or password.
    """
class CrdsExtraneousFileError(CrdsWebError):
    """Unexpected files are already in the ingest directory during a file submisssion."""

# -------------------------------------------------------------------------------------------

class CrdsBackgroundError(CrdsError):
    """An exception occurred in a background task and was re-raised in the foreground."""

# -------------------------------------------------------------------------------------------

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

class CrdsRemoteContextError(CrdsError):
    """There was a problem pushing or retrieving the value of a pipeline context
    recorded on the CRDS server, i.e. the pipeline's echo of the context
    they're using as reported by the sync tool.   A remote context is CRDS's
    attempt to track the default context actually sync'ed to a pipeline, i.e.
    what that particular cache says.  In contrast the operational context
    is a global maintained on the CRDS server defining what the default *should
    be* as a result of successful and current cache sync'ing by any pipeline
    or CRDS user.
    """

# -------------------------------------------------------------------------------------------

class FilePropertiesError(CrdsError):
    """Failure to determine instrument/or and reftype."""

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

class MappingInsertionError(MappingError):
    """The insertion of a new file into a mapping (rmap) failed for some reason."""

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

class OverlappingMatchError(ModificationError):
    """At least two of the references being added to an rmap had exactly the
    same matching criteria (for at least one of their applicable cases) causing
    one of the two submissions to be omitted from the update.
    """

class MatchingError(CrdsLookupError):
    """Represents a MatchSelector lookup which failed."""

class UseAfterError(CrdsLookupError):
    """None of the dates in the selector precedes the processing date."""

class VersionAfterError(CrdsLookupError):
    """Look up using version failed."""

# -------------------------------------------------------------------------------------------

class InvalidDatetimeError(CrdsError):
    """CRDS was unable to parse the value from date/time related keywords."""

class InvalidUseAfterFormat(InvalidDatetimeError):
    """CRDS was unable to parse the value from a USEAFTER keyword or equivalent."""

class InvalidVersionFormat(CrdsError):
    """CRDS was unable to parse the value from a CAL_VER keyword or equivalent."""

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

class FileFormatError(CrdsError):
    """Something was seriously wrong with a file's format."""

class JsonFormatError(FileFormatError):
    """What should be valid JSON didn't parse / load."""

class YamlFormatError(FileFormatError):
    """What should be valid YAML didn't parse / load."""

class UnsupportedFileOpError(CrdsError, NotImplementedError):
    """In CRDS,  some function is not supported for a particular file format."""

# -------------------------------------------------------------------------------------------

class CertifyError(CrdsError):
    """Certify exception baseclass."""

class MissingKeywordError(CertifyError):
    """A required keyword was not defined."""

class IllegalKeywordError(CertifyError):
    """A keyword which should not be defined was present."""

class InvalidFormatError(CertifyError):
    """The given file was not load-able."""

class TpnDefinitionError(CertifyError):
    """Something was wrong with a .tpn constraint."""

class MissingTpnIncludeError(CertifyError):
    """Any .tpn include files must exist or it's an error.  This is in contrast to other speculative .tpn loads."""

class InconsistentTpnReplaceError(CertifyError):
    """Within the closure of a .tpn text stream,  the same value was mentioned by "replace" twice... with different replacements."""

class TypeSetupError(CertifyError):
    """An error occured while trying to locate file constraints and row mode variables."""

class MissingReferenceError(CertifyError):
    """A reference file mentioned by a mapping isn't in CRDS yet."""

class RequiredConditionError(CertifyError):
    """An ExpressionValidator evaluated to False with respect to a file header."""

class BadKernelCenterPixelTooSmall(CertifyError):
    """A convolution kernel array had a center pixel <= 1.0."""

class BadKernelSumError(CertifyError):
    """A convolution kernel array had a sum too far from 1.0, or similar."""

class MissingArrayError(CrdsError):
    """A specified (named?) array was not found in a reference file."""

class MissingColumnError(CrdsError):
    """A specified (named?) column was not found in a reference file."""

class DuplicateSha1sumError(CrdsError):
    """This file is bit-for-bit identical with a file already in CRDS."""

class CrdsTypeSpecError(CrdsError):
    """Something was wrong with a CRDS type spec registering a type with CRDS."""

# -------------------------------------------------------------------------------------------

class NameComparisonError(CrdsError):
    """Failed to determine the time order of two names."""

class CrdsNamingError(CrdsError):
    """CRDS enountered an error(s) while trying to name a file."""

# -------------------------------------------------------------------------------------------

class CrdsPipelineCfgDeterminationError(CrdsError):
    """Problem determining cal code pipeline .cfg for a dataset."""

class CrdsPipelineTypeDeterminationError(CrdsError):
    """The process of inferring reference types from cal code pipeline .cfg files failed."""

# -------------------------------------------------------------------------------------------

_exception_names = [ name for name in dir() if name.endswith("Error") ]

__all__ = _exception_names
