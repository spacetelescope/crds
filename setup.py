#! /usr/bin/env python
import sys
import glob

from distutils.core import setup

setup_pars = {
    "packages" : [
        'crds',
        'crds.client',
        'crds.hst',
        'crds.jwst',
        'crds.tobs',
        'crds.tests',
        ],
    "package_dir" : {
        'crds' : 'crds',
        'crds.client' : 'crds/client',
        'crds.hst' : 'crds/hst',
        'crds.jwst' : 'crds/jwst',
        'crds.tobs' : 'crds/tobs',
        'crds.tests' : 'crds/tests',
        },
    "package_data" : {
        'crds.hst': [
            '*.dat',
            'tpns/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            ],
        'crds.jwst': [
            '*.dat',
            'tpns/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            ],
        'crds.tobs': [
            '*.dat',
            'tpns/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            ],
        },
    "scripts" : glob.glob("scripts/*"),
    }

import crds   #  local subdirectory...  ew...

setup(name="crds",
      provides=["crds","crds.hst","crds.jwst","crds.client","crds.tobs"],
      version=crds.__version__,
      description="Calibration Reference Data System,  HST/JWST reference file management",
      long_description=open('README.rst').read(),
      author="Todd Miller",
      author_email="jmiller@stsci.edu",
      url="https://hst-crds.stsci.edu",
      license="BSD",
      requires=["numpy","astropy"],
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      **setup_pars
      )
