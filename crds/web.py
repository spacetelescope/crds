"""This module codifies standard practices for scripted interactions with the 
web server file submission system.
"""

import sys
import os
import socket

from lxml import html
import requests

import crds
from crds import config, log, utils, pysh
from crds.client import api
from crds.python23 import *

# ================================================================================

class CrdsDjangoConnection(object):
    def __init__(self, locked_instrument="none", username=None, password=None, 
                 observatory=None, ingest_destination=None):
        self.locked_instrument = locked_instrument
        self.username = username or config.USERNAME.get()
        self.password = password or config.PASSWORD.get()
        self.observatory = observatory or api.get_default_observatory()
        self.ingest_destination = ingest_destination or api.get_submission_info(self.observatory, self.username).ingest_dir
        self.base_url = config.get_server_url(self.observatory)
        self.session = requests.session()
        self.session.headers.update({'referer': self.base_url})

    def abs_url(self, relative_url):
        """Return the absolute server URL constructed from the given `relative_url`."""
        return self.base_url + relative_url

    def divider(self, name="", char="-", n=75, func=log.verbose):
        """Create a log divider line consisting of `char` repeated `n` times
        possibly with `name` injected into the center of the divider.
        Output it as a string to logging function `func`.
        """
        if name:
            n2 = (n - len(name) - 2) // 2
            func(char*n2, name, char*n2)
        else:
            func(char*n)

    def dump_response(self, name, response):
        """Print out verbose output related to web `response` from activity `name`."""
        self.divider(name=name)
        log.verbose("headers:", response.headers)
        self.divider()
        log.verbose("text:", response.text, verbosity=60)
        self.divider()
        try:
            log.verbose("json:", response.json()) 
        except:
            pass
        self.divider()

    def get(self, relative_url):
        url = self.abs_url(relative_url)
        self.divider(name="GET")
        log.verbose("GET:", url)
        response = self.session.get(url)
        self.dump_response("GET response:", response)
        return response

    def post(self, relative_url, *post_dicts, **post_vars):
        url = self.abs_url(relative_url)
        vars = self.combine_dicts(*post_dicts, **post_vars)
        self.divider(name="POST " + url)
        log.verbose("POST:", vars)
        response = self.session.post(url, vars)
        self.dump_response("POST response: ", response)
        return response

    def repost(self, relative_url, *post_dicts, **post_vars):
        """First GET form from ``relative_url`,  next POST form to same
        url using composition of variables from *post_dicts and **post_vars.

        Maintain Django CSRF session token.
        """
        response = self.get(relative_url)

        csrf_token = html.fromstring(response.text).xpath(
            '//input[@name="csrfmiddlewaretoken"]/@value'
            )[0]
        post_vars['csrfmiddlewaretoken'] = csrf_token

        response = self.post(relative_url, *post_dicts, **post_vars)
        return response
    
    def combine_dicts(self, *post_dicts, **post_vars):
        """Combine positional parameters (dictionaries) and individual
        variables specified by keyword into a single parameter dict.
        """
        vars = dict()
        for pars in post_dicts:
            vars.update(pars)
        vars.update(post_vars)
        return vars

    def login(self, next="/"):
        self.repost("/login/", 
            username = self.username,
            password = self.password, 
            instrument = self.locked_instrument,
            next = next,
            )
    
    def ingest_files(self, filepaths):
        """Copy `filepaths` into the user's ingest directory on the CRDS server."""
        stats = self._start_stats(filepaths)

        destination = self.ingest_destination

        for name in filepaths:
            log.info("Copying", repr(name))
            if destination.startswith(socket.gethostname()):
                output = pysh.out_err("cp -v ${name} ${destination}")
            else:
                output = pysh.out_err("scp -v ${name} ${destination}")
            if output:
                log.verbose(output)

            stats.increment("bytes", os.stat(name).st_size)
            stats.increment("files", 1)

        self.divider()
        stats.report()
        self.divider(char="=", func=log.info)

    def _start_stats(self, filepaths):
        """Helper method to initialize stats keeping for ingest."""
        total_bytes = 0
        for name in filepaths:
            total_bytes += os.stat(name).st_size
        stats = utils.TimingStats(output=log.verbose)
        stats.start()
        self.divider(name="ingest files", char="=", func=log.info)
        log.info("Copying", len(filepaths), "file(s) totalling", total_bytes, "bytes")
        self.divider()
        return stats

    def get_pmap_selection_parameters(self, pmap_mode="pmap_edit", pmap_name=None, **keys):
        """Return a dictionary of parameters used so satisfy the pmap selection (Derived From Context)
        form variables on the CRDS web server.
        """
        assert pmap_mode in ["pmap_edit", "pmap_operational", "pmap_text"], "Invalid pmap selection mode."        
        if pmap_mode in ["pmap_edit", "pmap_operational"]:
            sym_name = pmap_mode.replace("pmap_", self.observatory+"-")
            pmap_name = api.get_context_by_date(sym_name, observatory=self.observatory)
        assert config.is_context(pmap_name), "Invalid pmap_name " + repr(pmap_name)
        return {                
            "pmap_mode" : pmap_mode,
            pmap_mode : pmap_name,
            }

    def jpoll_open(self):
        """Mimic opening a JPOLL status channel as do pages with real-time status."""
        response = self.session.get(self.abs_url("/jpoll/open_channel"))
        self.dump_response("jpoll_open", response)
        self.jpoll_key = response.json()


    def certify_files(self, filepaths, compare_old_reference="checked", pmap_mode="pmap_edit", pmap_name=None):
        """Run the CRDS server Certify Files page on `filepaths`."""
        self.ingest_files(filepaths)
        self.jpoll_open()
        pmap_pars = self.get_pmap_selection_parameters(pmap_mode, pmap_name)
        self.repost("/certify/", pmap_pars, compare_old_reference="checked")

def main(files):
    session = CrdsDjangoConnection()
    session.login()
    session.certify_files(files)
    
if __name__ == "__main__":
    main(sys.argv[1:])

