#!/usr/bin/env python
from distutils.core import setup

setup(name="crds",
      version= "0.1",
      description="Python based Calibration Reference Data System,  best reference file",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

      packages=[
        'crds',
        ],

      package_dir = {
        'crds' : '.',
        },

      package_data = {
#        'crds.hst.acs.rmaps': [ 'hst/acs/rmaps/*.rmap' ],
        }
    )
