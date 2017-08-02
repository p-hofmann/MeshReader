#!/usr/bin/env python

from setuptools import setup, find_packages
from meshlib import __author__ as author
from meshlib import __version__ as version

setup(
    name='MeshReader',
    version=version,
    description='Wrapper of 3D model file format readers',
    author=author,
    author_email='',
    url='https://github.com/p-hofmann/MeshReader',
    packages=find_packages(exclude=('unittest', '__pycache__')),
    )
