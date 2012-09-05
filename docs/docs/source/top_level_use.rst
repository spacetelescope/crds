Top Level Use
=============

This section describes the formal top level interfaces for CRDS intended as the
main entry points for the calibration software or basic use.  Functions
at this level should be assumed to require network connectivity with the CRDS
server.   

To function correctly,  these API calls may require the user to set the
environment variables CRDS_SERVER_URL and CRDS_PATH.   See the section on
*Installation* for more details.

crds.getreferences()
---------------------------

Given  dataset header containing parameters required to determine best
references, and optionally a specific .pmap to use as the best references
context,  and optionally a list of the reference types for which reference files
are to be determined,  getreferences() will determine best references,  cache
them on the local file system,  and return a mapping from reference types to
reference file paths::

    def getreferences(parameters, reftypes=None, context=None, ignore_cache=False,
                      observatory="jwst"):
        """Return the mapping from the requested `reftypes` to their 
        corresponding best reference file paths appropriate for a dataset 
        described by `parameters` with CRDS rules defined by `context`::
        
        parameters :    A mapping of parameter names to parameter value
                strings for parameters which define best reference file matches.
    
                { str  :   str, int, float, bool }
           
               e.g.  {
                       'INSTRUME' : 'ACS',
                       'CCDAMP' : 'ABCD',
                       'CCDGAIN' : '2.0',
                       ...
                    }
    
        reftypes :    A list of reference type names.   For HST these are the keywords
                     used to record reference files in dataset headers.   For JWST,  these
                     are the identifiers which will appear in instrument contexts and
                     reference mappings.
                
                    e.g.  [ 'darkfile', 'biasfile']
                    
                    If reftypes is None,  return all reference types defined by
                    the instrument mapping for the instrument specified in 
                    `parameters`.
                    
        context :   The name of the pipeline context mapping which should be
                used to define best reference lookup rules,  or None.  If 
                `context` is None,  use the latest operational pipeline mapping.
                
                str
                
                e.g. 'hst_0037.pmap'
                
        ignore_cache :   If True,  download all required mappings and references
                from the CRDS server.  If False,  download only those files not
                already in the local caches.
        
        observatory :  The name of the observatory this query applies to,  needed
                to support both 'hst' and 'jwst' from a single server.

        Returns
        -------
                a mapping from reftypes to cached best reference file paths.
        
                { str : str }
                
                e.g.   {
                    'biasfile' : '/path/to/file/hst_acs_biasfile_0042.fits',
                    'darkfile' : '/path/to/file/hst_acs_darkfile_0056.fits',
                    }
        """



crds.get_default_context()
---------------------------------

get_default_context() returns the name of the pipeline mapping which is 
currently in operational use.   When no

The default context defines the matching rules used to determine best 
reference files for a given set of parameters::

    def get_default_context():
        """Return the name of the latest pipeline mapping in use for processing
        files.  
        
        Returns   
        -------
        pipeline context name
        
            e.g.   'hst_0007.pmap'
        """
