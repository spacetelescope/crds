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

EXPR := CALL
EXPR := DATA

CALL := IDENT \( DICT \)
IDENT := [A-Za-z_]+[A-Za-z0-9_]*

DATA := STRING
DATA := TUPLE
DATA := DICT
DATA := INT
DATA := FLOAT
DATA := BOOL

STRING := " [^"]* "
STRING := ' [^']* '

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
            return result[0]
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
        
def collapse_plurals(parsing):
    rule, value = parsing
    if rule.endswith("S"):
        values = [value]
        nested = collapse_plurals(parsing)
        values.extend(nested[1])
        return rule, values
    else:
        return collapse_plurals(parsing)

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
    
if __name__ == "__main__":
    test()

