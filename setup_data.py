#!/usr/bin/env python
import sys
import glob

from distutils.core import setup

setup_pars = {
    "packages" : [
        'crds',
        'crds.tests',
        ],
    "package_dir" : {
        'crds' : 'crds',
        'crds.tests' : 'crds/tests',
        },
    "package_data" : {
            'crds.tests' : [
                'data/*',
                ],
        },
    }

import crds   #  local subdirectory...  ew...

setup(name="crds_test_data",
      provides=["crds.tests.data",],
      version=crds.__version__,
      description="Calibration Reference Data System,  HST/JWST reference file management (test data)",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",
      url="https://hst-crds.stsci.edu",
      license="BSD",
      requires=["numpy","astropy"],
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS-X, Linux',
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      **setup_pars
      )
