"""This module uses the package Parsley to parse CRDS mappings into a
header dictionary and a Selector Parameters object tree.  Selector
Parameters are uninstantiated Selectors which are first built up from
the mapping file.  Since the parser captures full item lists, with no
removal of duplicate keys, the results can be used to detect duplicate
dictionary entries which normally collide silently eliminating one
item.  This is principally intended to detect rmap cut-and-paste
errors in hand edited rmaps.
"""
import sys
import os.path
import cProfile
import pstats
import pprint

from crds import rmap, selectors, log

MAPPING_GRAMMAR = r"""

ws = (' ' | '\r' | '\n' | '\t')*

mapping = header_section:h selector_section:s -> (h, s)

header_section = ws 'header' ws '=' ws dict:d ws -> d

selector_section = ws 'selector' ws '=' ws selector:s ws -> s
selector = ( dict | parameters ):d -> d
parameters = ws parameters_name:n ws '(' ws dict:d ws ')' -> eval(n, globals(), locals())(d)
parameters_name = ('Match' | 'UseAfter' | 'SelectVersion' | 'Bracket' | 'GeometricallyNearest' | 'ClosestTime'):n -> n

dict = ws '{' items:m '}' ws -> m
items = ws (pair:first (ws ',' pair)*:rest ws ','? ws -> [first] + rest) | -> []
pair = ws immutable:k ws ':' ws value:v ws -> (k, v)
immutable = (string | immutable_tuple | number | true | false | none):i -> i

value = (string | tuple | number | selector | dict | set | true | false | none):v -> v

string = (('"' (escapedChar | ~'"' anything)*:c '"')
         |("'" (escapedChar | ~"'" anything)*:c "'") -> ''.join(c))
escapedChar = '\\' (('"' -> '"')    |('\\' -> '\\')
                   |('/' -> '/')    |('b' -> '\b')
	               |('f' -> '\f')   |('n' -> '\n')
	               |('r' -> '\r')   |('t' -> '\t')
	               |('\'' -> '\'')  )

number = ('-' | -> ''):sign (intPart:ds (floatPart(sign ds) | -> int(sign + ds)))
digit = :x ?(x in '0123456789') -> x
digits = <digit*>
digit1_9 = :x ?(x in '123456789') -> x
intPart = (digit1_9:first digits:rest -> first + rest) | digit
floatPart :sign :ds = <('.' digits exponent?) | exponent>:tail -> float(sign + ds + tail)
exponent = ('e' | 'E') ('+' | '-')? digits

# list = '[' elements:xs ws ','? ws ']' -> list(xs)
tuple = '(' elements:xs ws ','? ws ')' -> tuple(xs)
set = '{' elements:xs ws ','? ws '}' -> set(xs)
elements = (ws value:first (ws ',' ws value)*:rest ws -> [first] + rest) | -> []

immutable_tuple = '(' immutable_elements:xs ws ','? ws ')' -> tuple(xs)
immutable_elements = (ws immutable:first (ws ',' ws immutable)*:rest ws -> [first] + rest) | -> []

true = 'True' -> True
false = 'False' -> False
none = 'None' -> None
"""

try:
    from parsley import makeGrammar
except ImportError:
    MAPPING_PARSER = None
else:
    MAPPING_PARSER = makeGrammar(MAPPING_GRAMMAR, selectors.SELECTORS)

def profile_parse(filename="hst_cos_deadtab.rmap"):
    """Profile the parsing of `filename`, print stats, and instantiate the
    mapping to run the duplicates checking.
    """
    filename = rmap.locate_mapping(filename)
    statsname = os.path.splitext(filename)[0] + ".stats"
    cProfile.runctx('result = MAPPING_PARSER(open("{}").read()).mapping()'.format(filename), 
                    locals(), globals(), statsname)
    pprint.pprint(result)
    stats = pstats.Stats(statsname)
    stats.sort_stats("time")
    stats.print_stats(20)

def check_duplicates(filename="hst_acs_darkfile.rmap"):
    """Parse the specified mapping `filename` and check it for duplicate
    entries which would collide under the standard loader.
    """
    if MAPPING_PARSER:
        log.info("Checking for duplicate entries in", repr(filename))
        filename = rmap.locate_mapping(filename)
        header, selector = MAPPING_PARSER(open(filename).read()).mapping()
        selector.instantiate(header)
        # selector is actually a Parameter object tree.
        # duplicate checking is done as the tree is constructed in selectors.py
    else:
        raise NotImplementedError()

if __name__ == "__main__":
    profile_parse(sys.argv[1])

