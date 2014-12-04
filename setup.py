# -*- coding: utf-8 -*-
"""Setup script."""

import os
from setuptools import setup, find_packages

setup(
    name='gifts2',
    version='1.0',
    author="JM Ibanez",
    author_email="jm@teamcodeflux.com",
    description="Exchange Gifts 2",
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    install_requires=[
        'flask',
        'jinja2',
        'werkzeug',
    ],
    zip_safe=False,
)
