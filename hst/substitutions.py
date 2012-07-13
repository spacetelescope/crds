"""This module supports loading CDBS .rule files which define conditional
substitutions to be performed on reference file headers as they are submitted
to CRDS.

For instance,  from acs.rule:

    DETECTOR = WFC && CCDGAIN = -999 =>
    CCDGAIN = 1.0 || CCDGAIN = 2.0 || CCDGAIN = 4.0 || CCDGAIN = 8.0 ;

means that the value CCDGAIN=-999 really means CCDGAIN=1.0|2.0|4.0|8.0 whenever 
DETECTOR=WFC.

CRDS compiles the rules files into a mapping of the form:

    { relevance_expr:  (key, expansion_value) }

CRDS defines a function:

   expanded_header = expand_header_wildcards(header)

which will interpret the rules to expand appropriate values in header.

The naive algorithm CRDS initially uses to expand these rules evaluates *all* 
of the rules.
"""

from __future__ import print_function

import sys

def compile_rules(rules_file):
    expression_terms = []
    expansion_terms = []
    expected = "expression"
    compiled = {}
    for line in open(rules_file):
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
            expression_terms.extend(parse_terms(expr))
        else: # expected == "expansion"
            values = line
        if expected == "expansion":
            if values.endswith(";"):
                completed = True
            else:
                completed = False        
            expansion_terms.extend(parse_terms(values))
        if completed:
            compiled[format_relevance_expr(expression_terms)] = \
                format_expansion(expansion_terms)
            expression_terms = []
            expansion_terms = []
            completed = False
            expected = "expression"
    return compiled

def parse_terms(expr):
    """
    >>> parse_terms("VAR1 = VAL1 && VAR2 = VAL2 && VAR3 = VAL3")
    [('VAR1', 'VAL1'), ('VAR2', 'VAL2'), ('VAR3', 'VAL3')]
    """
    return [tuple([t.strip() for t in term.split("=")]) for term in expr.split("&&")]

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
    expansion = "|".join([t[1] for t in terms])
    return (var, expansion) 

def test():
    import doctest, substitutions
    return doctest.testmod(substitutions)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: ", sys.argv[0], "[compile|test] <rules_files...>")
        sys.exit(0)
    if sys.argv[1] == "test":
        test()
    elif sys.argv[1] == "compile":
        compile_files(sys.argv[1:])
    else:
        print("unknown command '{0}'".format(sys.argv[1]))
        
