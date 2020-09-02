#! /usr/bin/env python
import sys
import glob

from distutils.core import setup

import setuptools

setup_pars = {
    "packages" : [
        'crds',
        'crds.bestrefs',
        'crds.certify',
        'crds.certify.validators',
        'crds.client',
        'crds.core',
        'crds.io',
        'crds.submit',

        'crds.misc',
        'crds.misc.synphot',
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
        'crds.certify.validators' : 'crds/certify/validators',
        'crds.client' : 'crds/client',
        'crds.core' : 'crds/core',
        'crds.io' : 'crds/io',
        'crds.submit' : 'crds/submit',

        'crds.misc' : 'crds/misc',
        'crds.misc.synphot' : 'crds/misc/synphot',
        'crds.refactoring' : 'crds/refactoring',

        'crds.hst' : 'crds/hst',
        'crds.jwst' : 'crds/jwst',
        'crds.tobs' : 'crds/tobs',

        'crds.tests' : 'crds/tests',
        },
    "package_data" : {
        'crds.hst': [
            '*.dat',
            '*.yaml',
            '*.json',
            'tpns/*.tpn',
            'tpns/includes/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            'specs/*.json',
            ],
        'crds.jwst': [
            '*.dat',
            '*.yaml',
            '*.json',
            'tpns/*.tpn',
            'tpns/includes/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            'specs/*.json',
            ],
        'crds.tobs': [
            '*.dat',
            '*.yaml',
            '*.json',
            'tpns/*.tpn',
            'tpns/includes/*.tpn',
            'specs/*.spec',
            'specs/*.rmap',
            'specs/*.json',
            ],
        },
    "scripts" : glob.glob("scripts/*"),
    }

TEST_DEPS = ["lockfile", "mock", "nose", "pytest", "pylint", "flake8", "bandit",]

SUBMISSION_DEPS = ["requests", "lxml", "parsley"]

setup(name="crds",
      provides=["crds"],
      version = '7.6.0',
      description="Calibration Reference Data System,  HST/JWST reference file management",
      long_description=open('README.rst').read(),
      author="Todd Miller",
      author_email="jmiller@stsci.edu",
      url="https://hst-crds.stsci.edu",
      license="BSD",
      install_requires=["astropy", "numpy", "filelock"] + SUBMISSION_DEPS,
      extras_require={
          "jwst": ["jwst"],
          "submission": ["requests", "lxml", "parsley"],
          "dev" : ["ipython","jupyterlab","ansible","helm",
                   "nose-cprof", "coverage"],
          "test" : TEST_DEPS,
          "docs" : ["sphinx","sphinx_rtd_theme","docutils"],
          "aws" : ["boto3","awscli"],
          "synphot": ["stsynphot"],
      },
      tests_require=TEST_DEPS,
      zip_safe=False,
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Astronomy',
      ],
      **setup_pars
)
