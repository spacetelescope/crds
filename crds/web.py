"""This module codifies standard practices for scripted interactions with the 
web server file submission system.
"""

import sys
import os
import socket

from lxml import html
import requests

from crds import config, log, utils, pysh
from crds.client import api

# ================================================================================

def combine_dicts(*post_dicts, **post_vars):
    """Combine positional parameters (dictionaries) and individual
    variables specified by keyword into a single parameter dict.
    """
    combined_vars = dict()
    for pars in post_dicts:
        combined_vars.update(pars)
    combined_vars.update(post_vars)
    return combined_vars

def divider(name="", char="-", repeat=75, func=log.verbose):
    """Create a log divider line consisting of `char` repeated `n` times
    possibly with `name` injected into the center of the divider.
    Output it as a string to logging function `func`.
    """
    if name:
        repeat2 = (repeat - len(name) - 2) // 2
        func(char*repeat2, name, char*repeat2)
    else:
        func(char*repeat)

def start_stats(self, filepaths, name=None, char="="):
    """Helper method to initialize stats keeping for ingest."""
    total_bytes = 0
    for name in filepaths:
        total_bytes += os.stat(name).st_size
    stats = utils.TimingStats(output=log.verbose)
    stats.start()
    divider(name=name, char=char, func=log.info)
    log.info("Copying", len(filepaths), "file(s) totalling", total_bytes, "bytes")
    divider()
    return stats

# ================================================================================

class CrdsDjangoConnection(object):
    """This class provides the basis for authenticated GETS and POSTS to a CRDS server."""
    def __init__(self, username=None, password=None, locked_instrument=None, observatory=None, ingest_destination=None):
        self.locked_instrument = locked_instrument
        self.username = config.get_username(username)
        self.password = config.get_password(password)
        self.observatory = observatory or api.get_default_observatory()
        self.base_url = config.get_server_url(self.observatory)
        self.ingest_destination = ingest_destination or \
            api.get_submission_info(self.observatory, self.username).ingest_dir
        self.session = requests.session()
        self.session.headers.update({'referer': self.base_url})
        self.jpoll_key = None

    def abs_url(self, relative_url):
        """Return the absolute server URL constructed from the given `relative_url`."""
        return self.base_url + relative_url

    def dump_response(self, name, response):
        """Print out verbose output related to web `response` from activity `name`."""
        divider(name=name)
        log.verbose("headers:", response.headers)
        divider()
        log.verbose("text:", response.text, verbosity=60)
        divider()
        try:
            log.verbose("json:", response.json()) 
        except:
            pass
        divider()

    def get(self, relative_url):
        """Get from `relative_url` which should include any necessary encoded parameters."""
        url = self.abs_url(relative_url)
        divider(name="GET")
        log.verbose("GET:", url)
        response = self.session.get(url)
        self.dump_response("GET response:", response)
        return response

    def post(self, relative_url, *post_dicts, **post_vars):
        """Post to `relative_url` the combination of variables defined using the combined 
        sequence of *post_dicts overridden by **post_vars.
        """
        url = self.abs_url(relative_url)
        combined_vars = combine_dicts(*post_dicts, **post_vars)
        divider(name="POST " + url)
        log.verbose("POST:", combined_vars)
        response = self.session.post(url, combined_vars)
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
    
    def login(self, next="/"):
        self.repost(
            "/login/", 
            username = self.username,
            password = self.password, 
            instrument = self.locked_instrument,
            next = next,
            )
    
    def ingest_files(self, filepaths):
        """Copy `filepaths` into the user's ingest directory on the CRDS server."""
        stats = start_stats(filepaths)

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

        divider()
        stats.report()
        divider(char="=", func=log.info)

    def get_pmap_selection_parameters(self, pmap_mode="pmap_edit", pmap_name=None):
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
        self.repost("/certify/", pmap_pars, compare_old_reference=compare_old_reference)

def main(files):
    session = CrdsDjangoConnection()
    session.login()
    session.certify_files(files)
    
if __name__ == "__main__":
    main(sys.argv[1:])

