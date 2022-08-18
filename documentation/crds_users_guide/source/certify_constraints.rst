.. _header-certify-constraints:

Certify Constraints
===================

Certify Overview
----------------

This section documents the design and syntax of CRDS certify .tpn constraint
definition files. The .tpn constraints define many of the checks CRDS applies
to rule or reference files.  CRDS certify performs these forms of checks:

.. tabs::

   .. group-tab:: HST

       1. .tpn defined constraint checks unique to CRDS
       2. CRDS type spec defined unique table row checks, missing mode checks
       3. fitsverify checks, recategorized as needed
       4. FITS format checks
       5. .rmap update checks
       6. sha1sum checks (bit-for-bit identical file rejection)
      
   .. group-tab:: JWST

       1. .tpn defined constraint checks unique to CRDS
       2. CRDS type spec defined unique table row checks, missing mode checks
       3. fitsverify checks, recategorized as needed
       4. FITS, ASDF, JSON, YAML format checks
       5. JWST data models open() checks
       6. JWST data models scraped value checks
       7. .rmap update checks
       8. sha1sum checks (bit-for-bit identical file rejection)

   .. group-tab:: ROMAN

       1. .tpn defined constraint checks unique to CRDS
       2. CRDS type spec defined unique table row checks, missing mode checks
       3. ASDF format checks, recategorized as needed
       4. JSON, YAML format checks
       5. Roman data models open() checks
       6. Roman data models scraped value checks
       7. .rmap update checks
       8. sha1sum checks (bit-for-bit identical file rejection)


This section discusses syntax for (1), file constraints CRDS defines itself internally.

Overview of .tpn Files
----------------------

.. tabs::

   .. group-tab:: HST

       `.tpn` files are used by CRDS certify to define checks on reference files and `.rmaps`. For HST .tpn files define almost all CRDS checks (some table checks also exist) and were incorporated verbatim from CDBS certify. This is the origin of CRDS .tpn syntax.

   .. group-tab:: JWST

       `.tpn` files are used by CRDS certify to define checks on reference files and `.rmaps`. 
       
       Value checks are applied to CRDS `.rmap` files which are not modeled in JWST CAL code. 
       
       For JWST, .tpn checks are used to extend and augment the checks performed by the data models, e.g. adding the notion of "required", checking array dimensions, checking keyword interrelationships, differentiating acceptable values by instrument, etc.  
       
       CRDS .tpn syntax was significantly extended from HST to support additional forms and organizations of checks which have been utilized for JWST.

   .. group-tab:: ROMAN

       `.tpn` files are used by CRDS certify to define checks on reference files and `.rmaps`. 
       
       Value checks are applied to CRDS `.rmap` files which are not modeled in RomanCal code. 
       
       For Roman, .tpn checks are used to extend and augment the checks performed by the data models, e.g. adding the notion of "required", checking array dimensions, checking keyword interrelationships, differentiating acceptable values by instrument, etc.  
       
       CRDS .tpn syntax was significantly extended from HST to support additional forms and organizations of checks which have been utilized for Roman.


.tpn File Organizations
-----------------------

.. tabs::

   .. group-tab:: HST

       For HST, .tpn files were written for every combination of <instrument>_<type>.

   .. group-tab:: JWST

       For JWST, additional broader classes of .tpn are also defined and all applicable forms are loaded for any given reference file::

        all _ all .tpn                 (constraints on all instruments and types)
        <instrument> _ all .tpn        (constraints on all types of one instrument)
        all _ <type> .tpn              (constraints on one type of all instruments)
        <instrument> _ <type> .tpn     (constraint on one instrument and type)

       For JWST, the additional file classes permit generalization of constraints without added redundancy.   
       For example, `PEDIGREE` can be defined once in `all_all`.

   .. group-tab:: ROMAN

       For Roman, additional broader classes of .tpn are also defined and all applicable forms are loaded for any given reference file::

        all _ all .tpn                 (constraints on all instruments and types)
        <instrument> _ all .tpn        (constraints on all types of one instrument)
        all _ <type> .tpn              (constraints on one type of all instruments)
        <instrument> _ <type> .tpn     (constraint on one instrument and type)

       For Roman, the additional file classes permit generalization of constraints without added redundancy.   
       For example, `PEDIGREE` can be defined once in `all_all`.


