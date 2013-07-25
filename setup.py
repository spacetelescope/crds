#!/usr/bin/env python
from distutils.core import setup

    subpkgs = {
      "lib": {
            "packages" = [
                'crds',
                'crds.tests',
                ],
            "package_dir" = {
                'crds' : '.',
                'crds.tests': 'tests',
                },
            "package_data" = {
                'crds.tests' : ['data/*.fits','data/*.*map'],
                }
            },
      "client" :{
            "packages" : [
                'crds.client',
                ],
            "package_dir" : {
                'crds.client':'.',
                },
            "package_data" : {
                },
            },
      "hst" : {
            "packages" : [
                'crds.hst',
                'crds.mappings',
                'crds.mappings.hst',
                'crds.references',
                'crds.references.hst',
                ],
            "package_dir" : {
                'crds.hst':'.',
                'crds.mappings' : 'mappings',
                'crds.mappings.hst' : 'mappings/hst',
                'crds.references' : 'references',
                'crds.references.hst' : 'references/hst',
                },
            "package_data" : {
                '': [
                    'cdbs.paths',
                    'cdbs.paths.gz',
                    'cdbs/cdbs_tpns/*.tpn',
                    'cdbs/cdbs_tpns/*.rule',
                    'cdbs/cdbs_tpns/cdbscatalog.dat',
                    '*.dat',
                    ],
                'crds.mappings.hst' : [
                    '*.*map',
                    ],
                },
            },
      "jwst" : {
            "packages" : [
                'crds.jwst',
                'crds.mappings',
                'crds.mappings.jwst',
                'crds.references',
                'crds.references.jwst',
                ],
            "package_dir" : {
                'crds.jwst':'.',
                'crds.mappings' : 'mappings',
                'crds.mappings.jwst' : 'mappings/jwst',
                'crds.references' : 'references',
                'crds.references.jwst' : 'references/jwst',
                },
            "package_data" : {
                '': [
                    '*.dat',
                    'tpns/*.tpn',
                    ],
                'crds.mappings.jwst' : [
                    '*.*map',
                    ],
                'crds.references.jwst' : [
                    '*.*fits',
                    ],
                },
            },
      }


setup(name="crds",
      version= "0.1",
      description="Python based Calibration Reference Data System,  best reference file",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",

    )
