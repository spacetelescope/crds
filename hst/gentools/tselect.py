"""tselect.py is used to flatten a table hierarchy and to choose from among the flattened tables
those which should be retained.  tselect is used to munge away page layout tables and reduce HTML
to solely it's data content devoid of navigation bars, etc.   This was used to clean up NICMOS
HTML.

% python tselect.py nicmos_darkfile_0.xml  5

Selects non-table XML and the 5th table from the promoted table sequence.

"""
import sys

import crds.hst.gentools.scrape as scrape
import crds.hst.gentools.ezxml as ezxml

def select_tables(xmlstr, indices=[]):
    """Select_tables processes the tables in xmlstr,  replacing parent tables with any nested child tables.
    After "promoting" child tables in this fashion,  select_tables returns only non-table XML or those
    promoted tables enumerated in `indices`.
    """
    xml = ezxml.from_string(xmlstr)
    flatter = promote_nested_tables(xml)
    final = keep_selected_tables(xml, indices)
    tidy = scrape.flatten_rows(str(final))
    return tidy

def keep_selected_tables(xml, indices):
    """Iterate over `xml`,  keeping subelements which are not tables or are
    the enumerated in `indices`.
    """
    table = 1
    results = []
    for f in xml:
        if f.name == "table":
            if table in indices:
                results.append(f)
            table += 1
        else:
            results.append(f)
    return ezxml.Xml(xml.name, elements=results)

def _contains_table(xml):
    """Called directly on a <table>,  returns True.  Also True for nested <table>."""
    if isinstance(xml, (str, unicode)):
        return False
    elif xml.name == "table":
        return True
    else:
        for e in xml:
            if _contains_table(e):
                return True
        return False

def contains_nested_table(xml):
    """Called directly on a <table>,  returns False.  Returns True for nested <table>."""
    if isinstance(xml, (str, unicode)):
        return False
    else:
        for e in xml:
            if _contains_table(e):
                return True
        return False

def promote_nested_tables(xml):
    """Tables which contain other tables are replaced by their nested tables.  Strings or
    elements which don't contain nested tables are passed through unaltered.   The net
    effect is a flattening of any table hierarchy in `xml` and the elimination of parent
    tables.
    """
    if isinstance(xml, (str, unicode)) or not contains_nested_table(xml):
        return xml
    else:
        results = []
        for e in xml:
            if contains_nested_table(e):
                results.extend(promote_nested_tables(e))
            else:
                results.append(e)
        return ezxml.Xml(xml.name, elements=results)

def main():
    if len(sys.argv) > 1:
        selected = [int(x) for x in sys.argv[2].split(",")]
    else:
        selected = []
    xmlstr = open(sys.argv[1]).read()
    print select_tables(xmlstr, selected)

if __name__ == "__main__":
    main()
