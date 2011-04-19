"""This module defines Selector classes which are used to describe
which of a set of reference files is appropriate to use for a given execution
context.   Every Selector consists of two things:

1) a sequence of context variables which pull out pieces of the full runtime
context to match against selection keys.
2) a sequence "selections" from which a choice is made.

Each selection consists of:

1) a key to match context values against.
2) the value returned when the key matches.

Each Selector subclass implements a choose() method which defines how that
kind of Selector matches a context dictionary to its selections.

Presently the types of keys are unconstrained.   Values are presently either
filenames or nested Selectors.  In all cases,  the choice made at runtime is
essentially done by a tree walk through a set of nested Selectors.

A concrete example should make things clearer.   Here,  we describe which files
to use for a particular wavelength and software version:

>>> r = ClosestGeometricRatioSelector('effective_wavelength',
...        (1.2, SWVersionDepSelector(
...                ('<5','cref_XXX_flatfield_73.fits'),
...                ('default', 'cref_XXX_flatfield_123.fits'),
...        )),
...        (1.5, SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_74.fits'),
...                ('default', 'cref_XXX_flatfield_124.fits'),
...        )),
...        (5.0, SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_87.fits'),
...                ('default', 'cref_XXX_flatfield_137.fits'),
...        )),
... )

ClosestGeometricRatioSelector and SWVersionDepSelector are both Selector
subclasses.  At calibration time,  we choose from among the possible reference
files based on our rules and the known context:

>>> r.choose({"effective_wavelength":1.4, "sw_version":6.0})
'cref_XXX_flatfield_124.fits'

Selectors are designed to be nestable and can describe rules of arbitrary type
and complexity.   Here we add time to the selection criteria:

>>> r = ClosestGeometricRatioSelector('effective_wavelength',
...        (1.2, ClosestTimeSelector("time",
...            ('2017-4-24', SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_73.fits'),
...                ('default', 'cref_XXX_flatfield_123.fits'),
...            )),
...            ('2018-2-1', SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_223.fits'),
...                ('default', 'cref_XXX_flatfield_222.fits'),
...            )),
...            ('2019-4-15', SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_518.fits'),
...                ('default', 'cref_XXX_flatfield_517.fits'),
...            )),
...        )),
...        (1.5, ClosestTimeSelector("time",
...            ('2017-4-24', SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_74.fits'),
...                ('default', 'cref_XXX_flatfield_124.fits'),
...            )),
...            ('2019-1-1', SWVersionDepSelector(
...                ('<5', 'cref_XXX_flatfield_490.fits'),
...                ('default', 'cref_XXX_flatfield_489.fits'),
...            )),
...        )),
...        (5.0, SWVersionDepSelector(
...            ('<5', 'cref_XXX_flatfield_87.fits'),
...            ('default','cref_XXX_flatfield_137.fits'),
...        )),
... )

>>> r.choose({"effective_wavelength":1.6, "time":"2019-1-2", "sw_version":1.4})
'cref_XXX_flatfield_490.fits'

Note that the context variables used by some Selector's are implicit,
with ClosestTime utilizing "time" and SWVersionDep utilizing "sw_version".
"""
import datetime
import timestamp
import re
import pprint as pp

import numpy as np

import log

# ==============================================================================

class LookupError(KeyError):
    """Represents a Selector lookup which failed.
    """

class MatchingError(LookupError):
    """Represents a MatchingSelector lookup which failed.
    """

class AmbiguousMatchError(LookupError):
    """Represents a MatchingSelector which matched more than one equivalent choice.
    """

class MissingParameterError(KeyError):
    """A required parameter for a matching selector did not appear
    in the parameter dictionary.
    """

class BadValueError(KeyError):
    """A required parameter for a matching selector did not have
    any of the valid values.
    """

class UseAfterError(LookupError):
    """None of the dates in the RMAP precedes the processing date.
    """

# ==============================================================================

