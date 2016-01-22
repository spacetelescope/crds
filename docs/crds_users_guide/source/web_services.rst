Web Services
============

The CRDS servers support a JSONRPC based service mechanism which enables 
remote users to make calls to the CRDS server without installing the CRDS
Python based client library.   See http://json-rpc.org/wiki/specification
for more details on the JSONRPC protocol.

Users of the CRDS client library can access these JSONRPC functions using 
the crds.client module::

  >>> from crds import client
  >>> client.get_default_context('jwst')
  'jwst_0101.pmap'

Context Information
-------------------

The CRDS context is the version of CRDS rules used to select reference files.
The default CRDS context is maintained on the CRDS server and reported by
the function *get_default_context()*.  Remote pipelines which are operating
decoupled from the CRDS server can post their actual cached context to the CRDS
server for retrieval by *get_remote_context()*.

Centralized Default
+++++++++++++++++++

**get_default_context(observatory)**

get_default_context() returns the name of the pipeline mapping which is
currently in use by default in the archive pipeline, e.g. 'jwst_0001.pmap'.
This value is set and maintained on the CRDS Server using the Set Context web
page and reflects a commanded default for all users.  Remote pipeline instances
of CRDS running in 'local' mode only update their copy of this default when
their CRDS cache is synchronized with the server.  Hence this value represents
a commanded context and the actual pipeline context differs until
*pipeline_name* is synchronized with the CRDS server.

Pipeline Echo
+++++++++++++

**get_remote_context(observatory, pipeline_name)**

get_remote_context() returns the name of the pipeline mapping last reported as
synced by the specified *pipeline_name* (e.g. 'jwst-ops-pipeline').  This is
the value stored in a pipeline's CRDS cache and echoed back to the CRDS server
when the cache is synchronized.  Since this value is inapplicable if a pipeline
is run in "remote" mode computing best references on the CRDS Server, the
generally preferred value is from get_default_context() since it always
reflects the intended operational context regardless of the pipeline's CRDS
mode.

File Information
----------------

The CRDS server maintains a catalog of basic metadata for the rules and reference
files managed by CRDS.   Catalog information cab be 

Single File Metadata
++++++++++++++++++++

**get_file_info(pipeline_context, filename)**

Return a dictionary of CRDS catalog information about `filename`.  For instance::

 >>> get_file_info("jwst", "jwst_miri_flat_0023.fits")
 {'activation_date': '2014-09-25 18:30:27',
  'aperture': 'none',
  'blacklisted': 'false',
  'change_level': 'severe',
  'comment': 'cdp-2 from fm testing',
  'creator_name': 'jwst build 3 team',
  'deliverer_user': 'jmiller',
  'delivery_date': '2014-09-20 07:55:56',
  'derived_from': 'none',
  'description': 'all references from jwst build 3 delivery 2. update miri flats, fringes, straymasks, resets, lastframes, nirspec flat.',
  'filekind': 'flat',
  'instrument': 'miri',
  'name': 'jwst_miri_flat_0023.fits',
  'observatory': 'jwst',
  'pedigree': 'ground',
  'reference_file_type': 'flat',
  'rejected': 'false',
  'replaced_by_filename': '',
  'sha1sum': '3f0c92aae539cb67f8e8823cc6815130018948f7',
  'size': '10592640',
  'state': 'operational',
  'type': 'reference',
  'uploaded_as': 'jwst_miri_flat_0016.fits',
  'useafter_date': '2050-01-01 00:00:00'}

Multiple File Metadata
++++++++++++++++++++++

**get_file_info_map(observatory, files=None, fields=None)**

get_file_info_map() is a multi-file version of get_info_map() whihch returns
the information for several files with one call.  If `files` is not specified
then get_file_info_map() returns info for all files.

Return the info::
    
    { filename : { info, ... }, ... } 

on `files` of `observatory`.

`fields` can be used to limit info returned to specified keys::

    ['activation_date', 'aperture', 'blacklisted', 'change_level', 'comment', 
     'creator_name', 'deliverer_user', 'delivery_date', 'derived_from', 'description', 
     'filekind', 'instrument', 'name', 'observatory', 'pedigree', 'reference_file_type', 
     'rejected', 'replaced_by_filename', 'sha1sum', 'size', 'state', 'type', 
     'uploaded_as', 'useafter_date']

If `fields` is not specified then get_file_info_map() returns all fields.

Best References
---------------

Single Header
+++++++++++++

**get_best_references(context, header, reftypes)**

get_best_references() matches a set of parameters *header* against the lookup 
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

