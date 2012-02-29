"""Supports accessing CDBS reference and archive catalogs for the purposes
of generating rmaps and comparing CRDS best refs to CDBS best refs.
"""
import sys
import pprint
import cPickle
import random
import getpass
from collections import OrderedDict
import os.path
import datetime

import pyodbc

from crds import rmap, log, utils, timestamp
import crds.hst
import crds.hst.parkeys as parkeys

log.set_verbose(False)

"""  
IPPPSSOOT   ---   dataset naming breakdown

Denotes the instrument type:
J - Advanced Camera for Surveys
U - Wide Field / Planetary Camera 2
V - High Speed Photometer
W - Wide Field / Planetary Camera
X - Faint Object Camera
Y - Faint Object Spectrograph
Z - Goddard High Resolution Spectrograph
E - Reserved for engineering data
F - Fine Guide Sensor (Astrometry)
H-I,M - Reserved for additional instruments
N - Near Infrared Camera Multi Object Spectrograph
O - Space Telescope Imaging Spectrograph
S - Reserved for engineering subset data
T - Reserved for guide star position data
PPP     Denotes the program ID, any combination of letters or numbers
SS    Denotes the observation set ID, any combination of letters or numbers
OO    Denotes the observation ID, any combination of letters or numbers
T    Denotes the source of transmission:
R - Real time (not tape recorded)
T - Tape recorded
M - Merged real time and tape recorded
N - Retransmitted merged real time and tape recorded
O - Retransmitted real time
P - Retransmitted tape recorded
"""

IPPPSSOOT_INSTR = {
    "J" : "acs",
    "U" : "wfpc2",
    "V" : "hsp",
    "W" : "wfpc",
    "X" : "foc",
    "Y" : "fos",
    "Z" : "hrs",
    "E" : "eng",
    "F" : "fgs",
    "I" : "wfc3",
    "N" : "nicmos",
    "O" : "stis",
}

def dataset_to_instrument(dataset):
    instr = dataset[0].upper()
    try:
        return IPPPSSOOT_INSTR[instr]
    except KeyError:
        raise ValueError("Can't determine instrument for dataset " + repr(dataset))

class DB(object):
    def __init__(self, dsn, user, password=None):
        self.dsn = dsn
        self.user = user
        if password is None:
            password = getpass.getpass("password: ")
        self.connection = pyodbc.connect(
            "DSN=%s;Uid=%s;Pwd=%s" % (dsn, user, password))
        self.cursor = self.connection.cursor()

    def __repr__(self):
        return self.__class__.__name__ + "(%s, %s)" % (repr(self.dsn), repr(self.user))

    def execute(self, sql):
        return self.cursor.execute(sql)

    def get_tables(self):
        return [row.table_name for row in self.cursor.tables()]

    def get_columns(self, table):
        return [col.column_name for col in self.cursor.columns(table=table)]

    def make_dicts(self, table, col_list=None, ordered=False, 
                   where="", dataset=None, lowercase=True):
        if dataset is not None:
            all_cols = self.get_columns(table)
            for col in all_cols:
                if "data_set_name" in col:
                    dsname = col
                    break
            where += "where %s='%s'" % (dsname, dataset)

        if col_list is None:
            col_list = self.get_columns(table)
        col_names = ", ".join(col_list)

        for row in self.cursor.execute("select %s from %s %s" % (col_names, table, where)):
            items = zip(col_list, [str(x).lower() for x in row] if lowercase else row)
            kind = OrderedDict if ordered else dict
            yield kind(items)

HERE = os.path.dirname(__file__) or "."

def get_password():
    if not hasattr(get_password, "_password"):
        try:
            get_password._password = open(HERE + "/password").read()
        except:
            get_password._password = getpass.getpass("password: ")
    return get_password._password

def get_dadsops(user="jmiller"):
    """Cache and return a database connection to DADSOPS."""
    if not hasattr(get_dadsops, "_dadsops"):
        get_dadsops._dadsops = DB("DadsopsDsn", user, get_password())
    return get_dadsops._dadsops

