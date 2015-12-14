"""CheckingProxy derived from jsonrpc.proxy due to subclassing problems 
w/getattr. Converts service errors into ServiceError exceptions,  otherwise 
call returns the jsonrpc "result" field.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import uuid
import json
import time
import os
import ssl

from crds import python23

if sys.version_info < (3, 0, 0):
    import HTMLParser as parser_mod
    from urllib2 import urlopen
    unescape = parser_mod.HTMLParser().unescape
else:
    import html.parser as parser_mod
    from urllib.request import urlopen
    from html import unescape

from crds import log, config

from crds.exceptions import ServiceError

def apply_with_retries(f, *pars, **keys):
    """Apply function f() as f(*pargs, **keys) and return the result. Retry on any exception as defined in config.py"""
    retries = config.get_client_retry_count()
    delay = config.get_client_retry_delay_seconds()
    for retry in range(retries):
        try:
            return f(*pars, **keys)
        except Exception as exc:
            log.verbose("FAILED: Attempt", str(retry+1), "of", retries, "with:", str(exc))
            log.verbose("FAILED: Waiting for", delay, "seconds before retrying")  # waits after total fail...
            time.sleep(delay)
            exc2 = exc
    else:
        raise exc2

def program_id():
    """Return a nominal identifier for this program."""
    return os.path.basename(os.path.splitext(sys.argv[0])[0])
        
class CheckingProxy(object):
    """CheckingProxy converts calls to undefined methods into JSON RPC service 
    calls.   If the JSON rpc returns an error,  CheckingProxy raises a 
    ServiceError exception containing the error's message.
    
    XXX NOTE: Always underscore new methods or you may hide a real JSONRPC method
    which also appears in the proxy object's namespace with the same name.
    
    """
    def __init__(self, service_url, service_name=None, version='1.0'):
        self.__version = str(version)
        self.__service_url = service_url
        self.__service_name = service_name

    def __getattr__(self, name):
        if self.__service_name != None:
            name = "%s.%s" % (self.__service_name, name)
        return CheckingProxy(self.__service_url, name, self.__version)

    def __repr__(self):
        return self.__class__.__name__ + "(url='%s', method='%s')" % \
            (self.__service_url, self.__service_name)
        
    def _call(self, *args, **kwargs):
        """Core of RPC dispatch without error interpretation, logging, or return value decoding."""
        params = kwargs if len(kwargs) else args
        # if Any.kind(params) == Object and self.__version != '2.0':
        #   raise Exception('Unsupport arg type for JSON-RPC 1.0 '
        #                  '(the default version for this client, '
        #                  'pass version="2.0" to use keyword arguments)')
        jsonrpc_params = {"jsonrpc": self.__version,
                          "method": self.__service_name,
                          'params': params,
                          'id': program_id() + "-" + str(uuid.uuid1()) 
                          }
        
        parameters = json.dumps(jsonrpc_params)
        
        url = self._get_url(jsonrpc_params)
        
        if "serverless" in url or "server-less" in url:
            raise ServiceError("Configured for server-less mode.  Skipping JSON RPC " + repr(self.__service_name))

        if log.get_verbose() <= 50:
            log.verbose("CRDS JSON RPC", self.__service_name, params if len(str(params)) <= 60 else "(...)", "-->")
        else:
            log.verbose("CRDS JSON RPC to", url, "parameters", params, "-->")
        
        response = apply_with_retries(self._call_service, parameters, url)

        try:
            rval = json.loads(response)
        except Exception:
            log.warning("Invalid CRDS jsonrpc response:\n", response)
            raise
        
        return rval
    
    def _get_url(self, jsonrpc_params):
        """Return the JSONRPC URL used to perform a method call.   Since post parameters are not visible in the
        log,  annotate the URL with additional method id paths which are functionally ignored but visible in
        the log.
        """
        return self.__service_url + jsonrpc_params["method"] + "/" + jsonrpc_params["id"] + "/"

    def _call_service(self, parameters, url):
        """Call the JSONRPC defined by `parameters` and raise a ServiceError on any exception."""
        if not isinstance(parameters, bytes):
            parameters = parameters.encode("utf-8")
        try:
            # context = ssl.create_default_context()
            # channel = urlopen(url, parameters, context=context)
            channel = urlopen(url, parameters)
            return channel.read().decode("utf-8")
        except Exception as exc:
            raise ServiceError("CRDS jsonrpc failure " + repr(self.__service_name) + " " + str(exc))

    def __call__(self, *args, **kwargs):
        jsonrpc = self._call(*args, **kwargs)
        if jsonrpc["error"]:
            decoded = str(unescape(jsonrpc["error"]["message"]))
            log.verbose("RPC FAILED", decoded)
            raise ServiceError(decoded)
        result = crds_decode(jsonrpc["result"])
        result = fix_strings(result)
        log.verbose("RPC OK", log.PP(result) if log.get_verbose() >= 70 else "")
        return result

def fix_strings(rval):
    """Convert unicode to strings."""
    if isinstance(rval, python23.string_types):
        return str(rval)
    elif isinstance(rval, tuple):
        return tuple([fix_strings(x) for x in rval])
    elif isinstance(rval, list):
        return [fix_strings(x) for x in rval]
    elif isinstance(rval, dict):
        return { fix_strings(key):fix_strings(val) for (key, val) in rval.items()}
    else:
        return rval

# ============================================================================

# These operate transparently in the proxy and are optionally used by the server.
#
# This makes a new client with crds_decoder compatible with both encoding and 
# unencoding servers.
#
# An older client without crds_decoder will not work with a new server which is encoding.
# That could be achieved,  but wasn't because the function where the feature was
# needed would not work without compression anyway.

def crds_encode(obj):
    """Return a JSON-compatible encoding of `obj`,  nominally json-ified, compressed,
    and base64 encooded.   This is nominally to be called on the server.
    """
    return dict(crds_encoded = "1.0",
                crds_payload = json.dumps(obj).encode('zlib').encode('base64'))

def crds_decode(s):
    """Decode something which was crds_encode'd,  or return it unaltered if
    it wasn't.
    """
    if isinstance(s, dict) and "crds_encoded" in s:
        json_str = s["crds_payload"].decode('base64').decode('zlib')
        return json.loads(json_str)
    else:
        return s
