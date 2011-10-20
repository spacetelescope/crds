#!/usr/bin/env python
from distutils.core import setup

setup(name="crds.hst",
      version= "0.1",
      description="Python based Calibration Reference Data System,  best reference file maps for Hubble Space Telescope",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

      packages=[
        'crds.hst',

        'crds.hst.acs',
        'crds.hst.cos',
        'crds.hst.nicmos',
        'crds.hst.stis',
        'crds.hst.wfc3',
        'crds.hst.wfpc2',
        
        'crds.hst.gentools',

        'crds.mappings',
        'crds.mappings.hst',
        'crds.references',
        'crds.references.hst',
        
        ],

      package_dir = {
        'crds.hst':'.',

         'crds.hst.acs':'acs',
         'crds.hst.cos':'cos',
         'crds.hst.nicmos':'nicmos',
         'crds.hst.stis':'stis',
         'crds.hst.wfc3':'wfc3',
         'crds.hst.wfpc2':'wfpc2',

        'crds.hst.gentools' : 'gentools',
        
        'crds.mappings' : 'mappings',
        'crds.mappings.hst' : 'mappings/hst',
        'crds.references' : 'references',
        'crds.references.hst' : 'references/hst',
        },

      package_data = {

        '': [
            'cdbs.paths',
            'cdbs.paths.gz',
            'cdbs/cdbs_tpns/*.tpn',
            'cdbs/cdbs_tpns/cdbscatalog.dat',
            '*.dat',
            ],

        'crds.mappings.hst' : [
            '*.*map',
             ],
        },
    )
