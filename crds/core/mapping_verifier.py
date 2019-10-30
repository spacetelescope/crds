"""Defines and instantiates MAPPING_VERIFIER which is used to load Mappings and
restrict the allowable Python constructs to the declarative forms permissible
in rmaps.  Verfication is part of basic checking which is executed whenever and
Mapping is loaded, and is non-recursive.
"""
import ast
import sys

from . import exceptions as crexc
from . import selectors

# ===================================================================

class AstDumper(ast.NodeVisitor):
    """Debug class for dumping out rmap ASTs."""
    def visit(self, node):
        print(ast.dump(node), "\n")
        ast.NodeVisitor.visit(self, node)

    def dump(self, node):
        """Recursively print the names of AST `node`,  one per line."""
        print(ast.dump(node), "\n")
        self.generic_visit(node)

    visit_Assign = dump
    visit_Call = dump

ILLEGAL_NODES = {
    "visit_FunctionDef",
    "visit_ClassDef",
    "visit_Return",
    "visit_Yield",
    "visit_Delete",
    "visit_AugAssign",
    "visit_Print",
    "visit_For",
    "visit_While",
    "visit_If",
    "visit_With",
    "visit_Raise",
    "visit_TryExcept",
    "visit_TryFinally",
    "visit_Assert",
    "visit_Import",
    "visit_ImportFrom",
    "visit_Exec",
    "visit_Global",
    "visit_Pass",
    "visit_Repr",
    "visit_Lambda",
    "visit_Attribute",
    "visit_Subscript",
    "visit_Set",
    "visit_ListComp",
    "visit_SetComp",
    "visit_DictComp",
    "visit_GeneratorExp",
    "visit_Repr",
    "visit_AugLoad",
    "visit_AugStore",
    }

LEGAL_NODES = {
    'visit_Module',
    'visit_Name',
    'visit_Str',
    'visit_Load',
    'visit_Store',
    'visit_Tuple',
    'visit_List',
    'visit_Dict',
    'visit_Num',
    'visit_Expr',
    'visit_And',
    'visit_Or',
    'visit_In',
    'visit_Eq',
    'visit_NotIn',
    'visit_NotEq',
    'visit_Gt',
    'visit_GtE',
    'visit_Lt',
    'visit_LtE',
    'visit_Compare',
    'visit_IfExp',
    'visit_BoolOp',
    'visit_BinOp',
    'visit_UnaryOp',
    'visit_Not',
    'visit_NameConstant',
    'visit_USub',
    'visit_Constant',
}

CUSTOMIZED_NODES = {
    'visit_Call',
    'visit_Assign',
    'visit_Illegal',
    'visit_Unknown',
}

ALL_CATEGORIZED_NODES = set.union(ILLEGAL_NODES, LEGAL_NODES, CUSTOMIZED_NODES)

class MappingVerifier(ast.NodeVisitor):
    """MappingVerifier visits the parse tree of a CRDS mapping file and
    raises exceptions for invalid constructs.   MappingVerifier is concerned
    with limiting rmaps to safe code,  not deep semantic checks.
    """
    def __init__(self, *args, **keys):
        super(MappingVerifier, self).__init__(*args, **keys)

        # assert not set(self.LEGAL_NODES).intersection(self.ILLEGAL_NODES), "MappingVerifier config error."
        for attr in LEGAL_NODES:
            setattr(self, attr, self.generic_visit)
        for attr in ILLEGAL_NODES:
            setattr(self, attr, self.visit_Illegal)

    def compile_and_check(self, text, source="<ast>", mode="exec"):
        """Parse `text` to verify that it's a legal mapping, and return a
        compiled code object.
        """
        if sys.version_info >= (2, 7, 0):
            self.visit(ast.parse(text))
        return compile(text, source, mode)

    def __getattribute__(self, attr):
        if attr.startswith("visit_"):
            if attr in ALL_CATEGORIZED_NODES:
                rval = ast.NodeVisitor.__getattribute__(self, attr)
            else:
                rval = ast.NodeVisitor.__getattribute__(self, "visit_Unknown")
        else:
            rval = ast.NodeVisitor.__getattribute__(self, attr)
        return rval

    @classmethod
    def assert_(cls, node, flag, message):
        """Raise an appropriate MappingFormatError exception based on `node`
        and `message` if `flag` is False.
        """
        if not flag:
            if hasattr(node, "lineno"):
                raise crexc.MappingFormatError(message + " at line " + str(node.lineno))
            else:
                raise crexc.MappingFormatError(message)

    def visit_Illegal(self, node):
        """Handle explicitly forbidden node types."""
        self.assert_(node, False, "Illegal statement or expression in mapping " + repr(node))

    def visit_Unknown(self, node):
        """Handle new / unforseen node types."""
        self.assert_(node, False, "Unknown node type in mapping " + repr(node))

#     def generic_visit(self, node):
#         # print "generic_visit", repr(node)
#         return super(MappingVerifier, self).generic_visit(node)

    def visit_Assign(self, node):
        """Screen assignments to limit to a subset of legal assignments."""
        self.assert_(node, len(node.targets) == 1,
                     "Invalid 'header' or 'selector' definition")
        self.assert_(node, isinstance(node.targets[0], ast.Name),
                     "Invalid 'header' or 'selector' definition")
        self.assert_(node, node.targets[0].id in ["header","selector","comment"],
                     "Only define 'header' or 'selector' or 'comment' sections")
        self.assert_(node, isinstance(node.value, (ast.Call, ast.Dict, ast.Str)),
                     "Section value must be a selector call or dictionary or string")
        self.generic_visit(node)

    def visit_Call(self, node):
        """Screen calls to limit to a subset of legal calls."""
        self.assert_(node, node.func.id in selectors.SELECTORS,
                     "Selector " + repr(node.func.id) + " is not one of supported Selectors: " +
                     repr(sorted(selectors.SELECTORS.keys())))
        self.generic_visit(node)

MAPPING_VERIFIER = MappingVerifier()
