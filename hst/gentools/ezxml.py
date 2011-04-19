"""Manipulates a useful subset of XML in a straightforward manner.

Created in Python,  ezxml is a little awkward:

>>> x = Xml("Something", attributes={"this":"that"},
...         elements = [Xml("Nested"),XmlText("this"),Xml("Foo")])

But Xml objects print simply with decent default formatting:

>>> print x
<Something this="that">
    <Nested/>
    this
    <Foo/>
</Something>

Attributes are accessed as string-keyed-items:

>>> x["this"]
'that'

Sub-elements are accessed using the sequence protocol:

>>> for s in x:  print s
<Nested/>
this
<Foo/>

>>> print x[0]
<Nested/>

Element sub-nodes are Xml class objects, but text nodes are
simple Python strings:

>>> print repr(x[0])
Xml(name='Nested', attrs=[],  elements=[])

>>> print x[1]
this

There are from_string() and from_file() functions which construct
Xml instances from existing strings or files of XML:

>>> x = from_string("<fancy>here it is</fancy>")
>>> x
Xml(name='fancy', attrs=[],  elements=[])

from_string() and from_file() are lossy with respect to indentation
and newlines which it controls via the indent and eol parameters.

The name of an Xml object is visible in it's name attribute:

>>> x.name
'fancy'

String nodes are return as simple strings or unicode:

>>> x[0]
'here it is'

Note that Xml objects have Python attributes,  such as "name",  but
can also have XML attributes,  which could also include "name".   So
it's possible for an Xml object to have both x.name and x["name"]
and these are different things.
"""
import re
import xml.dom
import xml.dom.minidom as minidom
from xml.sax import saxutils

# ==========================================================================

DEFAULT_INDENT = " "*4
DEFAULT_EOL = "\n"

def from_string(xml_str, eol=DEFAULT_EOL, indent=DEFAULT_INDENT,
                preserve_unicode=False, del_whitespace=True, del_comments=True):
    """Converts a string of XML into an ezxml.Xml object.
    """
    dom = minidom.parseString(xml_str)
    return _dom_to_xml(dom, eol=eol, indent=indent,
                       preserve_unicode=preserve_unicode,
                       del_whitespace=del_whitespace,
                       del_comments=del_comments)

# ==========================================================================

def from_file(fname, eol=DEFAULT_EOL, indent=DEFAULT_INDENT,
              preserve_unicode=False, del_whitespace=True, del_comments=True):
    """Converts XML in file 'f' to an Xml object."""
    if isinstance(fname, str):
        the_file = open(fname, "r")
    else:
        the_file = fname
    return from_string(the_file.read(), eol=eol, indent=indent,
                       preserve_unicode=preserve_unicode,
                       del_whitespace=del_whitespace,
                       del_comments=del_comments)

# ==========================================================================

def dict_to_xml(rootname, dictionary, eol=DEFAULT_EOL, indent=DEFAULT_INDENT):
    """Converts `dictionary` into a tree of Xml elements rooted as
    `rootname`.  Each key becomes a new Xml element.  Nested
    dictionaries are recursively converted to Xml.  String values are
    not converted.  Note that any dictionary consisting of strings and
    nested dictionaries can be converted to this form of XML.
    However, not all XML can be converted to this dictionary format.
    Xml trees can be converted to strings with str().
    """
    elements = []
    for key, value in dictionary.items():
        if isinstance(value, dict):
            elem = dict_to_xml(key, value, eol=eol, indent=indent)
        elif isinstance(value, unicode):
            elem = Xml(key, elements=[value], eol="")
        else:
            elem = Xml(key, elements=[str(value)], eol="")
        elements.append(elem)
    return Xml(rootname, elements=elements, eol=eol, indent=indent)

# ==========================================================================

def _node_to_element(node, eol, indent, preserve_unicode,
                     del_whitespace, del_comments):
    """Convert DOM `node` into an Xml object."""
    name = str(node.nodeName)
    attrs = []
    anames = []
    if node.attributes is not None:
        for attr, val  in node.attributes.items():
            if not preserve_unicode:
                attr = str(attr)
                val = str(val)
            if attr in anames:
                raise ValueError("Attribute " + repr(attr) +
                                 " appears more than once.")
            attrs.append((attr, val))
            anames.append(attr)
    elems = []
    if node.hasChildNodes():
        for child_node in node.childNodes:
            child_xml = _node_to_xml(child_node, eol, indent,
                                     preserve_unicode,
                                     del_whitespace,
                                     del_comments)
            if child_xml is not None:
                elems.append(child_xml)
    return Xml(name, dict(attrs), elems, indent=indent, eol=eol)


# ELEMENT_NODE,
# ATTRIBUTE_NODE,
# TEXT_NODE,
# CDATA_SECTION_NODE,
# ENTITY_NODE,
# PROCESSING_INSTRUCTION_NODE,
# COMMENT_NODE,
# DOCUMENT_NODE,
# DOCUMENT_TYPE_NODE,
# NOTATION_NODE

def _node_to_xml(node, eol, indent, preserve_unicode,
                 delete_whitespace, delete_comments):
    """Converts a minidom.Node instance into an ezxml.Xml instance.
    """
    if node.nodeType == xml.dom.Node.ELEMENT_NODE:
        return _node_to_element(node, eol, indent, preserve_unicode,
                                delete_whitespace, delete_comments)
    elif node.nodeType == xml.dom.Node.COMMENT_NODE:
        if not delete_comments:
            return XmlComment(node.nodeValue)
        else:
            return None
    elif node.nodeType == xml.dom.Node.TEXT_NODE:
        if node.nodeValue:
            result = node.nodeValue
            if delete_whitespace:
                result = result.strip().replace("\n", " ")
                if not result:
                    return None
            if preserve_unicode:
                return result
            else:
                return str(result)
        else:
            return None
    else:
        raise NotImplementedError("Unimplemented node type.")

