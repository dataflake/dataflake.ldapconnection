##############################################################################
#
# Copyright (c) 2008-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os
from setuptools import find_packages
from setuptools import setup


NAME = 'dataflake.ldapconnection'
_boundary = '\n' + ('-' * 60) + '\n\n'
_dl = 'Download\n========'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name=NAME,
      version=read('version.txt').strip(),
      description='LDAP connection library',
      long_description=(read('README.txt') + _boundary + _dl),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: \
            Authentication/Directory :: LDAP",
        ],
      keywords='ldap ldapv3',
      author="Agendaless Consulting and Jens Vagelpohl",
      author_email="jens@dataflake.org",
      url="http://pypi.python.org/pypi/%s" % NAME,
      license="ZPL 2.1",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      tests_require=[
        'python-ldap>=2.3.0',
        'dataflake.cache',
        'dataflake.fakeldap',
        ],
      install_requires=[
        'setuptools',
        'python-ldap>=2.3.0',
        'zope.interface',
        'dataflake.cache',
        'dataflake.fakeldap',
        ],
      test_suite='%s.tests' % NAME,
      extras_require={
        'docs': ['sphinx', 'repoze.sphinx.autointerface'],
        'testing': ['nose', 'coverage'],
        },
      )
