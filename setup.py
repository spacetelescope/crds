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
#         'crds.cache',
#         'crds.cache.mappings',
#         'crds.cache.mappings.hst',
#         'crds.cache.mappings.jwst',
#         'crds.cache.mappings.tobs',
#         'crds.cache.references',
#         'crds.cache.references.hst',
#         'crds.cache.references.jwst',
#         'crds.cache.references.tobs',
        ],
    "package_dir" : {
        'crds' : 'crds',
        'crds.client' : 'crds/client',
        'crds.hst' : 'crds/hst',
        'crds.jwst' : 'crds/jwst',
        'crds.tobs' : 'crds/tobs',
        'crds.tests' : 'crds/tests',
#         'crds.cache' : 'crds/cache',
#         'crds.cache.mappings' : 'crds/cache/mappings',
#         'crds.cache.mappings.hst' : 'crds/cache/mappings/hst',
#         'crds.cache.mappings.jwst' : 'crds/cache/mappings/jwst',
#         'crds.cache.mappings.tobs' : 'crds/cache/mappings/tobs',
#         'crds.cache.references' : 'crds/cache/references',
#         'crds.cache.references.hst' : 'crds/cache/references/hst',
#         'crds.cache.references.jwst' : 'crds/cache/references/jwst',
#         'crds.cache.references.tobs' : 'crds/cache/references/tobs',
        },
    "package_data" : {
        'crds.tests' : [
            'data/*.fits',
            'data/*.*map'
            ],
        'crds.hst': [
            '*.dat',
            'tpns/*.tpn',
            'cdbs.paths.gz',
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
#         'crds.cache.mappings.jwst' : [
#             '*.*map',
#             ],
#         'crds.cache.mappings.tobs' : [
#             '*.*map',
#             ],
        },
    "scripts" : glob.glob("crds/scripts/*"),
    }

setup(name="crds",
      version= "1.0",
      description="Python based Calibration Reference Data System,  best reference file",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",
      **setup_pars
      )
