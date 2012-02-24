"""This module defines a parser for rmaps."""
import sys
import cStringIO
import re
import pprint
import cProfile

import crds.rmap as rmap

sys.setrecursionlimit(50000)

GRAMMAR = """
MAPPING  :=  WHITESPACES HEADER SELECTOR

HEADER  := header = EXPR
SELECTOR := selector = EXPR

EXPR := CALL
EXPR := STRING
EXPR := TUPLE
EXPR := DICT
EXPR := INT
EXPR := FLOAT
EXPR := BOOL

CALL := IDENT \( DICT \)
IDENT := [A-Za-z_]+[A-Za-z0-9_]*

STRING := "[^"]*"
STRING := '[^']*'

DICT := \{ KEYVALS \}
KEYVALS := KEYVAL , KEYVALS
KEYVALS := KEYVAL
KEYVALS := 
KEYVAL :=  STRING : EXPR 
KEYVAL :=  TUPLE : EXPR 

TUPLE := \( TUPLE_ITEMS \)
TUPLE_ITEMS := EXPR , TUPLE_ITEMS
TUPLE_ITEMS := EXPR
TUPLE_ITEMS :=

INT := [-]?\d+

FLOAT := [-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?

BOOL := True
BOOL := False

WHITESPACES := WHITESPACE WHITESPACES
WHITESPACES := WHITESPACE
WHITESPACES :=
WHITESPACE := COMMENT
WHITESPACE := \s+
COMMENT := #.*$
"""

class ParseError(ValueError):
    """Input could not be parsed."""
    
class Parser(object):
    def __init__(self, grammar, start):
        self.rules = {}
        self.start = start
        for line in cStringIO.StringIO(grammar):
            if not line.strip():
                continue
            words = line.split()
            assert words[1] == ":=", "error in grammar"
            self.add_rule(words[0], words[2:])
    
    def add_rule(self, name, expansion):
        if name not in self.rules:
            self.rules[name] = []
        self.rules[name].append(expansion)
        
    def parse(self, input):
        result = self.match_rule(self.start, input)
        if result:
            if result[1].strip():
                raise ParseError("unparsed input remaining")
            return [result[0]]
        else:
            raise ParseError("parse failed")
        
    def parse_file(self, filename):
        mapping = rmap.locate_mapping(filename)
        return self.parse(open(mapping).read())
    
    def trace(self, kind, name, input): pass
#        pure = input[:min(10,len(input))]
#        pure = pure.replace("\n","\\n")
        # print "matching", kind, name, pure
    
    def match_rule(self, rule, input):
        """Matches the expansions of rule against input,  returning the result
        from the first match.
        
        returns (rule, matched_input), remaining_input
        """
        self.trace("rule", rule, input)
        for expansion in self.rules[rule]:
            result = self.match_expansion(expansion, input)
            if result:
                # print "matched", rule, result[0]
                return (rule, result[0]), result[1]

    def match_expansion(self, expansion, input):
        """Match each of the terms in `expansion` against `input`,  optionally
        matching WHITESPACES between each term.   Terms which are in all caps
        name other rules to match.   Other terms are regexes which must match 
        exactly.
        
        Returns   ([matched_input_terms], remaining_input)
        """
        
        self.trace("expansion", expansion, input)
        parsed = []
        
        for term in expansion:
            if term in self.rules:
                result = self.match_rule(term, input)
            else:
                result = self.match_re(term, input)

            if not result:
                return None
            if result[0][1]:
                parsed.append(result[0])
                input = result[1]

            result = self.match_rule("WHITESPACES", input)
            if result and result[0][1]:
                # parsed.append(result[0])
                input = result[1]
                         
        return parsed, input

    def match_re(self, regex, input):
        """Match regular expression `regex` against `input`."""
        self.trace("regex", regex, input)
        m = re.match(regex, input, re.MULTILINE)
        if m:
            parsed = input[:m.end()]
            return (regex, input[:m.end()]), input[m.end():]
        else:
            return None
        
def simplify(parsing):
    if isinstance(parsing, str):
        return parsing
    simpler = []
    for node in parsing:
        name, value = node
        simplifier = "simplify_" + name
        if simplifier in globals():
            simpleval = simplify(value)
            result = globals()[simplifier](simpleval)
        elif name == value or isinstance(value, str) and name == "\\" + value:
            result = value
        else:
            nested = value if isinstance(value,str) else simplify(value)
            if nested is not None:
                result = (name, nested)
            else:
                result = None  
        if result is not None:
            simpler.append(result)
    if len(simpler) == 1  and isinstance(simpler[0], (str, tuple)):
        simpler = simpler[0]
#    print "Simplify", repr(parsing)
#    print "-->", repr(simpler)
    return simpler

def collapse_plurals(name, value, i=0):
    """Collapses grammar tail recursion into a list."""
    print i, name, "collapse_plurals", value
    if isinstance(value, str):
        return value
    result = []
    for node in value:
        if isinstance(node, str):
            result.append(node)
        elif node[0] == name:
            result.extend(collapse_plurals(name, node[1], i+1))
        else:
            result.append(collapse_plurals(name, node, i+1))
    print i, name, "-->", result
    return result

def simplify_EXPR(value):
    return value

def simplify_WHITESPACES(value):
    return None

def simplify_STRING(value):
    regex, strval = value
    if len(strval) >= 2 and strval[0] == "'" and strval[-1] == "'":
        strval = strval[1:-1]
    return strval

def simplify_KEYVAL(value):
    return value
    key, colon, val = value
    return (key, val)

def simplify_KEYVALS(value):
    vals = collapse_plurals("KEYVALS",  value)
    if isinstance(vals, str):
        return vals
    result = []
    for val in vals:
        if val != ",":
            result.append(val)
#    print "KEYVALS", value
#    print "-->", result
    return result

def simplify_TUPLE_ITEMS(value):
    print "TUPLE_ITEMS", value
    vals = collapse_plurals("TUPLE_ITEMS", value)
    if isinstance(vals, str):
        return vals
    result = []
    for val in vals:
        if val != ",":
            result.append(val)
    print "-->", result
    return result

def simplify_CALL(value):
    return ("CALL", value[0][1][1], tuple(value[2]))

def simplify_HEADER(value):
    return ("HEADER", value[2])

def simplify_SELECTOR(value):
    return ("SELECTOR", value[2])

def simplify_DICT(value):
    rval = ("DICT", [(x[0], x[2]) for x in value[1]])
    return rval

def simplify_TUPLE(value):
    # return tuple(value[1])
    return ("TUPLE", tuple(value[1]))

PARSER = Parser(GRAMMAR, "MAPPING") 

def test():
    if len(sys.argv) == 1:
        files = ["hst_cos_deadtab.rmap"]
    else:
        files = sys.argv[1:]
    for f in files:
        where = rmap.locate_file(f)
        print "text:", open(where).read()
        print "parsing:", where
        parsing = PARSER.parse_file(where)
        print "parsed."
        # print "parsed:", pprint.pformat(parsing)
        simplified = simplify(parsing)
        print "simplified:", pprint.pformat(simplified)
    
if __name__ == "__main__":
    # cProfile.run("test()")
    test()
