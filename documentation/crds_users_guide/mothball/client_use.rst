Client Usage
============

This section describes using the crds.client package to access remote
web services on the central CRDS server.  Remote services support the
determination of the best reference files for a dataset.  Remote
services support transparently downloading CRDS mappings and reference
files and caching them locally for use in development or dataset
processing.   This section is largely superseded by the section on 
*Top Level Use*,  but remains to document lower level features which 
are network oriented in nature.

Simplest Useage
---------------

After installing CRDS,  the simplest usage of CRDS is as follows::

  % source env.csh
  % python
  >>> import crds.client as client
  >>> bestrefs = client.cache_best_references_for_dataset("hst.pmap", "j8is01j0q_raw.fits")
  >>> bestrefs  
  {'atodtab': '.../site-packages/crds/hst/references/jtab/kcb1734ij_a2d.fits',
   'bpixtab': '.../site-packages/crds/hst/references/jref/m8r09169j_bpx.fits',
   'ccdtab': '.../site-packages/crds/hst/references/jref/o151506bj_ccd.fits',
   'crrejtab': '.../site-packages/crds/hst/references/jref/n4e12510j_crr.fits',
   'darkfile': '.../site-packages/crds/hst/references/jref/n3b10126j_drk.fits',
   'idctab': '.../site-packages/crds/hst/references/jref/p7d1548qj_idc.fits',
   'mdriztab': '.../site-packages/crds/hst/references/jref/ub215378j_mdz.fits',
   'mlintab': '.../site-packages/crds/hst/references/jtab/k9c13374j_lin.fits',
   'oscntab': '.../site-packages/crds/hst/references/jtab/m2j1057pj_osc.fits',
   'pfltfile': '.../site-packages/crds/hst/references/jref/n2d1344mj_pfl.fits',
   'spottab': '.../site-packages/crds/hst/references/jref/r3301467j_csp.fits'}
   
The first parameter is the name of the pipeline context file which should be used
to determine best references for the second parameter,  a dataset file.

Based on this single function call,  the client environment now has all the
information and system state required to process the dataset:  a mapping from
each required reference filekind to a local path to the reference.

Behind the scenes,  the following has occurred:

* CRDS used the pipeline context, "hst.pmap", to determine a set of mappings
  which should be used to compute best references.
* CRDS checked it's local cache for each mapping,  and downloaded it from the
  server if it was not already present locally.
* CRDS asked the server to compute best references based on the relevant
  parameters extracted from the FITS header.   This could also be done locally
  but asking the server gives an "official" answer.
* CRDS checked it's local cache for each best reference file, and
  downloaded it from the server if it was not already present locally.

Since I left CRDS_REFPATH undefined for this example,  the paths are all 
relative to .../site-packages/crds/hst/references where ... stands for the
absolute path of my Python standard library.

Just Give Me the Names
----------------------

cache_best_references_for_dataset() is built upon primitives which do
less.  A more basic function is to simply determine the names of the
best reference files based upon a pipeline context and *header*
parameters.  Nominally CRDS best reference parameters are extracted
from the dataset FITS header, but in principle the *header* can be a
dictionary which comes from anywhere::

  >>> header = { ... what matters ... }
  >>> bestrefs = client.get_best_references("hst.pmap", header)
  >>> bestrefs
  {'atodtab': 'kcb1734ij_a2d.fits',
   'bpixtab': 'm8r09169j_bpx.fits',
   'ccdtab': 'o151506bj_ccd.fits',
   'crrejtab': 'n4e12510j_crr.fits',
   'darkfile': 'n3b10126j_drk.fits',
   'idctab': 'p7d1548qj_idc.fits',
   'mdriztab': 'ub215378j_mdz.fits',
   'mlintab': 'k9c13374j_lin.fits',
   'oscntab': 'm2j1057pj_osc.fits',
   'pfltfile': 'n2d1344mj_pfl.fits',
   'spottab': 'r3301467j_csp.fits'}

In this case, get_best_references() started with a dictionary of
relevant best reference parameters, *header*, and returned the mapping
from reference filekinds to best reference filenames.  After executing
this function you only know what reference files should be used, not
where to get them.

OK,  Now Cache My Files
-----------------------

Once you've decided you're happy with your reference file choices,  you can
ask CRDS to cache them locally like this::

  >>> client.cache_references("hst.pmap", bestrefs)
  {'atodtab': '.../site-packages/crds/hst/references/jtab/kcb1734ij_a2d.fits',
   'bpixtab': '.../site-packages/crds/hst/references/jref/m8r09169j_bpx.fits',
   'ccdtab': '.../site-packages/crds/hst/references/jref/o151506bj_ccd.fits',
   'crrejtab': '.../site-packages/crds/hst/references/jref/n4e12510j_crr.fits',
   'darkfile': '.../site-packages/crds/hst/references/jref/n3b10126j_drk.fits',
   'idctab': '.../site-packages/crds/hst/references/jref/p7d1548qj_idc.fits',
   'mdriztab': '.../site-packages/crds/hst/references/jref/ub215378j_mdz.fits',
   'mlintab': '.../site-packages/crds/hst/references/jtab/k9c13374j_lin.fits',
   'oscntab': '.../site-packages/crds/hst/references/jtab/m2j1057pj_osc.fits',
   'pfltfile': '.../site-packages/crds/hst/references/jref/n2d1344mj_pfl.fits',
   'spottab': '.../site-packages/crds/hst/references/jref/r3301467j_csp.fits'}

There's an App for That
-----------------------

Maybe you've decided you don't want to worry about figuring out *what
matters* and how to format it after all.  In that case, call
get_minimum_header() on an instrument or reference mapping file and dataset
to determine the header parameters that matter::

  >>> client.get_minimum_header("hst_acs.imap", "test_data/j8bt05njq_raw.fits")
  {'CCDAMP': 'C',
   'CCDGAIN': '2.0',
   'DATE-OBS': '2002-04-13',
   'DETECTOR': 'HRC',
   'FILTER1': 'F555W',
   'FILTER2': 'CLEAR2S',
   'FW1OFFST': '0.0',
   'FW2OFFST': '0.0',
   'FWSOFFST': '0.0',
   'LTV1': '19.0',
   'LTV2': '0.0',
   'NAXIS1': '1062.0',
   'NAXIS2': '1044.0',
   'OBSTYPE': 'IMAGING',
   'TIME-OBS': '18:16:35'}

The above example uses an instrument context to determine the required
parameters to select best references for *all* filekinds.