There are two forms of .tpn, one which constrains reference file properties
(.tpn) and one which constrains rmap properties (_ld.tpn).  The _ld.tpn files
originally constrained CDBS database field values for matching parameters;
because of translations between FITS headers and database values,  reference
file and database values were not necessarily identical.   For JWST and Roman, .tpn
and _ld.tpn files are almost universally identical.

While HST's design of limiting the file structure to <instrument>_<type>
combinations was simple, there was also a significant penalty of redundant
definitions for keyword constraints like &USEAFTER or &PEDIGREE.

.tpn Directives
---------------

Explicit Directives
...................

Typical constraint directives result in a CRDS TpnInfo() object being defined
in CRDS certify, which corresponds 1:1 to a CRDS Validator() object/subclass.
The TpnInfo() is a bundle of constraint information, a Validator() is a class
which checks the constraint defined by a TpnInfo.  Ultimately the outcome of
.tpn files is a list of TpnInfo() constraints to check, which are tuples of
properties, interpreted via appropriate Validator() subclassses.

Synthetic Directives
....................

The CRDS certifier uses the JWST/Roman data models in two ways:

1. CRDS certify calls `datamodels.open()` on each reference to directly apply
data models checks.  This is very simple and fairly robust, but suffers from
the dependency of open() on the DATAMODL keyword which is used to specify the
model class of the reference file.  The model class implies the exact schema to
check.  If DATAMODL is not specified, open() won't validate specialized schema.

2. Second, CRDS loads the data models core schema and converts them into
synthetic TpnInfo() objects which don't appear in a .tpn file.  These synthetic
constraints are interpreted by CRDS normally to make that checking visible and
also to permit automatically promoting the constraints from "optional" (check
if present) to "definintely required" where keywords are needed for CRDS
matching.  The synthetic TpnInfo() objects generally scrape value enumerations
from the core schema for use in CRDS.

Include Directive
.................

The semantics of 'include' are roughly modeled after the C pre-processor's
#include directives.

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

An included file should also be located in the .tpn includes directory and
generally will not follow the JWST classes of include files (all_all, fgs_all,
etc.) or their naming conventions.

Replace Directive
.................

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

An important limitation of 'replace' to note is that it only applies within the
textual extent of on particular file class.   At this time,  it's not possible
to e.g. define a replacement in all_all and have it apply everywhere.


Constraint Directive
....................

By far the most common directive is the constraint directive, which defines one
condition on a reference file and is of the form::

 <name>  <keytype>  <datatype>  <presence>   <value constraint>

or sometimes with the values omitted::

 <name>  <keytype>  <datatype>  <presence>

Before explaining each field in detail, a typical (but abbreviated) example
constraint taken from JWST is::

 META.INSTRUMENT.PUPIL  H   C   O  CLEAR,CLEARP,F090W,F115W,F140M,F150W,F158M,\
                                    F162M,F164N,F200W,F323N,F405N,F466N

The columns of the constraint are interpreted as follows:

1. The first space delimited word defines the keyword / data model path: META.INSTRUMENT.PUPIL

2. The second word defines this as a (H)eader keyword constraint vs. e.g. (C)olumn

3. The third word defines this as a (C)haracter keyword value vs. e.g. (F)loat

4. The fourth word defines this as (O)ptional, it may be omitted.  Another
   common value is (R)equired.  An expression may also be used in this slot to
   define if/if-not the constraint should apply at all; additional semantic
   refinements may also be added by wrapping helper functions.

5. The final "word" is a comma separated list of values.  Multiple lines may be
   used by terminating each line with a backslash except the final line. In
   some cases the value list is replaced by a Python expression which should
   evaluate to True.    Literal numerical ranges may also be specified.

Whitespace in Constraint Fields
+++++++++++++++++++++++++++++++

Since whitespace is used to delimit fields within a constraint, spaces /
whitespace MAY NOT appear within any single field, i.e. the value list,
presence expressions, constraint expressions, etc.  This can be slightly
awkward at times but the addition of extra parentheses to existing punctuation
is generally sufficient to write expressions containing no spaces.

For example, even expressions such as::

  ("IFU" not in EXP_TYPE)

