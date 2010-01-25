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
""" test_connection_connect: Tests for the LDAPConnection connect method

$Id$
"""

import unittest

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ErrorLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_ENCODED
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_UNICODE

class ConnectionConnectTests(LDAPConnectionTests):

    def test_connect_initial_noargs(self):
        conn = self._makeSimple()
        conn = conn.connect()
        self.assertEqual(conn.binduid, u'')
        self.assertEqual(conn.bindpwd, '')

    def test_connect_initial_bind_dn_not_None(self):
        conn = self._makeSimple()
        bind_dn_apiencoded = 'cn=%s,dc=localhost' % ISO_8859_1_ENCODED
        bind_dn_unicode = u'cn=%s,dc=localhost' % ISO_8859_1_UNICODE
        bind_dn_serverencoded = bind_dn_unicode.encode(conn.ldap_encoding)
        conn = conn.connect(bind_dn_apiencoded, '')
        self.assertEqual(conn.binduid, bind_dn_serverencoded)
        self.assertEqual(conn.bindpwd, '')

    def test_connect_non_initial(self):
        conn = self._makeSimple()
        connection = conn.connect('cn=foo,dc=localhost', 'pass')
        self.assertEqual(connection.binduid, 'cn=foo,dc=localhost')
        connection = conn.connect(None, 'pass')
        self.assertEqual(connection.binduid, conn.bind_dn)

    def test_connect_setting_timeout(self):
        conn = self._makeSimple()
        connection = conn.connect()
        self.failIf(getattr(connection, 'timeout', 0))

        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, op_timeout=99)
        connection = conn.connect()
        self.assertEquals(connection.timeout, 99)

    def test_connect_noserver_raises(self):
        conn = self._makeSimple()
        conn.removeServer('host', '636', 'ldap')
        self.assertRaises(RuntimeError, conn.connect)

    def test_connect_ldaperror_raises(self):
        import ldap
        of = ErrorLDAPObjectFactory('conn_string')
        of.setException(ldap.SERVER_DOWN)
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, conn_timeout=1)
        self.assertRaises(ldap.SERVER_DOWN, conn.connect)


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

