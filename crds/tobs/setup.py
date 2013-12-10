#!/usr/bin/env python
from distutils.core import setup

setup(name="crds.tobs",
      version= "0.1",
      description="Python based Calibration Reference Data System,  best reference file maps for James Web Space Telescope",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

      packages=[
        'crds.tobs',

        'crds.tobs.tinstr',

        'crds.mappings',
        'crds.mappings.tobs',
        'crds.references',
        'crds.references.tobs',
        
        ],

      package_dir = {
        'crds.tobs':'.',
        
        'crds.tobs.tinstr':'tinstr',
        
        'crds.mappings' : 'mappings',
        'crds.mappings.tobs' : 'mappings/tobs',
        'crds.references' : 'references',
        'crds.references.tobs' : 'references/tobs',
        },

      package_data = {

        '': [
            '*.dat',
            'tpns/*.tpn',

            ],

        'crds.mappings.tobs' : [
            '*.*map',
             ],
        'crds.references.tobs' : [
            '*.*fits',
             ],
        },
    )