class Selector(object):
    """Baseclass for CRDS file selectors defining the basic protocol
    of a Selector:

    0. At initialization time, the __init__() method of a selector is called to
    define the variable names which will be used to make a choice at runtime as
    well as the selections of filenames or nested Selectors which will be chosen
    from.

    1. At runtime, the choose() method of a selector is called to implement the
    Selector's picking algorithm over it's selections. Once the algorthim has
    made a choice, it either returns a filename, or it recursively calls the
    choose() method of a nested selector.

    2. The choose() method is called with keyword parameters needed to make the
    complete set of nested choices.   Each nested Selector only uses those portions
    of the overall context that it requires.
    """
    def __init__(self, parameters, *selections):
        self._parameters = list(parameters)
        self._selections = list(selections)

    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self._parameters) + ")"

    def keys(self):
        return [s[0] for s in self._selections]

    def choices(self):
        return [s[1] for s in self._selections]

    def choose(self, header):
        raise NotImplementedError("Selector is an abstract class.   A subclass must re-define choose().")

    def get_choice(self, selection, header):
        choice = selection[1]
        if isinstance(choice, Selector):
            return choice.choose(header)
        else:
            return choice

# ==============================================================================

class MatchingSelector(Selector):
    """Matching selector does a modified dictionary lookup by directly matching the runtime
    (header) parameters specified as choose() header to the .   MatchingSelector
    differs from a simple dictionary in that some of the Selector parameters may begin with
    '*'.   '*' means that the parameter was considered optional by the HTML CDBS tables and
    not all selections supply it.   Explicit values for *-parameters presently
    come from one of two places:  from the CDBS table row,  or from the
    reference file header.   Literal *-values mean the parameter was not
    specified in the table and was not specified in the reference file,  or was
    specified in the reference file as ANY.

    What's hard is that for some selections,  the same parameter will be a "do care".   This
    complexity arises because different usages of the same instrument are parameterized differently,
    whereas there is only a single header keyword for all usages.   In essence,  within a single
    instrument, the same header keyword (file kind) maps onto different tables,  .e.g. for a
    different detector.

    >>> m = MatchingSelector(("*foo","bar"), {
    ...    ('1.0', '*') : "100",
    ...    ('1.0', '2.0') : "200",
    ...    ('*', '*') : "300",
    ... })

    >>> m.choose(dict(foo='1.0',bar='2.0'))
    '200'

    Since foo has a leading *,  it is optional:

    >>> m.choose(dict(bar='2.0'))
    '200'
    
    It matches 200 because bar=2.0 is weighted more than bar=*
    which also matches,  just not as strongly.

    Since bar has no leading *,  it is required:

    >>> m.choose({})
    Traceback (most recent call last):
    ...
    MissingParameterError: "The required parameter 'bar' is missing."

    """
    def __init__(self, parameters, selections, substitutions=None):
        self._parameters = []
        self._required = {}
        self._selections = {}
        self._value_map = {}
        self.setup_parameters(parameters)
        selections = self.fix_simple_keys(selections)
        selections = self.do_substitutions(
            selections, substitutions)
        self._selections = self.get_re_selections(selections)
        self._value_map = self.get_value_map()

    def setup_parameters(self, parameters):
        for par in parameters:
            if par.startswith("*"):
                par = par[1:]
                required = False
            else:
                required = True
            self._required[par] = required
            self._parameters.append(par)
            
    def fix_simple_keys(self, selections):
        """ Enable simple mappings like:  "ACS":"filename" rather than ("ACS",):"filename"
        """
        if len(self._parameters) != 1:
            return selections
        new_selections = {}
        for key, value in selections.items():
            if not isinstance(key, tuple):
                key = (key,)
            new_selections[key] = value
        return new_selections

    def do_substitutions(self, selections, substitutions):
        """Replace parkey values in `selections` which are specified
        in mapping `substitutions` as {parkey : { old_value : new_value }}
        """
        if substitutions is None:
            return selections
        for parkey in substitutions:
            which = self._parameters.index(parkey)
            matches = selections.keys()
            for match in matches:
                which = self._parameters.index(parkey)
                old_parvalue = match[which]
                if old_parvalue in substitutions[parkey]:
                    replacement = substitutions[parkey][old_parvalue]
                    new_match = list(match)
                    new_match[which] = replacement
                    new_match = tuple(new_match)
                    selections[new_match] = selections.pop(match)
        return selections


    def get_re_selections(self, mapping):
        selections = {}
        for keytuple, choice in mapping.items():
            re_keytuple = []
            for key in keytuple:
                if key == "*":
                    key = ".*"
                elif isinstance(key, tuple):
                    key = "|".join(["^" + k + "$" for k in key])
                else:
                    key = "^" + key + "$"
                re_keytuple.append(re.compile(key))
            re_keytuple = tuple(re_keytuple)
            selections[keytuple] = (re_keytuple, choice)
        return selections

    def keys(self):
        return [x[0] for x in sorted(self._selections.items())]

    def choices(self):
        return [x[1][1] for x in sorted(self._selections.items())]

    def get_choice(self, selection, header):
        raise NotImplemented("MatchingSelector isn't a uniform subclass.")

    def choose(self, header):
        """Match the specified `header` to this selector's selections and
        return the best matching choice.
        """
        self.validate_query(header)
        for choice in self._winnowing_match(header):
            if isinstance(choice, Selector):
                try:
                    return choice.choose(header)
                except Exception, e:
                    log.verbose("Nested selector failed", str(e))
                    continue
            else:
                return choice
        log.verbose("Match failed.")
        raise MatchingError("No match found.")

    def _winnowing_match(self, header):
        """Iterate through each of the parameters in `fitskeys`, binding
        them successively to corresponding values from `header`.  For
        each bound fitskey,  iterate through `selections` and winnow out
        keys which cannot match based on the value of the current fitskey.
        Successively yield any survivors,  in the order of most specific
        matching value (fewest *'s) to least specific matching value.
        """
        remaining = dict(self._selections)   # copy
        matches = {}

        for i, var in enumerate(self._parameters):
            value = header.get(var, "NOT PRESENT")
            log.verbose("Binding", repr(var), "=", repr(value))
            items = remaining.items()
            required = self._required[var]
            for key, (re_key, subselectors) in items:
                if key not in matches:
                    matches[key] = 0
                if re_key[i].match(value) and key[i] != "*":  # exact match to non-* is best.
                    matches[key] -= 1  # Lower weights are better matches
                elif not required or key[i] == "*":
                    matches[key] -= 0   # doesn't hurt,  doesn't help
                else:
                    del remaining[key]  # doesn't match and required,  deal breaker.

        candidates = {}
        for key, _junk in remaining.items():
            if matches[key] not in candidates:
                candidates[matches[key]] = []
            candidates[matches[key]].append(key)

        candidates = sorted([(x[0], tuple(x[1])) for x in candidates.items()])
        if log.get_verbose():
            log.verbose("Candidates", pp.pformat(candidates))

        for nmatch, group in candidates:
            selectors = [remaining[x][1] for x in group]
            selector = selectors[0]
            if len(group) > 1:
                if isinstance(selector, Selector):
                    log.verbose("Merging candidates", nmatch, repr(group))
                    selector = selectors[0].merge(selectors[1:])
                else:
                    raise AmbiguousMatchError("choices " + repr(selectors))
            else:
                selector = selectors[0]
            log.verbose("Matched", repr(group),"returning",repr(selector))
            yield selector

    def get_value_map(self, header=None):
        """Return the map { FITSVAR : ( possible_values ) }
        """
        if header is None:
            parameters = self._parameters
        else:
            parameters = self.get_parameters(header)
        map = {}
        for i, fitsvar in enumerate(parameters):
            map[fitsvar] = set()
            for key in self.keys():
                values = key[i]
                if not isinstance(values, tuple):
                    values = [values]
                for value in values:
                    map[fitsvar].add(value)
        for fitsvar in map:
            map[fitsvar] = tuple(sorted(map[fitsvar]))
        return map

    def validate_query(self, header):
        """Raise exceptions if `header` does not contain a required
        key,  or if the value of any key is not one of the possible
        values.
        """
        for fitsvar in self._parameters:
            if fitsvar in header:
                value = header[fitsvar]
                valid_values = self._value_map[fitsvar]
                if self._required[fitsvar] and value not in valid_values and '*' not in valid_values:
                    raise BadValueError("Key " + fitsvar + "=" + value +
                                        " not in valid values " + repr(valid_values))
            else:
                if self._required[fitsvar]:
                    raise MissingParameterError("The required parameter " + repr(fitsvar) + " is missing.")

    def get_binding(self, header):
        # get the parameter names that matter,  based on *dataset*
        binding = {}
        for fitsvar in self._parameters:
            if fitsvar in header:
                binding[fitsvar] = header[fitsvar]
            elif not self._required[fitsvar]:
                binding[fitsvar] = '*'
            else:
                binding[fitsvar] = '**required parameter not defined**'
        return binding

