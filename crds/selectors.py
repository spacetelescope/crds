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

>>> r = GeometricallyNearestSelector(('effective_wavelength',), {
...  1.2 : SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_73.fits',
...                'default': 'cref_flatfield_123.fits',
...          }),
...  1.5 : SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_74.fits',
...                'default': 'cref_flatfield_124.fits',
...         }),
...  5.0 : SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_87.fits',
...                'default': 'cref_flatfield_137.fits',
...        }),
... })

GeometricallyNearestSelector and SelectVersionSelector are both Selector
subclasses.  At calibration time,  we choose from among the possible reference
files based on our rules and the known context:

>>> r.choose({"effective_wavelength":'1.4', "sw_version":'6.0'})
'cref_flatfield_124.fits'

Selectors are designed to be nestable and can describe rules of arbitrary type
and complexity.   Here we add time to the selection criteria:

>>> r = GeometricallyNearestSelector(('effective_wavelength',), {
...   1.2: ClosestTimeSelector(("time",), {
...            '2017-04-24 00:00:00': SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_73.fits',
...                'default': 'cref_flatfield_123.fits',
...            }),
...            '2018-02-01 00:00:00': SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_223.fits',
...                'default': 'cref_flatfield_222.fits',
...            }),
...            '2019-04-15 00:00:00': SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_518.fits',
...                'default': 'cref_flatfield_517.fits',
...            }),
...        }),
...  1.5: ClosestTimeSelector(("time",), {
...            '2017-04-24 00:00:00': SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_74.fits',
...                'default': 'cref_flatfield_124.fits',
...            }),
...            '2019-01-01 00:00:00': SelectVersionSelector(('sw_version',), {
...                '<5': 'cref_flatfield_490.fits',
...                'default': 'cref_flatfield_489.fits',
...            }),
...        }),
...  5.0: SelectVersionSelector(('sw_version',), {
...            '<5': 'cref_flatfield_87.fits',
...            'default': 'cref_flatfield_137.fits',
...        }),
... })

>>> r.choose({"effective_wavelength":'1.6', "time":"2019-01-02 00:00:00", "sw_version":'1.4'})
'cref_flatfield_490.fits'

Note that the context variables used by some Selector's are implicit,
with ClosestTime utilizing "time" and SelectVersion utilizing "sw_version".
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from crds import timestamp
import re
import fnmatch
import sys
import numbers
from collections import namedtuple
import ast
import copy
from pprint import pprint as pp

# import numpy as np

import crds
from crds import log, utils

from crds.exceptions import ValidationError, CrdsLookupError, AmbiguousMatchError, MatchingError, UseAfterError
from crds import python23

# ==============================================================================

def dict_wo_dups(items):
    """Convert an item list to a dictionary,  ensuring no duplicate keys exist
    since they'd clobber one another.   Here duplicate keys are expected to correspond
    to cut-and-paste errors in hand edited rmaps which duplicate file cases.
    NOTE:  the Python exec code which nominally loads rmaps also silently removes dups...
    seems un-pythonic to me...  so this code only has a chance of working for specially 
    parsed item lists.
    
    >>> items = [
    ...     ('this', 1),
    ...     ('that', 2),
    ... ]
    >>> pp(dict_wo_dups(items))
    {'that': 2, 'this': 1}

    >>> items2 = [
    ...     ('this', 1),
    ...     ('this', 2),
    ... ]
    >>> pp(dict_wo_dups(items2))
    Traceback (most recent call last):
    ...
    ValueError: Key 'this' appears more than once 

    """
    d = {}
    for key, value in items:
        if key in d:
            raise ValueError("Key " + repr(key) + " appears more than once ")
        d[key] = value
    return d

# Selections are items from a Selector's dictionary.   Portions of the lookup return both.
# A "choice" is a Selector's ultimate choose() return value,  e.g. a filename or other Selector.
# Selection = namedtuple("Selection", ("key", "choice"))

