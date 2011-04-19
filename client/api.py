import sys
import os
import StringIO

sys.stdout = StringIO.StringIO()
from jsonrpc.proxy import ServiceProxy
sys.stdout = sys.__stdout__

URL = os.environ.get("CRDS_URL", 'http://localhost:8000/json/')

def get_best_refs(header):
    header = dict(header)
    S = ServiceProxy(URL)
    references = S.get_best_refs(header)["result"]
    return references

