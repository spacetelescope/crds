Web Services
============

The CRDS servers support a JSONRPC based service mechanism which enables 
remote users to make calls to the CRDS server without installing the CRDS
Python based client library.   See http://json-rpc.org/wiki/specification
for more details on the JSONRPC protocol.

Supported Methods
-----------------

get_default_context(observatory)
++++++++++++++++++++++++++++++++

**get_default_context** returns the name of the pipeline mapping which is currently 
in use by default in the operational pipeline, e.g. 'jwst_0001.pmap'.
get_default_context is called with a single parameter, *observatory*,  which can
be 'hst' or 'jwst'.

get_best_references(context, header, reftypes)
++++++++++++++++++++++++++++++++++++++++++++++

**get_best_references** matches a set of parameters *header* against the lookup 
rules specified by the pipeline mapping *context* to return a mapping of 
type names onto recommended reference file names.

A suitable *context* string can be obtained from get_default_context() above, 
although any archived CRDS context file can be specified.   

The *header* parameter of get_best_references is nominally a JSON object which 
maps CRDS parkey names onto dataset file header values.   CRDS parkey names can
be located by browsing reference mappings (.rmap's) and looking at the *parkey* 
header parameter of the rmap.

For JWST,  the rmap parkeys (matching parameter names) are currently specified 
as JWST stpipe data model dotted identifiers.  Example JSON for the get_best_references 
*header* parameter for JWST is::

    { "meta.instrument.type":"fgs", 
      "meta.instrument.detector":"fgs1", 
      "meta.instrument.filter":"any" }
    
For JWST,  it is also possible to use the equivalent FITS header keyword,  as
defined by the data model schema, to determine best references::

    { "instrume":"fgs", 
      "detector":"fgs1", 
      "filter":"any" }
    
For HST,  GEIS or FITS header keyword names are supported.  

*reftypes* should be a json array of strings,  each naming a single desired 
reference type.  If reftypes is passed as null,  recommended references for 
all reference types are returned.   Reference types which are defined for an
instrument but which are not applicable to the mode defined by *header* are
returned with the value *NOT FOUND n/a*.

Example JSON for *reftypes* might be::

    ["amplifier","mask"]

JSONRPC URL
-----------
The base URL used for making CRDS JSONRPC method calls is essentially */json/*.
All further information,  including the method name and the parameters,  are 
POSTed using a JSON serialization scheme.   Example absolute server URLs are:

JWST
++++

  http://jwst-crds.stsci.edu/json/
  
HST
+++

  http://hst-crds.stsci.edu/json/


JSONRPC Request
---------------

An example CRDS service request can be demonstrated in a language agnostic way
using the UNIX command line utility curl::

    % curl -i -X POST -d '{"jsonrpc": "1.0", "method": "get_default_context", "params": ["jwst"], "id": 1}' http://jwst-crds.stsci.edu/json/
    HTTP/1.1 200 OK
    Date: Fri, 12 Oct 2012 17:29:46 GMT
    Server: Apache/2.2.3 (Red Hat) mod_python/3.3.1 Python/2.7.2
    Vary: Cookie
    Content-Type: application/json-rpc
    Connection: close
    Transfer-Encoding: chunked
    
The *jsonrpc* attribute is used to specify the version of the JSONRPC standard
being used,  currently 1.0 for CRDS.

The *method* attribute specifies the name of the service being called.

The *params* attribute specifies a JSON array of parameters which are passed 
positionally to the CRDS method.

The *id* can be used to associate calls with their responses in asynchronous
environments.

JSONRPC Response
----------------

The reponse returned by the server for the above request is the following JSON::

    {"error": null, "jsonrpc": "1.0", "id": 1, "result": "jwst_0000.pmap"}
    
Error Handling
--------------

Because **get_best_references** determines references for a list of types,  lookup
errors are reported by setting the value of a reference type to 
"NOT FOUND " + error_message.   A value of "NOT FOUND n/a" indicates that CRDS
determined that a particular reference type does not apply to the given
parameter set.

Fatal errors are handled by setting the error attribute of the result object to
an error object.   Inspect the result.error.message attribute to get descriptive
text about the error.

JSONRPC Demo Page
-----------------

The CRDS servers support demoing the JSONRPC services and calling them interactively
by visiting the URL *.../json/browse/*.    The resulting page is shown here:

.. figure:: images/web_jsonrpc_browse.png
   :scale: 100 %
   :alt: jsonrpc browser demo page

An example dialog for get_best_references from the CRDS jsonrpc demo page is
shown here with FITS parkey names::

    >>> jsonrpc.get_best_references("jwst_0000.pmap", {'INSTRUME':'FGS','DETECTOR':'FGS1', 'FILTER':'ANY'}, null)
    Requesting ->
    {"id":"jsonrpc", "params":["jwst_0000.pmap", {"INSTRUME":"FGS", "DETECTOR":"FGS1", "FILTER":"ANY"}, null], "method":"get_best_references", "jsonrpc":"1.0"}
    Deferred(12, unfired)
    Got ->
    {"error": null, "jsonrpc": "1.0", "id": "jsonrpc", "result": {"linearity": "jwst_fgs_linearity_0000.fits", "amplifier": "jwst_fgs_amplifier_0000.fits", "mask": "jwst_fgs_mask_0000.fits"}}

And the same query is here with JWST data model parkey names:

    >>> jsonrpc.get_best_references("jwst_0000.pmap", {'META.INSTRUMENT.TYPE':'FGS','META.INSTRUMENT.DETECTOR':'FGS1', 'META.INSTRUMENT.FILTER':'ANY'}, null)
    Requesting ->
    {"id":"jsonrpc", "params":["jwst_0000.pmap", {"META.INSTRUMENT.TYPE":"FGS", "META.INSTRUMENT.DETECTOR":"FGS1", "META.INSTRUMENT.FILTER":"ANY"}, null], "method":"get_best_references", "jsonrpc":"1.0"}
    Deferred(14, unfired)
    Got ->
    {"error": null, "jsonrpc": "1.0", "id": "jsonrpc", "result": {"linearity": "jwst_fgs_linearity_0000.fits", "amplifier": "jwst_fgs_amplifier_0000.fits", "mask": "jwst_fgs_mask_0000.fits"}}

**NOTE:** An apparent bug in the demo interpreter makes it impossible to pass 
the get_best_references *reftypes* parameter as an array of strings.   In the
current demo reftypes can only be specified as null.


