# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in b2b_marketing/__init__.py
from b2b_marketing import __version__ as version

setup(
	name='b2b_marketing',
	version=version,
	description='marketing',
	author='Dexciss',
	author_email='dexciss@info.com',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
