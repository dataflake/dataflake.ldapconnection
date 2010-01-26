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
""" test_connection_insert: Tests for the LDAPConnection insert method

$Id$
"""

import unittest

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_ENCODED
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_UTF8

class ConnectionInsertTests(LDAPConnectionTests):

    def test_insert_noauthentication(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=jens', attrs={})
        connection = conn._getConnection()
        self.assertEqual(connection.binduid, '')
        self.assertEqual(connection.bindpwd, '')

    def test_insert_authentication(self):
        conn = self._makeSimple()
        bind_dn_apiencoded = 'cn=%s,dc=localhost' % ISO_8859_1_ENCODED
        bind_dn_serverencoded = 'cn=%s,dc=localhost' % ISO_8859_1_UTF8
        conn.insert( 'dc=localhost'
                   , 'cn=jens'
                   , attrs={}
                   , bind_dn=bind_dn_apiencoded
                   , bind_pwd='foo'
                   )
        connection = conn._getConnection()
        self.assertEqual(connection.binduid, bind_dn_serverencoded)
        self.assertEqual(connection.bindpwd, 'foo')

    def test_insert(self):
        attributes = { 'cn' : 'jens'
                     , 'multivaluestring' : 'val1;val2;val3'
                     , 'multivaluelist' : ['val1', 'val2']
                     }
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=jens', attrs=attributes)
        connection = conn._getConnection()
        self.failUnless(connection.added)
        self.assertEqual(len(connection.added_values.keys()), 1)
        dn, values = connection.added_values.items()[0]
        self.assertEqual(dn, 'cn=jens' + ',' + 'dc=localhost')
        self.assertEqual(values['cn'], ['jens'])
        self.assertEqual(values['multivaluestring'], ['val1','val2','val3'])
        self.assertEqual(values['multivaluelist'], ['val1','val2'])

    def test_insert_readonly(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory, read_only=True)
        self.assertRaises(RuntimeError, conn.insert, 'dc=localhost', 'cn=jens')

    def test_insert_referral(self):
        import ldap
        of = DummyLDAPObjectFactory('conn_string')
        of.add_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string, who='', cred=''):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.insert('dc=localhost', 'cn=jens', attrs={'cn':['jens']})
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')
        self.failUnless(of.added)
        self.assertEqual(len(of.added_values.keys()), 1)
        dn, values = of.added_values.items()[0]
        self.assertEqual(dn, 'cn=jens' + ',' + 'dc=localhost')
        self.assertEqual(values['cn'], ['jens'])

    def test_insert_binary(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=jens', {'myvalue;binary' : u'a'})
        connection = conn._getConnection()
        self.failUnless(connection.added)
        self.assertEqual(len(connection.added_values.keys()), 1)
        dn, values = connection.added_values.items()[0]
        self.assertEqual(values['myvalue'], u'a')


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

