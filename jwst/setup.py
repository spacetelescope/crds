#!/usr/bin/env python
from distutils.core import setup

setup(name="crds.jwst",
      version= "0.1",
      description="Python based Calibration Reference Data System,  best reference file maps for James Web Space Telescope",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

      packages=[
        'crds.jwst',

        'crds.jwst.miri',
        'crds.jwst.nirspec',
        'crds.jwst.nircam',

        'crds.mappings',
        'crds.mappings.jwst',
        'crds.references',
        'crds.references.jwst',
        
        ],

      package_dir = {
        'crds.jwst':'.',
        
        'crds.jwst.miri':'miri',
        'crds.jwst.nirspec':'nirspec',
        'crds.jwst.nircam':'nircam',
        
        'crds.mappings' : 'mappings',
        'crds.mappings.jwst' : 'mappings/jwst',
        'crds.references' : 'references',
        'crds.references.jwst' : 'references/jwst',
        },

      package_data = {

        '': [
            '*.dat',
            'tpns/*.tpn',

            ],

        'crds.mappings.jwst' : [
            '*.*map',
             ],
        },
    )
