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
""" test_connection_basic: Basic tests for the LDAPConnection class
"""

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import UNENCODED_GREEK
from dataflake.ldapconnection.tests.dummy import UNENCODED_LATIN1
from dataflake.fakeldap import FakeLDAPConnection


class ConnectionBasicTests(LDAPConnectionTests):

    def test_conformance(self):
        # Test to see if the given class implements the ILDAPConnection
        # interface completely.
        from zope.interface.verify import verifyClass
        from dataflake.ldapconnection.interfaces import ILDAPConnection
        verifyClass(ILDAPConnection, self._getTargetClass())

    def test_constructor_defaults(self):
        conn = self._makeSimple()
        self.assertTrue(isinstance(conn.bind_dn, str))
        self.assertEqual(conn.bind_dn, '')
        self.assertEqual(conn.bind_pwd, '')
        self.failIf(conn.read_only)
        self.assertEqual(conn._getConnection(), None)
        self.assertEqual(conn.c_factory, FakeLDAPConnection)
        self.assertEqual(conn.ldap_encoding.lower(), 'utf-8')
        self.assertEqual(conn.api_encoding.lower(), 'utf-8')

    def test_constructor(self):
        bind_dn = u'cn=%s,dc=localhost' % UNENCODED_LATIN1
        bind_dn_encoded = bind_dn.encode('ISO-8859-1')
        conn = self._makeOne('localhost', 389, 'ldap', 'factory',
                             bind_dn=bind_dn_encoded, bind_pwd='foo',
                             read_only=True, conn_timeout=5,
                             op_timeout=10, logger='logger',
                             ldap_encoding='', api_encoding='latin-1')
        self.assertTrue(isinstance(conn.bind_dn, str))
        self.assertEqual(conn.bind_dn, bind_dn_encoded)
        self.assertEqual(conn.bind_pwd, 'foo')
        self.failUnless(conn.read_only)
        self.assertEqual(conn._getConnection(), None)
        self.assertEqual(conn.c_factory, 'factory')
        self.assertEqual(conn.logger(), 'logger')
        self.assertEqual(conn.ldap_encoding, '')
        self.assertEqual(conn.api_encoding, 'latin-1')

    def test_constructor_unicode_bind_dn(self):
        bind_dn_unicode = u'cn=%s,dc=localhost' % UNENCODED_LATIN1
        conn = self._makeOne('localhost', 389, 'ldap', 'factory',
                             bind_dn=bind_dn_unicode, bind_pwd='foo')
        self.assertTrue(isinstance(conn.bind_dn, unicode))
        self.assertEqual(conn.bind_dn, bind_dn_unicode)

    def test_encode_incoming(self):
        conn = self._makeSimple()

        self.assertEqual(conn._encode_incoming(None), None)

        conn.api_encoding = None
        conn.ldap_encoding = None
        self.assertEqual(conn._encode_incoming(UNENCODED_GREEK),
                         UNENCODED_GREEK)

        conn.api_encoding = 'iso-8859-7'
        conn.ldap_encoding = None
        result = conn._encode_incoming(UNENCODED_GREEK.encode('iso-8859-7'))
        self.assertEqual(result, UNENCODED_GREEK)

        conn.api_encoding = None
        conn.ldap_encoding = 'iso-8859-7'
        self.assertEqual(conn._encode_incoming(UNENCODED_GREEK),
                         UNENCODED_GREEK.encode('iso-8859-7'))

        conn.api_encoding = 'iso-8859-7'
        conn.ldap_encoding = 'UTF-8'
        result = conn._encode_incoming(UNENCODED_GREEK.encode('iso-8859-7'))
        self.assertEqual(result, UNENCODED_GREEK.encode('UTF-8'))

    def test_encode_outgoing(self):
        conn = self._makeSimple()

        self.assertEqual(conn._encode_outgoing(None), None)

        conn.api_encoding = None
        conn.ldap_encoding = None
        self.assertEqual(conn._encode_outgoing(UNENCODED_GREEK),
                         UNENCODED_GREEK)

        conn.api_encoding = 'iso-8859-7'
        conn.ldap_encoding = None
        self.assertEqual(conn._encode_outgoing(UNENCODED_GREEK),
                         UNENCODED_GREEK.encode('iso-8859-7'))

        conn.api_encoding = None
        conn.ldap_encoding = 'iso-8859-7'
        result = conn._encode_outgoing(UNENCODED_GREEK.encode('iso-8859-7'))
        self.assertEqual(result, UNENCODED_GREEK)

        conn.api_encoding = 'iso-8859-7'
        conn.ldap_encoding = 'UTF-8'
        result = conn._encode_outgoing(UNENCODED_GREEK.encode('UTF-8'))
        self.assertEqual(result, UNENCODED_GREEK.encode('iso-8859-7'))
