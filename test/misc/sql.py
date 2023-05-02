"""This module defines a command line tool for executing SQL queries on downloaded versions of
the CRDS catalog database.  It is a wrapper around a sqlite3 database download service and the
sqlite3 command line program which can be used to query  it.
"""
import sys
import os
import os.path
import sqlite3

from crds.core import log, cmdline, config
from crds.client import api

# ===================================================================

class CrdsSqlQueryScript(cmdline.Script):
    """Command line script for querying a downloaded copy of the CRDS catalog using sqlite3."""

    description = """crds.misc.sql is a thin wrapper around sqlite3 operating on a downloaded copy of
    the crds catalog or context history.   It is capable of doing basic select queries.    Fully general
    queries can be run under the external sqlite3 program operating on the dowloaded CRDS catalog
    sqlite3 database file.
"""

    epilog = """
* Dumping the table names supported can be done as follows:

crds sql --list-tables
crds_hst_catalog
crds_hst_context_history

* Dumping the columns of a table can be done as follows:

crds sql --list-columns
id, name, blob, state, blacklisted, rejected, observatory, instrument, filekind, type, derived_from, sha1sum, delivery_date, activation_date, useafter_date, change_level, pedigree, reference_file_type, size, uploaded_as, creator_name, deliverer_user, deliverer_email, description, catalog_link, replaced_by_filename, comment, aperture

* Executing a SQL query can be done as follows:

crds sql "select name, state, pedigree from crds_hst_catalog"
('h230851po_pfl.fits', 'operational', 'GROUND')
('h230851qo_pfl.fits', 'operational', 'GROUND')
('h230851so_pfl.fits', 'operational', 'GROUND')
('h2310096o_pfl.fits', 'operational', 'GROUND')
('h241320gn_ilm.fits', 'operational', 'DUMMY 04/02/1997')
('h241320in_ilm.fits', 'operational', 'DUMMY 04/02/1997')
('h241320jn_ilm.fits', 'operational', 'DUMMY 04/02/1997')
('h241320ln_ilm.fits', 'operational', 'DUMMY 04/02/1997')
...
"""

    def add_args(self):
        super(CrdsSqlQueryScript, self).add_args()
        self.add_argument("sql_query", nargs="*", help="sqlite3 query to run on cached database.")
        self.add_argument("-u", "--update-db", action="store_true",
                          help="Updates local cached copy of CRDS catalog and context history from CRDS server.")
        self.add_argument("-t", "--list-tables", action="store_true",
                          help="Print out the table names contained in the database")
        self.add_argument("-c", "--list-columns", metavar="TABLE", nargs="+",
                          help="Print out the column names contained in the specified table of the database")
        self.add_argument("-p", "--list-database-path", action="store_true",
                          help="Print out the path of the local sqlite3 database file,  useable by sqlite3.")

    def main(self):
        """Process command line parameters in to a context and list of
        reference files.   Print out the match tuples within the context
        which contain the reference files.
        """
        if self.args.update_db or not os.path.exists(self.sqlite_db_path):
            self.fetch_sqlite_db()

        if self.args.list_tables:
            self.list_tables()

        if self.args.list_columns:
            self.list_columns(self.args.list_columns[0])

        if self.args.list_database_path:
            print(self.sqlite_db_path)

        if self.args.sql_query:
            self.run_query(" ".join(self.args.sql_query))

        return log.errors()

    @property
    def sqlite_db_path(self):
        """Return the path to the sqlite3 database file."""
        return config.get_sqlite3_db_path(self.observatory)

    def fetch_sqlite_db(self):
        """Download a SQLite version of the CRDS catalog from the server."""
        log.info("Downloading CRDS catalog database file.")
        with log.warn_on_exception("Failed updating local CRDS database"):
            db_path = api.get_sqlite_db(self.observatory)
            log.info("Sqlite3 database file downloaded to:", db_path)

    def list_tables(self):
        """Print out the names of the database tables,  one per line."""
        for table in self.get_tables():
            print(table)

    def list_columns(self, table):
        """Print out an ordered comma separated list of database table column names"""
        print(", ".join(self.get_columns(table)))

    def get_tables(self):
        """Return the list of database table names."""
        connection = sqlite3.connect(self.sqlite_db_path)
        cursor = connection.cursor()
        query = 'select name from sqlite_master where type=\'table\''
        log.verbose("querying:", repr(query))
        tables = [row[0] for row in cursor.execute(query)]
        connection.close()
        return tables

    def get_columns(self, table):
        """Return the list of database column names for `table`."""
        connection = sqlite3.connect(self.sqlite_db_path)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        query = "select * from {};".format(table)
        log.verbose("querying:", repr(query))
        row = cursor.execute(query).fetchone()
        columns = row.keys()
        connection.close()
        return columns

    def run_query(self, query):
        """Run the string `query` on the downloaded CRDS sqlite database."""
        connection = sqlite3.connect(self.sqlite_db_path)
        cursor = connection.cursor()
        log.verbose("querying:", repr(query))
        for row in cursor.execute(query):
            print(self.format_row(row))
        connection.commit()
        connection.close()

    def format_row(self, row):
        """Return a query row formatted for output."""
        row = squash_unicode(row)
        return row

# ===================================================================

def squash_unicode(row):
    """Convert unicode strings in row to ordinary strings."""
    row2 = []
    for field in row:
        if isinstance(field, str):
            row2.append(str(field))
        else:
            row2.append(field)
    return tuple(row2)

# ===================================================================

if __name__ == "__main__":
    sys.exit(CrdsSqlQueryScript()())
