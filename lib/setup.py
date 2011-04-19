#!/usr/bin/env python
from distutils.core import setup

import pytools.stsci_distutils_hack as dh
f = open('svn_version.py', 'w' )
f.write("__svn_version__ = '%s'\n" % dh.__get_svn_rev__('.'))
f.write("\n__full_svn_info__ = '''\n%s'''\n\n" % dh.__get_full_info__('.'))
f.close()

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
