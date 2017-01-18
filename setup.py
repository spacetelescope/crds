#! /usr/bin/env python
import sys
import glob

from distutils.core import setup

setup_pars = {
    "packages" : [
        'crds',
        'crds.bestrefs',
        'crds.certify',
        'crds.client',
        'crds.core',
        'crds.submit',

        'crds.misc',
        'crds.refactoring',

        'crds.hst',
        'crds.jwst',
        'crds.tobs',

        'crds.tests',
        ],
    "package_dir" : {
        'crds' : 'crds',
        'crds.bestrefs' : 'crds/bestrefs',
        'crds.certify' : 'crds/certify',
        'crds.client' : 'crds/client',
        'crds.core' : 'crds/core',
        'crds.submit' : 'crds/submit',

        'crds.misc' : 'crds/misc', 
        'crds.refactoring' : 'crds/refactoring', 

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
            'specs/*.json',
            ],
        'crds.jwst': [
            '*.dat',
            'tpns/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            'specs/*.json',
            ],
        'crds.tobs': [
            '*.dat',
            'tpns/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            'specs/*.json',
            ],
        },
    "scripts" : glob.glob("scripts/*"),
    }

import crds   #  local subdirectory...  ew...

setup(name="crds",
      provides=["crds", "crds.client", "crds.core",
                
                "crds.hst","crds.jwst", "crds.tobs",
                
                "crds.bestrefs", "crds.certify",

                "crds.misc", "crds.refactoring",
                
                "crds.tests"
      ],
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

