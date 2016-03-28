"""
This module defines functions for accessing server web pages programatically.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# =====================================================================

import sys
import os

if sys.version_info < (3, 0, 0):
    from urllib2 import urlopen, Request
    from urllib import urlencode
else:
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode

# =====================================================================

from crds import log, config, python23

from crds.exceptions import ServiceError

HEADERS = {
    'User-Agent': 'python',
    'Content-Type': 'application/x-www-form-urlencoded',
}

def post(server, path, values=dict(), headers=HEADERS):
    url = server + path
    params = urlencode(values)
    response = urlopen(url, data=params, headers=headers)
    data = response.read()
    status = response.getcode()
    return status, data

def get(server, path, values=dict(), headers=HEADERS):
    params = urlencode(values)
    url = server + path + "?" + params
    response = urlopen(url)
    data = response.read()
    status = response.getcode()
    return status, data

