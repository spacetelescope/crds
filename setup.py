#! /usr/bin/env python
import glob

from setuptools import setup

setup(
    scripts=glob.glob("scripts/*"),
)
