##############################################################################
#
# Copyright (c) 2008 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" test_fakeldap: Tests for the FakeLDAP testing fixture

$Id$
"""

import doctest
import unittest

from dataflake.ldapconnection.tests import fakeldap

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(fakeldap))
    return suite