def get_reffile_ops(user="jmiller"):
    """Cache and return a database connection to REFFILE_OPS."""
    if not hasattr(get_reffile_ops, "_reffile_ops"):
        get_reffile_ops._reffile_ops = DB("ReffileOpsRepDsn", user, get_password())
    return get_reffile_ops._reffile_ops

def get_instrument_db_parkeys(instrument):
    """Return the union of the database versions of all parkeys for all
    filekinds of instrument.
    """
    dbkeys = set()
    for filekind in parkeys.get_filekinds(instrument):
        dbkeys = dbkeys.union(set(parkeys.get_db_parkeys(instrument, filekind)))
        dbkeys = dbkeys.union(set(parkeys.get_extra_keys(instrument, filekind)))
    return list(dbkeys)

def required_keys(instr):
    """Get both the input parkeys and expected results keywords for
    all filekinds of `instr`ument`.
    """
    pars = get_instrument_db_parkeys(instr)
    pars.append("expstart" if instr != "stis" else "texpstrt")
    pars.append("data_set")
    imap = rmap.get_cached_mapping("hst_%s.imap" % instr)
    pars.extend(imap.selections.keys())
    return pars

def gen_header_tables(datfile="header_tables.dat"):
    """gen_header_tables() generates the mapping: 
    
    { instrument : { best_refs_item : "table.column"  } }
    
    where best_refs_item is nominally the name of a best refs parameter or
    result or other relevant info,  assumed to be a substring of `column`.
    """
    table = {}
    for instr in crds.hst.INSTRUMENTS:
        table[instr] = clean_scan(instr)
    open(datfile, "w+").write(pprint.pformat(table) + "\n")
        
def clean_scan(instr):
    """clean_scan() sorts out the map produced by scan_tables(),  mapping each
    parameter of `instr` to a single "table.column" database location.
    Emits a warning for parameters which are not automatically mapped to the
    database.
    """
    columns, remainder = scan_tables(instr)
    if remainder:
        log.warning("For", repr(instr), "can't locate", sorted(list(remainder)))
    else:
        log.info("Collected", repr(instr), "ok")
    clean = {}
    for var in columns:
        tvar2 = columns[var]
        tvar = []
        for cand in tvar2:
            if "_old" not in cand:
                tvar.append(cand)

        for cand in tvar:
            if "best" in cand:
                tvar = [cand]
                break

        for cand in tvar:
            if "ref_data" in cand and "tv_ref_data" not in cand:
                tvar = [cand]
                break

        for cand in tvar:
            if "science" in cand and "tv_science" not in cand:
                tvar = [cand]
                break

        if len(tvar) == 1:
            clean[var] = tvar[0]
        elif len(tvar) == 2 and "best" in tvar[1] and "best" not in tvar[0]:
            clean[var] = tvar[1]
        else:
            clean[var] = tvar

    return clean

def scan_tables(instr):
    """scan_tables() automatically matches the required parameters for each
    instrument against the available instrument tables and columns in DADSOPS,
    returning a map  { parameter : [ "table.column", ...] } finding plausible
    locations for each CRDS best refs parameter in the dataset catalog.
    """
    dadsops = get_dadsops()
    pars = required_keys(instr)
    columns = {}
    for table in dadsops.get_tables():
        if instr not in table:
            continue
        for par in pars:
            for col in dadsops.get_columns(table):
                if par in col:
                    if par not in columns:
                        columns[par] = []
                    columns[par].append(table + "." + col)
    return columns, set(pars) - set(columns.keys())

"""
SELECT Persons.LastName, Persons.FirstName, Orders.OrderNo
FROM Persons
FULL JOIN Orders
ON Persons.P_Id=Orders.P_Id
ORDER BY Persons.LastName
"""