which contain instrinsic whitespace can often be rephrased in a workable way
as::

  (not(("IFU")in(EXP_TYPE)))

A limitation of this approach is that literal strings containing white space
are not permitted/straightforward in expressions.  In that area, writing
additional helper functions or custom validators might provide a way out.

While the idea of modernizing .tpn syntax is pretty obvious, the downsides of
switching to more readable file formats like JSON or YAML are a combination of::

  * Up-front work
  * Additional testing for multiple projects
  * Constraints which become more verbose and less dense.

Since constraints are easier to read and consider en masse when they're
expressed in a dense format, not even readability is a complete slam dunk as a
motivation for modernizing formats.

<Name> Field
++++++++++++

The name field specifies the name of a header keyword, table column, array,
or expression constraint.

Header Keyword Names
!!!!!!!!!!!!!!!!!!!!

Header and table keyword names correspond roughly to FITS keywords or JWST CAL
data models paths flattened into a single string, e.g.::

  READPATT
  META.EXPOSURE.READPATT

Array Names
!!!!!!!!!!!

Array names are specified as the bare HDU name in the <name> field, e.g. SCI.
These are referenced within expressions as <name>_ARRAY.  These are case
insensitive and specified in all capital letters, numbers, or underscores much
like FITS keywords.  They should begin with a letter and be valid program
identifiers.

There are two additional specification cases for array names:

1. FITS extensions can also named by number, e.g.  EXT1 or EXTENSION1 refers to
   the data of HDU #1.  In constraint expressions these are referred to as
   e.g. EXT1_ARRAY.  These can be discriminated from normal header keywords by
   the keytype, which will be array vs. header.

2. FITS extensions can be named by (name, ver), in CRDS this is denoted as
   <name>__<ver>, which corresponds to e.g. ('SCI', 1).  In constraint
   expressions they are referred to as as <name>__<ver>_ARRAY,
   e.g. SCI__1_ARRAY.  These can be differentiated from normal array extension
   names by the double-underscore-digit convention,  an imperfect compromise.

Expression Constraint Names
!!!!!!!!!!!!!!!!!!!!!!!!!!!

Expression constraint names describe the check performed by the value
expression, they do not describe any physical entity within the reference file.
Note that expression here refers to a keytype=X constraint and have no relation
to expressions used in the <presence> field described below.

<Keytype> Field
+++++++++++++++

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
!!!!!!!!!!!!!!!!!!!

Header keyword names correspond to values taken from the union of all HDU
headers.

Almost all of the HST constraints taken from CDBS are enumerations applying to
a single FITS or GEIS keyword, e.g.  READPATT.

Many JWST and Roman constraints are written using the format independent (FITS, ASDF,
JSON...)  data model hiearchical path names munged for CRDS purposes into all
capital letters with periods replaced by underscores so that they can be
evaluated as a single keyword name rather than as nested objects.

Columns (C)
!!!!!!!!!!!

Column names generally apply to the name of a FITS table column and the
corresponding constraint applies only to the values of that single column in
isolation.

Column expressions

Array Format (A)
!!!!!!!!!!!!!!!!

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
!!!!!!!!!!!!!!

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
!!!!!!!!!!!!!!!

Expressions replace the typical value enumeration, range, etc. with a Python
expression written in terms of the reference file header and array properties.
While A and D array constraints are also generally written as as expressions,
in contrast, an X constraint loads no new array properties and includes no
arrays.  The value expression should be written in terms of header keywords
only.   Arrays are pre-loaded and remain available to all expressions for the
duration of a single reference file check.

Group (G)
!!!!!!!!!

Not implemented but parsed for the sake of HST CDBS backward compatibility.

<Datatype> Field
++++++++++++++++

The datatype field conceptually corresponds to the type of a FITS/ASDF keyword
defined in the reference file header or table.  Similar properties are imposed
on data models paths/keywords which may or may not correspond to a FITS/ASDF
keyword.

The datatype is written as a single character with these translations::

 datatypes = {
    "C" : "CHARACTER",      #  ignores case differences
    "S" : "CASE_SENSITIVE_CHARACTER",
    "I" : "INTEGER",
    "L" : "LOGICAL",
    "R" : "REAL",           #  float32 value(s)
    "D" : "DOUBLE",         #  float64 value(s)
    "X" : "EXPRESSION",     #  constraint expression expected
 }

