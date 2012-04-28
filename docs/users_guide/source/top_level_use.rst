Top Level Use
=============

This section describes the formal top level interfaces for CRDS intended as the
main entry points for the calibration software or basic use.  Functions
at this level should be assumed to require network connectivity with the CRDS
server.   

To function correctly,  these API calls require the user to set the environment
variables CRDS_REFPATH,  CRDS_MAPPATH,  and CRDS_SERVER_URL.   See the section
on *Installation* for more details.

crds.getreferences()
--------------------

Given  dataset header containing parameters required to determine best
references, and optionally a specific .pmap to use as the best references
context,  and optionally a list of the reference types for which reference files
to be determined,  getreferences() returns a mapping from reference types to
reference file base names::

    def getreferences(header_parameters, reftypes=None, context=None, ignore_cache=False):
        """Return the mapping from the requested `reftypes` to their 
        corresponding best reference file names appropriate for a dataset 
        described by `parameters` with CRDS rules defined by `context`::
        
        Parameters
        ----------
        
        header :    A mapping of parameter names to parameter value
                strings for parameters which define best reference file matches.
    
                { str  :   str, int, float, bool }
           
               e.g.  {
                       'INSTRUME' : 'ACS',
                       'CCDAMP' : 'ABCD',
                       'CCDGAIN' : '2.0',
                       ...
                    }
    
        reftypes :    A list of reference type names,  where each reftype is the
                    keyword used to record that kind of reference file in a 
                    dataset header.
                
                    [ str ]

                    e.g.  [ 'darkfile', 'biasfile']
                    
                    If reftypes is None,  return all reference types defined by
                    the instrument mapping for the instrument specified in 
                    `header_parameters`.
                    
        context :   The name of the pipeline context mapping which should be
                used to define best reference lookup rules,  or None.  If 
                `context` is None,  use the latest operational pipeline mapping.
                
                str
                
                e.g. 'hst_0037.pmap'
                
        ignore_cache :   If True,  download all required mappings and references
                from the CRDS server.  If False,  download only those files not
                already in the local caches.

        Returns
        -------
                a mapping from reftypes to best reference file basenames.
        
                { str : str }
                
                e.g.   {
                    'biasfile' : '/path/to/file/hst_acs_biasfile_0042.fits',
                    'darkfile' : '/path/to/file/hst_acs_darkfile_0056.fits',
                    }
        """



crds.get_default_context()
--------------------------

Given the observatory name,  get_default_context() returns the name
of the pipeline mapping which is currently in operational use.   The default
context defines the matching rules used to determine best reference files for
a given set of parameters::

    def get_default_context(observatory):
        """Return the name of the latest pipeline mapping in use for processing
        files for `observatory`.  
    
        Parameters
        -----------
        observatory  :  name of the observatory the returned context applies to.
        
            str 
                
            e.g. 'hst' or 'jwst'

        Returns   
        -------
        pipeline context mapping   
        
            str
        
            e.g.   'hst_0007.pmap'
        """


