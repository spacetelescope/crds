#!/usr/bin/env python
from distutils.core import setup

setup(name="crds",
      version= "0.1",
      description="Python based Calibration Reference Data System,  best reference file",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

      packages=[
        'crds',
        'crds.tests',
        ],

      package_dir = {
        'crds' : '.',
        'crds.tests': 'tests',
        },

      package_data = {
        'crds.tests' : ['data/*.fits'],
        }
    )
