#!/usr/bin/env python

"""Setup script for qc."""

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


setup(
  name = 'qc',
  version = '0.1',
  description = 'QuickCheck: randomized testing made trivial.',
  author = 'Peter Scott',
  author_email = 'peter@greplin.com',
  url = 'https://github.com/Greplin/qc',
  package_dir = {'':'src'},
  packages = ['qc'],
  zip_safe = True,
  test_suite = 'nose.collector',
  include_package_data = True,
  license = 'Apache',
)
