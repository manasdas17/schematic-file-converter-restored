#!/usr/bin/env python

from setuptools import setup

setup(
    name='python-upconvert',
    version='0.1',
    description='Upconvert library',
    packages=['upconvert', 'upconvert.core', 'upconvert.library', 'upconvert.library.fritzing', 'upconvert.library.kicad', 'upconvert.parser', 'upconvert.writer'],
)
