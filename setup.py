#!/usr/bin/env python
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
        'crds.tests' : [
            'data/*.fits',
            'data/*.*map'
            ],
        'crds.hst': [
            '*.dat',
            'cdbs.paths.gz',
            'tpns/*.tpn',
            'tpns/*.rule',
            'tpns/cdbscatalog.dat',
            ],
        'crds.jwst': [
            '*.dat',
            'tpns/*.tpn',
            ],
        'crds.tobs': [
            '*.dat',
            'tpns/*.tpn',
            ],
        'crds' : [
            'cache/mappings/hst/*.*map',
            'cache/mappings/jwst/*.*map',
            'cache/mappings/tobs/*.*map',
            ],
        },
    "scripts" : glob.glob("scripts/*"),
    }

setup(name="crds",
      provides=["crds","crds.hst","crds.jwst","crds.client","crds.tobs"],
      version="1.1",
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
          'Operating System :: OS-X, Linux', 
          'Programming Language :: Python :: 2.7',
          # 'Programming Language :: Python :: 3',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      **setup_pars
      )
