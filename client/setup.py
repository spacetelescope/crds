#!/usr/bin/env python
from distutils.core import setup

import pytools.stsci_distutils_hack as dh
f = open('svn_version.py', 'w' )
f.write("__svn_version__ = '%s'\n" % dh.__get_svn_rev__('.'))
f.write("\n__full_svn_info__ = '''\n%s'''\n\n" % dh.__get_full_info__('.'))
f.close()

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
