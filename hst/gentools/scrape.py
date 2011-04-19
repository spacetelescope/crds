"""scrape.py is a crude tool for scraping tables from the CDBS reference file web pages,
rearranging it as simplified XML,  and saving it.   Downstream stages can then process
the XML into CRDS reference file maps.
"""
import sys
import os.path
import argparse
import urllib2
import xml.sax.saxutils as sax
import re

from BeautifulSoup import BeautifulSoup, Comment

import crds.hst.gentools.ezxml as ez
from crds import log

# URL = "http://www.stsci.edu/hst/observatory/cdbs/SIfileInfo/ACS/reftablequeryindex"
# URL = "http://www.stsci.edu/hst/observatory/cdbs/SIfileInfo/ACS/HRCBiasReference"

# ==========================================================================================

def dump_tables(url, saveroot, selected_tables="all"):
    """Dump the `selected_tables` found at `url` out to `saveroot`.xml"""
    flat_rows = get_xml_from_cached_url(url, saveroot + ".html", selected_tables)
    xml_file = open(saveroot + ".xml", "w+")
    xml_file.write(flat_rows)
    xml_file.close()

def get_xml_from_cached_url(url, savename, selected_tables="all"):
    """Dump the tables in `url`.  Return as flattened XML with one table row per line.
    If `savename` already exists,  treat it as a cache (possibly hand edited) and
    use that rather than reading from `url`.
    """
    page = get_cached_page(url, savename)
    flat_rows = page_to_flat_xml(page, url, selected_tables)
    return flat_rows

def get_cached_page(url, savename):
    """If file `savename` already exists,  return the contents.  Otherwise,
    fetch the contents of `url` and cache them in file `savename`.   This kludge
    facilitates editing bad raw HTML prior to doing XML processing.
    """
    if not os.path.exists(savename):
        page = urllib2.urlopen(url).read()
        open(savename, "w").write(page)
    else:
        page = open(savename).read()
    return page

def page_to_flat_xml(html, url, selected_tables="all"):
    """Given a page of HTML,  simplify it and flatten it so that table rows appear
    on a single line.  Return the result as XML.  `url` indicates where `html` page
    came from and is used to convert relative URLs to absolute ones in the resulting
    XML.
    """
    soup = BeautifulSoup(html)
    soup = cleanup_soup(soup)
    xmlstr = get_xml(soup, url, selected_tables)
    flat_rows = flatten_rows(xmlstr)
    return flat_rows

# ==========================================================================================

def cleanup_soup(soup):
    """Delete presentation attributes, embedded newlines, comments, etc."""
    # I hate doing this, but HTML comments often cause problems in
    # XML... else I wouldn't have known or bothered.
    remove_comments(soup)
    # presentation attributes account for most of the clutter in html
    remove_formatting_and_encode(soup)
    # XML preserves line breaks in the middle of strings.  Ditch those.
    remove_eol(soup)
    sanitize_hrefs(soup)
    soup = replace_tag(soup, "strong", open="**", close="**")
    soup = replace_tag(soup, "br", open= " ")
    soup = replace_tag(soup, "font", open=" ", close=" ")
    return soup


def killattr(item, attr):
    try:
        del item[attr]
    except KeyError:
        pass

def remove_formatting_and_encode(t):
    if isinstance(t, (str, unicode)):
        t.replaceWith(sax.escape(t))
    else:
        for attr in ["class","style","width","height","border",
                     "rowspan", "colspan",
                     "align", "halign", "valign",
                     "cellpadding", "cellspacing",
                     "bgcolor", "fgcolor", "color",
                     "vspace", "hspace", "nowrap"]:
            killattr(t, attr)
        for x in t.contents:
            remove_formatting_and_encode(x)

def remove_comments(t):
    comments = t.findAll(text=lambda text:isinstance(text, Comment))
    for comment in comments:
        comment.extract()

def remove_eol(t):
    for s in t.findAll(text="\n"):
        s.replaceWith(" ")

def replace_tag(t, tag, open="", close=""):
    for s in t.findAll(tag):
        s.replaceWith(BeautifulSoup(open + " ".join([str(i) for i in s.contents]) + close))
    return BeautifulSoup(str(t))

def sanitize_hrefs(soup):
    changes = False
    for a in soup.findAll("a", href=re.compile(".*")):
        newval = sax.escape(a["href"])
        if newval != a["href"]:
            # log.info("replacing", repr(a["href"]),"with", repr(newval))
            a["href"] = newval
            changes = True
    return changes

# ==========================================================================================

def get_xml(soup, url, selected_tables="all"):
    """Try to write out `soup` as XML rooted as <document> and containing
    a <url> element to give relative URLs context.  Only extract <table> elements
    and their contents,  ignoring the rest.   If selected_tables is "all",  extract
    all tables.  Otherwise,  only extract tables listed in `selected_tables` where
    numbers are the from enumeration of HTML tables.
    """
    xml = "<document>\n"
    xml += "<url>" + url + "</url>\n"
    for i, t in enumerate(soup.findAll("table")):
        if (selected_tables == "all") or (i in selected_tables):
            xml += str(t)
    xml += "</document>\n"
    return hack_out_lame_html_ampersands(xml)

def hack_out_lame_html_ampersands(xml):
    xml2 = xml.replace("&amp;nbsp;"," ")
    xml2 = xml2.replace("&amp;lang=en"," ")
    return xml2

def get_url(xml_str):
    """Fetch the source URL from XML produced by get_xml.
    """
    x = ezxml.from_string(xml_str)
    for e in x:
        if e.name == "url":
            return e[0]
    raise ValueError("URL element not found.")

# ==========================================================================================

def flatten_rows(xml_str):
    x = ezxml.from_string(xml_str)
    for table in x:
        for row in table:
            fix_whitespace(row)
    return str(x)

def fix_whitespace(e):
    if isinstance(e, (str, unicode)):
        return e.strip().replace("\n"," ")
    else:
        e.indent = ""
        e.eol = ""
        for f in e:
            fix_whitespace(f)


# ==========================================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Scrape the specified tables from an HTML file and re-emit as XML,  one table row per line.')
    parser.add_argument('URL', help='URL or file of HTML to scrape.')
    parser.add_argument('saveroot', help='Prefix of filename for .html and .xml results.')
    parser.add_argument('-t', '--table_numbers', dest='table_numbers', metavar='N', type=int, nargs='*',
        help='Which tables should be extracted,  numbered in order of appearance.  Specifying [] equivalent to "all".')
    args = parser.parse_args()
    dump_tables(args.URL, args.saveroot, args.table_numbers or "all")

# ==========================================================================================

if __name__ == "__main__":
    main()

