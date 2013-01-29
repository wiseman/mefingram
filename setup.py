#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup


PACKAGE_NAME = 'mefingram'
VERSION = '0.0.1'


settings = dict(
  name=PACKAGE_NAME,
  version=VERSION,
  description='Metafilter infodump n-gram tools.',
  long_description='woo',
  author='John Wiseman',
  author_email='jjwiseman@gmail.com',
  url='https://github.com/jjwiseman/mefingram',
  packages=['mefingram'],
  install_requires=[
    'python-gflags',
    'mrjob',
    'nltk'],
  license='MIT',
  classifiers=(
    # 'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Natural Language :: English',
    'Programming Language :: Python',
    # 'Programming Language :: Python :: 2.5',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    ),
  entry_points={
    'console_scripts': [
      'legit = legit.cli:main',
      ],
    },
  )


setup(**settings)