The X datatype indicates that the constraint will be a boolean expression and
hence has no data type.  For 'A' and 'D' keytypes, the expression is abstract,
referring to no particular keyword or array by definition.  In the case of 'C'
keytypes, the expression is only permitted to refer to the current column value.

<Presence> Field
++++++++++++++++

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
!!!!!!!!!!!!!!!!!!!!!!

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

For HST, every instrument and type specified the presence requirement for every
keyword.  This resulted in value enumerations repeated over and over throughout
the .tpn files.

For JWST and Roman, CRDS support specifying keywords as optional...  with one twist: if
an optional keyword is used by an rmap to perform matching (appears in the
'parkey' header field), then every optional constraint on that keyword for that
particular reftype becomes required.

This permits constraints to be specified once as optional at a relatively
global level for easier maintenance, but then become "required" if a particular
reftype uses the keyword directly within CRDS for matching.  (This is a
reflection of the "prime directive" of the CRDS certifier: while general checks
can be implemented, the most crucial aspect of CRDS checking is to ensure that
files work within CRDS.  Although CRDS does strive to implement additional
checks, the only real measure that references will work with the CAL code is
running calibrations.)

For even more control, or for keywords not used by CRDS matching, additional
constraints can be defined in more specialized .tpn's.

Presence Expressions and Helpers
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

A Python expression can be specified to define when a constraint does or
doesn't apply based on keyword values.

The expression should begin with ( and end with ) and should contain no spaces.
(Sometimes extra parens are required to break up the expression into words
using punctuation instead of spaces.)

An example of a presence expression is::

   (EXP_TYPE!='FGS_ID-STACK')

which means that the constraint only applies when EXP_TYPE is not FGS_ID-STACK.

Keyword names used in presence expressions follow the usual rules and must be
valid Python identifiers in all caps.  Periods from data model paths are
replaced by underscores to make the paths into simple identifiers suitable for
Python's eval().

Presence helpers have been defined to convert the boolean result of a presence
expression into a simple presence value.  This enables conditional optional
keywords, conditional warnings, conditional subarray expressions, etc::

   optional(expr)     -->   False or 'O'
   full_frame(expr)   -->   False or 'F'
   subarray(expr)     -->   False or 'S'
   any_subarray(expr) -->   False or 'A'
   required(expr)     -->   False or 'R'
   warning(expr)         -->   False or 'W'

For example, an expression further refined by the full_frame() helper::

   (full_frame(EXP_TYPE!='FGS_ID-STACK'))

means that fundamentally, it only implies when EXP_TYPE is not FGS_ID-STACK,
but in addition,  it only applies when SUBARRAY keywords are defined and the
SUBARRAY is some form of full frame, e.g.FULL or GENERIC.  In effect,  the
helper arranges things so that the presence field is 'F' if the wrapped
expression is satisfied.

Note that an expression return value of False indicates a constraint does not
apply at all.  An expression return value of True indicates the constraint is
REQUIRED.

Helper functions in .tpn files are distinguished by being written in all lower
case; this prevents collisions with keyword, column, or array names which are
always written in upper case.

<Values>
++++++++

The <values> field of each constraint can define a number of things, including
enumerations of literal values::

  GUIDER1,GUIDER2

numerical ranges::

  1:10

constraint expressions:

  (not("IRS2")in(READPATT))

custom validator identifiers::

  &PEDIGREE

or nothing at all.

Enumerations
!!!!!!!!!!!!

Value enumerations list the possible literal values that can be assigned to
a keyword, e.g.::

 FGS,NIRCAM,NIRISS,NIRSPEC,MIRI,SYSTEM

Ranges
!!!!!!

Ranges specify inclusive numerical ranges which keyword values must lie within,
e.g.::

 1.0:10.0

means the value should be within 1 and 10 inclusive.  An equivalent expression
constraint would be::

 (1.0<=KEYWORD<=10.0)

where KEYWORD is the name of the constrained keyword.

Custom Constraint Validators
!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Custom constraint handlers define new classes of validators and are always
specified by a value / validator name beginning with &, e.g.::

  META.USEAFTER   H   C   R               &JWSTDATE

