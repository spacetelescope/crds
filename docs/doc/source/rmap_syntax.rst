About Mappings
==============

CRDS mappings are organized in a 3 tier hierarchy:  pipeline (.pmap),
instrument (.imap), and reference (.rmap).   Based on dataset parameters,
the pipeline context is used to select an instrument mapping,  the instrument 
mapping is used to select a reference mapping,  and finally the reference 
mapping is used to select a reference file.   

CRDS mappings are written in a subset of Python and given the proper global
definitions can be parsed directly by the Python interpreter.   Nothing 
precludes writing a parser for CRDS mappings in some other language.

.. figure:: file_relationships.png
   :scale: 50 %
   :alt: diagram of file relationships, .pmap -> .imap -> .rmap -> .reference
   

Naming
------

The CRDS HST mapping prototypes which are generated from information scraped from 
the CDBS web site are named with the forms::

  <observatory> .pmap                               .e.g. hst.pmap
  <observatory> _ <instrument> .imap                .e.g. hst_acs.imap 
  <observatory> _ <instrument> _ <filekind> .rmap   .e.g. hst_acs_darkfile.rmap
  
The names of subsequent derived mappings include a version number::

  <observatory> _ <version> .pmap                               .e.g. hst_00001.pmap
  <observatory> _ <instrument> _ <version> .imap                .e.g. hst_acs_00047.imap 
  <observatory> _ <instrument> _ <filekind> _ <version> .rmap  .e.g. hst_acs_darkfile_00012.rmap

Basic Structure
---------------

All mappings have the same basic structure consisting of a "header" section
followed by a "selector" section.   The header provides meta data describing
the mapping,  while the selector provides matching rules used to look up
the results of the mapping.   A critical field in the mapping header is the
"parkey" field which names the dataset header parameters which are used by 
the selector to do its lookup.

Pipeline Mappings (.pmap)
-------------------------

A sample pipeline mapping for HST looks like::

    header = {
        'name' : 'hst.pmap',
        'derived_from' : 'created by hand 12-23-2011',
        'mapping' : 'PIPELINE',
        'observatory' : 'HST',
        'parkey' : ('INSTRUME',),
        'description' : 'Initially generated on 12-23-2011',
        'sha1sum' : 'e2c6392fd2731df1e8d933bd990f3fd313a813db',
    }
    
    selector = {
        'ACS' : 'hst_acs.imap',
        'COS' : 'hst_cos.imap',
        'NICMOS' : 'hst_nicmos.imap',
        'STIS' : 'hst_stis.imap',
        'WFC3' : 'hst_wfc3.imap',
        'WFPC2' : 'hst_wfpc2.imap',
    }

A pipeline mapping matches the dataset "INSTRUME" header keyword against its
selector to look up an instrument mapping file.

Instrument Mappings (.imap)
---------------------------

A sample instrument mapping for HST's COS instrument looks like::

    header = {
        'derived_from' : 'scraped 2011-12-23 11:57:10',
        'description' : 'Initially generated on 2011-12-23 11:57:10',
        'instrument' : 'COS',
        'mapping' : 'INSTRUMENT',
        'name' : 'hst_cos.imap',
        'observatory' : 'HST',
        'parkey' : ('REFTYPE',),
        'sha1sum' : '800fb1567cb5bed4031402c7396aeb86c5e1db61',
        'source_url' : 'http://www.stsci.edu/hst/observatory/cdbs/SIfileInfo/COS/reftablequeryindex',
    }
    
    selector = {
        'badttab' : 'hst_cos_badttab.rmap',
        'bpixtab' : 'hst_cos_bpixtab.rmap',
        'brftab' : 'hst_cos_brftab.rmap',
        'brsttab' : 'hst_cos_brsttab.rmap',
        'deadtab' : 'hst_cos_deadtab.rmap',
        'disptab' : 'hst_cos_disptab.rmap',
        'flatfile' : 'hst_cos_flatfile.rmap',
        'fluxtab' : 'hst_cos_fluxtab.rmap',
        'geofile' : 'hst_cos_geofile.rmap',
        'lamptab' : 'hst_cos_lamptab.rmap',
        'phatab' : 'hst_cos_phatab.rmap',
        'spwcstab' : 'hst_cos_spwcstab.rmap',
        'tdstab' : 'hst_cos_tdstab.rmap',
        'wcptab' : 'hst_cos_wcptab.rmap',
        'xtractab' : 'hst_cos_xtractab.rmap',
    }

