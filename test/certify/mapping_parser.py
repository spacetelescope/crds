"""This module uses the package Parsley to parse CRDS mappings into a
header dictionary and a Selector Parameters object tree.  Selector
Parameters are uninstantiated Selectors which are first built up from
the mapping file.  Since the parser captures full item lists, with no
removal of duplicate keys, the results can be used to detect duplicate
dictionary entries which normally collide silently eliminating one
item.  This is principally intended to detect rmap cut-and-paste
errors in hand edited rmaps.
"""
from collections import namedtuple

from crds.core import rmap, selectors, log, exceptions, config

# NOTE:  #-comments are treated as white space and currently dropped when an rmap is rewritten
# as a new version.

MAPPING_GRAMMAR = r"""

ws = (' ' | '\r' | '\n' | '\t' | pound_comment)*

pound_comment = '#' (~'\n' anything)*:c '\n' -> ''.join(c)

mapping = header_section:h comment_section:c selector_section:s -> (h, s, c)

header_section = ws 'header' ws '=' ws dict:d ws -> d

comment_section = ((ws 'comment' ws '=' ws block_string:c ws -> c)
                  | -> None)
selector_section = ws 'selector' ws '=' ws selector:s ws -> s

selector = ( dict | parameters ):d -> d
parameters = ws parameters_name:n ws '(' ws dict:d ws ')' -> eval(n, globals(), locals())(d)
parameters_name = ('Match' | 'UseAfter' | 'VersionAfter' | 'SelectVersion' | 'Bracket' | 'GeometricallyNearest' | 'ClosestTime'):n -> n

# NOTE:  dict is returned as an item-list to preserve duplicates (considered errors)
dict = ws '{' items:m '}' ws -> m
items = ws (pair:first (ws ',' pair)*:rest ws ','? ws -> [first] + rest) | ws -> []
pair = ws immutable:k ws ':' ws value:v ws -> (k, v)
immutable = (string | immutable_tuple | number | true | false | none):i -> i

value = (string | tuple | number | selector | dict | set | true | false | none):v -> v

string = (('"' (escapedChar | ~'"' anything)*:c '"')
         |("'" (escapedChar | ~"'" anything)*:c "'") -> ''.join(c))

block_string = (('\"\"\"' (escapedChar | ~'\"\"\"' anything)*:c '\"\"\"')
               |("\'\'\'" (escapedChar | ~"\'\'\'" anything)*:c "\'\'\'")) -> ''.join(c)

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
    import parsley
except ImportError:
    parsley = None

MAPPING_PARSER = None

'''
def profile_parse(filename="hst_cos_deadtab.rmap"):
    """Profile the parsing of `filename`, print stats, and instantiate the
    mapping to run the duplicates checking.
    """
    import cProfile
    import pstats
    filename = config.locate_mapping(filename)
    statsname = os.path.splitext(filename)[0] + ".stats"
    cProfile.runctx('result = MAPPING_PARSER(open("{}").read()).mapping()'.format(filename),
                    locals(), globals(), statsname)
    stats = pstats.Stats(statsname)
    stats.sort_stats("time")
    stats.print_stats(20)
'''

Parsing = namedtuple("Parsing", "header,selector,comment")

def parse_mapping(filename):
    """Parse mapping `filename`.   Return parsing."""
    global parsley, MAPPING_PARSER

    if parsley is None:
        raise NotImplementedError("Parsley parsing package must be installed.")

    if MAPPING_PARSER is None:
        MAPPING_PARSER = parsley.makeGrammar(MAPPING_GRAMMAR, selectors.SELECTORS)

    log.verbose("Parsing", repr(filename))
    filename = config.locate_mapping(filename)
    with log.augment_exception("Parsing error in", repr(filename), exception_class=exceptions.MappingFormatError):
        with open(filename) as pfile:
            parser = MAPPING_PARSER(pfile.read())
            header, selector, comment = parser.mapping()
            return Parsing(header, selector, comment)

def check_duplicates(parsing):
    """Examine mapping `parsing` from parse_mapping() for duplicate header or selector entries."""
    if isinstance(parsing.selector, selectors.Parameters):
        parsing.selector.instantiate(parsing.header)
    else:
        selectors.check_duplicates(parsing.header, ["header"])
        selectors.check_duplicates(parsing.selector, ["selector"])