where validator values have meanings like::

 &PEDIGREE  -- implements algorithm to check various PEDIGREE value forms
 &USEAFTER  -- implements HST USEAFTER date/time format checking
 &JWSTDATE  -- implements JWST/Roman datetime format checking,  e.g. JWST USEAFTER


*NOTE:* Roman also uses the `&JWSTDATE` format validator.

Custom constraint validators can perform arbitrary processing to validate a
single keyword value, i.e. specify precise date formats, etc.  Custom
constraint validators are defined in the crds.certify.validators submodules with
classes named like e.g.  PedigreeValidator, UseafterValidator,
JwstdateValidator.

Expressions Constraints
!!!!!!!!!!!!!!!!!!!!!!!

Unlike presence expressions which define when a constraint should or should not
be applied, expressions constraints define the condition which should be
satisfied when the constraint is applicable.

Someone might briefly wonder if both presence and constraint value expressions
are needed.  The answer is "yes" because a negative result of a value
expression is limited to "constraint failed" while a negative result for the
presence expression is limited to "do not evaluate",  so the concerns truly
are separate and two expressions are needed.

Constraint expressions always begin with '(' and end with ')' and should
contain no spaces.

An example expression constraint is::

  (1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048)

which asserts that XSTART + XSIZE - 1 should fall within the boundaries of
the detector's 2048 X-dimension.

When specified within CRDS .tpn files, JWST CAL data models paths (ie. keyword
names) are flattened to simple strings that resemble FITS keywords in all upper
case::

  meta.subarray.xstart -->  META.SUBARRAY.XSTART

Within expressions,  the periods are replaced with underscores:

  META.SUBARRAY.XSTART -->  META_SUBARRAY_XSIZE

so that when the name is eval()'ed it is a simple Python identifier instead of
a e.g. three nested objects.

Array identifiers appear in expression constraints as e.g. SCI_ARRAY to refer
to the SCI HDU properties.  In this case SCI_ARRAY is a true utils.Struct()
object so it refers to Struct() properties within the eval() expression using
normal Python object attribute access, e.g. SCI_ARRAY.SHAPE not
SCI_ARRAY_SHAPE.

In expression constraints over (C)olumn keytypes, the only variable available
is VALUE, which contains the column value currently under consideration.

Expression warn_only() Mutator/Wrapper
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Expression constraints have the unique property that they can be mutated to
generate warnings instead of errors.  In contrast, there is no such mechanism
for value enumerations or ranges.  Custom validators can be written to issue
warnings as needed.

The example constraint expression above can be mutated to a warning like this::

  (warn_only(1<=META_SUBARRAY_XSTART+META_SUBARRAY_XSIZE-1<=2048))

If the constraint fails, a log ERROR which would fail the file submission is
replaced with a WARNING which can be investigated and/or ignored.   Warnings
truly are warnings,  they can flag fatal conditions but may not be applicable
in all cases.

Note that this is distinct from the *Presence* field "W" designator and related
warning() mutator which only alter the "required" status of a
constraint/keyword,  not the result of a constraint failure.

Table Expression Helpers
,,,,,,,,,,,,,,,,,,,,,,,,

Expression helper functions were added to check basic table properties based
on the contents of HDUS.   To some degree these are redundant to the HST "C"
column style constraints...  but have the advantage that they operate directly
on HDU array properties and type information.  In contrast,  the "C" column
constraints followed HST practices relying more on value string formatting,
e.g. "if it looks like a FLOAT,  it is a FLOAT."  In practice,  file developers
actually do make the error of adding FLOAT repr()'s to references instead of
actual FLOAT values so this minor extension was added to enable checking that.

Some of the table helpers::

(is_table(xxx_ARRAY))
(is_image(xxx_ARRAY))
(has_columns(DQ_DEF_ARRAY,['BIT','VALUE','NAME','DESCRIPTION']))
(has_column_type(DQ_DEF_ARRAY,'BIT','INT'))

Empty Value Lists
+++++++++++++++++

The value list can be empty, in which case the constraint is limited to
checking presence and type.

Unique Row Table Checks
-----------------------

CRDS has an HST requirement to attempt to detect missing table modes.  This
is done by specifying table columns which should identify unique rows,  and
then comparing the unique rows of and old and new table to see if any unique
rows are dropped.   The same generic capability can also be used by JWST.

