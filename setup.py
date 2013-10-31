#!/usr/bin/env python
import sys
import glob

from distutils.core import setup

subpkgs = {
    "lib": {
        "packages" : [
            'crds',
            'crds.tests',
            ],
        "package_dir" : {
            'crds' : 'lib',
            'crds.tests': 'lib/tests',
            },
        "package_data" : {
            'crds.tests' : ['data/*.fits','data/*.*map'],
            },
        "scripts" : glob.glob("lib/scripts/*"),
        },
    "client" :{
        "packages" : [
            'crds.client',
            ],
        "package_dir" : {
            'crds.client':'client',
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
            'crds.hst':'hst',
            'crds.mappings' : 'hst/mappings',
            'crds.mappings.hst' : 'hst/mappings/hst',
            'crds.references' : 'hst/references',
            'crds.references.hst' : 'hst/references/hst',
            },
        "package_data" : {
            'crds.hst': [
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
            'crds.jwst':'jwst',
            'crds.mappings' : 'jwst/mappings',
            'crds.mappings.jwst' : 'jwst/mappings/jwst',
            'crds.references' : 'jwst/references',
            'crds.references.jwst' : 'jwst/references/jwst',
            },
        "package_data" : {
            'crds.jwst': [
                '*.dat',
                'tpns/*.tpn',
                ],
            'crds.mappings.jwst' : [
                '*.*map',
                ],
            },
        },
    "tobs": {
        "packages" : [
            'crds.tobs',
            'crds.tobs.tinstr',           
            'crds.mappings',
            'crds.mappings.tobs',
            'crds.references',
            'crds.references.tobs',
            ],

        "package_dir" : {
            'crds.tobs':'tobs',
            'crds.tobs.tinstr':'tobs/tinstr',
            'crds.mappings' : 'tobs/mappings',
            'crds.mappings.tobs' : 'tobs/mappings/tobs',
            'crds.references' : 'tobs/references',
            'crds.references.tobs' : 'tobs/references/tobs',
            },
        "package_data" : {
            'crds.tobs': [
                '*.dat',
                'tpns/*.tpn',
                ],
            'crds.mappings.tobs' : [
                '*.*map',
                ],
            'crds.references.tobs' : [
                '*.*fits',
                ],
            },
        }
    }

installed_subpkgs = ["lib", "client", "tobs"]
if "--hst" in sys.argv:
    sys.args.remove("--hst")
    installed_subpkgs.append("hst")
elif "--jwst" in sys.argv:
    sys.args.remove("--jwst")
    installed_subpkgs.append("jwst")
else:
    installed_subpkgs.extend(["hst","jwst"])

# Merge all the subpackage spaces into common parameter dict
setup_pars = {}
for sub in installed_subpkgs:
    for par,val in subpkgs[sub].items():
        if isinstance(val, dict):
            if not par in setup_pars:
                setup_pars[par] = {}
            setup_pars[par].update(val)
        elif isinstance(val, list):
            if not par in setup_pars:
                setup_pars[par] = []
            setup_pars[par].extend(val)
        else:
            raise ValueError("Unknown setup parameter type: {} {}".format(par, val)) 

setup(name="crds",
      version= "1.0",
      description="Python based Calibration Reference Data System,  best reference file",
      author="Todd Miller",
      author_email="jmiller@stsci.edu",
      **setup_pars
    )
