.tpn File Organizations
=======================

For HST, .tpn files were written for every combination of <instrument>_<type>.

There are two forms of .tpn, one which constraints reference file properties
(.tpn) and one which constraints rmap properties (_ld.tpn).  The _ld.tpn files
originally constrained the expanded CDBS database matching parameter values.

For JWST, additional broader classes of .tpn are also defined and all
applicable forms are loaded for any given reference file::

    all _ all .tpn                 (constraints on all instruments and types)
    <instrument> _ all .tpn        (constraints on all types of one instrument)
    all _ <type> .tpn              (constraints on one type of all instruments)
    <instrument> _ <type> .tpn     (constraint on one instrument and type)

File Directives
===============

.tpn files contain several forms of directives:

Include Directive
-----------------

The include directive permits one .tpn file to include the text of another as
if the directive was replaced by the contents of the included file.  This
permits factoring out common constraints into a single file and using them
in multiple locations, e.g.::

 include nir_sci_array.tpn

defines constraints on the SCI array for all NIR instruments except NIRSPEC.

For the sake of simplicity, the line of the directive should begin with
'include' (unquoted), a single space, and the name of the included .tpn file
(also unquoted).  Like many CRDS directives it is space delimited and consists
of exactly two words,  written on a single line.

The included file should also be located in the same .tpn directory as the .tpn
that includes it.

Replace Directive
-----------------

The replace directive causes CRDS to do substitutions on all subsequent lines
in the .tpn file, even lines included from other .tpn files.  The replace
directive consists of 3 words in the general form of::

 replace <original_pattern> <replacement>

where an example directive is::

 replace SCI COEFFS

which means that all subsequent instances of the pattern SCI in a particular
.tpn (or included .tpns) should be replaced by COEFFS.  In this case, it
effectively rewrites constraints on the SCI array as constraints on the COEFFS
array.


Constraint Directive
--------------------

By far the most common directive is the constraint directive, which defines one
condition on a reference file and is of the form::

 <name>  <keytype>  <datatype>  <presence>   <value constraint>

or sometimes with the values omitted::

 <name>  <keytype>  <datatype>  <presence>

<Name> Field
------------

The name field specifies the name of a header keyword, table column, array,
or expression constraint.

Header and table keyword names correspond rougly to FITS keywords or JWST CAL
data models paths flattened into a single string, e.g.::

  READPATT
  META.EXPOSURE.READPATT

Array names are specified as the bare HDU name in the <name> field, e.g. SCI.
These are referenced within expressions as <name>_ARRAY.  These are case
insensitive and specified in all capital letters, numbers, or underscores much
like FITS keywords.  They should begin with a letter and be valid program
identifiers.

Expression constraint names describe the check performed by the value
expression, they does not describe any physical entity within the reference
file.  Note that expression here refers to a keytype=X constraint and have no
relation to expressions used in the <presence> field described below.

<Keytype> Field
---------------

The keytype field consists of one character corresponding to::

 keytypes = {
    "H" : "HEADER",
    "C" : "COLUMN",
    "G" : "GROUP",
    "A" : "ARRAY_FORMAT",
    "D" : "ARRAY_DATA",
    "X" : "EXPRESSION",
 }

Header Keywords (H)
...................

Header keyword names correspond to values taken from the union of all HDU
headers.

Almost all of the HST constraints taken from CDBS are enumerations applying to
a single FITS or GEIS keyword, e.g.  READPATT.

Many JWST constraints are written using the format independent (FITS, ASDF,
JSON...)  data model hiearchical path names munged for CRDS purposes into all
capital letters with periods replaced by underscores so that they can be
evaluated as a single keyword name rather than as nested objects.

Columns (C)
...........

Column names generally apply to the name of a FITS table column and the
corresponding constraint applies only to the values of that single column in
isolation.

Array Format (A)
................

Array format constraints apply to lightweight array properties taken from
FITS HDU data::

 utils.Struct( 
     SHAPE = hdu.data.shape,
     KIND = generic_class,
     DATA_TYPE = typespec,
     COLUMN_NAMES = column_names,
     EXTENSION = i,
     DATA = None,
 )

Most notably, the array data itself is not available for constraint checking
but the lightweight properties are relatively fast and small to load.

Generally, array format and data keytypes have expression constraints rather
than value enumerations, ranges, etc.  Most commonly expressions limit the
array shape and type.

Array expressions can be written in terms of all arrays for which constraints
are defined.  So an ERR array constraint might also refer to SCI if it was
known to be loaded elsewhere.

Array Data (D)
..............

