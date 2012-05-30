"""CheckingProxy derived from jsonrpc.proxy due to subclassing problems 
w/getattr. Converts service errors into ServiceError exceptions,  otherwise 
call returns the jsonrpc "result" field.
"""
import urllib
import uuid

from json import loads, dumps

from crds.utils import CrdsError

class ServiceError(CrdsError):
    """The service call failed for some reason."""
        
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
        return self.__class__.__name__ + "(jsonrpc='%s', method='%s')" % \
            (self.__version, self.__service_name)
        
    def _call(self, *args, **kwargs):
        params = kwargs if len(kwargs) else args
        # if Any.kind(params) == Object and self.__version != '2.0':
        #   raise Exception('Unsupport arg type for JSON-RPC 1.0 '
        #                  '(the default version for this client, '
        #                  'pass version="2.0" to use keyword arguments)')
        parameters = dumps({"jsonrpc": self.__version,
                            "method": self.__service_name,
                            'params': params,
                            'id': str(uuid.uuid1())})
        try:    
            channel = urllib.urlopen(self.__service_url, parameters)
            response = channel.read()        
        except Exception, exc:
            raise ServiceError("CRDS network service call failure " + repr(parameters))
        rval = loads(response)
        return rval
    
    def __call__(self, *args, **kwargs):
        jsonrpc = self._call(*args, **kwargs)
        if jsonrpc["error"]:
            raise ServiceError(jsonrpc["error"]["message"])
        return jsonrpc["result"]