class UseAfterSelector(Selector):
    """A UseAfter selector chooses the greatest time which is less than
    the "date" condition and returns the corresponding item.

    >>> u = UseAfterSelector("DATE", {
    ...        '2003-09-26 01:28:00':'nal1503ij_bia.fits',    # ACS/HRC superbias for Sep 26 - Oct, 11270, Oct 21 2003 09:33PM
    ...        '2004-02-14 00:00:00':'o3913216j_bia.fits',    # ACS/HRC superbias for Feb 14 - Ma, 11368, Mar 18 2004 02:39PM
    ...        '2004-04-25 21:31:00':'o5d10135j_bia.fits',    # ACS/HRC superbias for Apr 25 - May, 11429, May 17 2004 12:34PM
    ...        '2004-06-18 04:36:00':'o9s16388j_bia.fits',    # HRC superbias reference file, 11490, Sep 28 2004 04:55PM
    ...        '2004-07-02 08:09:00':'o9t1525sj_bia.fits',    # ACS/HRC superbias reference file, 11495, Sep 30 2004 12:04PM
    ...        '2004-07-14 16:52:00':'o9f15549j_bia.fits',    # ACS/HRC superbias reference file, 11488, Sep 15 2004 08:49PM
    ...        '2004-07-30 00:18:00':'o9t1553tj_bia.fits',    # HRC reference file, 11497, Sep 30 2004 07:04PM
    ... })

    >>> u.choose({'DATE': '2004-07-02 08:09:00'})   # exact match
    'o9t1525sj_bia.fits'

    >>> u.choose({'DATE': '2004-07-02 08:08:59'})   # just before, in between
    'o9s16388j_bia.fits'

    >>> u.choose({'DATE': '2005-07-02 08:08:59'})   # later than all entries
    'o9t1553tj_bia.fits'

    >>> u.choose({'DATE': '2000-07-02 08:08:59'})   # earlier than all entries
    Traceback (most recent call last):
    ...
    UseAfterError: "No selection with time < '2000-07-02 08:08:00'"
    """
    def __init__(self, datename, datemapping):
        selections = sorted(datemapping.items())
        Selector.__init__(self, [datename], *selections)

    def choose(self, header):
        date = timestamp.reformat_date(header[self._parameters[0]])
        log.verbose("Matching date", date, " ")
        selection = self.bsearch(date, self._selections)
        return self.get_choice(selection, header)

    def bsearch(self, date, selections):
        """Do a binary search over a sorted selections list."""
        if len(selections) == 0:
            raise UseAfterError("No selection with time < " + repr(date))
        elif len(selections) > 1:
            left = selections[:len(selections)/2]
            right = selections[len(selections)/2:]
            compared = right[0][0]
            log.verbose("...against", compared, eol="")
            if date >= compared:
                return self.bsearch(date, right)
            else:
                return self.bsearch(date, left)
        else:
            if date >= selections[0][0]:
                log.verbose("matched", repr(selections[0]))
                return selections[0]
            else:
                raise UseAfterError("No selection with time < " + repr(date))

    def merge(self, others):
        """Merge a list of UseAfterSelectors in to a common UseAfterSelector.
        """
        selections = dict(self._selections)
        for more in others:
            assert isinstance(more, UseAfterSelector)
            for key, value in dict(more._selections).items():
                if (key in selections) and (selections[key] != value):
                    log.warning("Date collision during merge at", repr(key), repr(value), repr(selections[key]))
                selections[key] = value
        return UseAfterSelector(self._parameters[0], selections)

