"""CheckingProxy derived from jsonrpc.proxy due to subclassing problems 
w/getattr. Converts service errors into ServiceError exceptions,  otherwise 
call returns the jsonrpc "result" field.
"""
import sys
import urllib2 as urllib
import uuid
import json
import time

if sys.version_info < (3,0,0):
    import HTMLParser as parser_mod
else:
    import html.parser as parser_mod
PARSER = parser_mod.HTMLParser()

from crds import log, config

class CrdsError(Exception):
    """Baseclass for all client exceptions."""

class ServiceError(CrdsError):
    """The service call failed for some reason."""
    
def apply_with_retries(f, *pars, **keys):
    """Apply function f() as f(*pargs, **keys) and return the result. Retry on any exception as defined in config.py"""
    retries = config.get_client_retry_count()
    delay = config.get_client_retry_delay_seconds()
    for retry in range(retries):
        try:
            return f(*pars, **keys)
        except Exception, exc:
            log.verbose("FAILED: Attempt", str(retry), "of", retries, "with:", str(exc))
            log.verbose("FAILED: Waiting for", delay, "seconds before retrying")  # waits after total fail...
            time.sleep(delay)
    else:
        raise exc
        
class CheckingProxy(object):
    """CheckingProxy converts calls to undefined methods into JSON RPC service 
    calls.   If the JSON rpc returns an error,  CheckingProxy raises a 
    ServiceError exception containing the error's message.
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
        params = kwargs if len(kwargs) else args
        # if Any.kind(params) == Object and self.__version != '2.0':
        #   raise Exception('Unsupport arg type for JSON-RPC 1.0 '
        #                  '(the default version for this client, '
        #                  'pass version="2.0" to use keyword arguments)')
        parameters = json.dumps({"jsonrpc": self.__version,
                                 "method": self.__service_name,
                                 'params': params,
                                 'id': str(uuid.uuid1())})
        log.verbose("CRDS JSON RPC to", repr(self.__service_url), 
                    "method", repr(self.__service_name), 
                    "parameters", params,
                    "-->",
                    verbosity=55, end="")

        response = apply_with_retries(self._call_service, parameters)

        try:
            rval = json.loads(response)
        except Exception, exc:
            log.warning("Invalid CRDS jsonrpc response:\n", response)
            raise
        
        return rval

    def _call_service(self, parameters):
        """Call the JSONRPC defined by `parameters` and raise a ServiceError on any exception."""
        try:
            channel = urllib.urlopen(self.__service_url, parameters)
            return channel.read()
        except Exception, exc:
            raise ServiceError("CRDS jsonrpc failure " + repr(self.__service_name) + " " + str(exc))

    def __call__(self, *args, **kwargs):
        jsonrpc = self._call(*args, **kwargs)
        if jsonrpc["error"]:
            decoded = str(PARSER.unescape(jsonrpc["error"]["message"]))
            log.verbose("FAILED", decoded, verbosity=55)
            raise ServiceError(decoded)
        log.verbose("SUCCEEDED", verbosity=55)
        result = crds_decode(jsonrpc["result"])
        return fix_strings(result)
    
def fix_strings(rval):
    """Convert unicode to strings."""
    if isinstance(rval, basestring):
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
