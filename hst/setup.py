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
        'crds.hst.wfc3',
        'crds.hst.cos',
        'crds.hst.stis',

        'crds.hst.gentools',
        ],

      package_dir = {
        'crds.hst':'.',

        'crds.hst.acs':'acs',
        'crds.hst.cos':'cos',
        'crds.hst.stis':'stis',
        'crds.hst.wfc3':'wfc3',

        'crds.hst.gentools' : 'gentools',
        },

      package_data = {

        '': [

            '*.pmap',
            'cdbs.paths',
            'cdbs.paths.gz',

            'acs/*.rmap',
            'acs/*.imap',

            'cos/*.rmap',
            'cos/*.imap',

            'stis/*.rmap',
            'stis/*.imap',

            'wfc3/*.rmap',
            'wfc3/*.imap',

            'cdbs/cdbs_tpns/*.tpn',

             'gentools/header_cache',

            ],
        },
    )