# ==============================================================================

class ClosestGeometricRatioSelector(Selector):
    """ClosestGeometricRatio selects the choice whose key is at the smallest
    distance from the specified condition value.

    >>> r = ClosestGeometricRatioSelector("effective_wavelength",
    ...          (1.2, "cref_XXX_flatfield_120.fits"),
    ...          (1.5, "cref_XXX_flatfield_124.fits"),
    ...          (5.0, "cref_XXX_flatfield_137.fits")
    ... )

    >>> r.choose({"effective_wavelength":1.0})
    'cref_XXX_flatfield_120.fits'

    >>> r.choose({"effective_wavelength":1.2})
    'cref_XXX_flatfield_120.fits'

    >>> r.choose({"effective_wavelength":1.25})
    'cref_XXX_flatfield_120.fits'

    >>> r.choose({"effective_wavelength":1.4})
    'cref_XXX_flatfield_124.fits'

    >>> r.choose({"effective_wavelength":3.25})
    'cref_XXX_flatfield_124.fits'

    >>> r.choose({"effective_wavelength":3.26})
    'cref_XXX_flatfield_137.fits'

    >>> r.choose({"effective_wavelength":5.0})
    'cref_XXX_flatfield_137.fits'

    >>> r.choose({"effective_wavelength":5.1})
    'cref_XXX_flatfield_137.fits'
    """
    def __init__(self, keyname, *selections):
        if not isinstance(keyname, str):
            raise TypeError("First parameter of ClosestGeometricRatio should be the name of a variable to check,  i.e. an str.")
        Selector.__init__(self, [keyname], *selections)

    def choose(self, header):
        keyval = float(header[self._parameters[0]])
        nkeys = np.array(self.keys(), dtype='f')
        diff = np.abs(nkeys - keyval)
        index = np.argmin(diff)
        return self.get_choice(self._selections[index], header)