Instrument mappings match the desired reference file type against the 
reference mapping which can be used to determine a best reference recommendation 
for a particular dataset.  An instrument mapping lists all possible reference 
types for all modes of the instrument,  some of which may not be appropriate 
for a particular mode.   The selector key of an instrument mapping is the
value of a reference file header keyword "REFTYPE",  and is the name of the
dataset header keyword which will record the best reference selection.

Reference Mappings (.rmap)
--------------------------

A sample reference mapping for HST COS DEADTAB looks like::

    header = {
        'derived_from' : 'scraped 2011-12-23 11:54:56',
        'description' : 'Initially generated on 2011-12-23 11:54:56',
        'filekind' : 'DEADTAB',
        'instrument' : 'COS',
        'mapping' : 'REFERENCE',
        'name' : 'hst_cos_deadtab.rmap',
        'observatory' : 'HST',
        'parkey' : (('DETECTOR',), ('DATE-OBS', 'TIME-OBS')),
        'sha1sum' : 'e27984a6441d8aaa7cd28ead2267a6be4c3a153b',
    }
    
    selector = Match({
        ('FUV',) : UseAfter({
            '1996-10-01 00:00:00' : 's7g1700gl_dead.fits',
        }),
        ('NUV',) : UseAfter({
            '1996-10-01 00:00:00' : 's7g1700ql_dead.fits',
        }),
    })

Reference mapping selectors are constructed as a nested hierarchy of selection
operators which match against various dataset header keywords.

Parkeys
.......

For reference mappings,  the header "parkey" field is a tuple of tuples.  Each 
stage of the nested selector consumes the next tuple of header keys.  For the 
example above,   the Match operator matches against the value of the dataset 
keyword "DETECTOR".   Based on that match, the selected UseAfter operator
matches against the dataset's "DATE-OBS" and "TIME-OBS" keywords to lookup
the name of a reference file.

Selectors
---------

All the CRDS selection operators are written to select either a filename *or*
a nested operator.   In the case of HST,  the Match operator locates a nested
UseAfter operator which in turn locates the reference file.

Match
.....

