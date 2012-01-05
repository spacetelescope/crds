Mapping Syntax
==============

CRDS reference mappings are organized in a 3 tier hierarchy:  pipeline (.pmap),
instrument (.imap), and reference type (.rmap).   

Basic Structure
---------------

All mappings have the same basic structure consisting of a "header" section
followed by a "selector" section.   The header provides meta data describing
the mapping,  while the selector provides matching rules used to look up
the results of the mapping.   A critical field in the mapping header is the
"parkey" field which is a tuple naming the dataset header parameters which are 
used by the selector to do its lookup.

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
for a paricular dataset.  An instrument mapping lists all possible reference 
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

For reference mappings,  the header "parkey" field is a tuple of tuples.  Each 
stage of the nested selector consumes the next tuple of header keys.  For the 
example above,   the Match operator matches against the value of the dataset 
keyword "DETECTOR".   Based on that match, the selected UseAfter operator
matches against the data set's "DATE-OBS" and "TIME-OBS" keywords to lookup
the name of a reference file.

HST Selectors
-------------
For HST,  all reference mapping selectors are defined as a two tiered hierarchy 
with one general matching step (Match) and one date-time match step (UseAfter).   

Match
.....

Conceptually,  the Match selector does a dictionary lookup based on the header
keyword values listed in the first tuple of rmap header field "parkey".   In
actuality however,  CRDS does a winnowing search based on each successive 
parkey value,  eliminating impossible matches and returning the best matching
survivor.   There are a number of special values associated with the CRDS Match
operator:  *,  NOT PRESENT, %NO REFERENCE%.

Wild Cards and Optional Match Parameters
,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

Star * is used in two places in CRDS rmaps.   When * precedes a header keyword 
listed in "parkey" it means the header keyword is not *required* to be defined 
by a dataset.   So an rmap header looking like::

  'parkey' : (("*CCDGAIN", ...), ...)
  
indicates that the CCDGAIN parameter is only used for some matches. In this 
instance,  when a dataset does not define CCDGAIN at all,  a match can still 
occur.

When * is used as a value in a Match pattern, it indicates that the pattern will
match any value for that field.

Match Weighting
,,,,,,,,,,,,,,,

A consequence of optional parameters and wild card matches is that CRDS cannot
do a direct lookup based on dataset header values.  Consequently CRDS  does a
winnowing match which iterates over all possible selector matches and each
parkey keyword,  discarding at each step selections which cannot possibly match
a dataset.   Each parameter which does match contributes to the selection's
match weight,  where greater weights correspond to better matches.   A parameter
which matches literally contributes +1 to the weight.  A parameter which matches
via a wild card contributes 0 to the weight.   Thus,  more specific matches are
given greater weights and considered better.

After all of the keywords listed in "parkey" have been examined,  one of the
surviving selections should have a unique greatest weight. It's possible to
define rmaps or datasets which match two selections with identical weights;
this is considered an error and CRDS raises an exception for these ambiguous
matches.

NOT PRESENT
,,,,,,,,,,,

The initial HST rmaps were all scraped from the CDBS web site which lists
reference file selection criteria.  The value NOT PRESENT means that a match
value could not be found in the CDBS HTML table.   In cases where the rmap
generator was instructed to look into reference files for undefined parkey
values,   NOT PRESENT means the associated reference file didn't define it
either.  Since not all parameter values are always required or relevant, a value
of NOT PRESENT is generally not an error.   A value of NOT PRESENT does however
imply that the parameter itself is considered optional and the corresponding
parkeys keyword will be prefixed with *.

%NO REFERENCE%
,,,,,,,,,,,,,,

To first order, CRDS expects the CDBS web site to list required parameter values
for best reference matching. In practice,  the CDBS website doesn't list all
required parameter values so CRDS sometimes finds them by looking inside the
rerefence files themselves.  For match tuples containing %NO REFERENCE%, the
rmap generator was instructed to look inside reference files but could not find
the reference file in order to do so.   This suggests a missing or obsoleted 
reference file.    Note that the rmap generator is not always instructed to 
search inside reference files.

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
under that match tuple define CCDAMP=G280_AMPS.   Second, data sets which should
use those references define CCDAMP to a particular amplifier configuration,
.e.g.  ABCD.   Hence,  the reference file specifies a set of applicable
amplifier configurations,  while the dataset specifies a particular
configuration.   CRDS automatically expands substitutions into equivalent sets
of match rules.

UseAfter
........

The UseAfter selector matches an ordered sequence of date time values to
corresponding reference filenames.   UseAfter finds the greatest date-time which
is less than or equal to ( <= ) DATE-OBS and TIME-OBS of the dataset.   Unlike
reference file and dataset timestamp values,  all CRDS rmaps represent times in
the single format shown in the rmap example above.