class LinearInterpolationSelector(Selector):
    """LinearInterpolation selects the the bracketing values of the
    given context variable,  returning a two-tuple.

    >>> r = LinearInterpolationSelector("effective_wavelength",
    ...          (1.2, "cref_XXX_flatfield_120.fits"),
    ...          (1.5, "cref_XXX_flatfield_124.fits"),
    ...          (5.0, "cref_XXX_flatfield_137.fits"),
    ... )

    >>> r.choose({"effective_wavelength":1.25})
    ('cref_XXX_flatfield_120.fits', 'cref_XXX_flatfield_124.fits')

    Note that an exact match still produces a two-tuple.

    >>> r.choose({"effective_wavelength":1.2})
    ('cref_XXX_flatfield_120.fits', 'cref_XXX_flatfield_120.fits')

    >>> r.choose({"effective_wavelength":1.5})
    ('cref_XXX_flatfield_124.fits', 'cref_XXX_flatfield_124.fits')

    >>> r.choose({"effective_wavelength":5.0})
    ('cref_XXX_flatfield_137.fits', 'cref_XXX_flatfield_137.fits')

    Selections off either end choose the boundary value:

    >>> r.choose({"effective_wavelength":1.0})
    ('cref_XXX_flatfield_120.fits', 'cref_XXX_flatfield_120.fits')

    >>> r.choose({"effective_wavelength":6.0})
    ('cref_XXX_flatfield_137.fits', 'cref_XXX_flatfield_137.fits')
    """
    def __init__(self, keyname, *selections):
        if not isinstance(keyname, str):
            raise TypeError("First parameter of ClosestGeometricRatio should be the name of a variable to check,  i.e. an str.")
        Selector.__init__(self, [keyname], *selections)

    def choose(self, header):
        keyval = header[self._parameters[0]]
        index = 0
        while index < len(self._selections) and keyval > self._selections[index][0]:
            index += 1
        if index == len(self._selections):
            choice1 = choice2 = self.get_choice(self._selections[index-1], header)
        elif index == 0 or keyval == self._selections[index][0]:
            choice1 = choice2 = self.get_choice(self._selections[index], header)
        else:
            choice1 = self.get_choice(self._selections[index-1], header)
            choice2 = self.get_choice(self._selections[index], header)
        return choice1, choice2

# ==============================================================================

RELATION_RE = re.compile('^([<=][=]?|default)(.*)$')

