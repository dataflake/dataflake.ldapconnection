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
""" test_connection_insert: Tests for the LDAPConnection insert method
"""

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import UNENCODED_LATIN1


class ConnectionInsertTests(LDAPConnectionTests):

    def test_insert_noauthentication(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=jens', attrs={})
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, '')
        self.assertEqual(bindpwd, '')

    def test_insert_authentication(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             api_encoding='iso-8859-1')
        bind_dn = u'cn=%s,dc=localhost' % UNENCODED_LATIN1
        bind_dn_apiencoded = bind_dn.encode('iso-8859-1')
        bind_dn_serverencoded = bind_dn.encode('UTF-8')
        self._addRecord(bind_dn_serverencoded, userPassword='foo')
        conn.insert('dc=localhost', 'cn=jens', attrs={},
                    bind_dn=bind_dn_apiencoded, bind_pwd='foo')
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, bind_dn_serverencoded)
        self.assertEqual(bindpwd, 'foo')

    def test_insert(self):
        attributes = {'cn': 'jens',
                      'multivaluestring': 'val1;val2;val3',
                      'multivaluelist': ['val1', 'val2']}
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=jens', attrs=attributes)

        results = conn.search('dc=localhost', fltr='(cn=jens)')
        self.assertEqual(len(results['results']), 1)
        self.assertEqual(results['size'], 1)

        record = results['results'][0]
        self.assertEqual(record['dn'], 'cn=jens,dc=localhost')
        self.assertEqual(record['cn'], ['jens'])
        self.assertEqual(record['multivaluestring'],
                         ['val1', 'val2', 'val3'])
        self.assertEqual(record['multivaluelist'], ['val1', 'val2'])

    def test_insert_readonly(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             read_only=True)
        self.assertRaises(RuntimeError, conn.insert, 'dc=localhost',
                          'cn=jens')

    def test_insert_referral(self):
        import ldap
        exc_arg = {'info': 'please go to ldap://otherhost:1389'}
        conn, ldap_connection = self._makeRaising('add_s', ldap.REFERRAL,
                                                  exc_arg)
        conn.insert('dc=localhost', 'cn=jens', attrs={'cn': ['jens']})
        self.assertEqual(ldap_connection.conn_string, 'ldap://otherhost:1389')
        self.assertEqual(ldap_connection.args,
                         ('cn=jens,dc=localhost', [('cn', ['jens'])]))

    def test_insert_binary(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=jens', {'objectguid;binary': u'a'})

        results = conn.search('dc=localhost', fltr='(cn=jens)')
        self.assertEqual(len(results['results']), 1)
        self.assertEqual(results['size'], 1)

        record = results['results'][0]
        self.assertEqual(record['objectguid'], u'a')
