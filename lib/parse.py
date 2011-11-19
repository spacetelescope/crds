"""This module defines a parser for rmaps."""

import cStringIO
import re

import crds.rmap as rmap


GRAMMAR = """
MAPPING  :=  HEADER SELECTOR

HEADER  := header = DICT
SELECTOR := selector = CALL

DICT := \{ KEYVALS \}

KEYVALS := KEYVAL , KEYVALS
KEYVALS := 

KEYVAL :=  STRING : EXPR 

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

STRING := '.*'
STRING := ".*"

TUPLE := \( \)
TUPLE := \( TUPLE_ITEMS \)

TUPLE_ITEMS := DATA , TUPLE_ITEM
TUPLE_ITEMS := DATA ,?
TUPLE_ITEMS :=

INT := \d+

FLOAT := [-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?

BOOL := True
BOOL := False
"""

class Parser(object):
    def __init__(self, grammar, start):
        self.rules = {}
        self.start = start
        for line in cStringIO.StringIO(grammar):
            if not line.strip():
                continue
            words = line.split()
            self.add_rule(words[0], words[2:])
    
    def add_rule(self, name, expansion):
        if name not in self.rules:
            self.rules[name] = []
        self.rules[name].append(expansion)
        
    def parse(self, input):
        result = self.match_rule(self.start, input)
        if result:
            if result[1].strip():
                raise RuntimeError("unparsed input remaining")
            return result[0]
        else:
            raise RuntimeError("parse failed")
        
    def parse_file(self, filename):
        mapping = rmap.locate_mapping(filename)
        return self.parse(open(mapping).read())
    
    def trace(self, kind, name, input):
        pure = input[:min(10,len(input))]
        pure = pure.replace("\n","\\n")
        print "matching", kind, name, pure
    
    def match_rule(self, rule, input):
        self.trace("rule", rule, input)
        for expansion in self.rules[rule]:
            result = self.match_expansion(expansion, input)
            if result:
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
            parsed.append(result[0])
            input = result[1]
            result = self.match_re("\s*", input)
            if result and result[0]:
                parsed.append(result[0])
                input = result[1]            
        return parsed, input
        
    def match_re(self, regex, input):
        self.trace("regex", regex, input)
        m = re.match(regex, input)
        if m:
            parsed = input[:m.end()]
            return input[:m.end()], input[m.end():]
        else:
            return None

PARSER = Parser(GRAMMAR, "MAPPING") 

def test():
    print open(rmap.locate_file("hst.pmap")).read()
    PARSER.parse_file("hst.pmap")
    
if __name__ == "__main__":
    test()

