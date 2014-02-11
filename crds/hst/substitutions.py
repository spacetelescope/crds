"""This module supports loading CDBS .rule files which define conditional
expansions to be performed on reference file headers as they are submitted
to CRDS.

For instance,  from acs.rule:

    DETECTOR = WFC && CCDGAIN = -999 =>
    CCDGAIN = 1.0 || CCDGAIN = 2.0 || CCDGAIN = 4.0 || CCDGAIN = 8.0 ;

means that the value CCDGAIN=-999 really means CCDGAIN=1.0|2.0|4.0|8.0 whenever 
DETECTOR=WFC.   The abbreviated forms need to be expanded fully in order to 
determine where a reference file should be inserted into an rmap.

CRDS compiles the rules files into a mapping of the form:

    { variable:  { relevance_expr: expansion } }
    
For our example above the expansion looks like:

    { "CCDGAIN" : { "DETECTOR='WFC3' and CCDGAIN='-999'" : "1.0|2.0|4.0|8.0" }

CRDS defines a function:

   expanded_header = expand_wildcards(instrument, header)

which will interpret the rules to expand appropriate values in header.
"""

from __future__ import print_function

import sys
import os.path
import pprint
import glob
import re
import collections

from crds.hst import INSTRUMENTS

from crds import log, utils

# ============================================================================

HERE = os.path.dirname(__file__) or "."
    
# ============================================================================    

class HeaderExpander(object):
    """HeaderExpander applies a set of expansion rules to a header.  It 
    precompiles the applicability expression of each rule.
    
    >>> expansions = {
    ...  'FILTER1' : { "DETECTOR=='HRC' and FILTER1=='ANY'": 'F555W|F775W|F625W'},
    ...  'OBSTYPE' : { "DETECTOR=='HRC' and FILTER1=='G800L' and OBSTYPE=='ANY'": 'IMAGING|CORONAGRAPHIC'},
    ... }
    >>> expander = HeaderExpander(expansions)

    >>> header = { "DETECTOR":"HRC", "FILTER1":"ANY" }
    >>> expander.expand(header)
    {'DETECTOR': 'HRC', 'FILTER1': 'F555W|F775W|F625W'}

    >>> header = { "DETECTOR":"HRC", "FILTER1":"G280L", "OBSTYPE":"ANY" }
    >>> expander.expand(header)
    {'OBSTYPE': 'ANY', 'DETECTOR': 'HRC', 'FILTER1': 'G280L'}

    >>> header = { "DETECTOR":"HRC", "FILTER1":"G800L", "OBSTYPE":"ANY" }
    >>> expander.expand(header)
    {'OBSTYPE': 'IMAGING|CORONAGRAPHIC', 'DETECTOR': 'HRC', 'FILTER1': 'G800L'}
    """
    def __init__(self, expansion_mapping, expansion_file="(none)"):
        self.mapping = {}
        for var, substitutes in expansion_mapping.items():
            for expr, replacement in substitutes.items():
                self.mapping[(var, expr)] = (replacement, compile(expr, expansion_file, "eval"))  # compiled code is from static file.
        self._required_keys = self.required_keys()

    def expand(self, header):
        header = dict(header)
        expanded = dict(header)
        log.verbose("Unexpanded header", self.required_header(header))
        for (var, expr), (expansion, compiled) in self.mapping.items():
            try:
                applicable = eval(compiled, {}, header)  # compiled code is from static file.
            except Exception, exc:
                log.verbose_warning("Header expansion for",repr(expr), 
                            "failed for", repr(str(exc)))
                continue
            if applicable:
                log.verbose("Exapanding", repr(expr), "yields", 
                            var + "=" + repr(expansion))
                expanded[var] = expansion
            else:
                log.verbose("Expanding", repr(expr), "doesn't apply.")
        log.verbose("Expanded header", self.required_header(expanded))
        return expanded
    
    def required_keys(self):
        required = []
        for (_var, expr) in self.mapping:
            required.extend(required_keys(expr))
        return sorted(set(required))
    
    def required_header(self, header):
        return sorted({ key: header.get(key, "UNDEFINED") for key in self._required_keys }.items())
        
def required_keys(expr):
    """
    >>> required_keys("VAR1=='VAL1' and VAR2=='VAL2' and VAR3=='VAL3'")
    ['VAR1', 'VAR2', 'VAR3']
    """
    return sorted(set([term.split("=")[0].strip() for term in expr.split("and")]))
    