def _dom_to_xml(dom, eol, indent, preserve_unicode,
                del_whitespace, del_comments):
    """Convert dom document to an Xml object of the contents."""
    return _node_to_xml(dom.childNodes[0], eol, indent, preserve_unicode,
                        del_whitespace, del_comments)

# ==========================================================================

class XmlNode(object):
    """Abstract baseclass for tree of XML nodes."""
    def __str__(self):
        raise NotImplementedError("XmlNode is an abstract baseclass.")

class XmlComment(XmlNode):
    """Node representing commented out XML <!-- ... -->"""
    def __init__(self, comment):
        XmlNode.__init__(self)
        self.name = "#comment"
        self._comment = comment

    def __str__(self):
        return "<!-- " + self._comment + " -->"

class XmlText(XmlNode):
    """Node representing content between <elements>"""
    def __init__(self, text):
        XmlNode.__init__(self)
        self.name = "#text"
        self._text = text

    def __str__(self):
        return saxutils.escape(self._text)

# ==========================================================================

_NAME_PATTERN = re.compile("[a-zA-Z0-9_]+[a-zA-Z0-9_\-\.]*")

class Xml(XmlNode):
    """Node representing and XML <element>"""
    def __init__(self, name, attributes=None, elements=None,
                 indent=DEFAULT_INDENT, eol=DEFAULT_EOL):
        XmlNode.__init__(self)
        if attributes is None:
            attributes = {}
        if elements is None:
            elements = []
        self.name        = name
        self.indent     = indent
        self.eol        = eol
        self.attributes = dict() # for now
        self.elements   = []
        for name, value in attributes.items():
            assert self._legal_attribute(name, value), "illegal Xml attribute"
            assert name not in self.attributes, "duplicate Xml attribute"
            self.attributes[name] = value
        for elem in elements:
            assert self._legal_value(elem),  "illegal Xml element"
        self.elements = elements[:]

    def __repr__(self):
        return "Xml(name='%s', attrs=%s,  elements=%s)" % \
               (self.name,
                [attr for attr in self.attributes],
                [elem.name for elem in self.elements if isinstance(elem, XmlNode)])

    @classmethod
    def _legal_attribute(cls, name, value):
        """Return True IFF `name` and `value` work as an Xml attribute."""
        return cls._legal_name(name) and \
            isinstance(value, (str, unicode, int, float, bool, long))

    @classmethod
    def _legal_name(cls, key):
        """Return True iff key is a legal attribute or element name."""
        if not isinstance(key, (str, unicode)):
            return False
        if _NAME_PATTERN.match(key) is None:
            return False
        return True

    @classmethod
    def _legal_value(cls, value):
        """Return True IFF `value` works as an Xml element value."""
        return isinstance(value, (XmlNode, str, unicode))

    def _indent_string(self, s):
        """Returns a multiline string `s` with each line indented
        with by self.indent
        """
        if not self.eol:
            return s
        lines = []
        for line in s.split(self.eol):
            lines.append(self.indent+line)
        return self.eol.join(lines)

    def __len__(self):
        return len(self.elements)

    def first(self, name, default=None):
        """Returns the first element named `name`.
        """
        for elem in self.elements:
            if elem.name == name:
                return elem
        if default is None:
            raise KeyError("Element name not found: ", repr(name))
        else:
            return default

    def all(self, name):
        """Generates all the elements named `name`.
        """
        for elem in self.elements:
            if elem.name == name:
                yield elem

    def has(self, name):
        """Returns TRUE iff this Xml has an element named `name`"""
        for elem in self.elements:
            if elem.name == name:
                return True
        else:
            return False


    def __getitem__(self, index):
        if isinstance(index, (str, unicode)):
            return self.attributes[index]
        else:
            return self.elements[index]

    def __setitem__(self, index, value):
        if isinstance(index, (str, unicode)):
            self.attributes[index] = value
        else:
            self.elements[index] = value

    def __delitem__(self, index):
        if isinstance(index, (str, unicode)):
            del self.attributes[index]
        else:
            del self.elements[index]

    def __str__(self):
        attrs = []
        for attr in self.attributes:
            attrs.append('%s="%s"' % (attr, saxutils.escape(self.attributes[attr])))
        if len(attrs):
            attrstr = " " + " ".join(attrs)
        else:
            attrstr = ""
        if not len(self.elements):
            return "<%s%s/>" % (self.name, attrstr)
        else:
            elems = []
            for elem in self.elements:
                if isinstance(elem, XmlNode):
                    val = str(elem)
                else:
                    val = saxutils.escape(str(elem))  # BUG unicode
                elems.append(val)
            elemstr = self.eol.join(elems)
            if self.indent != "":
                elemstr = self._indent_string(elemstr)
            if self.eol != "":
                elemstr = self.eol + elemstr + self.eol
            return "<%s%s>%s</%s>" % (self.name, attrstr, elemstr, self.name)

# ==========================================================================

def test():
    """Runs the module doctests.  Returns (error, tests run) tuple."""
    import doctest, ezxml
    return doctest.testmod(ezxml, optionflags=doctest.NORMALIZE_WHITESPACE)

# ==========================================================================

if __name__ == "__main__":
    print test()

