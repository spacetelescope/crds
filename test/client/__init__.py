"""
The crds.client package is a light weight web client which accesses
the CRDS server using jsonrpc to compute best references and obtain reference
files.   Although it has some dependencies on the core crds package,  the client
module tries to minimize them to lightweight functions from: config, utils,
and log.
"""
from .api import *
