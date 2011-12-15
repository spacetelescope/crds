"""This module defines a parser for rmaps."""
import sys
import cStringIO
import re
import pprint

import crds.rmap as rmap

GRAMMAR = """
MAPPING  :=  WHITESPACES HEADER SELECTOR

HEADER  := header = EXPR
SELECTOR := selector = EXPR

EXPR := IDENT \( DICT \)
IDENT := [A-Za-z_]+[A-Za-z0-9_]*

EXPR := STRING
EXPR := TUPLE
EXPR := DICT
EXPR := INT
EXPR := FLOAT
EXPR := BOOL

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
    
    def trace(self, kind, name, input):
        pure = input[:min(10,len(input))]
        pure = pure.replace("\n","\\n")
        # print "matching", kind, name, pure
    
    def match_rule(self, rule, input):
        self.trace("rule", rule, input)
        for expansion in self.rules[rule]:
            result = self.match_expansion(expansion, input)
            if result:
                # print "matched", rule, result[0]
                return (rule, result[0]), result[1]

    def match_expansion(self, expansion, input):
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
                parsed.append(result[0])
                input = result[1]
                         
        return parsed, input

    def match_re(self, regex, input):
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
        if "simplify_" + name in globals():
            simpleval = simplify(value)
            result = globals()["simplify_"+name](simpleval)
        elif name == value or isinstance(value, str) and name == "\\" + value:
            result = value
        else:
            if isinstance(value, str):
                nested = value
            else:
                nested = simplify(value)
            if nested is not None:
                result = (name, nested)
            else:
                result = None  
        if result is not None:
            simpler.append(result)
    if len(simpler) == 1  and isinstance(simpler[0], (str, tuple)):
        simpler = simpler[0]
    return simpler

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
    key, colon, val = value
    return (key, val)

def simplify_KEYVALS(value):
    vals = collapse_plurals("KEYVALS",  value)
    result = []
    for val in vals:
        if val != ",":
            result.append(val)
    return result

def simplify_TUPLE_ITEMS(value):
    vals = collapse_plurals("TUPLE_ITEMS", value)
    result = []
    for val in vals:
        if val != ",":
            result.append(val)
    return result

def simplify_DICT(value):
    return ("DICT", [tuple(x) for x in value[1:-1][0]])

def simplify_HEADER(value):
    return ("HEADER", value[-1][1])

def simplify_SELECTOR(value):
    return ("SELECTOR", value[-1][1])

def simplify_TUPLE(value):
    return ("TUPLE", tuple(value[1]))

def collapse_plurals(name, value, i=0):
    """Collapses grammar tail recursion into a list."""
    if isinstance(value, str):
        return value
    result = []
    for node in value:
        if isinstance(node, str):
            nested = node
        elif node[0] == name:
            nested = collapse_plurals(name, node[1], i+1)
        else:
            nested = collapse_plurals(name, node, i+1)
        if isinstance(nested, list) and nested and isinstance(nested[0], list):
            result.extend(nested)
        else:
            result.append(nested)
    return result

PARSER = Parser(GRAMMAR, "MAPPING") 

def test():
    if len(sys.argv) == 1:
        files = ["hst.pmap"]
    else:
        files = sys.argv[1:]
    for f in files:
        where = rmap.locate_file(f)
        print "parsing:", where
        parsing = PARSER.parse_file(where)
        print "parsed."
        print "parsed:", pprint.pformat(parsing)
        simplified = simplify(parsing)
        print "simplified:", pprint.pformat(simplified)
    
if __name__ == "__main__":
    test()

