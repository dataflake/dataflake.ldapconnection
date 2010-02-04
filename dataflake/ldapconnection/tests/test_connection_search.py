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
""" test_connection_search: Tests for the LDAPConnection search method

$Id$
"""

import unittest

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_ENCODED
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_UTF8

class ConnectionSearchTests(LDAPConnectionTests):

    def test_search_noauthentication(self):
        conn = self._makeSimple()
        response = conn.search('o=base', 'scope')
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, u'')
        self.assertEqual(bindpwd, '')

    def test_search_authentication(self):
        conn = self._makeSimple()
        bind_dn_apiencoded = 'cn=%s,dc=localhost' % ISO_8859_1_ENCODED
        bind_dn_serverencoded = 'cn=%s,dc=localhost' % ISO_8859_1_UTF8
        self._addRecord(bind_dn_serverencoded, userPassword='foo')
        response = conn.search( 'dc=localhost'
                              , 'scope'
                              , bind_dn=bind_dn_apiencoded
                              , bind_pwd='foo'
                              )
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, bind_dn_serverencoded)
        self.assertEqual(bindpwd, 'foo')

    def test_search_simple(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo', attrs={'a':'a','b':['x','y','z']})
        response = conn.search('dc=localhost', fltr='(cn=foo)')
        self.assertEqual(response['size'], 1)
        self.assertEqual(len(response['results']), 1)
        self.assertEqual( response['results'][0]
                        , { 'a': ['a']
                          , 'dn': 'cn=foo,dc=localhost'
                          , 'cn': ['foo']
                          , 'b': ['x', 'y', 'z']
                          }
                        )

    def test_search_nonascii(self):
        conn = self._makeSimple()
        attrs = {'a': [ISO_8859_1_ENCODED], 'b': ISO_8859_1_ENCODED }
        conn.insert('dc=localhost', 'cn=foo', attrs=attrs)
        response = conn.search('dc=localhost', fltr='(cn=foo)')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual( results[0]
                        , { 'dn': 'cn=foo,dc=localhost'
                          , 'a': [ISO_8859_1_ENCODED]
                          , 'b': [ISO_8859_1_ENCODED]
                          , 'cn': ['foo']
                          }
                        )

    def test_search_bad_results(self):
        # Make sure the resultset omits "useless" entries that may be
        # emitted by some servers, notable Microsoft ActiveDirectory.
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'})
                 , ('dn2',['thisvalueisuseless']) 
                 , ('dn3','anotheruselessvalue')
                 , ('dn4', ('morebadstuff',))
                 ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('o=base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_partial_results(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.partial = (None, [('dn', {'a':'a'})])
        import ldap
        of.search_exc = (ldap.PARTIAL_RESULTS, '')
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('o=base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        import ldap
        of.search_exc = ( ldap.REFERRAL
                        , {'info':'please go to ldap://otherhost:1389'}
                        )
        def factory(conn_string, who='', cred=''):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('o=base', 'scope')
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')

    def test_search_bad_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        import ldap
        of.search_exc = ( ldap.REFERRAL
                        , {'info':'please go to BAD_URL'}
                        )
        def factory(conn_string, who='', cred=''):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        self.assertRaises(ldap.CONNECT_ERROR, conn.search, 'o=base', 'scope')

    def test_search_binaryattribute(self):
        # A binary value will remain untouched, no transformation 
        # to and from UTF-8 will happen.
        conn = self._makeSimple()
        attrs = {'objectguid;binary':u'a'}
        conn.insert('dc=localhost', 'cn=foo', attrs=attrs)
        response = conn.search('dc=localhost', fltr='(cn=foo)')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual( results[0]
                        , { 'dn': 'cn=foo,dc=localhost'
                          , 'cn': ['foo']
                          , 'objectguid': u'a'
                          }
                        )


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

