"""This module defines a command line tool for executing SQL queries on downloaded versions of 
the CRDS catalog database.  It is a wrapper around a sqlite3 database download service and the
sqlite3 command line program which can be used to query  it.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import os
import os.path
from collections import defaultdict
from pprint import pprint as pp

from crds import rmap, log, cmdline, utils, config, pysh
from crds.client import api
from crds import python23

# ===================================================================

def test():
    """Run any doctests."""
    import doctest, crds.sql
    return doctest.testmod(crds.sql)

class CrdsSqlQueryScript(cmdline.Script):
    """Command line script for querying a downloaded copy of the CRDS catalog using a SQLite3 subprocess."""

    description = """

"""

    epilog = """
"""
    
    def add_args(self):
        super(CrdsSqlQueryScript, self).add_args()
        self.add_argument("sql_query", nargs="*", help="sqlite3 query to run on cached database.")
        self.add_argument("-u", "--update-db", action="store_true",
            help="Updates local cached copy of CRDS catalog and context history from CRDS server.")

    def main(self):
        """Process command line parameters in to a context and list of
        reference files.   Print out the match tuples within the context
        which contain the reference files.
        """
        if self.args.update_db or not os.path.exists(self.sqlite_db_path):
            self.fetch_sqlite_db()

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
        self.db_path = api.get_sqlite_db(self.observatory)
        log.info("Sqlite3 database file downloaded to:", self.db_path)

    def run_query(self, query):
        import sqlite3
        connection = sqlite3.connect(self.sqlite_db_path)
        cursor = connection.cursor()
        log.info("querying:", repr(query))
        for row in cursor.execute(query):
            row = self.condition_row(row)
            print(row)
        connection.commit()
        connection.close()

    def condition_row(self, row):
        row2 = []
        for field in row:
            if isinstance(field, (str, unicode)):
                row2.append(str(field))
            else:
                row2.append(field)
        return tuple(row2)
        
if __name__ == "__main__":
   sys.exit(CrdsSqlQueryScript()())