Multiple Headers
++++++++++++++++

**get_best_references_by_header_map(context, header_map, reftypes)**

This service is an adaptation of get_best_references() to support returning
best references for multiple datasets with a single service call.  All
parameters are as for get_best_references() with the modification that *header*
above is replaced with a mapping from multiple dataset ids to their
corresponding headers, i.e. *header_map*::
    
    { dataset_id : header, ... }

The return value is likewise adapted to return best references for multiple
datasets::

    { dataset_id : best_references, ... }

Where *dataset_id* is nominally an HST IPPPSSOOT id (e.g. 'I9ZF01010') or JWST
dataset identifier (TBD).  Since *dataset_id* is only a keyword not used in best
references computations, it can be any unique abstract identifier consisting of
alphanumeric characters, period, colon, hyphen, or plus sign of 128 characters
or less.

Selection Parameters
++++++++++++++++++++

**get_required_parkeys(context)**

Return a mapping from instruments to lists of parameter names required to
compute bestrefs under `context`,  i.e. matching header keys::

    { instrument : [ matching_parkey_name, ... ], ... }

In CRDS the matching parameters are defined by each set of rules, e.g. for 
one HST context (hst_0366.pmap) the reference file selection parameters 
for all instruments are as follows::

    {'acs': ['INSTRUME', 'APERTURE', 'ATODCORR', 'BIASCORR', 'CCDAMP', 'CCDCHIP',
         'CCDGAIN', 'CRCORR', 'DARKCORR', 'DATE-OBS', 'DETECTOR', 'DQICORR',
         'DRIZCORR', 'FILTER1', 'FILTER2', 'FLASHCUR', 'FLATCORR', 'FLSHCORR', 
         'FW1OFFST', 'FW2OFFST', 'FWSOFFST', 'GLINCORR', 'LTV1', 'LTV2', 'NAXIS1', 
         'NAXIS2', 'OBSTYPE', 'PCTECORR', 'PHOTCORR', 'REFTYPE', 'RPTCORR', 
         'SHADCORR', 'SHUTRPOS', 'TIME-OBS', 'XCORNER', 'YCORNER'], 
    'cos': ['INSTRUME', 'ALGNCORR', 'BADTCORR', 'BRSTCORR', 'DATE-OBS', 'DEADCORR',
        'DETECTOR', 'EXPTYPE', 'FLATCORR', 'FLUXCORR', 'LIFE_ADJ', 'OBSMODE', 'OBSTYPE', 
        'OPT_ELEM', 'REFTYPE', 'TDSCORR', 'TIME-OBS', 'TRCECORR', 'WALKCORR'], 
    'nicmos': ['INSTRUME', 'CAMERA', 'DATE-OBS', 'FILTER', 'NREAD', 'OBSMODE', 'READOUT', 
            'REFTYPE', 'SAMP_SEQ', 'TIME-OBS'], 
     'stis': ['INSTRUME', 'APERTURE', 'BINAXIS1', 'BINAXIS2', 'CCDAMP', 'CCDGAIN', 'CCDOFFST', 
          'CENWAVE', 'DATE-OBS', 'DETECTOR', 'OBSTYPE', 'OPT_ELEM', 'REFTYPE', 'TIME-OBS'], 
     'wfc3': ['INSTRUME', 'APERTURE', 'ATODCORR', 'BIASCORR', 'BINAXIS1', 'BINAXIS2', 'CCDAMP', 
          'CCDGAIN', 'CHINJECT', 'DARKCORR', 'DATE-OBS', 'DETECTOR', 'DQICORR', 'DRIZCORR', 
          'FILTER', 'FLASHCUR', 'FLATCORR', 'FLSHCORR', 'PHOTCORR', 'REFTYPE', 'SAMP_SEQ', 
          'SHUTRPOS', 'SUBARRAY', 'SUBTYPE', 'TIME-OBS'], 
     'wfpc2': ['INSTRUME', 'ATODGAIN', 'DATE-OBS', 'FILTER1', 'FILTER2', 'FILTNAM1', 'FILTNAM2', 
            'IMAGETYP', 'LRFWAVE', 'MODE', 'REFTYPE', 'SERIALS', 'SHUTTER', 'TIME-OBS']
    }

The required parkeys can be used to reduce a complete file header to only those keywords
necessary to select references under the given context.

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

    % curl -i -X POST -d '{"jsonrpc": "1.0", "method": "get_default_context", "params": ["jwst"], "id": 1}' https://jwst-crds.stsci.edu/json/
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


