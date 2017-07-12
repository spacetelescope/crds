Reference File Conventions
==========================

Supported CRDS file formats
---------------------------

  - FITS
  - ASDF
  - JSON
  - YAML

Required Keywords and Properties
--------------------------------

Reference files specify metadata as keyword values that CRDS can check and that
CRDS also applies to automatically update CRDS rules files (rmaps) that define
the assignments of best reference files.  In essence, each reference file is
required to specify the instrument configurations for which it is the best
reference file.

Boilerplate Keywords
....................

Both the HST and JWST projects define a small set of required keywords that
define reference file provenance information,  shown here in FITS format for
simplicity:

  TELESCOP
  INSTRUME
  REFTYPE (JWST) or FILETYPE (HST)
  USEAFTER
  AUTHOR (JWST)
  PEDIGREE
  HISTORY
  COMMENT (HST)
  DESCRIP (HST)

Keywords For New File Formats
.............................
 
Newer file formats used for JWST such as ASDF and JSON have equivalent
"keywords" that are generally organized hierarchically in a reference's
metadata tree.

For JWST, the calibration code defines file format schema which show the
correspondence between "data model path" and more primitive representations
like FITS keywords.  The schema also describe related facts such as parameter
type and valid values.  For instance,  the model path::

  META.INSTRUMENT.DETECTOR

is equivalent to the FITS keyword::

  DETECTOR

while:

  META.INSTRUMENT.NAME

corresponds to:

  INSTRUME

To isolate CRDS from physical file formats for JWST, CRDS generally uses data
model paths specified in all upper case for keyword parameters names.

Similar paths are used in the calibration code to define and access model
parameters.  Format-specific facts such as the corresponding FITS keyword are
hidden in the calibration code datamodels schema... if such keywords exist at
all.  In ASDF, the equivalent metadata might be hierarchically encoded as::

  meta:
     instrument:
         detector: NRS1
         name: NIRSPEC

In this case, the keyword DETECTOR does not exist at all in ASDF, but the model
path still does.

Matching Keyword Patterns
.........................

Any keyword used in an rmap to assign best references must be added to the FITS
header or other metadata of that type of reference file.  For example, if a reference
type uses DETECTOR to assign the reference in the rmap, the reference file is
*required* to define DETECTOR or P_DETECT.

Discrete/Real Values
++++++++++++++++++++

Very often the applicability of a reference file can be defined by a single
discrete real world value, or by a simple one word wild card such as ANY or
N/A::

  META.INSTRUMENT.DETECTOR = NRS1

Where applicable, a discrete valued keyword will describe the instrument
configuration used to create the reference file.

Pattern Values
++++++++++++++

Sometimes it is useful to apply one reference file to a number of specific real
world keyword values, i.e. some limited set of filters or detectors or readout
patterns, not merely the discrete instrument configuration used to obtain the
file data.

The legacy approaches used by HST to describe patterns of values are not
detailed here; the key property was that simple values were added to reference
files, but then translated to related values for the CDBS database or CRDS by
hidden conditional substitution rules.

A more explicit approach has been devised for JWST.  In particular, the
value patterns a reference should be applied to can be defined directly in the
reference's metadata when needed...  nominally with no hidden substitutions.

To do this JWST calibration code and CRDS define "pattern keywords" that
correspond to the discrete valued keywords described earlier, but that override
them to define how a reference should be assigned by CRDS and to automatically
insert the file into the CRDS rules (rmap).

If no pattern keyword is defined, CRDS will use the normal discrete valued
keyword specified in the rules.  If the related pattern keyword is defined, it
describes to CRDS a set of values for which the reference file should be
applied.  For instance::

  META.INSTRUMENT.P_DETECTOR = NRCA1 | NRCA4 |

means that the reference file should be used for both NRCA1 and NRCA4.  The
trailing |-bar is a necessary part of the value needed to satisfy the
calibration code data model schema that checks allowed patterns.

In the case of a FITS file, the above value would be specified similarly in a
keyword like this:

  P_DETECT = NRCA1 | NRCA4 |

where typically the keyword name will simply be truncated to the FITS 8
character limit as needed.


Arbitrary Format Properties
...........................

CRDS can also be configured to check more arbitrary file format properties such
as:

  * array types
  * array dimensions
  * covered table modes

Whether or not these are checked depends on the definition of constraints
within the CRDS code base.