Based on a dataset`s header values,  Match locates the match tuple which best
matches the dataset.   Conceptually this is a dictionary lookup.   In actuality,
CRDS processes each match parameter in succession,  at each step eliminating
match candidates that cannot possibly match.

Parameter Tuples and Simple Matches
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

The CRDS Match operator typically matches a dataset header against a tuple
which defines multiple parameter values whose names are specified in the rmap 
header `parkey`::

   ("UVIS", "F122LP")   :  'some_file_or_nested_selection'

Alternately,  for simple use cases the Match operator can match against single
strings,  which is a simplified syntax for a 1-tuple::

   'UVIS'  :  'some_file_or_nested_selection'
   ('UVIS',) : 'this_is_the_equivalent_one_tuple'

Single Parameter Values
,,,,,,,,,,,,,,,,,,,,,,,

Each value within the match tuples of a Match operator can be an expression in
its own right.   There are a number of special values associated with each
match expression:  Ors |, Wildcards *,  Regular Expressions (), Literals {},
Relationals, between, N/A, and Substitutions.

Or |
,,,,

Many CRDS match expressions consist of a series of match patterns separated by
vertical bars.   The vertical bar is read as "or" and means that a match occurs
if either pattern matches that dataset header.   For example, the expression::

   ("either_this|that","1|2|3")  : "some_file.fits"
   
will match::

   ("either_this", "2")
   
and also::
   
   ("that", "1")

Wild Cards * 
,,,,,,,,,,,,

By default,  * is interpreted in CRDS as a glob pattern,  much like UNIX shell
file name matching.  * matches any sequence of characters.  The expression::

  ("F*122",) : "some_file.fits"

will match any value starting with "F" and ending with "122".

Regular Expressions
,,,,,,,,,,,,,,,,,,,

CRDS can match on true regular expressions.   A true regular expression match is
triggered by bracketing the match in parentheses ()::

  ("(^F[^13]22$)",)  : "some_file.fits"

The above corresponds to matching the regular expression "^F[^1234]22$" (note
that the bracketing parentheses within the string are removed.)   Regular
expression syntax is explained in the Python documentation for the re module.
The above expression will match values starting with "F", followed by any
character which is not "1" or "3" followed by "22".

Literal Expressions
,,,,,,,,,,,,,,,,,,,

A literal expression is bracketed with curly braces {} and is matched without
any interpretation whatsoever.   Hence,  special characters like * or | are
interpreted literally rather than as ors or wildcards.  The expression::

  ("{F|*G}",) : "some_file.fits"

matches the value "F|*G" as opposed to "F" or anything ending with "G".

Relational Expressions
,,,,,,,,,,,,,,,,,,,,,,

Relational expressions are bracketed by the pound character #.   Relational
expressions do numerical comparisons on the header value to determine a match.
Relational expressions have implicit variables and support the operators::
 
   > >= < <= == and or

The expression::

  ("# >1 and <37 #",)  : "some_file.fits"

will match any number greater than 1 and less than 37.

Between
,,,,,,,

A special relational operator "between" is used to simply express a range
of numbers >= to the lower bound and < the upper bound,  similar to Python 
slicing::

  ("between 1  47",) : "some_file.fits"

will match any number greater than or equal to 1 and less than 47.   This is 
equivalent to::

  ("# >=1 and <47 #",) : "some_file.fits"
  
Note that "between" matches sensibly stack into a complete range.  The expressions::

  ("between 1 47",) : "some_file.fits"
  ("between 47 90", ) : "another_file.fits"

provide complete coverage for the range between 1 and 90.

N/A
,,,

Some rmaps have match tuple values of "N/A",  or Not Applicable.   
A value of N/A is matched as a special version of "*", matching anything,  but
not affecting the "weight" of the match.

   ('HRC', 'N/A') :  "some_file.fits"

There are a couple uses for N/A parameters.    First,  sometimes a parameter is
irrelevant in the context of the other parameters.   So for an rmap which covers
multiple instrument modes,  a parameter may not apply to all modes. Second, 
sometimes a parameter is relevant to custom lookup code,  but is not used by the 
match directly.  In this second case,   the "N/A" parameter may be used by custom
header preconditioning code to assist in mutating the other parameter values
that *are* used in the match.

Substitution Parameters
,,,,,,,,,,,,,,,,,,,,,,,

Substituion parameters are short hand notation which eliminate the need to
duplicate rmap rules.  In order to support WFC3 biasfile conventions,  CRDS
rmaps permit the definition of meta-match-values which correspond to a set of
actual dataset header values. For instance,  when an rmap header contains a
"substitutions" field like this::

    'substitutions' : {
        'CCDAMP' : {
            'G280_AMPS' : ('ABCD', 'A', 'B', 'C', 'D', 'AC', 'AD', 'BC', 'BD'),
        },
    },

then a match tuple line like the following could be written::

    ('UVIS', 'G280_AMPS', '1.5', '1.0', '1.0', 'G280-REF', 'T') : UseAfter({

Here the value of G280_AMPS works like this:  first,   reference files listed
under that match tuple define CCDAMP=G280_AMPS.   Second, datasets which should
use those references define CCDAMP to a particular amplifier configuration,
.e.g.  ABCD.   Hence,  the reference file specifies a set of applicable
amplifier configurations,  while the dataset specifies a particular
configuration.   CRDS automatically expands substitutions into equivalent sets
of match rules.

Match Weighting
,,,,,,,,,,,,,,,

Because of the presence of special values like regular expressions, CRDS uses a
winnowing match algorithm which works on a parameter-by-parameter basis by
discarding match tuples which cannot possibly match. After examining all
parameters,   CRDS is left with a list of candidate matches.

For each literal, *, or regular expression parameter that matched,  CRDS
increases its sense of the goodness of the match by 1.   For each N/A that was
ignored, CRDS doesn't change the weight of the match.   The highest ranked match
is the one CRDS chooses as best.   When more than one match tuple has the same 
highest rank, we call this an "ambiguous" match.   Ambiguous matches will 
either be merged,  or treated as errors/exceptions that cause the match to fail.   
Talk about ambiguity.

For the initial HST rmaps, there are a number of match cases which overlap,
creating the potential for ambiguous matches by actual datasets.   For HST,  all
of the match cases refer to nested UseAfter selectors.  A working approach for
handling ambiguities here is to merge the two or more equal weighted UseAfter
lists into a single combined UseAfter which is then searched.

The ultimate goal of CRDS is to produce clear non-overlapping rules.  However,
since the initial rmaps are generated from historical mission data in CDBS,  
there are eccentricities which need to be accomodated by merging or eventually 
addressed by human beings who will simplify the rules by hand.

UseAfter
........

The UseAfter selector matches an ordered sequence of date time values to
corresponding reference filenames.   UseAfter finds the greatest date-time which
is less than or equal to ( <= ) EXPSTART of a dataset.   Unlike
reference file and dataset timestamp values,  all CRDS rmaps represent times in
the single format shown in the rmap example below::

 selector = Match({
    ('HRC',) : UseAfter({
        '1991-01-01 00:00:00' : 'j4d1435hj_a2d.fits',
        '1992-01-01 00:00:00' : 'kcb1734ij_a2d.fits',
    }),
    ('WFC',) : UseAfter({
        '1991-01-01 00:00:00' : 'kcb1734hj_a2d.fits',
        '2008-01-01 00:00:00' : 't3n1116mj_a2d.fits',
    }),
 })

In the above mapping,  when the detector is HRC,  if the dataset's date/time
is before 1991-01-01,  there is no match.   If the date/time is between
1991-01-01 and 1992-01-01,  the reference file 'j4d1435hj_a2d.fits' is matched.
If the dataset date/time is 1992-01-01 or after,  the recommended reference
file is 'kcb1734ij_a2d.fits'

SelectVersion
.............

The SelectVersion() rmap operator uses a software version and various relations
to make a selection::

   selector = SelectVersion({
      '<3.1':    'cref_flatfield_65.fits',
      '<5':      'cref_flatfield_73.fits',
      'default': 'cref_flatfield_123.fits',
   })
   
While similar to relational expressions in Match(),   SelectVersion() is 
dedicated, simpler,  and more self-documenting.  With the exception of default,
versions are examined in sorted order.

ClosestTime
...........

The ClosestTime() rmap operator does a lookup on a series of times and selects
the closest time which either precedes or follows the given parameter value::

    selector = ClosestTime({
         '2017-04-24 00:00:00':  "cref_flatfield_123.fits",
         '2018-02-01 00:00:00' : "cref_flatfield_222.fits",
         '2019-04-15 00:00:00':  "cref_flatfield_123.fits",
    })

So a parameter of '2017-04-25 00:00:00' would select 'cref_flatfield_123.fits'.

GeometricallyNearest
....................

The GeometricallyNearest() selector applies a distance relation between a
numerical parameter and the match values.   The match value which is closest to
the supplied parameter is chosen::

    selector = GeomtricallyNearest({
        1.2 : "cref_flatfield_120.fits",
        1.5 : "cref_flatfield_124.fits",
        5.0 : "cref_flatfield_137.fits",
    })

In this case,  a value of 1.3 would match 'cref_flatfield_120.fits'.


Bracket
.......

The Bracket() selector is unusual because it returns the pair of selections which
enclose the supplied parameter value::

    selector = Bracket({
        1.2: "cref_flatfield_120.fits",
        1.5: "cref_flatfield_124.fits",
        5.0: "cref_flatfield_137.fits",
    })

Here,  a parameter value of 1.3 returns the value::

    ('cref_flatfield_120.fits', 'cref_flatfield_124.fits')

