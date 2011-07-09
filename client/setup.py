#!/usr/bin/env python
from distutils.core import setup

setup(name="crds.client",
      version= "0.1",
      description="Python based Calibration Reference Data System,  client module for accessing web service",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

      packages=[
        'crds.client',
        ],

      package_dir = {
        'crds.client':'.',
        },

      package_data = {

        # '': ['acs/*.rmap',
        #     'cos/*.rmap' ,
        #     'stis/*.rmap',
        #     'wfc3/*.rmap',
        #     'cdbs_data/*.tpn'
        #     ],
        },
    )