class HeaderGenerator(object):
    def __init__(self, instrument, header_to_db_map):
        self.h_to_db = header_to_db_map
        self.instrument = instrument.lower()

    @property
    def header_keys(self):
        return [key.upper() for key in self.h_to_db.keys()]

    @property
    def db_columns(self):
        return self.h_to_db.values()

    @property
    def db_tables(self):
        tables = set()
        for column in self.db_columns:
            table, col = column.split(".")
            tables.add(table)
        return list(tables)

    def getter_sql(self, extra_constraints={}):
        sql = "SELECT %s FROM %s " % (", ".join(self.db_columns), 
                                      ", ".join(self.db_tables))
        if len(self.db_tables) >= 2:
            sql += "WHERE %s" % self.join_expr(extra_constraints)
        return sql

    def join_expr(self, extra_constraints={}):
        dadsops = get_dadsops()
        all_cols = []
        for table in self.db_tables:
            all_cols += [table + "." + col for col in dadsops.get_columns(table)]
        clauses = []
        for suffix in ["program_id", "obset_id", "obsnum"]:
            joined = []
            for col in all_cols:
                if col.endswith(suffix):
                    joined.append(col)
            if len(joined) >= 2:
                for more in joined[1:]:
                    clauses.append(joined[0] + "=" + more)
        for key in extra_constraints:
            for col in all_cols:
                if key.lower() in col:
                    break
            else:
                raise ValueError("No db column found for constraint " + repr(key))
            clauses.append(col + "=" + repr(extra_constraints[key]))
        return (" and ").join(clauses)

    def get_headers(self, extra_constraints={}):
        dadsops = get_dadsops()
        sql = self.getter_sql(extra_constraints)
        for dataset in dadsops.execute(sql):
            hdr = dict(zip(self.header_keys, [utils.condition_value(x) for x in dataset]))
            self.fix_time(hdr)
            hdr["INSTRUME"] = self.instrument
            yield hdr

    def fix_time(self, hdr):
        expstart = hdr.get("EXPSTART", hdr.get("TEXPSTRT"))
        try:
            hdr["DATE-OBS"], hdr["TIME-OBS"] = timestamp.format_date(expstart).split()
        except:
            log.warning("Bad database EXPSTART", expstart)

try:
    HEADER_MAP = eval(open("header_tables.dat").read())

    HEADER_GENERATORS = {}
    for instr in HEADER_MAP:
        HEADER_GENERATORS[instr] = HeaderGenerator(instr, HEADER_MAP[instr])
except:
    log.error("Failed loading 'header_tables.dat'")


def get_dataset_header(dataset):
    """Get the header for a particular dataset,  nominally in a context where
    one only cares about a small list of specific datasets.
    """
    instrument = dataset_to_instrument(dataset)
    try:
        igen = HEADER_GENERATORS[instrument]
        headers = list(igen.get_headers({"DATA_SET":dataset.upper()}))
    except Exception, exc:
        raise RuntimeError("Error accessing DADSOPS for dataset" + repr(dataset) + ":" + str(exc))
    if len(headers) == 1:
        return headers[0]
    elif len(headers) == 0:
        raise LookupError("No header found for " + repr(instrument) + " dataset " + repr(dataset))
    elif len(headers) > 1:
        raise LookupError("More than one header found for " + repr(instrument) + " dataset " + repr(dataset))

