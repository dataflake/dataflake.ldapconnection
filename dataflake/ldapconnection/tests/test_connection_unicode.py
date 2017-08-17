# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" test_connection_unicode: Tests for the LDAPConnection Unicode support
"""

import six
import unittest

from dataflake.fakeldap.utils import hash_pwd

from dataflake.ldapconnection.tests.base import LDAPConnectionTests


@unittest.skipIf(six.PY3, 'Not supported in Python 3')
class UnicodeSupportTests(LDAPConnectionTests):

    def test_search_unicode_results(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': 'Bjørn'}
        conn.insert('dc=localhost', 'cn=føø', attrs=attrs)

        response = conn.search('dc=localhost', fltr='(cn=føø)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=f\xf8\xf8,dc=localhost',
                          'cn': [u'f\xf8\xf8'],
                          'displayName': [u'Bj\xf8rn']})

    def test_search_raw_results(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': 'Bjørn'}
        conn.insert('dc=localhost', 'cn=føø', attrs=attrs)

        response = conn.search('dc=localhost', fltr='(cn=føø)', raw=True)
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': 'cn=føø,dc=localhost',
                          'cn': ['føø'],
                          'displayName': ['Bjørn']})

    def test_insert_unicode_data(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': u'Bjørn'}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)

        response = conn.search(u'dc=localhost', fltr=u'(cn=føø)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=føø,dc=localhost',
                          'cn': [u'føø'],
                          'displayName': [u'Bjørn']})

    def test_modify_unicode_data(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': u'Bjørn'}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)
        attrs = {'displayName': u'Bjørn Åge'}
        conn.modify(u'cn=føø,dc=localhost', attrs=attrs)

        response = conn.search(u'dc=localhost', fltr=u'(cn=føø)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=føø,dc=localhost',
                          'cn': [u'føø'],
                          'displayName': [u'Bjørn Åge']})

    def test_modify_multivalued_unicode_data(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'cn': [u'føø', u'Bjørn Åge']}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)
        attrs = {'cn': [u'føø', u'Bjørn', u'Bjørn Åge']}
        conn.modify(u'cn=føø,dc=localhost', attrs=attrs)
        attrs = {'cn': [u'føø', u'Bjørn']}
        conn.modify(u'cn=føø,dc=localhost', attrs=attrs)

        response = conn.search(u'dc=localhost', fltr=u'(cn=føø)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=føø,dc=localhost',
                          'cn': [u'føø', u'Bjørn']})

        response = conn.search(u'dc=localhost', fltr=u'(cn=Bjørn)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=føø,dc=localhost',
                          'cn': [u'føø', u'Bjørn']})

        response = conn.search(u'dc=localhost', fltr=u'(cn=Bjørn Åge)')
        self.assertEqual(response['size'], 0)

    def test_modify_unicode_rdn(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': u'Bj\xf8rn', 'cn': u'f\xf8\xf8'}
        conn.insert(u'dc=localhost', u'cn=f\xf8\xf8', attrs=attrs)
        attrs = {'cn': u'b\xe5r'}
        conn.modify(u'cn=f\xf8\xf8,dc=localhost', attrs=attrs)

        response = conn.search(u'dc=localhost', fltr=u'(cn=b\xe5r)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=b\xe5r,dc=localhost',
                          'cn': [u'b\xe5r'],
                          'displayName': [u'Bj\xf8rn']})

    def test_modify_multivalued_unicode_rdn(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': u'Bj\xf8rn', 'cn': [u'f\xf8\xf8', u'Bj\xf8rn']}
        conn.insert(u'dc=localhost', u'cn=f\xf8\xf8', attrs=attrs)
        attrs = {'cn': [u'b\xe5r', u'Bj\xf8rn']}
        conn.modify(u'cn=f\xf8\xf8,dc=localhost', attrs=attrs)

        response = conn.search(u'dc=localhost', fltr=u'(cn=b\xe5r)')
        self.assertEqual(response['size'], 1)

        results = response['results']
        self.assertEqual(results[0],
                         {'dn': u'cn=b\xe5r,dc=localhost',
                          'cn': [u'b\xe5r', u'Bj\xf8rn'],
                          'displayName': [u'Bj\xf8rn']})

    def test_delete_by_unicode_dn(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'displayName': u'Bjørn'}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)
        conn.delete(u'cn=føø,dc=localhost')

        response = conn.search(u'dc=localhost', fltr=u'(cn=føø)')
        self.assertEqual(response['size'], 0)

    def test_bind_with_valid_unicode_credentials(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'userPassword': hash_pwd('secret')}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)

        response = conn.search(u'dc=localhost', fltr=u'(cn=føø)',
                               bind_dn=u'cn=føø,dc=localhost',
                               bind_pwd=u'secret')
        self.assertEqual(response['size'], 1)

    def test_bind_with_invalid_unicode_credentials(self):
        import ldap
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'userPassword': hash_pwd('secret')}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)

        self.assertRaises(ldap.INVALID_CREDENTIALS, conn.search,
                          u'dc=localhost', fltr=u'(cn=føø)',
                          bind_dn=u'cn=føø,dc=localhost',
                          bind_pwd=u'geheim')

    def test_bind_with_valid_unicode_credentials_from_connection(self):
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'userPassword': hash_pwd('secret')}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)

        conn.bind_dn = u'cn=føø,dc=localhost'
        conn.bind_pwd = u'secret'
        response = conn.search(u'dc=localhost', fltr=u'(cn=føø)')
        self.assertEqual(response['size'], 1)

    def test_bind_with_invalid_unicode_credentials_from_connection(self):
        import ldap
        conn = self._makeSimple()
        conn.api_encoding = None

        attrs = {'userPassword': hash_pwd('secret')}
        conn.insert(u'dc=localhost', u'cn=føø', attrs=attrs)

        conn.bind_dn = u'cn=føø,dc=localhost'
        conn.bind_pwd = u'geheim'
        self.assertRaises(ldap.INVALID_CREDENTIALS, conn.search,
                          u'dc=localhost', fltr=u'(cn=føø)')