EXPANDERS = {}
def load_all():
    global EXPANDERS
    rules = utils.evalfile(HERE + "/substitutions.dat")
    for instrument in rules:
        EXPANDERS[instrument] = HeaderExpander(rules[instrument])

def expand_wildcards(instrument, header):
    if not EXPANDERS:
        load_all()
    try:
        header = EXPANDERS[instrument].expand(header)
    except KeyError:
        header = dict(header)
        # log.warning("Unknown instrument", repr(instrument), " in expand_wildcards().")
    return header

# =============================================================================

def compile_all(path):
    files = []
    for f in glob.glob(path +"/*.rule"):
        if os.path.basename(f).replace(".rule","") in INSTRUMENTS:
            files.append(f)
    compile_files(files)
    
def compile_files(files):
    """Generate variable expansion files for each of the CDBS .rule `files`.
    """
    expansions = {}
    for f in files:
        instrument = os.path.basename(f).replace(".rule","")
        log.info("Compiling expansion rules for", instrument)
        expansions[instrument] = compile_rules(f)
    open(HERE + "/substitutions.dat", "w+").write(pprint.pformat(expansions))

def get_substitutions(instr):
    return utils.evalfile(HERE+"/substitutions.dat").get(instr.lower(), {})

def compile_rules(rules_file):
    """Compile a single `rules_file` into a variable expansion mapping."""
    expression_terms = []
    expansion_terms = []
    expected = "expression"
    compiled = collections.defaultdict(dict)
    source = ""
    for line in open(rules_file):
        source += "\t" + line
        line = line.strip();
        if line.startswith("#"):
            continue
        if not line:
            continue
        if expected == "expression":
            if "=>" in line:
                expr, values = line.split("=>")
                expected = "expansion"
            else:
                expr = line
                values = ""
            expression_terms.extend(parse_terms(expr, "&&"))
        else: # expected == "expansion"
            values = line
        if expected == "expansion":
            if values.endswith(";"):
                completed = True
            else:
                completed = False        
            expansion_terms.extend(parse_terms(values, "||"))
        if completed:
            log.verbose("Compiling:", source[:-1])
            relevance = format_relevance_expr(expression_terms)
            var, expansion = format_expansion(expansion_terms)
            log.verbose("Expansion:", "\n\t", repr(relevance), ":", expansion)
            compiled[var][relevance] = expansion
            expression_terms = []
            expansion_terms = []
            completed = False
            expected = "expression"
            source = ""
    return dict(compiled)

def parse_terms(expr, delimeter):
    """
    >>> parse_terms("VAR1 = VAL1 && VAR2 = VAL2 && VAR3 = VAL3", "&&")
    [('VAR1', 'VAL1'), ('VAR2', 'VAL2'), ('VAR3', 'VAL3')]
    """
    return [tuple([t.replace(";","").strip() for t in term.split("=")]) \
                for term in expr.split(delimeter) if term.strip()]

def format_relevance_expr(terms):
    """
    >>> format_relevance_expr([('VAR1', 'VAL1'), ('VAR2', 'VAL2'), ('VAR3', 'VAL3')])
    "VAR1=='VAL1' and VAR2=='VAL2' and VAR3=='VAL3'"
    """
    return " and ".join([t[0]+"=="+repr(t[1]) for t in terms])

def format_expansion(terms):
    """
    >>> format_expansion([('VAR', 'VAL1'), ('VAR', 'VAL2'), ('VAR', 'VAL3')])
    ('VAR', 'VAL1|VAL2|VAL3')

    >>> format_expansion([('VAR1', 'VAL1'), ('VAR2', 'VAL2'), ('VAR3', 'VAL3')])
    Traceback (most recent call last):
    ...
    AssertionError: more than one expansion variable.
    """
    assert len(set([t[0] for t in terms])) == 1, "more than one expansion variable."
    var = terms[0][0]
    expansion = "|".join(sorted([utils.condition_value(t[1]) for t in terms]))
    return (var, expansion) 

def test():
    import doctest, substitutions
    return doctest.testmod(substitutions)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ", sys.argv[0], "compileall | test")
        sys.exit(0)
    if "--verbose" in sys.argv:
        sys.argv.remove("--verbose")
        log.set_verbose(True)
    if sys.argv[1] == "test":
        print(test())
    elif sys.argv[1] == "compileall":
        compile_all(HERE + "/tpns")
    else:
        print("unknown command '{0}'".format(sys.argv[1]))
        