class VersionRelation(object):
    """A version relation consists of a relation operator <,=,== and an expression
    representing a version.   VersionRelations can be compared to themselves to support
    generating a sorted list:

    >>> s = VersionRelation('< 5')
    >>> t = VersionRelation('< 6')
    >>> s < t
    True
    >>> s == t
    False
    >>> s > t
    False
    >>> VersionRelation("= 4.5") < VersionRelation("= 5.0")
    True

    VersionRelations can be compared to versions to support choosing from a sorted list:

    >>> 5 < s
    False
    >>> 5 == s
    False
    >>> 5 > s
    True
    >>> 5.0 < t
    True
    >>> 5.0 == t
    False
    >>> 6.1 > t
    True

    The special version 'default' is greater than all versions:

    >>> d = VersionRelation("default")
    >>> 5 < d
    True
    >>> 5 > d
    False
    >>> d > 51
    True
    >>> 5 == d
    False

    Versions don't have to be simple numbers:

    >>> e = VersionRelation("< (5,0,1)")
    >>> (5,0,0) < e
    True

    Non-numerical versions should only be compared to equivalent types:

    >>> (5,0) < VersionRelation('< 5.1')
    Traceback (most recent call last):
    ...
    ValueError: Incompatible version expression types: 5.1 and (5, 0)

    >>> VersionRelation('< 3.1') < 6
    True

    """
    def __init__(self, relation_str):
        m = RELATION_RE.match(relation_str)
        if not m:
            raise ValueError("RelationRelation " + repr(relation_str) + " does not begin with one of >,<,>=,<=,=,==")
        relation = m.group(1)
        if relation == "==":
            relation = "="
        self._relation = relation
        version = m.group(2).strip()
        if self._relation != "default":
            try:
                self._version = eval(version)
            except ValueError, e:
                raise ValueError("Invalid version expression.  Expression must evaluate to a comparable object.")
        else:
            if version:
                raise ValueError("Illegal version expression " + repr(version))
            self._version = "default"
            self._relation = "default"

    def __repr__(self):
        if self._version == "default":
            return "VersionRelation('default')"
        else:
            return 'VersionRelation(%s)' % (repr(self._relation + " " + repr(self._version)))

    def compatible_types(self, other):
        if type(self._version) == type(other):
            return True
        elif isinstance(other, (int,float,long)) and isinstance(self._version, (int,float,long)):
            return True
        else:
            return False

    def __cmp__(self, other):
        if self._version == "default":
            result = 1
        elif isinstance(other, VersionRelation):
            if self._relation != other._relation and self._version == other._version:
                result = cmp(self._relation, other._relation)  # '<' < '=',  '<' < '=='
            else:
                result = cmp(self._version, other._version)
        else:
            if self.compatible_types(other):
                result = cmp(self, VersionRelation("= " + str(other)))
            else:
                raise ValueError("Incompatible version expression types: " + repr(self._version) + " and " + repr(other))
        return result

class VersionDepSelector(Selector):
    """VersionDep chooses from among it's selections based on a number of
    version relations. Each selection of a VersionDep consists of a version
    relation and a filename or nested Selector:

    ('< 5', 'cref_XXX_flatfield_518.fits')

    A special relation,  'default', is selected when none of the other relations
    applies:

    ('default', 'cref_XXX_flatfield_500.fits')

    Version relations are expressed as strings which consist of a relation
    symbol followed by an expression,  as in:

    '< 5.03'
    '= 6.66'
    '== 6.66'

    Version relations consist of two parts,  the relation symbol (=,==,<) and
    the version expression.  The simplest version expression consists of a string which
    represents a number.   However,  the requirement on the version expression (the
    remainder of the string following the relation) is simply that it be eval()'able
    and that the result of the eval() supports comparison operators.  Hence,  a more
    elaborate version selector might look like:

    ('= (5,0,1)', 'cref_XXX_flatfield_501.fits')

    In this case the tuple (5,0,1) directly represents the common representation of
    versions as major, minor, and point releases.   Note that for non-numerical version
    expressions,  the type of the eval'ed expression must exactly match the type of the
    choose()-time parameter,  i.e. in the previous example the choose()-time parameter
    must be a tuple.
    """
    versionvar = "header variable name for this version kind"

    def __init__(self, *selections):
        parsed_selections = self.parse_selections(selections)
        Selector.__init__(self, [], *parsed_selections)

    def parse_selections(self, selections):
        parsed = [(VersionRelation(x[0]), x[1]) for x in selections]
        if parsed != sorted(parsed):
            raise ValueError("VersionDep not specified in sorted order.")
        return parsed

    def choose(self, header):
        version = header[self.versionvar]
        index = 0
        while self._selections[index][0] < version:
            index += 1
        return self.get_choice(self._selections[index], header)