class Selection(tuple):
    def __new__(cls, t):
        return super(Selection, cls).__new__(cls, t)

    def __init__(self, t):
        self.key = t[0]
        self.choice = t[1]
    
    def _cmp_key(self, key):
        return tuple(str(field) for field in key) if isinstance(key, tuple) else str(key)

    def __lt__(self, other):
        return self._cmp_key(self.key) < self._cmp_key(other.key)

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
    complete set of nested choices.   Each nested Selector only uses those 
    portions of the overall context that it requires.
    """
    def __init__(self, parameters, selections=None, rmap_header=None, merge_selections=None):
        assert isinstance(parameters, (list, tuple)), \
            "parameters should be a list or tuple of header keys"
        self._rmap_header = rmap_header or {}
        self._parameters = tuple(parameters)
        if selections is not None:
            assert isinstance(selections, dict),  \
                "selections should be a dictionary { key: choice, ... }."
            self._raw_selections = sorted([Selection(s) for s in selections.items()])
            self._substitutions = dict(self._rmap_header.get("substitutions", {}))
            if self._substitutions:
                selects = self.do_substitutions(parameters, selections, self._substitutions)
            else:
                selects = selections
            self._selections = [Selection(s) for s in self.condition_selections(selects)]
        else:
            # This branch exists to efficiently implement the
            # UseAfter merge operation.   It's not really intended
            # for uses beyond that capacity and the resulting Selector
            # is really only good for a single lookup operation.
            assert isinstance(merge_selections, list),  \
                "merge_selections should be a sorted item list,  not: " + repr(merge_selections)
            self._raw_selections = merge_selections  # XXX not really,  nominally unused XXXX
            self._selections = merge_selections
        self._parkey_map = self.get_parkey_map()
    
    def do_substitutions(self, parameters, selections, substitutions):
        """Replace parkey values in `selections` which are specified
        in mapping `substitutions` as {parkey : { old_value : new_value }}
        
        >>> header = {
        ...    'name' : 'jwst_miri_flat_0015.rmap',
        ...    'parkey' : (('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.FILTER', 'META.INSTRUMENT.BAND', 'META.EXPOSURE.READPATT', 'META.SUBARRAY.NAME'),),
        ...    'substitutions' : {
        ...        'META.SUBARRAY.NAME' : {
        ...            'GENERIC' : 'N/A',
        ...        },
        ...     },
        ... }
        >>> sel = MatchSelector(
        ...    ('META.INSTRUMENT.DETECTOR', 'META.INSTRUMENT.FILTER', 'META.INSTRUMENT.BAND', 'META.EXPOSURE.READPATT', 'META.SUBARRAY.NAME'),
        ...    {
        ...        ('MIRIFULONG', 'N/A', 'LONG', 'ANY', 'GENERIC') : 'jwst_miri_flat_0025.fits',
        ...        ('MIRIFUSHORT', 'N/A', 'LONG', 'ANY', 'FULL') : 'jwst_miri_flat_0034.fits',
        ...        ('MIRIMAGE', 'F1000W', 'N/A', 'FAST', 'MASK1065') : 'jwst_miri_flat_0038.fits',
        ...    },
        ...    header
        ... )

        Since substitutions are defined in the header,  internally GENERIC is translated to N/A:
        
        >>> pp(sel._selections)
        [(('MIRIFULONG', 'N/A', 'LONG', '*', 'N/A'), 'jwst_miri_flat_0025.fits'),
         (('MIRIFUSHORT', 'N/A', 'LONG', '*', 'FULL'), 'jwst_miri_flat_0034.fits'),
         (('MIRIMAGE', 'F1000W', 'N/A', 'FAST', 'MASK1065'),
          'jwst_miri_flat_0038.fits')]

        For external representation and rewriting the rmap,  the original unchanged version of the
        match parameters is retained:

        >>> pp(sel._raw_selections)
        [(('MIRIFULONG', 'N/A', 'LONG', 'ANY', 'GENERIC'), 'jwst_miri_flat_0025.fits'),
         (('MIRIFUSHORT', 'N/A', 'LONG', 'ANY', 'FULL'), 'jwst_miri_flat_0034.fits'),
         (('MIRIMAGE', 'F1000W', 'N/A', 'FAST', 'MASK1065'),
          'jwst_miri_flat_0038.fits')]

        """
        selections = copy.deepcopy(selections)
        for parkey in substitutions:
            try:
                which = parameters.index(parkey)
            except ValueError as exc:
                continue
            for match in selections:
                old_parvalue = match[which]
                if old_parvalue in substitutions[parkey]:
                    replacement = substitutions[parkey][old_parvalue]
                    if isinstance(replacement, list):
                        replacement = tuple(replacement)
                    new_match = list(match)
                    new_match[which] = replacement
                    new_match = tuple(new_match)
                    log.verbose("In", repr(self._rmap_header["name"]), "applying substitution", 
                                (parkey, old_parvalue, replacement), "transforms",
                                repr(match), "-->", repr(new_match), verbosity=70)
                    selections[new_match] = selections.pop(match)
        return selections

    def todict(self):
        """Return a 'pure data' dictionary representation of this selector and it's children
        suitable for conversion to json.
        """
        return {
                "parameters" : self.todict_parameters(),
                "selections" : [ (self.fix_singleton_match_case(key), val.todict()) if isinstance(val, Selector) 
                                 else (self.fix_singleton_match_case(key), val) 
                                 for key,val in self._raw_selections ]
                }

    def todict_flat(self):
        """Return a flat representation of this Selector hierarchy where the path to each terminal node (file)
        is enumerated as one long tuple of key values.   Return a dictionary with one tuple of parameter names
        and a list of tuples of parameter values / files.
        
        To illustrate what "flat" is,  we define nested selectors,  Match --> UseAfter,  as-is typical for HST:
        
        >>> sel = MatchSelector(('DETECTOR',), {
        ...    ('FUV',) : UseAfterSelector(('DATE-OBS', 'TIME-OBS'), {
        ...        '1996-10-01 00:00:00' : 's7g1700gl_dead.fits',
        ...    }),
        ...    ('NUV',) : UseAfterSelector(('DATE-OBS', 'TIME-OBS'), {
        ...        '1996-10-01 00:00:00' : 's7g1700ql_dead.fits',
        ...    }),
        ... }, )
        
        The "flat" result combines the nested keys and values into single tuples suitable for display in tables:
        
        >>> pp(sel.todict_flat())
        {'parameters': ['DETECTOR', 'USEAFTER', 'REFERENCE'],
         'selections': [('FUV', '1996-10-01 00:00:00', 's7g1700gl_dead.fits'),
                        ('NUV', '1996-10-01 00:00:00', 's7g1700ql_dead.fits')]}
                        
        Since the selector is already defined,  also test todict():
        
        >>> pp(sel.todict())
        {'parameters': ('DETECTOR',),
         'selections': [(('FUV',),
                         {'parameters': ('USEAFTER',),
                          'selections': [(('1996-10-01 00:00:00',),
                                          's7g1700gl_dead.fits')]}),
                        (('NUV',),
                         {'parameters': ('USEAFTER',),
                          'selections': [(('1996-10-01 00:00:00',),
                                          's7g1700ql_dead.fits')]})]}

        NOTE on N/A modes:
        
        Some modes can be defined as N/A by replacing sub-selectors and/or filenames
        with N/A as the return value.   Where sub-selectors are omitted,  the length
        of selections and parameters varies.   The implementation below
        """
        flat = []
        subpars = []
        for key, val in self._raw_selections:
            if isinstance(val, Selector):
                nested = val.todict_flat()
                latest_pars = nested["parameters"]
                # XXX hack!  convert or-globs to comma separated strings for web rendering
                key = tuple([", ".join(str(parval).split("|")) for parval in self.fix_singleton_match_case(key)])
                flat.extend([self.fix_singleton_match_case(key) + row for row in nested["selections"]])
            else:
                latest_pars = ["REFERENCE"]
                flat.extend([self.fix_singleton_match_case(key) + (val,)])
            if len(latest_pars) > len(subpars):
                subpars = latest_pars
        pars = list(self.todict_parameters()) + subpars
        return {
            "parameters" : pars,
            "selections" : flat,
            }

    def fix_singleton_match_case(self, case):
        """Change special match cases with singleton parameters which remove the tuple notation
        into standard tuple parameters.
        """
        return (case,) if isinstance(case, (python23.string_types, int, float, bool)) else case

    def delete_match_param(self, parameter):
        """Delete the value of `parameter` name in every match case,  recursively
        if `parameter is not in self._parameters.
        """
        for i, (old_key, choice) in enumerate(self._raw_selections):
            try:
                ix = self._parameters.index(parameter)
                new_key = old_key[:ix] + old_key[ix+1:]
                self._raw_selections[i] = (new_key, choice)
                log.verbose("Replacing match case", repr(old_key), "with", repr(new_key))
            except ValueError:
                choice.delete_match_param(parameter)

    def todict_parameters(self):
        """Overridable,  generally self._parameters."""
        return self._parameters

    def condition_selections(self, selections):
        """Replace the keys of selections with "conditioned" keys,  keys in
        which all the values have passed through self.condition_key().        
        """
        result = [(self.condition_key(key), value) for (key, value) in selections.items()]
        # XXX duplicate checking is most likely dead code here,  now in mapping_parser.py
        if len(result) != len(dict(result).keys()):    # fast check
            dict_wo_dups(result)  # slow generate more informative message
        return sorted(result)
    
    @classmethod
    def condition_key(cls, key):
        """Identity conditioning,  i.e. no change in key."""
        return key
    
    def __repr__(self):
        return self.__class__.__name__ + "(" + repr(self._parameters) \
            + ", nselections=" + str(len(self._selections)) + ")"

    @property
    def short_name(self):
        return self.__class__.__name__[:-len("Selector")]

    def raw_keys(self):
        """Return the list of keys as they appear in the rmap text,  prior to substitutions."""
        return [s.key for s in self._raw_selections]

    def raw_choices(self):
        """Return the list of items which can be selected."""
        return [s.choice for s in self._raw_selections]

    def keys(self):
        """Return the list of keys used to make selections."""
        return [s.key for s in self._selections]

    def choices(self):
        """Return the list of items which can be selected."""
        return [s.choice for s in self._selections]

    def choose(self, header):
        """Given `header`,  operate on self.keys() to choose one of self.choices()."""
        self._check_defined(header)
        lookup_key = self._validate_header(header)  # may return header or a key
        last_exc = None
        for selection in self.get_selection(lookup_key):  # iterate over weighted selections, best match first.
            try:
                log.verbose("Trying", selection, verbosity=60)
                return self.get_choice(selection, header) # recursively,  what's final choice?
            except CrdsLookupError as exc:
                last_exc = exc
                continue
        more_info = " last exception: " + str(last_exc) if last_exc else ""
        raise CrdsLookupError("All lookup attempts failed." + more_info)
                
    def get_selection(self, lookup_key):
        """Most selectors are based on a sorted items list which represents a
        dictionary.  get_selection() typically returns one such item,  both the
        key and the value,  which can be used rapidly to recurse if need be.
        
        yields Selection  to support multiple weighted recursive lookup attempts
        
        NOTE: several Selection's don't meet the same tuple API.   The key
        requirement is that the Selection returned from get_selection() is
        suitable for the corresponding get_choice() method.
        """
        raise NotImplementedError("Selector is an abstract class."
                                  " Subclasses must re-define get_selection().")

    def get_choice(self, selection, header):
        """Provide boiler-plate code to extract a choice or recurse.   Sometimes overridden."""
        assert isinstance(selection, Selection), repr(selection)
        if isinstance(selection.choice, Selector):
            return selection.choice.choose(header)
        else:
            return selection.choice
        
    def get_parkey_map(self):
        """Return a mapping from parkeys to values for them."""
        parmap = {}
        npars = len(self._parameters)
        for i, par in enumerate(self._parameters):
            if par not in parmap:
                parmap[par] = set()
            for key in self.keys():
                if not isinstance(key, tuple):
                    key = (key,)
                if len(key) != npars:
                    raise ValidationError(
                        self.short_name + " key=" + repr(key) + 
                        " is wrong length for parameters " + repr(self._parameters))
                if esoteric_key(key[i]):
                    parmap[par] = []  # == no checking
                    break
                else:
                    parmap[par] |= set(key[i].split("|"))
        for par, val in parmap.items():
            parmap[par] = sorted(val)
        return parmap

    def reference_names(self):
        """Return the list of reference files located by this selector.
        Assume any choice that is a string is a reference file.  Recursively
        search for reference files in nested selectors.
        """ 
        files = []
        for choice in self.choices():
            if isinstance(choice, Selector):
                new_files = choice.reference_names()
            elif isinstance(choice, python23.string_types):
                new_files = [choice]
            elif isinstance(choice, tuple):
                new_files = list(choice)
            elif isinstance(choice, dict):
                new_files = choice.values()
            files.extend(new_files)
        return sorted(set(files))
    
    def format(self, indent=0):
        """Recursively pretty-format the Selector tree rooted in `self` 
        indenting each line with 4*`indent` spaces.   Return the resulting
        string.
        """
        rmap_name = getattr(self, "rmap_name",  self.short_name)
        lines = [rmap_name + "({"]
        for key, sel in self._raw_selections:  
            if isinstance(sel, Selector):
                pf_sel = sel.format(indent+1)
            else:
                pf_sel = repr(sel)
            lines.append((indent+1)*" "*4 + repr(key) + " : " + pf_sel + ",")
        lines.append(indent*4*" " + "})")
        return "\n".join(lines)
    
    def validate_selector(self, valid_values_map):
        """Validate the parameters and keys of `self` against the legal
        values spec'ed in `valid_values_map`.
        """
        with log.error_on_exception(self.short_name + repr(self._parameters)):
            self._validate_selector(valid_values_map)

    def _validate_selector(self, valid_values_map):
        """Iterate over this Selector's keys checking each field
        of each key against `valid_values_map`.
        
        valid_values_map:    { parkey : [ legal values... ], ... }
        
        Raise a ValidationError if there are any problems.
        """
        for selection in self._selections:
            key, choice = selection.key, selection.choice
            with log.augment_exception(repr(key)):
                log.verbose("Validating key", repr(key))
                self._validate_key(key, valid_values_map)
            with log.augment_exception(repr(key)):
                if isinstance(choice, Selector):
                    choice._validate_selector(valid_values_map)
                elif isinstance(choice, python23.string_types):
                    pass
                elif isinstance(choice, tuple):
                    for val in choice:
                        if not isinstance(val, python23.string_types): 
                            raise ValidationError("Non-string tuple value for choice " + repr(choice) + 
                                                  " at " + repr(key))
                elif isinstance(choice, dict):
                    for val in choice:
                        if not isinstance(val, python23.string_types):
                            raise ValidationError("Non-string dictionary key for choice " + repr(choice) +  
                                                  " at " + repr(key))
                    for val in choice.values():
                        if not isinstance(val, python23.string_types):
                            raise ValidationError("Non-string dictionary value for choice " + repr(choice)  + 
                                                  " at " + repr(key))
                else:
                    raise ValidationError("Illegal type for selector primitive value", repr(choice))

    def _validate_header(self, header):
        """Check self._parameters in `header` against the values found in the
        selector's keys.  Ignore nested selectors.
        """
        for name in self._parameters:
            value = header.get(name, "UNDEFINED")
            self._validate_value(name, value, self._parkey_map[name])
        return header
    
    def _check_defined(self, header):
        """Check that this selector's parkeys are all defined in `header`,
        else raise ValidationError.
        """
        for name in self._parameters:
            if name not in header:
                if name in self._parkey_map and "N/A" not in self._parkey_map[name]:
                    raise ValidationError(
                        self.short_name + " required lookup parameter " + 
                        repr(name) + " is undefined.")
            
    def _validate_value(self, name, value, valid_list, runtime=True):
        """Verify that parameter `name` with `value` is in `valid_list` or
        meets some other generic criteria for validity.
        
        This is an overloaded method which is used to validate both runtime header values
        and rmap match tuple values,  so it is run against two different kinds of valid lists,
        valids which come from .rmaps,  and valids which come from .tpn files.   
        
        The .tpn's define what .rmaps and references *can* say,  but the .rmap defines what 
        it *does* say.   The latter is more relevant at diagnosing runtime match failures,  
        basically values like N/A or * are currently loopholes in rmap validation and bestrefs
        checking.
        
        Note that the .tpn assumption applies primarily to HST, the valid value constraints
        for JWST may (eventually) come from the data model schema instead.
        """
        if value in valid_list or utils.condition_value(value) in valid_list:   # typical |-glob valid_list membership
            log.verbose("Value for", repr(name), "of", repr(value), "is in", repr(valid_list), verbosity=60)
            return
        # Wild-cards in the rmap are handled here for the sake of runtime match headers
        if runtime and ("*" in valid_list or "ANY" in valid_list or "N/A" in valid_list):
            log.verbose("Valid list for", repr(name), "includes wild cards. OK, no other check.", verbosity=60)
            return
        # Some TPNs are type-only, empty list
        if not valid_list:
            log.verbose("Valid list for", repr(name), "is empty.  No other check.", verbosity=60)
            return
        if value.startswith("NOT"):
            log.verbose("NOT expression for", repr(name), "of", repr(value), 
                        "validating negated sub-expression value.", verbosity=60)
            self._validate_value(name, value[len("NOT"):].strip(), valid_list, runtime)
            return
        if esoteric_key(value) or value in ["*", "ANY", "N/A"]:   # exempt
            log.verbose("Value of", repr(name), "of", repr(value), 
                        "is unchecked esoteric or wild card.  OK, no other check.", verbosity=60)
            return
        if value.lower().startswith("between"):
            log.verbose("Checking 'between' expression for", repr(name), "of", repr(value), verbosity=60)
            _btw, value1, value2 = value.split()
            self._validate_value(name, value1, valid_list, runtime)
            self._validate_value(name, value2, valid_list, runtime)
            return
        if len(valid_list) == 1 and ":" in valid_list[0]:   # handle ranges in .tpns as n1:n2
            min, max = [float(x) for x in valid_list[0].split(":")]  # normalize everything as float
            if min <= float(value) <= max:
                log.verbose("Numeric value of", repr(name), "of", repr(value), 
                            "is in range", repr(min), "...", repr(max), verbosity=60)
                return
            else:
                raise ValidationError(
                    " parameter=" + repr(name) + " value =" +  repr(value) + " is not in range [" + 
                    str(min) + " .. " + str(max) + "]")
        if name in self._substitutions and value in self._substitutions[name]:
            log.verbose("Value of", repr(name), "of", repr(value), "is substitution from", 
                        repr(value), "to", repr(self._substitutions[name])+". Checking subsititution value.", verbosity=60)
            self._validate_value(name, self._substitutions[name][value], valid_list, runtime)
            return
        raise ValidationError(
            " parameter=" + repr(name) + " value=" + repr(value) + 
            " is not in " + repr(valid_list))
            
    def _validate_key(self, key, valid_values_map):
        """Abstract method used to validate a selector key as part of validating rmaps."""
        raise NotImplementedError(
            self.__class__.__name__ + " hasn't defined _validate_key.")
        
    def _validate_number(self, parname, value):
        """Convert `value` to a float and return it,  else ValidationError.
        Generic methiod for validating header values.
        """
        try:
            return float(value)
        except ValueError:
            raise ValidationError(
                self.short_name + " Invalid number for " + repr(parname) + 
                " value=" + repr(value))

    def _validate_datetime(self, pars, value):
        """Convert `value` to CRDS timestamp and return it,  else ValidationError.
        Generic method for validating and converting header date/times.
        """
        try:
            return timestamp.reformat_date(value)
        except Exception as exc:
            raise ValidationError(
                self.short_name + " Invalid date/time format for " + repr(pars) +
                " value=" + repr(value) + " exception is " + repr(str(exc)))

    def file_matches(self, filename, sofar=()):
        """Return the nested match keys leading to selections of `filename`.
        Assume the deepest value in the Selector tree must be a filename.
        """
        matches = []
        for key, value in self._raw_selections:
            here = tuple(sofar + (self.match_item(key),))
            if isinstance(value, Selector):
                matches += value.file_matches(filename, here)
            else:
                if filename == value:
                    matches.append(here)
        return sorted(matches)
    
    def match_item(self, key):
        """Return ((parkey, key_field), ...) for match key `key`.   Fix string `key`s to unary tuples."""
        if not isinstance(key, tuple):
            key = (key,)
        return tuple(zip(self._parameters, [str(x) for x in key]))
    
    def merge(self, other):
        raise AmbiguousMatchError("More than one match was found at the same weight and " +
            self.short_name + " does not support merging.")
        
    # ------------------------------------------------------------------------
    
    def delete(self, terminal):
        """Remove all instances of `terminal` from `self`."""
        deleted = self._delete(self._selections, terminal)
        deleted += self._delete( self._raw_selections, terminal)
        return deleted
    
    def _delete(self, selections, terminal):
        """Remove all instances of `terminal` from `selections`.   Directly mutates selections."""
        deleted = 0
        for i in range(len(selections)-1,-1,-1):
            selection = selections[i]
            choice = selection[1]
            if choice == terminal:
                log.verbose("Deleting selection[%d] with key='%s' and terminal='%s'" % (i, selection[0], terminal))
                del selections[i]
                deleted += 1
            elif isinstance(choice, Selector):
                deleted += choice.delete(terminal)
                if not len(choice.reference_names()):
                    del selections[i]
        return deleted
    
    def insert(self, header, value, valid_values_map):
        """Based on `header` recursively insert `value` into the Selector hierarchy,
        either adding it as a new choice or replacing the existing choice with 
        the same parameter set.   Add nested Selectors as required.
        
        `value` is a primitive element,  e.g. a filename, not a sub-Selector.
        
        As usual, `header` should be complete, containing definitions for parkeys
        at all levels of the hierarchy.
        
        This call defines the starting point for parkeys and classes,  whereas
        _insert has diminishing lists passed down to nested Selectors.
        """
        self._insert(header, value, self._rmap_header["parkey"], self.class_list, valid_values_map)

    @property
    def class_list(self):
        """Return the pattern of selector nesting for this rmap."""
        if "classes" in self._rmap_header:
            return tuple(self._rmap_header["classes"])
        elif self._rmap_header["observatory"] == "jwst":
            return ("Match",)
        else:  # nominally HST / CDBS
            return ("Match", "UseAfter")
        
    @property
    def parkey(self):
        return self._rmap_header["parkey"]
    
    def _insert(self, header, value, parkey, classes, valid_values_map):
        """Execute the insertion,  popping off parkeys and classes on the way down."""
        key = self._make_key(header, parkey[0])
        log.verbose("Validating key", repr(key))
        self._validate_key(key, valid_values_map)
        i = self._find_key(key)
        if len(classes) > 1:   # add or insert nested selector
            if i is None:
                log.verbose("Modify couldn't find", repr(key), "adding new selector.")
                new_value = self._create_path(header, value, parkey[1:], classes[1:])
                self._add_item(key, new_value)
            else:
                old_key, old_value = self._raw_selections[i]
                if isinstance(old_value, Selector):
                    log.verbose("Modify found", repr(old_key), "augmenting", repr(old_value), "with", repr(value))
                    old_value._insert(header, value, parkey[1:], classes[1:], valid_values_map)
                else:
                    log.verbose("Selector replaces terminal at", repr(key), "adding new selector.")
                    new_value = self._create_path(header, value, parkey[1:], classes[1:])
                    self._add_item(key, new_value)
        else:  # add or replace primitive result
            if i is None:
                log.verbose("Modify couldn't find", repr(key), "adding new value", repr(value))
                self._add_item(key, value)
            else:
                old_key, old_value = self._raw_selections[i]
                log.verbose("Modify found", repr(key), "as primitive", repr(old_value), "replacing with", repr(value))
                self._replace_item(old_key, value)
        
    def _create_path(self, header, value, parkey, classes):
        """Create the Selector tree corresponding to `header` and `value` based on the
        current position in the hierarchy defined by `parkey` and `classes`.
        """
        if classes:   # add new Selectors defined by classes
            selector_class = utils.get_object("crds.selectors." + classes[0] + "Selector")
            key = selector_class._make_key(header, parkey[0])
            nested = self._create_path(header, value, parkey[1:], classes[1:])
            selections = { key : nested }
            log.verbose("creating nested", repr(classes[0]), "with", repr(key), "=", repr(nested))
            return selector_class(parkey[0], selections, rmap_header=self._rmap_header)
        else:   # end of the line,  just return the primitive value.
            return value
    
    def _add_item(self, key, value):
        """Add a new `value` to selections at `key`.  Flat:  this selector only."""
        i = self._find_key(key)
        assert i is None, self.__class__.__name__ + " already contains " + repr(key)
        self._raw_selections.append((key, value))
        self.__init__(self._parameters, dict_wo_dups(self._raw_selections), rmap_header=self._rmap_header)

    def _remove_item(self, key):
        """Remove the selection at `key`.   Flat:  this selector only."""
        i = self._find_key(key)
        assert i is not None, self.__class__.__name__ + " doesn't contain " + repr(key)
        del self._raw_selections[i]
        self.__init__(self._parameters, dict_wo_dups(self._raw_selections), rmap_header=self._rmap_header)

    def _replace_item(self, key, value):
        """Replace the selection at `key` with `value`.   Flat:  this selector only."""
        self._remove_item(key)
        self._add_item(key, value)
        
    def _find_key(self, key):
        """Return the index of `key` in selections."""
        for i, (old_key, _old_value) in enumerate(self._raw_selections):
            if self._equal_keys(key, old_key):
                return i
        else:
            return None

    def _equal_keys(self, key1, key2):
        """Return True IFF `key1` is equivalent to `key2` for rmap modification."""
        return self._normalize_key(key1) == self._normalize_key(key2)
    
    def _normalize_key(self, key):
        """Return the simple version of single element keys.   Include key
        conditioning so that numbers are matched as float strings, times are
        uniform, etc.
        
        e.g.   ('something',) -->   'something'
        e.g.   ('something','else') --> ('something','else')
        """
        if isinstance(key, tuple) and len(key) == 1:
            key = key[0]
        return self.condition_key(key)
    
    @classmethod    
    def _make_key(self, header, parameters):
        """For rmap modification,  make a key for this Selector based on reference
        file `header` and self's lookup `parameters`.
        """
        key = tuple([header[par] for par in parameters])
        if len(key) == 1:
            key = key[0]
        return key
    
    # ------------------------------------------------------------------------

    def get_value_map(self):
        """Returns { parameter : sorted(parameter values in use) }"""
        vmap = self._get_value_map()  # mapping of sets
        for fitsvar in vmap:
            vmap[fitsvar] = tuple(sorted(vmap[fitsvar]))
        return vmap
            
    def _get_value_map(self):
        """Recursively combine get_selector_value_map()."""
        vmap = self.get_selector_value_map()
        for choice in self.choices():
            if isinstance(choice, Selector):
                nested = choice._get_value_map()
                for parkey in nested:
                    if parkey not in vmap:
                        vmap[parkey] = set()
                    vmap[parkey] |= set(nested[parkey])
        return vmap

    def get_selector_value_map(self):
        """Return { parameter : set( values in use ) } for this Selector only.
        Many Selectors do not have meaningful discrete sets of values for their
        parameters for the purpose of populating get_best_refs menus.
        """
        return {} # Not really relevant for UseAfter
    

    # XXXX changes to the format of difference messages need to be coordinated with
    # crds.diff,  crds.rmap and the website interative application (crds.server.interactive.web_certify).
    # IOW,  the messages are part of the software API,  don't change without review.
    def difference(self, new_selector, path=(), pars=(), top_selector=True):
        """Return the list of differences between `self` and `new_selector` where 
        `path` names the
        """
        msg = self._get_msg(path, pars)
        
        def short_name(obj):
            return obj.short_name if isinstance(obj, Selector) else obj.__class__.__name__
        
        if self.__class__ != new_selector.__class__:
            return [msg(None, "different classes", short_name(self), ":", short_name(new_selector))]
        if self._parameters != new_selector._parameters:
            return [msg(None, "different parameter lists ", 
                    repr(self._parameters), ":", repr(new_selector._parameters))]

        differences = []
        new_selector_keys = new_selector.raw_keys()
        self_keys = self.raw_keys()
        new_selector_map = dict_wo_dups(new_selector._raw_selections)
        # Warning:  the message formats here are important to client code.
        # don't change without doing a survey. e.g. replaced blank1 with blank2.
        for key, choice in self._raw_selections:
            pkey = self._diff_key(key)
            if key not in new_selector_keys:
                if isinstance(choice, Selector):
                    differences.extend(choice.flat_diff("deleted {} rule for".format(self.short_name), 
                                                         path + (pkey,), pars + (self._parameters,)))
                elif top_selector:
                    differences.append(msg(key, "deleted {} rule for".format(self.short_name), repr(choice)))
                else:
                    differences.append(msg(key, "deleted terminal", repr(choice)))
            else:
                new_selector_choice = new_selector_map[key]
                if isinstance(choice, Selector):
                    differences.extend(
                        choice.difference(new_selector_choice, path + (pkey,), pars + (self._parameters,), 
                                          top_selector=False))
                elif choice != new_selector_choice:
                    differences.append(msg(key, "replaced", repr(choice), "with", repr(new_selector_choice)))
        for key in new_selector_keys:
            pkey = self._diff_key(key)
            if key not in self_keys:
                new_selector_choice = new_selector_map[key]
                if isinstance(new_selector_choice, Selector):
                    differences.extend(
                        new_selector_choice.flat_diff("added {} rule for".format(self.short_name), 
                                                       path + (pkey,), pars + (self._parameters,)))
                elif top_selector:
                    differences.append(msg(key, "added {} rule for".format(self.short_name), repr(new_selector_choice)))
                else:
                    differences.append(msg(key, "added terminal", repr(new_selector_choice)))
        return differences
    
    def flat_diff(self, change, path, pars):
        """Return `change` messages relative to `path` for all of `self`s selections
        as a simple flat list of one change tuple per nested choice.
        """
        diffs = []        
        for key, choice in self._raw_selections:
            pkey = self._diff_key(key)
            if isinstance(choice, Selector):
                diffs.extend(choice.flat_diff(change, path + (pkey,), pars + (self._parameters,)))
            else:
                msg = self._get_msg(path, pars)
                diffs.append(msg(key, change, repr(choice)))
        return diffs
    
    def _get_msg(self, path, pars):
        """Return a message tuple generation function bound to `path` and `pars`."""
        def msg(key, *args):
            path2 = path
            pars2 = pars
            if key:
                path2 = path2 + (self._diff_key(key),)
                pars2 = pars2 + (self._parameters,)
            pars2 = pars2 + ("DIFFERENCE",)
            path2 = path2 + (" ".join(args),)
            return DiffTuple(*path2, parameter_names=pars2)
        return msg
 
    def _diff_key(self, key):
        """Use the ((parname, parvalue), ...) format of match_item to produce (parvalues, ...) for diff.
        Handles UseAfter / odd cases where `key` and match_item values aren't quite the same.
        """
        item = self.match_item(key)
        if item:
            pars, vals = list(zip(*item))
            return tuple([str(x) for x in vals])
        else:
            return ()

class DiffTuple(tuple):
    """Class similar to named tuple for reporting mapping differences and the affected parkeys."""
    def __new__(cls, *args, **keys):
        return super(DiffTuple, cls).__new__(cls, tuple(args))
        
    def __init__(self, *args, **keys):
        pars = keys.pop("parameter_names", None)
        super(DiffTuple, self).__init__()
        self.parameter_names = pars
        self.instrument = keys.pop("instrument", None)
        self.filekind = keys.pop("filekind", None)
        
    @property
    def flat(self):
        """Removes the Selector nesting structure and return an equivalent tuple."""
        pars2 = []
        vals2 = []
        for i, par in enumerate(self.parameter_names):
            if isinstance(par, python23.string_types):
                pars2.append(par)
                vals2.append(self[i])
            else:
                pars2.extend(list(par))
                vals2.extend(list(self[i]))
        return DiffTuple(*vals2, parameter_names=pars2, instrument=self.instrument, filekind=self.filekind)

    def __lt__(self, other):
        if len(self) > len(other):
            return True
        elif len(self) < len(other):
            return False
        else:
            return super(DiffTuple, self).__lt__(other)

    def __eq__(self, other):
        if len(self) == len(other):
            return super(DiffTuple, self).__eq__(other)
        else:
            return False

    def items(self):
        """Return [ (param_name, val), ... ]"""
        return [ (str(x), str(y)) for (x, y) in zip(self.parameter_names, self) ]
 

# ==============================================================================

def match_superset(reference_tuple, rmap_tuple, match_na=False):
    """Return True IFF match reference_tuple is equal to or more general than
    rmap_tuple.
    
     A specific reference_tuple should match an rmap_tuple N/A.   
     
    A specific rmap_tuple should not match
    a reference_tuple N/A since it means the reference file isn't guaranteeing
    the condition of the rmap.
    
    >>> match_superset(('1','2'),  ('1','2'))
    True
    >>> match_superset(('1','*'),  ('1','2'))
    True
    >>> match_superset(('1','2'),  ('1','*'))
    False
    >>> match_superset(('1|a','2'),  ('1','2'))
    True
    >>> match_superset(('1','2'),  ('1','2|b'))
    False
    >>> match_superset(('1|a','2'),  ('1','2|b'))
    False
    >>> match_superset(('1','2'),  ('1','3'))
    False
    >>> match_superset(('1','N/A'), ('1','3'))
    False
    >>> match_superset(('1','3'), ('1','N/A'))  # controversial
    True
    >>> match_superset(('1','*'), ('1','N/A'))
    True
    >>> match_superset(('1','N/A'), ('1','*'))
    True
    >>> match_superset(('A|B|C|D','1'), ('A|B|C', '1'))
    True
    >>> match_superset(('A|B|C','1'), ('A|B|C|D', '1'))
    False
    """
    for i in range(len(reference_tuple)):
        v1 = reference_tuple[i]
        v2 = rmap_tuple[i]
        if v1 == v2:
            continue
        if v1 == "*":
            continue
        if v2 == "N/A":
            continue
        if v1 == "N/A" and v2 == "*":
            continue
        if match_na and v1 == "N/A":
            continue
        if v2 == "*":
            return False
        if set(v1.split("|")) > set(v2.split("|")):
            continue
        if set(v1.split("|")) < set(v2.split("|")):
            return False
        if v1 != v2:
            return False
    return True

def match_equivalent(tuple1, tuple2):
    """Returns True IFF tuple1 ~ tuple2 accounting for N/A and *.
    Returns False if tuple1 < tuple2 or tuple2 < tuple1.
    """
    return match_superset(tuple1, tuple2) and match_superset(tuple2, tuple1)

def different_match_weight(subkey, superkey):
    """The criteria for "ambiguous matches" are:
    
    1. Superkey must be a match superset of subkey,  i.e. it matches any
    time subkey does.
    2. The match weights of superkey and subkey must be the same for an
    ambiguity to exist. Where one key has the value N/A and the other 
    does not, the weights of their matches diverge.   Unequally weighted
    matches aren't merged and hence aren't considered an ambiguity.
    """
    super_count = sub_count = len(subkey)
    for i in range(sub_count):
        if subkey[i] == "N/A" and superkey[i] != "N/A":
            sub_count -= 1
        elif superkey[i] == "N/A" and subkey[i] != "N/A":
            super_count -= 1
    return sub_count != super_count

class Matcher(object):
    """Matches a single key of a matching tuple to a dataset value.  Every
    key of a MatchSelector will have a tuple of corresponding Matchers.
    """
    def __init__(self, key):
        self._key = key
        
    def match(self, value):
        """Return 1 (match),  0 (don't care), or -1 (no match).
        """
        if value == self._key or value == "*":
            return 1
        elif value == "N/A":
            return 0
        else:
            return -1

    def __repr__(self):
        return self.__class__.__name__ + "('%s')" % self._key
        
class RegexMatcher(Matcher):
    """Matcher for raw regular expressions."""
    def __init__(self, key):
        super(RegexMatcher, self).__init__(key)
        self._regex = re.compile(key)
        self._exceptional_matches = ["*"]
        
    def match(self, value):
        result = super(RegexMatcher, self).match(value)
        if result != -1:
            return result
        return 1 if self._regex.match(value) else -1
    
class GlobMatcher(RegexMatcher):
    """Matcher for |-joined or *-containing expressions which basically work
    as or-ed name globs.  Globs are translated into regexes.
    
    >>> m = GlobMatcher("foo")
    
    A Matcher repr generally shows the underlying regex.
    
    >>> repr(m)
    "GlobMatcher('^(foo\\\\Z(?ms))$')"

    >>> m.match("bar")
    -1
    >>> m.match("foo")
    1
    >>> m.match("fo")
    -1
    
    >>> n = GlobMatcher("fo*o|bar*|baz")
    >>> n.match("far")
    -1
    >>> n.match("fo")
    -1
    >>> n.match("foo")
    1
    >>> n.match("fo1o")
    1
    >>> n.match("baz")
    1
    >>> n.match("ba")
    -1
    >>> n.match("bar12")
    1

    >>> p = GlobMatcher("UVIS-SUB-QUAD|UVIS-SUB-W2K")
    >>> p.match("UVIS-SUB")
    -1
    >>> p.match("UVIS-SUB-QUAD")
    1
    
    >>> p.match("*")
    1
    >>> p.match("N/A")
    0
    """
    def __init__(self, key):
        parts = key.split("|")
        exprs = [fnmatch.translate(part) for part in parts]
        new_key = "^(" + "|".join(exprs) + ")$"
        super(GlobMatcher, self).__init__(new_key)
        # To support automatic refactoring in the refactor module,  also
        # match on the original key such as A|B|C|D
        self._exceptional_matches.append(key)
        
class InequalityMatcher(Matcher):
    """
    >>> m = InequalityMatcher(">1.2")
    >>> m.match("1.3")
    1
    >>> m.match("1.2")
    -1
    >>> m.match("-100")
    -1

    >>> m = InequalityMatcher("<1.2")
    >>> m.match("1.3")
    -1
    >>> m.match("1.2")
    -1
    >>> m.match("-100")
    1
    >>> m.match("*")
    1
    >>> m.match("N/A")
    0
    """
    def __init__(self, key):
        super(InequalityMatcher, self).__init__(key)
        parts = re.match(
            r"^([><]=?)\s*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)", key)
        self._operator = parts.group(1)
        self._value =  float(parts.group(2))
        
    def match(self, value):
        result = super(InequalityMatcher, self).match(value)
        if result != -1:
            return result
        try:
            float_value = float(value)
        except Exception:
            return -1
        return { 
            ">" : lambda m, n :  1 if m > n else -1,
            "<" : lambda m, n :  1 if m < n else -1,
            ">=" : lambda m, n :  1 if m >= n else -1,
            "<=" : lambda m, n :  1 if m <= n else -1,
         }[self._operator](float_value, self._value)

class BinaryMatcher(Matcher):
    """A matcher which supports logical "or" and "and" for relational
    expressions.
    """
    def __init__(self, key, operator):
        super(BinaryMatcher, self).__init__(key)
        self._operator = operator.strip()
        assert self._operator in ["AND","OR"], "bad binary operator"
        if key.strip().startswith("#"):
            key = key.strip()[1:-1]
        parts = [x.strip() for x in key.split(operator)]
        self._matcher1 = matcher(parts[0])
        self._matcher2 = matcher(parts[1])
        
    def match(self, value):
        value = value.upper()
        result = super(BinaryMatcher, self).match(value)
        if result != -1:
            return result
        if self._operator == "AND" :
            return 1 if ((self._matcher1.match(value)==1) and \
                    (self._matcher2.match(value)==1)) else -1
        elif self._operator == "OR":
            return 1 if ((self._matcher1.match(value)==1) or \
                    (self._matcher2.match(value)==1)) else -1
        else:
            raise RuntimeError("BinaryMatcher logic error.")

class NaMatcher(Matcher):
    """Matcher that always matches,  simplifies/speeds code elsewhere."""
    def __init__(self, key="N/A"):
        super(NaMatcher, self).__init__(key)
        
    def match(self, value):
        """Always match with "don't care" status."""
        return 0


class NotMatcher(Matcher):
    """Matcher which matches the negation of `key`."""
    def __init__(self, key):
        super(NotMatcher, self).__init__(key)
        self._unnegated_matcher = matcher(key[len("NOT "):].strip())

    def match(self, value):
        """Matches unnegated key normally to `value` and then returns the inverted result."""
        unnegated = self._unnegated_matcher.match(value)
        return {
            1 : -1,
            -1 : 1,
            0 : 0,
            }[unnegated]

def esoteric_key(key):
    """Return True if `key` validation is a tautology or too complicated.

    >>> esoteric_key('NOT FUN')
    True
    >>> esoteric_key('FUN')
    False
    >>> esoteric_key('{ThisIsATest}')
    True
    >>> esoteric_key('#ThisIsATest#')
    True
    >>> esoteric_key('(ThisIsATest)')
    True
    >>> esoteric_key('{ThisIsATest)')   # a compromise,  ideally False
    True
    >>> esoteric_key('BETWEEN 100 200')
    True
    """
    key = key.upper()
    return key.startswith(("{","(","#")) and key.endswith(("}",")","#")) or key.startswith("BETWEEN") or key.startswith("NOT")

def matcher(key):
    """Factory for different matchers based on key types.
    
    A tuple of values is treated as an or-ed glob expression.
    
    >>> n = matcher(("foo","bar","baz"))
    >>> n.match("far")
    -1
    >>> n.match("fo")
    -1
    >>> n.match("foo")
    1
    >>> n.match("baz")
    1
    >>> n.match("ba")
    -1
    
    An expression bracketed with {} is matched with string equality, ignoring
    glob and regex special characters.  The {} is removed.
    
    >>> literal = matcher("{||*|}")
    >>> literal.match("0")
    -1
    >>> literal.match("||*|")
    1
    
    >>> someor = matcher("{for|me}")
    >>> someor.match("for")
    -1
    >>> someor.match("me")
    -1
    >>> someor.match("for|me")
    1
    
    An expression bracketed with () is treated as a raw regular expression which
    is used without modification.  The () is removed.
    
    >>> regex = matcher("(something(0|1|2)f?tricky)")
    >>> regex.match("something5tricky")
    -1
    >>> regex.match("something1tricky")
    1
    >>> regex.match("something1ftricky")
    1
    >>> regex.match("somethingttricky")
    -1
    >>> regex.match("foo")
    -1
    >>> regex.match("N/A")
    0
    >>> regex.match("*")
    1
    
    An match expression bracketed with # is treated as a relational expression 
    supporting short circuiting binary operators (and, or) and relational
    operators (<,<=,==,>,>=)
    
    >>> b = matcher("# >1 and <=20 #")
    >>> b.match("4")
    1
    >>> b.match("-1")
    -1
    >>> b.match("20")
    1
    >>> b.match("21")
    -1
    >>> b.match("*")
    1
    >>> b.match("N/A")
    0
    
    >>> c = matcher("#>20 or <5#")
    >>> c.match("4")
    1
    >>> c.match("5")
    -1
    >>> c.match("-1")
    1
    >>> c.match("20")
    -1
    >>> c.match("21")
    1
    >>> c.match("20.1")
    1

    For simple support of ranges displayed as parameter choices,  match them literally as well:

    >>> c.match("#>20 OR <5#")
    1
    >>> c.match("#>20 or <27#")
    -1
    
    A simplified special relation,  between,  defines a slice range:
    
    >>> d = matcher("between 3000 3200")
    >>> d.match("2999.99")
    -1
    >>> d.match("3000")
    1
    >>> d.match("3100")
    1
    >>> d.match("3199.99")
    1
    >>> d.match("3200")
    -1
    >>> d.match("*")
    1
    >>> d.match("N/A")
    0
    >>> matcher("between 42 39")
    Traceback (most recent call last):
    ...
    AssertionError: Invalid between relation 'between 42 39' should be 'between lower_bound upper_bound'

    A value of N/A becomes a matcher which always returns 0.
    
    >>> na = matcher("N/A")
    >>> na.match("1")
    0
    >>> na.match("N/A")
    0
    >>> na.match("*")
    0

    An expression preceded by the keyword "NOT " can be the negation of most other matchers:

    >>> d = matcher("not between 3000 3200")
    >>> d.match("2999.99")
    1
    >>> d.match("3000")
    -1
    >>> d.match("3100")
    -1
    >>> d.match("3199.99")
    -1
    >>> d.match("3200")
    1
    >>> d.match("*")
    -1
    >>> d.match("N/A")
    0

    >>> c = matcher("not #>20 or <5#")
    >>> c.match("#>20 OR <5#")
    -1
    >>> c.match("#>20 or <27#")
    1
    
    >>> regex = matcher("not (something(0|1|2)f?tricky)")
    >>> regex.match("something5tricky")
    1
    >>> regex.match("something1tricky")
    -1
    >>> regex.match("something1ftricky")
    -1
    >>> regex.match("somethingttricky")
    1
    >>> regex.match("foo")
    1
    >>> regex.match("N/A")
    0
    >>> regex.match("*")
    -1
    
    >>> literal = matcher("not {||*|}")
    >>> literal.match("0")
    1
    >>> literal.match("||*|")
    -1
    
    >>> someor = matcher("not {for|me}")
    >>> someor.match("for")
    1
    >>> someor.match("me")
    1
    >>> someor.match("for|me")
    -1
    
    """
    if isinstance(key, tuple):
        return GlobMatcher("|".join(key))
    elif key.startswith("(") and key.endswith(")"):
        return RegexMatcher(key[1:-1])
    elif key.startswith("{") and key.endswith("}"):
        return Matcher(key[1:-1])
    elif key.startswith("#") and key.endswith("#"):
        key = key.upper()
        if " AND " in key:
            return BinaryMatcher(key, "AND")
        elif " OR " in key:
            return BinaryMatcher(key, "OR")
        else:
            return matcher(key[1:-1])
    elif key.upper().startswith("BETWEEN"):
        parts = key.split()
        assert len(parts) == 3, "Invalid between relation " + repr(key)
        assert float(parts[1]) <= float(parts[2]), \
            "Invalid between relation " + repr(key) + \
            " should be 'between lower_bound upper_bound'"
        return BinaryMatcher(">=" + parts[1]+ " AND <" + parts[2], "AND")
    elif key.upper().startswith("NOT "):
        return NotMatcher(key)
    elif "|" in key or "*" in key:
        return GlobMatcher(key)
    elif key == "N/A":
        return NaMatcher("N/A")
    elif key.startswith((">","<")):
        return InequalityMatcher(key)
    else:
        return Matcher(key)

class MatchSelection(Selection):
    """
    MatchSelection's are an atypical Selection consisting of multiple keys
    which,  merged,  lead to one typical Selection taken from self._selections.   Often,  
    the equal weight keys will be a tuple of a single key.   For HST,  merges are also common,  
    and there are indeed multiple equal weighted keys.   Note that a MatchSelection still
    reduces to a single merged choice.
    """

class MatchSelector(Selector):
    """Matching selector does a modified dictionary lookup by directly matching
    the runtime (header) parameters to the selector keys.  

Set error_on_exception() and augment_exception() behavior to reraise:

    >>> old_debug = log.set_exception_trap(False)

The value 'N/A' is equivalent to "don't care" and does not add to the value
of a match.   Literal matches or "*" increase confidence of a good match.

    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : "100",
    ...    (1.0, 2.0) : "200",
    ...    (4.0, '*') : "300",
    ... })

    >>> m.choose(dict(foo='1.0',bar='2.0'))
    '200'
    
    >>> print(m.format())
    Match({
        (1.0, 2.0) : '200',
        (1.0, 'N/A') : '100',
        (4.0, '*') : '300',
    })
    
All match tuple fields should appear in the valid_values_map which is nominally
derived from TPN files:

    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })
    Traceback (most recent call last):
    ...
    ValidationError:  parameter='bar' value='2.0' is not in ('3.0',)
    
Match tuples should have the same length as the parameter list:
    
    >>> m = MatchSelector(("foo","bar"), { (1.0,) : "100", })
    Traceback (most recent call last):
    ...
    ValidationError: Match key=('1.0',) is wrong length for parameters ('foo', 'bar')

Even though 'bar' is not defined in this call,  it is accepted because "N/A" is
one of the choices for 'bar':

    >>> choice = m.choose({"foo" : "1.0"})  

On the other hand,  since "N/A" is not a value of 'foo',  it's definitely not
OK to forget to define 'foo':

    >>> choice = m.choose({"foo" : "1.0"})  

Selector's can verify header values against a valid values map which is 
derived from the rmap itself rather than TPNs:   
    
    >>> m.choose({"foo" : "doh!", "bar":"1.0"})  
    Traceback (most recent call last):
    ...
    ValidationError:  parameter='foo' value='doh!' is not in ['1.0', '4.0']
 
The last thing matched in a selector tree is assumed to be a file:
    
    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, '*') : "100",
    ...    (1.0, 2.0) : "200",
    ...    ('*', '*') : "300",
    ...    (5.0, 3.0) : "200",
    ... })
    
file_matches() returns a list of recursive trails/lists of keys which lead 
to a given file:
    
    >>> m.file_matches("200")
    [((('foo', '1.0'), ('bar', '2.0')),), ((('foo', '5.0'), ('bar', '3.0')),)]
    
The result of file_matches() is a list of lists of keys because it is
used recursively on trees of mappings and selectors.
    
Tuple results are legal as long as the elements are simple strings:
    
    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : ("100","200"),
    ... })
    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })

    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : (100,"200"),
    ... })
    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })
    Traceback (most recent call last):
    ...
    ValidationError: Non-string tuple value for choice (100, '200') at ('1.0', 'N/A')

Dictionary results are legal as long as the keys and values are simple strings:
    
    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : {"flummox":"200"},
    ... })
    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })

    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : {"flummox":200},
    ... })
    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })
    Traceback (most recent call last):
    ...
    ValidationError: Non-string dictionary value for choice {'flummox': 200} at ('1.0', 'N/A')

    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : { 1:"200"},
    ... })
    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })
    Traceback (most recent call last):
    ...
    ValidationError: Non-string dictionary key for choice {1: '200'} at ('1.0', 'N/A')

No other primitive choices are legal,  so None is invalid:

    >>> m = MatchSelector(("foo","bar"), {
    ...    (1.0, 'N/A') : None,
    ... })
    >>> m.validate_selector({ "foo" : ("1.0",), "bar":("3.0",) })
    Traceback (most recent call last):
    ...
    ValidationError: Illegal type for selector primitive value None

Inconsistencies between parameter lists and match tuples are detected:
    
    >>> m = MatchSelector(("foo",), {
    ...    (1.0, 'N/A') : { "1":"200"},
    ... })
    Traceback (most recent call last):
    ...
    ValidationError: Match key=('1.0', 'N/A') is wrong length for parameters ('foo',)
    
The special case of matching an empty set also needs to work for the sake
of uniform rmap structure for HST:
    
    >>> m = MatchSelector((), {
    ...    () : "100",
    ... })
    >>> m.choose({})
    '100'

Restore original debug behavior:

    >>> _jnk = log.set_exception_trap(old_debug)
    
    """
    rmap_name = "Match"
    
    def __init__(self, parameters, selections, rmap_header={}):
        super(MatchSelector, self).__init__(parameters, selections, rmap_header)
        self._match_selections = self.get_matcher_selections(dict_wo_dups(self._selections))
        self._value_map = self.get_value_map()
     
    @classmethod
    def condition_key(cls, match_tuple):
        """Normalize the elements of match_tuple using utils.condition_value()"""
        if isinstance(match_tuple, tuple):
            return tuple([cls.condition_key_element(elem) for elem in match_tuple])
        else:  # simple strings
            return (cls.condition_key_element(match_tuple),)
    
    @classmethod
    def condition_key_element(cls, elem):
        """Condition one element of a match tuple."""
        if isinstance(elem, str):
            if (elem.startswith("{") and elem.endswith("}")) or \
                (elem.startswith("(") and elem.endswith(")")):
                pass  # raw regexes and equalities are not conditioned
            elif "|" in elem:
                elem = "|".join([utils.condition_value(x) for x in elem.split("|")])
            else:
                elem = utils.condition_value(elem)
        elif isinstance(elem, (tuple, list)):
            elem = "|".join([utils.condition_value(key) for key in elem])
        else:
            elem = utils.condition_value(elem)
        return elem

    def get_matcher_selections(self, mappings):
        """Expand the selections from the spec file to include a tuple
        of Matcher objects for each selection key.   Return new selections
        of the form:
               { spec_key_tuple :  (Matcher_tuple, choice) }
        """
        selections = {}
        for keytuple, choice in mappings.items():
            matchers = []
            for parkey in keytuple:
                matchers.append(matcher(parkey))
            selections[keytuple] = MatchSelection((tuple(matchers), choice))
        return selections

    def get_selection(self, header):
        """Get the matching selection for `self` based on parameters in `header`.

        yield MatchSelection
        """
#         return self.winnowing_match(header)   # Return the nested generator directly...
        for selection in self.winnowing_match(header):
            yield selection

    def winnowing_match(self, header, raise_ambiguous=None):
        """Iterate through each of the parameters in `fitskeys`, binding
        them successively to corresponding values from `header`.  For
        each bound fitskey,  iterate through `selections` and winnow out
        keys which cannot match based on the value of the current fitskey.
        Successively yield any survivors,  in the order of most specific
        matching value (fewest *'s) to least specific matching value.
        """
        if raise_ambiguous is None:
            if "raise_ambiguous" in self._rmap_header:
                raise_ambiguous = self._rmap_header["raise_ambiguous"] in ["True", "true", "TRUE", "1"]
            else:
                raise_ambiguous =  self._rmap_header.get("observatory", None) != "hst"

        weights, remaining = self._winnow(header, dict(self._match_selections))

        sorted_candidates = self._rank_candidates(weights, remaining)
        
        # Yield successive candidates in order from best match to worst, 
        # merging equivalently weighted candidate match_tuples.
        for _weight, match_tuples in sorted_candidates:
            if len(match_tuples) > 1:
                if raise_ambiguous:
                    raise AmbiguousMatchError("More than one match clause matched.")
                subselectors = tuple([remaining[match_tuple].choice for match_tuple in match_tuples])
                if isinstance(subselectors[0], Selector):
                    selector = self.merge_group(subselectors)
                else:
                    selector = subselectors
            else:
                selector = remaining[match_tuples[0]].choice
            log.verbose("Matched", repr(match_tuples[0]), "returning", repr(selector), verbosity=60)
            yield MatchSelection((match_tuples, selector))
        raise MatchingError("No match found.")

    def _winnow(self, header, remaining):
        """Based on the parkey values in `header`, winnow out selections
        from `remaining` which cannot possibly match.  For each surviving
        selection,  weight each parkey which matches exactly as -1 and 
        "don't care" matches as 0.
        
        returns   ( {match_tuple:weight ...},   remaining_selections
        """
        # weights counts the # of parkey value matches, establishing a
        # goodness-of-match weighting.  negative weights are better matches
        weights = { match_tuple:0 for match_tuple in remaining.keys() }

        for i, parkey in enumerate(self._parameters):
            value = header.get(parkey, "UNDEFINED")
            log.verbose("Binding", repr(parkey), "=", repr(value), verbosity=60)
            for match_tuple, (matchers, _subselector) in list(remaining.items()):
                # Match the key to the current header vaue
                match_status = matchers[i].match(value)
                # returns 1 (match), 0 (don't care), or -1 (no match)
                if match_status == -1:
                    log.verbose("Eliminating", match_tuple, "based on", parkey + "=" + repr(value), verbosity=60)
                    del remaining[match_tuple]   # winnow!
                else: # matched or don't care,  set weights accordingly
                    weights[match_tuple] -= match_status   
        return weights, remaining

    def _rank_candidates(self, weights, remaining):
        """Rank the possible matches in `remaining` according to
        their corresponding `weights`,  with lowest values indicating
        best matches.
        
        Return  sorted( [(weight, [match_tuples...])...]
        """        
        # Create a mapping of candidate matches: { weight : [ match_tuples...] }
        candidates = {}
        for match_tuple, _junk in remaining.items():
            if weights[match_tuple] not in candidates:
                candidates[weights[match_tuple]] = []
            candidates[weights[match_tuple]].append(match_tuple)
        # Sort candidates into:  [ (weight, [match_tuples...]) ... ]
        # Lowest weight is best match
        candidates = sorted([(x[0], tuple(x[1])) for x in candidates.items()])
        log.verbose("Candidates:\n", log.PP(candidates), verbosity=60)
        return candidates

    @utils.cached
    def merge_group(self, equivalent_selectors):
        """Merge a group of equal-weighted selectors into a single
        combined selector.  Nominally this merges special case
        Useafter clauses into a more general UseAfter creating
        something appropriate only for the special case.  Doing this
        dynamically helps keep rmaps small by factoring out the
        special cases and not repeating common info for every special
        case.
        """
        log.verbose("Merging equivalent selectors", equivalent_selectors, verbosity=60)
        combined = equivalent_selectors[0]
        for esel in equivalent_selectors[1:]:
            combined = combined.merge(esel)
        log.verbose("Merge result:\n", log.Deferred(combined.format), verbosity=70)
        return combined

    def get_selector_value_map(self):
        """Return { parameter : set([values in use...]) }"""
        vmap = {}
        for i, fitsvar in enumerate(self._parameters):
            vmap[fitsvar] = set()
            for key in self.keys():
                try:
                    values = key[i]
                except IndexError:
                    raise ValueError("Match tuple " + repr(key) +
                                     " wrong length for parameter list " + 
                                     repr(tuple(self._parameters)))
                if not isinstance(values, tuple):
                    values = [values]
                for value in values:
                    for regex_case in value.split("|"):
                        vmap[fitsvar].add(regex_case)
        return vmap

    def _validate_selector(self, valid_values_map):
        self._check_valid_values(valid_values_map)
        Selector._validate_selector(self, valid_values_map)
            
    def _check_valid_values(self, valid_values_map):
        """Issue warnings for parkeys which aren't covered by valid_values_map."""
        for name in self._parameters:
            if name not in valid_values_map:
                log.verbose_warning(self.short_name, "Parameter ",
                                    repr(name), " is unchecked.")

    def _validate_key(self, key, valid_values_map):
        """Validate each field of a single Match `key` against the possible 
        values in `valid_values_map`.   Note that each `key` is 
        nominally a tuple with values for multiple parkeys.
        """
        if isinstance(key, (python23.string_types, int, float)):
            key = (key,)
        if len(key) != len(self._parameters):
            raise ValidationError("wrong length for parameter list " + 
                                  repr(self._parameters) + " for key " + repr(key))
        for i, name in enumerate(self._parameters):
            if name not in valid_values_map:
                log.verbose("Unchecked", repr(name), "=", repr(key[i]))
                continue
            for value in str(key[i]).split("|"):
                log.verbose("Checking", repr(name), "=", repr(key[i]), "against",
                            valid_values_map[name])
                self._validate_value(name, value, valid_values_map[name], runtime=False)
        for other in self.keys():
            if key != other and match_superset(other, key) and \
                not different_match_weight(key, other):
                log.verbose_warning("Match tuple " + repr(key) + 
                                    " is an equal weight special case of " + repr(other),
                                    " requiring dynamic merging.")
                
# ==============================================================================

class UseAfterSelector(Selector):
    """A UseAfter selector chooses the greatest time which is less than
    the "date" condition and returns the corresponding item.


Enable debugging which causes trapped exceptions to raise rather than issue ERROR.

    >>> from crds import log
    >>> old_debug = log.set_exception_trap(False)

Construct a test UseAfterSelector

    >>> u = UseAfterSelector(("DATE-OBS", "TIME-OBS"), {
    ...        '2003-09-26 01:28:00':'nal1503ij_bia.fits',
    ...        '2004-02-14 00:00:00':'o3913216j_bia.fits',
    ...        '2004-04-25 21:31:00':'o5d10135j_bia.fits',
    ...        '2004-06-18 04:36:00':'o9s16388j_bia.fits', 
    ...        '2004-07-02 08:09:00':'o9t1525sj_bia.fits',
    ...        '2004-07-14 16:52:00':'o9f15549j_bia.fits',
    ...        '2004-07-30 00:18:00':'o9t1553tj_bia.fits',
    ... })

Exact match

    >>> u.choose({'DATE-OBS': '2004-07-02', 'TIME-OBS': '08:09:00'})   
    'o9t1525sj_bia.fits'

Just before, in between

    >>> u.choose({'DATE-OBS': '2004-07-02', 'TIME-OBS': '08:08:59'})   
    'o9s16388j_bia.fits'

Later than all entries

    >>> u.choose({'DATE-OBS': '2005-07-02', 'TIME-OBS': '08:08:59'}) 
    'o9t1553tj_bia.fits'

Earlier than all entries

    >>> u.choose({'DATE-OBS': '2000-07-02', 'TIME-OBS': '08:08:59'})   
    Traceback (most recent call last):
    ...
    UseAfterError: No selection with time < '2000-07-02 08:08:59'
    
UseAfter dates should look like YYYY-MM-DD HH:MM:SS or:    

    >>> u = UseAfterSelector(("DATE-OBS", "TIME-OBS"), {
    ...        '2003-09-26 foo 01:28:00':'nal1503ij_bia.fits',
    ... })
    
    >>> u.validate_selector({"DATE-OBS":"*", "TIME-OBS":"*"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter Invalid date/time format for ('DATE-OBS', 'TIME-OBS') value='2003-09-26 foo 01:28:00' exception is "invalid literal for int() with base 10: 'foo 01'"

A more subtle error in the date or time should still be detected:

    >>> u = UseAfterSelector(("DATE-OBS", "TIME-OBS"), {
    ...        '2003-09-35 01:28:00':'nal1503ij_bia.fits',
    ... })
    >>> u.validate_selector({"DATE-OBS":"*", "TIME-OBS":"*"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter Invalid date/time format for ('DATE-OBS', 'TIME-OBS') value='2003-09-35 01:28:00' exception is 'day is out of range for month'
    
    >>> choice = u.choose({"DATE-OBS":"2003-09-22", "TIME-OBS":"01:28:00"})
    Traceback (most recent call last):
    ...
    UseAfterError: No selection with time < '2003-09-22 01:28:00'
   
    >>> u.choose({"DATE-OBS":"2003-09-52", "TIME-OBS":"01:28:00"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter Invalid date/time format for ('DATE-OBS', 'TIME-OBS') value='2003-09-52 01:28:00' exception is 'day is out of range for month'

    >>> u.choose({"DATE-OBS":"2003/messed/up", "TIME-OBS":"01:28:00"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter Invalid date/time format for ('DATE-OBS', 'TIME-OBS') value='2003/messed/up 01:28:00' exception is "Unknown numerical date format: '2003/messed/up 01:28:00'"

    >>> u.choose({"DATE-EXP":"2003/messed/up", "TIME-OBS":"01:28:00"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter required lookup parameter 'DATE-OBS' is undefined.

    >>> u.choose({"DATE-OBS":"2003/12/20", "TIME-OBS":"01:28:00QM"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter Invalid date/time format for ('DATE-OBS', 'TIME-OBS') value='2003/12/20 01:28:00QM' exception is 'invalid literal for float(): 00QM'

    >>> u.choose({"DATE-OBS":"2003/12/2", "TIME-OBS":"01:28:00"})
    Traceback (most recent call last):
    ...
    ValidationError: UseAfter Invalid date/time format for ('DATE-OBS', 'TIME-OBS') value='2003/12/2 01:28:00' exception is "Unknown numerical date format: '2003/12/2 01:28:00'"

Alternate date/time formats are accepted as header parameters.
    
    >>> choice = u.choose({"DATE-OBS":"2003/12/20", "TIME-OBS":"01:28"})
    
Empty UseAfterSelectors always raise an exception on choose():
    
    >>> u = UseAfterSelector(("DATE-OBS", "TIME-OBS"), { })
    >>> u.choose({"DATE-OBS":"2003-09-01", "TIME-OBS":"01:28:00"})
    Traceback (most recent call last):
    ...
    UseAfterError: No selection with time < '2003-09-01 01:28:00'

Restore debug configuration.

    >>> _jnk = log.set_exception_trap(old_debug)

    """
    def get_selection(self, date):
        log.verbose("Matching date", date, " ", verbosity=60)
        yield self.bsearch(date, self._selections)
    
    def bsearch(self, date, selections):
        """Do a binary search over a sorted selections list."""
        if len(selections) == 0:
            raise UseAfterError("No selection with time < " + repr(date))
        elif len(selections) > 1:
            left = selections[:len(selections)//2]
            right = selections[len(selections)//2:]
            compared = right[0].key
            log.verbose("...against", compared, end="", verbosity=60)
            if date >= compared:
                return self.bsearch(date, right)
            else:
                return self.bsearch(date, left)
        else:
            if date >= selections[0].key:
                log.verbose("matched", repr(selections[0]), verbosity=60)
                return selections[0]
            else:
                raise UseAfterError("No selection with time < " + repr(date))
            
    def _validate_key(self, key, valid_values_map):
        """Validate a selector date/time field for this UseAfter."""
        self._validate_datetime(self._parameters, key)
        
    def _validate_header(self, header):
        """Validate the `header` parameters which apply only to this UseAfter.
        Ignore `valid_values_map`.   
        
        Return lookup date.
        """
        date = self._raw_date(header)
        return self._validate_datetime(self._parameters, date)
        
    def _raw_date(self, header):
        """Combine the values of self.parameters from `header` into a single raw date separated by spaces."""
        date = ""
        for par in self._parameters:
            date += header[par] + " "
        return date.strip()

    def match_item(self, key):
        """Account for succinct UseAfter syntax hack,  space joined date + time is really two parameters for HST."""
        if len(self._parameters) == 1:
            return ((self._parameters[0], key),)
        else:
            return tuple(zip(self._parameters, key.split()))
    
    def merge(self, other):
        """Merge two UseAfterSelectors into a single selector.  Resolve
        collisions of selections by using the "greater" of the colliding
        selections...  nominally the greater filename which is the most
        recent for CDBS and CRDS naming conventions.
        """
        merge_selections = []
        ownsel = self._selections[:]
        othersel = other._selections[:]
        while ownsel and othersel:
            own = ownsel[0]
            other = othersel[0]
            if own.key < other.key:
                appended = own
                ownsel = ownsel[1:]
            elif other.key < own.key:
                appended = other
                othersel = othersel[1:]
            else: # collision
                ownsel.pop(0)
                othersel.pop(0)
                if own.choice >= other.choice:
                    appended = own
                    overwritten = other
                else:
                    appended = other
                    overwritten = own
                log.verbose("Merge collision at", repr(appended.key), "using",
                            repr(appended.choice), "not", overwritten.choice, verbosity=60)
            merge_selections.append(appended)
        merge_selections.extend(ownsel)
        merge_selections.extend(othersel)
        return self.__class__(self._parameters[:], merge_selections=merge_selections)
    
    def get_parkey_map(self):
        return { par:"*" for par in self._parameters}
    
    @classmethod
    def _make_key(self, header, parkeys):
        """Join reference file datetime parameters with spaces."""
        return " ".join([header[par] for par in parkeys])
    
    def todict_parameters(self):
        return ("USEAFTER",)

# ==============================================================================

class ClosestTimeSelector(UseAfterSelector):
    """ClosestTime chooses the selection whose time most closely matches the
    choose() method "time" keyword parameter

    >>> t = ClosestTimeSelector(("time",), {
    ...  '2017-04-24 00:00:00': "cref_flatfield_123.fits",
    ...  '2018-02-01 00:00:00': "cref_flatfield_222.fits",
    ...  '2019-04-15 00:00:00': "cref_flatfield_123.fits",
    ... })

    >>> t.choose({"time":"2016-05-05 00:00:00"})
    'cref_flatfield_123.fits'

    >>> t.choose({"time":"2016-04-24 00:00:00"})
    'cref_flatfield_123.fits'

    >>> t.choose({"time":"2018-02-02 00:00:00"})
    'cref_flatfield_222.fits'

    >>> t.choose({"time":"2019-03-01 00:00:00"})
    'cref_flatfield_123.fits'

    >>> t.choose({"time":"2019-04-15 00:00:00"})
    'cref_flatfield_123.fits'

    >>> t.choose({"time":"2019-04-16 00:00:00"})
    'cref_flatfield_123.fits'
    """
    def get_selection(self, date):        
        import numpy as np
        diff = np.array([abs_time_delta(date, key) for key in self.keys()], 'f')
        index = np.argmin(diff)
        yield self._selections[index]

# ==============================================================================

class GeometricallyNearestSelector(Selector):
    """GeometricallyNearest selects the choice whose key is at the smallest
    distance from the specified condition value.

    >>> r = GeometricallyNearestSelector(("effective_wavelength",), {
    ...  1.2 : "cref_flatfield_120.fits",
    ...  1.5 : "cref_flatfield_124.fits",
    ...  5.0 : "cref_flatfield_137.fits",
    ... })

    >>> r.choose({"effective_wavelength":'1.0'})
    'cref_flatfield_120.fits'

    >>> r.choose({"effective_wavelength":'1.2'})
    'cref_flatfield_120.fits'

    >>> r.choose({"effective_wavelength":'1.25'})
    'cref_flatfield_120.fits'

    >>> r.choose({"effective_wavelength":'1.4'})
    'cref_flatfield_124.fits'

    >>> r.choose({"effective_wavelength":'3.25'})
    'cref_flatfield_124.fits'

    >>> r.choose({"effective_wavelength":'3.26'})
    'cref_flatfield_137.fits'

    >>> r.choose({"effective_wavelength":'5.0'})
    'cref_flatfield_137.fits'

    >>> r.choose({"effective_wavelength":'5.1'})
    'cref_flatfield_137.fits'
    
A GeometricallyNearestSelector doesn't know now to resolve an ambiguous match by
merging two selectors:
    
    >>> r.merge(r)
    Traceback (most recent call last):
    ...
    AmbiguousMatchError: More than one match was found at the same weight and GeometricallyNearest does not support merging.

Effective_wavelength doesn't have to be covered by valid_values_map:
    
    >>> r.validate_selector({})
    
    >>> r.choose({"effective_wavelength":"foo"})
    Traceback (most recent call last):
    ...
    ValidationError: GeometricallyNearest Invalid number for 'effective_wavelength' value='foo'
    
    """
    @classmethod
    def condition_key(cls, key):
        return utils.condition_value(key)
    
    def get_selection(self, keyval):
        import numpy as np
        nkeys = np.array(self.keys(), dtype='f')
        diff = np.abs(nkeys - keyval)
        index = np.argmin(diff)
        yield self._selections[index]
    
    def _validate_key(self, key, valid_values_map):
        parname = self._parameters[0]
        self._validate_number(parname, key)
        
    def _validate_header(self, header):
        parname = self._parameters[0]
        return self._validate_number(parname, header[parname])

    def _validate_value(self, name, value, valid_list, runtime=True):
        self._validate_number(name, value)

    @classmethod
    def _make_key(self, header, parkeys):
        """Always return key as a simple float."""
        return float(header[parkeys[0]])

# ==============================================================================

# Different interface,  not a true subclass of Selection so get_choice() is overridden also.
BracketSelection = namedtuple("BracketSelection", ("less", "greater"))

class BracketSelector(Selector):
    """Bracket selects the the bracketing values of the
    given context variable,  returning a two-tuple.

    >>> r = BracketSelector(("effective_wavelength",), {
    ...   1.2: "cref_flatfield_120.fits",
    ...   1.5: "cref_flatfield_124.fits",
    ...   5.0: "cref_flatfield_137.fits",
    ... })

    >>> r.choose({"effective_wavelength":'1.25'})
    ('cref_flatfield_120.fits', 'cref_flatfield_124.fits')

    Note that an exact match still produces a two-tuple.

    >>> r.choose({"effective_wavelength":'1.2'})
    ('cref_flatfield_120.fits', 'cref_flatfield_120.fits')

    >>> r.choose({"effective_wavelength":'1.5'})
    ('cref_flatfield_124.fits', 'cref_flatfield_124.fits')

    >>> r.choose({"effective_wavelength":'5.0'})
    ('cref_flatfield_137.fits', 'cref_flatfield_137.fits')

    Selections off either end choose the boundary value:

    >>> r.choose({"effective_wavelength":'1.0'})
    ('cref_flatfield_120.fits', 'cref_flatfield_120.fits')

    >>> r.choose({"effective_wavelength":'6.0'})
    ('cref_flatfield_137.fits', 'cref_flatfield_137.fits')
    """        
    def get_selection(self, keyval):
        """Returns BracketSelection() corresponding to keyval.   This is an atypical
        Selection which is really two selections, right and left.   Consequently,  the
        get_selection() followed by get_choice() protocol has to be carefully observed
        here.  
        
        returns BracketSelection(less, greater)
        
        BracketSelection is atypical because it does not meet the (key, choice) protocol
        of Selection but is rather (less, greater) where `less` and `greater` are normal 
        (key, choice) Selections.
        """
        index = 0
        selections = self._selections
        while index < len(selections) and keyval > selections[index].key:
            index += 1
        if index == len(selections):
            less, greater = selections[index-1], selections[index-1]
        elif index == 0 or keyval == selections[index].key:
            less, greater = selections[index], selections[index]
        else:
            less, greater = selections[index-1], selections[index]
        yield BracketSelection(less, greater)   # XXXX non-standard interface
    
    def get_choice(self, bracket_selection, header):
        """Return the paired choices of the BracketSelector based on an atypical
        "BracketSelection" pair.   Recursively calls the standard get_choice() on
        each half of the BracketSelection.
        
        Return  (less_choice, greater_choice)   a pair of choices.
        """
        # YYYYY weird get_selection() yield-value is handled/required/fixed here
        assert isinstance(bracket_selection, BracketSelection), repr(bracket_selection)
        result1 = super(BracketSelector, self).get_choice(bracket_selection.less, header)
        if bracket_selection.less != bracket_selection.greater:
            result2 = super(BracketSelector, self).get_choice(bracket_selection.greater, header)
        else:
            result2 = result1
        return result1, result2

    def get_parkey_map(self):
        return {}

    def _validate_key(self, key, valid_values_map):
        return self._validate_number(self._parameters[0], key)

    def _validate_value(self, name, value, valid_list, runtime=True):
        self._validate_number(name, value)

    def _validate_header(self, header):
        parname = self._parameters[0]
        return self._validate_number(parname, header[parname])
    
    @classmethod
    def _make_key(self, header, parkeys):
        """Always return key as a simple float."""
        return float(header[parkeys[0]])

# ==============================================================================

class ComparableMixin(object):
    
    def _compare(self, other, method):
        if not isinstance(other, self.__class__):
            other = self._convert(other)
        self._check_compatible(other)            
        try:
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            # _cmpkey not implemented, or return different type,
            # so I can't compare with "other".
            return NotImplemented
    
    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)
    
    def __hash__(self):
        return hash(self._cmpkey())
    
    def _check_compatible(self, other):
        pass
    
RELATION_RE = re.compile(r'^([<=][=]?|default)(.*)$')

FIXED_RE = re.compile(r"\d+[.]*\d*")

class VersionRelation(ComparableMixin):
    """A version relation consists of a relation operator <,=,== and an 
    expression representing a version.   VersionRelations can be compared to 
    themselves to support generating a sorted list:

    >>> s = VersionRelation('<5')
    >>> t = VersionRelation('<6')
    >>> s < t
    True
    >>> s == t
    False
    >>> s > t
    False
    >>> VersionRelation("= 4.5") < VersionRelation("= 5.0")
    True

    VersionRelations can be compared to versions to support choosing from a 
    sorted list:

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
    ValidationError: Incompatible version expression types: 5.1 and (5, 0)

    >>> VersionRelation('< 3.1') < 6
    True

    """
    def __init__(self, relation_str):
        self.relation_str = str(relation_str)
        if self.relation_str.replace("=","").strip() == "default":
            self.relation = "="
            self.version = sys.maxsize
        else:
            if not self.relation_str.startswith(("<","=")):
                self.relation_str = "=" + self.relation_str
            match = RELATION_RE.match(self.relation_str)
            if match:
                self.relation = match.group(1).replace("==","=")
                version = match.group(2).strip()
                try:
                    self.version = ast.literal_eval(version)
                except ValueError:
                    raise ValidationError("Invalid version expression in: " + repr(self.relation_str))
            else:
                raise ValidationError("Illegal version expression in: " + repr(self.relation_str))
            
    def __repr__(self):
        return 'VersionRelation(%s)' % repr(self.relation_str)
    
    def __str__(self):
        return self.relation_str
   
    def _cmpkey(self):
        return (self.version, self.relation)
    
    def _convert(self, other):
        return self.__class__(str(other))
    
    def _check_compatible(self, other):
        if self.version == "default":
            return True
        elif isinstance(self.version, numbers.Number) and isinstance(other.version, numbers.Number):
            return True
        elif isinstance(self.version, type(other.version)):
            return True
        else:
            raise ValidationError("Incompatible version expression types: " + 
                                  str(self.version) + " and " + str(other.version))

class SelectVersionSelector(Selector):
    """SelectVersion chooses from among it's selections based on a number of
    version relations. Each selection of a SelectVersion consists of a version
    relation and a filename or nested Selector:

    ('< 5', 'cref_flatfield_518.fits')

    A special relation,  'default', is selected when none of the other relations
    applies:

    ('default', 'cref_flatfield_500.fits')

    Version relations are expressed as strings which consist of a relation
    symbol followed by an expression,  as in:

    '< 5.03'
    '= 6.66'
    '== 6.66'

    Version relations consist of two parts,  the relation symbol (=,==,<) and
    the version expression.  The simplest version expression consists of a 
    string which represents a number.   However,  the requirement on the 
    version expression (the remainder of the string following the relation) is 
    simply that it be eval()'able and that the result of the eval() supports 
    comparison operators.  Hence,  a more elaborate version selector might 
    look like:

    ('= (5,0,1)', 'cref_flatfield_501.fits')

    In this case the tuple (5,0,1) represents the common representation of
    versions as major, minor, and point releases.   Note that for non-numerical
    version expressions,  the type of the eval'ed expression must exactly match
    the type of the choose()-time parameter,  i.e. in the previous example the
    choose()-time parameter must be a tuple.

    >>> r = SelectVersionSelector(("sw_version",), {
    ...  '<3.1':    'cref_flatfield_65.fits',
    ...  '<5':      'cref_flatfield_73.fits',
    ...  'default': 'cref_flatfield_123.fits',
    ... })

    >>> r.choose({"sw_version":'4.5'})
    'cref_flatfield_73.fits'

    >>> r.choose({"sw_version":'5'})
    'cref_flatfield_123.fits'

    >>> r.choose({"sw_version":'6'})
    'cref_flatfield_123.fits'

    >>> r.choose({"sw_version":'2.0'})
    'cref_flatfield_65.fits'

    >>> r.choose({"sw_version":'default'})
    'cref_flatfield_123.fits'
    """
    def get_parkey_map(self):
        return {}

    @classmethod    
    def condition_key(cls, key):
        if isinstance(key, VersionRelation):
            return key
        else:
            return VersionRelation(key)

    def get_selection(self, version):
        """Based on `version`,  return the corresponding selection."""
        index = 0
        while self._selections[index][0] < version:
            index += 1
        yield self._selections[index]
    
    def _validate_key(self, key, valid_values_map):
        """Keys effectively validated at __init__ time."""
        pass

    def _validate_value(self, name, value, valid_list, runtime=True):
        if value.replace("=","").strip() != "default":
            self._validate_number(name, value)
    
    def _validate_header(self, header):
        parname = self._parameters[0]
        self._validate_value(parname, header[parname], [])
        return header[parname]

def abs_time_delta(time1, time2):
    """Return abs(time1 - time2) in total seconds."""
    date1 = timestamp.parse_date(time1)
    date2 = timestamp.parse_date(time2)
    return abs((date1-date2).total_seconds())

# ==============================================================================

class Parameters(object):
    """Parameters are a place to stash Selector parameters while an entire rmap
    is being read so that the header can be used to help instantiate the 
    selectors.
    
    When the rmap is compiled,  the selectors are compiled into Parameter 
    objects.  Later,  when both the full header and stubbed selectors are 
    available,  the Parameter objects are converted into Selectors by 
    instantiate().
    """
    selector = Selector   # Parameters is abstract class
    def __init__(self, selections):
        if isinstance(selections, dict):
            self.selections = selections.items()
        else:
            self.selections = selections

    def __repr__(self):
        return self.__class__.__name__[:-len("Parameters")]

    def keys(self):
        return [x[0] for x in self.selections]

    def instantiate(self, rmap_header):
        """Recursively construct Selector tree with `rmap_header` available.
        When possible check for duplicate keys in `self.selections` and `rmap_header`.
        """
        check_duplicates(rmap_header, ["header"])
        if not isinstance(rmap_header, dict):
            rmap_header = dict(rmap_header)   # drop header item list form here.
        parkeys = rmap_header["parkey"]   
        return self._instantiate(parkeys, rmap_header, ["selector"])

    def _instantiate(self, parkeys, rmap_header, parents=None):
        """Guts of instantiate,  w/o repeatedly checking `rmap_header` for
        duplicates,  popping off parkeys during selector descent.
        """
        if parents is None:
            parents = []
        check_duplicates(self.selections, parents)
        selections = dict()
        for key, selpars in self.selections:
            if isinstance(selpars, Parameters):
                parent = repr(self) + '(' + repr(key) + ')'
                selections[key] = selpars._instantiate(parkeys[1:], rmap_header, parents+[parent])
            else:
                selections[key] = selpars
        return self.selector(parkeys[0], selections=selections, rmap_header=rmap_header)

def check_duplicates(items, parents=None):
    """Scan the `keys` list for keys which have been repeated and issue errors.
    These correspond to mapping entries which would be silently dropped by 
    the normal Python dictionary evaluation process that is used to quickly
    load rmaps.
    """
    if isinstance(items, dict):   # duplicates impossible
        return
    if parents is None:
        parents = []
    already_seen = dict()
    for key, value in items:
        if key in already_seen:
            log.error("Duplicate entry at", " ".join(parents + [repr(key)]), "=",
                      repr(value), "vs.", repr(already_seen[key]))
        else:
            already_seen[key] = value

class MatchParameters(Parameters):
    """Parameters for MatchSelector"""
    selector = MatchSelector
    
class UseAfterParameters(Parameters):
    """Parameters for UseAfterSelector"""
    selector = UseAfterSelector
    
class SelectVersionParameters(Parameters):
    """Parameters for SelectVersionSelector"""
    selector = SelectVersionSelector
    
class ClosestTimeParameters(Parameters):
    """Parameters for ClosestTimeSelector"""
    selector = ClosestTimeSelector
    
class GeometricallyNearestParameters(Parameters):
    """Parameters for GeometricallyNearestSelector"""
    selector = GeometricallyNearestSelector
    
class BracketParameters(Parameters):
    """Parameters for BracketSelector"""
    selector = BracketSelector

# Appearance in rmap has slightly abbreviated syntax,  minus "Parameters"
SELECTORS = {
    "Match"  : MatchParameters,
    "UseAfter" : UseAfterParameters,
    "SelectVersion" : SelectVersionParameters,
    "ClosestTime" : ClosestTimeParameters,
    "GeometricallyNearest": GeometricallyNearestParameters,
    "Bracket": BracketParameters,
}

# ==============================================================================

def test():
    """Run module doctest."""
    import doctest
    from crds import selectors
    return doctest.testmod(selectors, optionflags=doctest.IGNORE_EXCEPTION_DETAIL)

if __name__ == "__main__":
    print(test())
