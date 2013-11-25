#!/usr/bin/env python
import sys
import glob

from distutils.core import setup

subpkgs = {
    "crds": {
        "packages" : [
            'crds',
            'crds.client',
            'crds.hst',
            'crds.jwst',
            'crds.tobs',
            'crds.tests',
            'crds.cache',
            'crds.cache.mappings',
            'crds.cache.mappings.hst',
            'crds.cache.mappings.jwst',
            'crds.cache.mappings.tobs',
            'crds.cache.references',
            'crds.cache.references.hst',
            'crds.cache.references.jwst',
            'crds.cache.references.tobs',
            ],
        "package_dir" : {
            'crds' : 'crds',
            'crds.client' : 'crds/client',
            'crds.hst' : 'crds/hst',
            'crds.jwst' : 'crds/jwst',
            'crds.tobs' : 'crds/tobs',
            'crds.tests' : 'crds/tests',
            'crds.cache' : 'crds/cache',
            'crds.cache.mappings' : 'crds/cache/mapping',
            'crds.cache.mappings.hst' : 'crds/cache/mappings/hst',
            'crds.cache.mappings.jwst' : 'crds/cache/mappings/jwst',
            'crds.cache.mappings.tobs' : 'crds/cache/mappings/tobs',
            'crds.cache.references' : 'crds/cache/references',
            'crds.cache.references.hst' : 'crds/cache/references/hst',
            'crds.cache.references.jwst' : 'crds/cache/references/jwst',
            'crds.cache.references.tobs' : 'crds/cache/references/tobs',
            },
        "package_data" : {
            'crds.tests' : ['data/*.fits','data/*.*map'],
            'crds.hst': [
                'cdbs.paths.gz',
                'cdbs/cdbs_tpns/*.tpn',
                'cdbs/cdbs_tpns/*.rule',
                'cdbs/cdbs_tpns/cdbscatalog.dat',
                '*.dat',
                ],
            },
            'crds.jwst': [
                '*.dat',
                'tpns/*.tpn',
                ],
            'crds.tobs': [
                '*.dat',
                'tpns/*.tpn',
                ],
            'crds.cache.mappings.hst' : [
                '*.*map',
                ],
            'crds.cache.mappings.jwst' : [
                '*.*map',
                ],
            'crds.cache.mappings.tobs' : [
                '*.*map',
                ],
            },
        "scripts" : glob.glob("crds/scripts/*"),
        },
        "package_data" : {
            'crds.cache.mappings.tobs' : [
                '*.*map',
                ],
            'crds.cache.references.tobs' : [
                '*.*fits',
                ],
            },
        },
    }

installed_subpkgs = ["crds", "client", "tobs"]
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