Array data checks are heavy weight and entail loading the actual reference data
so that constraints can be applied to it::

 utils.Struct( 
     SHAPE = hdu.data.shape,
     KIND = generic_class,
     DATA_TYPE = typespec,
     COLUMN_NAMES = column_names,
     EXTENSION = i,
     DATA = hdu.data      #  XXX the difference between 'A' and 'D' constraints!
 )

Generally,  array format and data keytypes have expression constraints rather than
value enumerations, ranges, etc.  Most commonly expressions limit the array shape
and type.

Expressions (X)
...............

Expressions replace the typical value enumeration, range, etc. with a Python
expression written in terms of the reference file header and array properties.
While A and D array constraints are also generally written as as expressions,
an X constraint loads no new array properties and includes no arrays.

Group (G)
.........

Not implemented but parsed for the sake of HST CDBS backward compatibility.



<Datatype> Field
----------------

The datatype field conceptually corresponds to the type of a FITS keyword
defined in the reference file header or table.  Similar properties are imposed
on data models paths/keywords which may or may not correspond to a FITS
keyword.

The datatype is written as a single character with these translations::

 datatypes = {
    "C" : "CHARACTER",
    "I" : "INTEGER",
    "L" : "LOGICAL",
    "R" : "REAL",           #  float32 value(s)
    "D" : "DOUBLE",         #  float64 value(s)
    "X" : "EXPRESSION",     #  constraint expression expected
 }

The X datatype indicates that the constraint will be an boolean expression and
hence has no data type.

<Presence> Field
----------------

The presence field determines the conditions under which a constraint applies
and what should happen when it is omitted::

 presences = {
     "E" : "EXCLUDED",
     "R" : "REQUIRED",
     "P" : "REQUIRED",
     "W" : "WARN",
     "O" : "OPTIONAL",
     "F" : "IF_FULL_FRAME",
     "S" : "IF_SUBARRAY",
     "A" : "ANY_SUBARRAY"
 }

Simple Presence Values
......................

Simple presence values are specified as a single character which correspond to
these classifications:

*REQUIRED* or True results in an error if the keyword is not present in the file
header or tables or is UNDEFINED or the constraint is not satisfied.

*False* means a constraint does not apply.

*WARN* results in a warning if the keyword is not present or is UNDEFINED.

*OPTIONAL* indicates that a constraint should be satisfied if the keyword is
present and not UNDEFINED but is not an error when omitted.

*IF_FULL_FRAME* means that the constraint only applies when SUBARRAY keywords are
defined (SUBARRAY,SUBSTRT1,SUBSTRT2,SUBSIZE1,SUBSIZE2) and SUBARRAY describes a
full frame (FULL,GENERIC,N/A,ANY,*).

*IF_SUBARRAY* means that the constraint only applies when SUBARRAY keywords are
defined and SUBARRAY does not describe a full frame.

*ANY_SUBARRAY* means that the constraint only applies when SUBARRAY keywords are
defined.

*EXCLUDED* means that a keyword should not be specified and was supplied for
backwards compatibility with HST CDBS and is generally unused.

Expression Presence Values
..........................

A Python expression can be specified to define when a constraint does or
doesn't apply based on keyword values.  The expression should begin with ( and
end with ) and should contain no spaces.  (Sometimes extra parens are required
to break up the expression into words using punctuation instead of spaces.)

An example of a presence expression is::

   (full_frame(EXP_TYPE!='FGS_ID-STACK'))

which means that the constraint only applies to full frame reference files when
EXP_TYPE is not FGS_ID-STACK.

Keyword names used in presence expressions follow the usual rules and must be
valid Python identifiers in all caps.  Periods from data model paths are
replaced by underscores to make the paths into simple identifiers suitable for
eval().

Presence helpers have been defined to convert the boolean result of a presence
expression into a simple presence value.  This enables conditional optional keywords,
conditional warnings,  conditional subarray expressions, etc::

   optional(expr)     -->   False or 'O'
   full_frame(expr)   -->   False or 'F'
   subarray(expr)     -->   False or 'S'
   any_subarray(expr) -->   False or 'A'
   required(expr)     -->   False or 'R'
   warn(expr)         -->   False or 'W'

Note that an expression return value of False indicates a constraint does not
apply at all.  An expression return value of True indicates the constraint is
REQUIRED.  The purpose of the helpers is to mutate True to one of the other
single character presence specifiers like e.g. 'W',  which creates a
conditionally applied warning constraint.
   
Helper functions in .tpn files are distinguished by being written in all lower
case; this prevents collisions with keyword, column, or array names which are
always written in upper case.

<Values>
--------

The <values> field of each constraint can define a number of things, including
enumerations of literal values, numerical ranges, constraint expressions,
custom validator identifiers, or nothing at all.

Enumerations
............