def test(header_generator, ncases=None, context="hst.pmap", dataset=None, 
         ignore=[], include=[], dump_header=False, verbose=False):
    """Evaluate the first `ncases` best references cases from 
    `header_generator` against similar results attained from CRDS running
    on pipeline `context`.
    """
    log.reset()
    if header_generator in crds.hst.INSTRUMENTS:
        headers = HEADER_GENERATORS[instr].get_headers()
    elif isinstance(header_generator, str): 
        if header_generator.endswith(".pkl"):
            headers = cPickle.load(open(header_generator))
        else:
            headers = eval(open(header_generator).read())
    else:
        raise ValueError("header_generator should name an instrument, pickle, or eval file.")

    count = 0
    mismatched = {}
    oldv = log.get_verbose()
    if verbose:
        log.set_verbose(verbose)

    start = datetime.datetime.now()

    for header in headers:
        if ncases is not None and count >= ncases:
            break
        count += 1
        if dataset is not None:
            if dataset != header["DATA_SET"]:
                continue
            log.set_verbose(True)
        if dump_header:
            pprint.pprint(header)
            continue
        if log.get_verbose():
            log.verbose("="*70)
            log.verbose("DATA_SET:", header["DATA_SET"])
        crds_refs = rmap.get_best_references(context, header, include)
        compare_results(header, crds_refs, mismatched, ignore)

    # by usage convention all headers share the same instrument
    instrument = header["INSTRUME"]

    elapsed = datetime.datetime.now() - start
    log.write()
    log.write()
    for filekind in mismatched:
        log.write(filekind, "mismatched:", mismatched[filekind])
    log.write()
    log.write(instrument, count, "datasets")
    log.write(instrument, elapsed, "elapsed")
    log.write(instrument, count/elapsed.total_seconds(), "best refs / sec")
    log.write()
    log.standard_status()
    log.set_verbose(oldv)

def compare_results(header, crds_refs, mismatched, ignore):
    """Compare the old best ref recommendations in `header` to those 
    in `crds_refs`,  recording a list of error tuples by filekind in
    dictionary `mismatched`.  Disregard any filekind listed in `ignore`.
    """
    mismatches = 0
    for filekind in crds_refs:
        if filekind in ignore:
            continue
        if filekind not in mismatched:
            mismatched[filekind] = {}
        try:
            old = header[filekind.upper()].lower()
        except:
            log.verbose_warning("No comparison for", repr(filekind))
            sys.exc_clear()
            continue
        new = crds_refs[filekind]
        if old in ["n/a", "*", "none"] or new == "NOT FOUND n/a":
            log.verbose("Ignoring", repr(filekind), "as n/a")
            continue
        if old != new:
            dataset = header["DATA_SET"]
            instr = header["INSTRUME"]
            if not mismatches:
                log.verbose("dataset", dataset, "...", "ERROR")
            mismatches += 1
            log.error("mismatch:", dataset, instr, filekind, old, new)
            if (old, new) not in mismatched[filekind]:
                mismatched[filekind][(old,new)] = 0
            mismatched[filekind][(old,new)] += 1
        else:
            log.verbose("CDBS/CRDS matched:", filekind, old)
    if not mismatches:
        log.write(".", eol="", sep="")

def testall(ncases=10**10, context="hst.pmap", instruments=None, 
            suffix="_headers.pkl"):
    if instruments is None:
        pmap = rmap.get_cached_mapping(context)
        instruments = pmap.selections
    for instr in instruments:
        log.write(70*"=")
        log.write("instrument", instr + ":")
        test(instr+suffix, ncases, context)
        log.write()

def dump(instr, ncases=10**10, random_samples=True, suffix="_headers.pkl"):
    """Store `ncases` header records taken from DADSOPS for `instr`ument in 
    a pickle file,  optionally sampling randomly from all headers.
    """
    samples = []
    headers = list(HEADER_GENERATORS[instr].get_headers())
    while len(samples) < ncases and headers:
        selected = int(random.random()*len(headers)) if random_samples else 0
        samples.append(headers.pop(selected))
    cPickle.dump(samples, open(instr + suffix, "w+"))


def dumpall(context="hst.pmap", ncases=10**10, random_samples=True, 
            suffix="_headers.pkl"):
    """Generate header pickles for all instruments referred to by `context`,
    where the headers are taken from the DADSOPS database.   Optionally collect
    only `ncases` samples taken randomly accoring to the `random_samples` flag.
    """
    pmap = rmap.get_cached_mapping(context)
    for instr in pmap.selections.keys():
        log.info("collecting", repr(instr))
        dump(instr, ncases, random_samples, suffix)


def main():
    if sys.argv[1] == "dumpall":
        dumpall()
    elif sys.argv[1] == "testall":
        testall()
    else:
        print "usage: python cdbs_db.py [ dumpall | testall ]"
        sys.exit(-1)

if __name__ == "__main__":
    main()
