##############################################################################
#
# Copyright (c) 2008-2010 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" test_connection_basic: Basic tests for the LDAPConnection class

$Id$
"""

import unittest

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_ENCODED
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_UNICODE

class ConnectionBasicTests(LDAPConnectionTests):

    def test_conformance(self):
        # Test to see if the given class implements the ILDAPConnection
        # interface completely.
        from zope.interface.verify import verifyClass
        from dataflake.ldapconnection.interfaces import ILDAPConnection
        verifyClass(ILDAPConnection, self._getTargetClass())

    def test_constructor_defaults(self):
        conn = self._makeSimple()
        self.assertEqual(conn.bind_dn, u'')
        self.assertEqual(conn.bind_pwd, '')
        self.failIf(conn.read_only)
        self.assertEqual(conn._getConnection(), None)
        self.assertEqual(conn.c_factory, DummyLDAPObjectFactory)

    def test_constructor(self):
        bind_dn_encoded = 'cn=%s,dc=localhost' % ISO_8859_1_ENCODED
        bind_dn_unicode = u'cn=%s,dc=localhost' % ISO_8859_1_UNICODE
        conn = self._makeOne( 'localhost'
                            , 389
                            , 'ldap'
                            , 'factory'
                            , bind_dn=bind_dn_encoded
                            , bind_pwd='foo'
                            , read_only=True
                            , conn_timeout=5
                            , op_timeout=10
                            , logger='logger'
                            )
        self.assertEqual(conn.bind_dn, bind_dn_unicode)
        self.assertEqual(conn.bind_pwd, 'foo')
        self.failUnless(conn.read_only)
        self.assertEqual(conn._getConnection(), None)
        self.assertEqual(conn.c_factory, 'factory')
        self.assertEqual(conn.logger(), 'logger')


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