class SWVersionDepSelector(VersionDepSelector):
    """SWVersionDep represents using the client application s/w version as the
    selection criteria.  SWVersionDep implicitly uses the choose() method
    keyword parameter 'sw_version'.

    >>> r = SWVersionDepSelector(
    ...     ('<3.1',    'cref_XXX_flatfield_65.fits'),
    ...     ('<5',      'cref_XXX_flatfield_73.fits'),
    ...     ('default', 'cref_XXX_flatfield_123.fits'),
    ... )

    >>> r.choose({"sw_version":4.5})
    'cref_XXX_flatfield_73.fits'

    >>> r.choose({"sw_version":5})
    'cref_XXX_flatfield_123.fits'

    >>> r.choose({"sw_version":6})
    'cref_XXX_flatfield_123.fits'

    >>> r.choose({"sw_version":2.0})
    'cref_XXX_flatfield_65.fits'
    """
    versionvar = "sw_version"

# ==============================================================================

class ClosestTimeSelector(Selector):
    """ClosestTime chooses the selection whose time most closely matches the choose()
    method "time" keyword parameter

    >>> t = ClosestTimeSelector("time",
    ...    ('2017-4-24', "cref_XXX_flatfield_123.fits"),
    ...    ('2018-2-1',  "cref_XXX_flatfield_222.fits"),
    ...    ('2019-4-15', "cref_XXX_flatfield_123.fits"),
    ... )

    >>> t.choose({"time":"2016-5-5"})
    'cref_XXX_flatfield_123.fits'

    >>> t.choose({"time":"2016-4-24"})
    'cref_XXX_flatfield_123.fits'

    >>> t.choose({"time":"2018-2-2"})
    'cref_XXX_flatfield_222.fits'

    >>> t.choose({"time":"2019-3-1"})
    'cref_XXX_flatfield_123.fits'

    >>> t.choose({"time":"2019-4-15"})
    'cref_XXX_flatfield_123.fits'

    >>> t.choose({"time":"2019-4-16"})
    'cref_XXX_flatfield_123.fits'
    """
    def __init__(self, timevar, *selections):
        Selector.__init__(self, [timevar], *selections)
        self._selections.sort()

    def choose(self, header):
        time = header[self._parameters[0]]
        diff = np.array([abs_time_delta(time, key) for key in self.keys()], 'f')
        index = np.argmin(diff)
        return self.get_choice(self._selections[index], header)

def str_to_datetime(s):
    return datetime.datetime(*[int(x) for x in s.split("-")])

def abs_time_delta(s, t):
    ds = str_to_datetime(s)
    dt = str_to_datetime(t)
    return abs((ds-dt).total_seconds())


# ==============================================================================

class ReferenceSelector(MatchingSelector):
    """ReferenceSelector builds a Selector tree from an rmap header,data tuple.

    A ReferenceSelector lookup is a two stage process:

    1.  First, the rmap fitskeys are bound to a dataset header and used to
    match a UseAfterSelector.

    2.  Next, the UseAfterSelector is called with a parcitular date to choose
    an appropriate reference file.
    
    This is the standard top-level selector for HST.
    """
    def __init__(self, header, data):
        selections = {}
        for mapping in data:
            selections[mapping] = UseAfterSelector("DATE", data[mapping])
        substitutions = header.pop("substitutions", None)
        MatchingSelector.__init__(self, header["parkey"][:-1], selections, substitutions)

# ==============================================================================

def test():
    import doctest, selectors
    return doctest.testmod(selectors)

if __name__ == "__main__":
    print test()