Value enumerations list the possible literal values that can be assigned to
a keyword, e.g.::

 FGS,NIRCAM,NIRISS,NIRSPEC,MIRI,SYSTEM
   
Ranges
......

Ranges specify inclusive numerical ranges which keyword values must lie within,
e.g.::

 1.0:10.0

means the value should be within 1 and 10 inclusive.  An equivalent expression
constraint would be::

 (1.0<=KEYWORD<=10.0)

where KEYWORD is the name of the constrained keyword.

Custom Constraints
..................

Custom constraint handlers define new classes of validators and are always
specified by a value and validator name beginning with &, e.g.::

 &PEDIGREE  -- implements algorithm to check simple values and INFLIGHT dates
 &USEAFTER  -- implements USEAFTER date/time format checking
 &JWSTDATE  -- implements JWST date/time format checking

Custom constraint validators can perform arbitrary processing to validate a
single keyword value, i.e. specify precise date formats, etc.  Custom
constraint validators are defined in the crds.certify.validators module with
classes named like e.g.  PedigreeValidator, UseafterValidator,
JwstdateValidator.

Constraint Expressions
......................

Constrating expressions always begin with '(' and end with ')'.  An example
expression value is::

  (1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048)

which asserts that the SUBARRAY X ending pixel location should fit on an array
with an X dimension of 2048.
  
At this time,  expressions are not permitted to contain spaces to make breaking
up the overall constraint definition line a simple split.

When specified within CRDS .tpn files,  JWST CAL data models paths are
flattened to simple strings that resemble FITS keywords in all upper case:

  meta.subarray.xstart -->  META.SUBARRAY.XSTART

This is the form used for constraint 'keyword' names.

Within expressions, dotted JWST CAL data models path names replace the periods
with underscores, forming a simple Python identifier, e.g.::

  META.SUBARRAY.XSTART -->  META_SUBARRAY_XSIZE

This enables use of the dotted keyword names within eval() without being
interpreted as nested objects.

Empty
.....

The value list can be empty, in which case the constraint is limited to
checking presence and type.


Other Notes
===========

#1
--

NIRSpec IRS2 readouts produce 3200 pixels in one image dimension. In the native
detector readout orientation it's nx=3200, ny=2048 (i.e. it's a horizontal
rectangle). But all science data and all reference data in CRDS always need to
be in DMS (science) orientation, which for NIRSpec means the x/y axes get
swapped, so that means IRS2 images have nx=2048, ny=3200 (i.e. a vertical
rectangle). Taking a quick look at one of the NIRSpec MASK ref files in CRDS
for IRS2 mode, it correctly shows that the image has dimensions of
2048x3200. So that's the correct orientation you're looking for. If anyone ever
delivers a NIRSpec ref file to CRDS that has dimensions 3200x2048, it's wrong
(it's still in native detector orientation) and needs to be rejected.

The complicating factor in all of this is that a conscious decision was made to
still have the SUBSTRTn keywords (datamodel meta.subarray.[xy]size) retain
their original values of 2048, rather than 3200, because the extra pixels in
the image do not correspond to real pixels on the detector (they're virtual
values inserted into the image). So the detector was still commanded to readout
2048x2048 pixels, hence the decision to make the size keywords still say
2048x2048. Even though ny=3200 in the actual image. So any comparison of
subarray size keyword values against the actual image size needs to allow for
this (i.e. it's OK to have meta.subarray.ysize=2048 when data.shape[-2] =
3200), as long as READPATT has the string "IRS2" somewhere in it.

#2
--

For the JWST detectors all reference pixels are physical pixels that are
counted as part of the detector dimensions (unlike virtual overscan regions
in CCD's). So the 2048x2048 detector dimensions of the near-IR detectors
already includes the reference pixels and the MIRI detectors are always
referenced in the full 1032x1024 space that includes their reference
pixels. The SUBSTRTn and SUBSIZEn values also always include the reference
pixels (i.e. SUBSTRT1 = 1 means the subarray is starting on the first
reference pixel. The first "live" pixel is at SUBSTRT1 = 5.) So for MIRI
full-frame readouts SUBSIZE1 = 1032, not 1024 (the same as NAXIS1).

The only exception to this is the NIRSpec IRS2 readout mode that includes
many more columns of reference pixels interspersed within the live pixels,
resulting in total image dimensions that are greater than 2048 (at least
along the y image axis). So this is the only case where SUBSIZEn != NAXISn,
because NAXIS2 2048, while a decision was made to still set SUBSIZE2 = 2048.


# 3
---

Comments about array dimensions and array shape equivalence:

DARK: non-MIRI: SCI=ERR=3D, DQ=2D; MIRI: SCI=ERR=DQ=4D

LINEARITY: COEFFS=3D, DQ=2D