Because the table row checks are crude approximations, the net result is
generally one of two kinds of warnings.  First, a table may define more than
once instance of a row which should be uniquely identified; these are referred
to in a warning as "duplicate" rows.  Second, the new version of a table may
drop unique rows found in the original version; this is reported loosely as one
or more missing "modes".

Unique rows are defined by combinations of column parameters.  The parameter
names used to select unique rows are defined in the "spec" file of each
reference type as needed in a unique_rows header field,  e.g.::

  miri_cubepar.rmap:    'unique_rowkeys' : ('GRATING', 'FILTER'),

The spec files are located in the "specs" directory of each project directory,
e.g. crds/jwst/specs/miri_cubepar.rmap.  Spec files also define other static
reference type properties like short and long form names, etc.  To speed
loading on slow file systems,  specs for all instruments and types are combined
into a single combined_specs.json file for each project.

Because one reference may define more than one table, unique row names are only
used in the row selection combination if they're present in a particular table.
Independent .tpn checks can verfy that all required columns are present.

In the above example, if one table defined unique rows by GRATING, and a second
table defined unique rows by FILTER, CRDS would correctly support both table
checks.  In a different situation, unique table rows might be defined by
combinations of both FILTER and GRATING.   This dicey interpretation of unique
rows turns out to be good enough in practice,  it's relatively uncommon to
check multiple tables in one reference.

Debugging Certify Updates
-------------------------

When run without --verbose, CRDS certify is relatively quiet about what it is
checking unless checks fail.  (A current exception which may change is the
regurgitation of the complete fitsverify output.  But most .tpn checks are
silent unless --verbose is set or they fail.)

Verifying changes to CRDS certify .tpn files can generally done by running
certify over some context, imap, or rmap in *--deep* mode which will attempt to
certify each reference file and/or sub-mapping.  Further, turning on the debug
messages with --verbose or --verbosity=60 or 70 or.. will generate output on
what CRDS is checking, how, and why / why not.

An example of running CRDS this way would be:

.. tabs::

   .. group-tab:: HST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu
           $ export CRDS_PATH=/grp/crds/cache
           $ crds certify hst-acs-biasfile-edit --deep --dump-unique-errors --verbose --dump-provenance

   .. group-tab:: JWST

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu
           $ export CRDS_PATH=/grp/crds/cache
           $ crds certify jwst-nirspec-superbias-edit --deep --dump-unique-errors --verbose --dump-provenance

   .. group-tab:: ROMAN

       .. code-block:: bash

           $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu
           $ export CRDS_PATH=/grp/crds/cache
           $ crds certify roman-wfi-dark-edit --deep --dump-unique-errors --verbose --dump-provenance


The output, which is copious, is relatively self-explanatory.  Typically one
greps through it for output from the constraint being added or modified.

For extensive changes to certify,  it can be useful to run it on all the
active reference files like this:


.. tabs::

   .. group-tab:: HST

       Where the symbolic context name 'hst-edit' is interpreted to something more literal like 'hst_0442.pmap':

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu
            $ export CRDS_PATH=/grp/crds/cache
            $ crds certify hst-edit --deep --dump-unique-errors --verbose --dump-provenance

       Likewise, exhaustive testing may require running certify on 'hst-edit' as well after setting:

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://hst-crds.stsci.edu

   .. group-tab:: JWST

       Where the symbolic context name 'jwst-edit' is interpreted to something more literal like 'jwst_0442.pmap':

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu
            $ export CRDS_PATH=/grp/crds/cache
            $ crds certify  jwst-edit --deep --dump-unique-errors --verbose --dump-provenance

       Likewise, exhaustive testing may require running certify on 'jwst-edit' as well after setting:

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://jwst-crds.stsci.edu

   .. group-tab:: ROMAN

       Where the symbolic context name 'roman-edit' is interpreted to something more literal like 'roman_0442.pmap':

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu
            $ export CRDS_PATH=/grp/crds/cache
            $ crds certify roman-edit --deep --dump-unique-errors --verbose --dump-provenance

       Likewise, exhaustive testing may require running certify on 'roman-edit' as well after setting:

        .. code-block:: bash

            $ export CRDS_SERVER_URL=https://roman-crds.stsci.edu
