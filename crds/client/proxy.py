"""CheckingProxy derived from jsonrpc.proxy due to subclassing problems 
w/getattr. Converts service errors into ServiceError exceptions,  otherwise 
call returns the jsonrpc "result" field.
"""
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

# ============================================================================

import sys
import uuid
import json
import time
import os

# import crds
from crds.core import python23, exceptions, log, config

# ============================================================================

def apply_with_retries(func, *pars, **keys):
    """Apply function func() as f(*pargs, **keys) and return the result. Retry on any exception as defined in config.py"""
    retries = config.get_client_retry_count()
    delay = config.get_client_retry_delay_seconds()
    for retry in range(retries):
        try:
            return func(*pars, **keys)
        except Exception as exc:
            log.verbose("FAILED: Attempt", str(retry+1), "of", retries, "with:", str(exc))
            log.verbose("FAILED: Waiting for", delay, "seconds before retrying")  # waits after total fail...
            time.sleep(delay)
            exc2 = exc
    raise exc2

def message_id():
    """Return a nominal identifier for this program."""
    import crds
    return _program_name() + "-" + crds.__version__ + "-" + _PROCESS_ID + "-" + _request_id()

def _program_name():
    """Return the name of this program."""
    return os.path.basename(os.path.splitext(sys.argv[0])[0])

try:
    _PROCESS_ID = str(uuid.uuid4())
except Exception:
    _PROCESS_ID = "00000000-0000-0000-00000000000000000"
        
MSG_NO = 0
def _request_id():
    """Return an identifier unique to this particular JSONRPC request."""
    global MSG_NO
    MSG_NO += 1
    return "%08x" % MSG_NO

class CheckingProxy(object):
    """CheckingProxy converts calls to undefined methods into JSON RPC service 
    calls bindings.   If the JSON rpc returns an error,  CheckingProxy raises a 
    ServiceError exception containing the error's message.
    
    XXX NOTE: Always underscore new methods or you may hide a real JSONRPC method
    which also appears in the proxy object's namespace with the same name.
    
    """
    def __init__(self, service_url, version='1.0'):
        self.__version = str(version)
        self.__service_url = service_url

    def __getattr__(self, name):
        """Return a callable corresponding to JSONRPC method `name`."""
        return ServiceCallBinding(self.__service_url, name, self.__version)

    def __repr__(self):
        return self.__class__.__name__ + "(url='%s', version='%s')" % \
            (self.__service_url, self.__version)
        
class ServiceCallBinding(object):
    """When called,  ServiceCallBinding issues a JSONRPC call to the associated
    service URL.
    """
    def __init__(self, service_url, service_name=None, version='1.0'):
        self.__version = str(version)
        self.__service_url = service_url
        self.__service_name = service_name

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
                          'id': message_id()
                         }
        
        parameters = json.dumps(jsonrpc_params)
        
        url = self._get_url(jsonrpc_params)
        
        if "serverless" in url or "server-less" in url:
            raise exceptions.ServiceError("Configured for server-less mode.  Skipping JSON RPC " + repr(self.__service_name))

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
            channel = python23.urlopen(url, parameters)
            return channel.read().decode("utf-8")
        except Exception as exc:
            raise exceptions.ServiceError("CRDS jsonrpc failure " + repr(self.__service_name) + " " + str(exc))

 

    def __call__(self, *args, **kwargs):
        jsonrpc = self._call(*args, **kwargs)
        if jsonrpc["error"]:
            decoded = str(python23.unescape(jsonrpc["error"]["message"]))
            raise self.classify_exception(decoded)
        else:
            result = crds_decode(jsonrpc["result"])
            result = fix_strings(result)
            if isinstance(result, (python23.string_types,int,float,bool)):
                log.verbose("RPC OK -->", repr(result))
            else:
                log.verbose("RPC OK", log.PP(result) if log.get_verbose() >= 70 else "")
            return result

    def classify_exception(self, decoded):
        """Interpret exc __str__ to define as more precise CRDS exception."""
        if "Channel" in decoded and "not found" in decoded:
            return exceptions.StatusChannelNotFoundError(decoded)
        elif "External agent requested calling process termination." in decoded:
            return exceptions.OwningProcessAbortedError(decoded)
        else:
            msg = "CRDS jsonrpc failure " + repr(self.__service_name) + " " + str(decoded)
            return exceptions.ServiceError(msg)

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

def crds_decode(msg):
    """Decode something which was crds_encode'd,  or return it unaltered if
    it wasn't.
    """
    if isinstance(msg, dict) and "crds_encoded" in msg:
        json_str = msg["crds_payload"].decode('base64').decode('zlib')
        return json.loads(json_str)
    else:
        return msg
