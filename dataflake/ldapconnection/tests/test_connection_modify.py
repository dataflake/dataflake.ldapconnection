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
""" test_connection_modify: Tests for the LDAPConnection modify method
"""

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import UNENCODED_LATIN1


class ConnectionModifyTests(LDAPConnectionTests):

    def test_modify_noauthentication(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo')
        import ldap
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_ADD,
                    attrs={'b': 'b'})
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, b'')
        self.assertEqual(bindpwd, b'')

    def test_modify_authentication(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             api_encoding='iso-8859-1')
        conn.insert('dc=localhost', 'cn=foo')
        bind_dn = u'cn=%s,dc=localhost' % UNENCODED_LATIN1
        bind_dn_apiencoded = bind_dn.encode('iso-8859-1')
        bind_dn_serverencoded = bind_dn.encode('UTF-8')
        self._addRecord(bind_dn_serverencoded, userPassword='foo', cn='foo')
        import ldap
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_ADD,
                    attrs={'b': 'b'}, bind_dn=bind_dn_apiencoded,
                    bind_pwd='foo')
        connection = conn._getConnection()
        binduid, bindpwd = connection._last_bind[1]
        self.assertEqual(binduid, bind_dn_serverencoded)
        self.assertEqual(bindpwd, b'foo')

    def test_modify_explicit_add(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo')
        import ldap
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_ADD,
                    attrs={'b': 'b'})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'b'], [b'b'])

        # Trying to add an empty new value should not cause more operations
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_ADD,
                    attrs={'c': ''})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertFalse(rec.get(b'c'))

    def test_modify_explicit_modify(self):
        attrs = {'a': 'a', 'b': ['x', 'y', 'z']}
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo', attrs=attrs)
        import ldap
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_REPLACE,
                    attrs={'a': 'y', 'b': ['f', 'g', 'h']})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'a'], [b'y'])
        self.assertEqual(rec[b'b'], [b'f', b'g', b'h'])

    def test_modify_explicit_delete(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo',
                    attrs={'a': 'a', 'b': ['b', 'c']})

        import ldap
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_DELETE,
                    attrs={'a': 'a'})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertFalse(rec.get('a'))

        # Delete a subset of a multi-valued field
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_DELETE,
                    attrs={'b': ['c']})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'b'], [b'b'])

        # Trying to modify the record by providing an empty or non-matching
        # value should not result in any changes.
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_DELETE,
                    attrs={'b': ''})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'b'], [b'b'])

        # Trying a deletion with non-matching key and value must fail
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_DELETE,
                    attrs={'b': 'UNKNOWN'})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'b'], [b'b'])

        # Trying a deletion with partial intersecting values fails as well
        conn.modify('cn=foo,dc=localhost', mod_type=ldap.MOD_DELETE,
                    attrs={'b': ['a', 'b']})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'b'], [b'b'])

    def test_modify_implicit_add(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo', attrs={'a': 'a'})
        conn.modify('cn=foo,dc=localhost', attrs={'b': 'b'})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'b'], [b'b'])

        # Trying to add an empty new value should not cause more operations
        conn.modify('cn=foo,dc=localhost', attrs={'c': ''})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertFalse(rec.get(b'c'))

    def test_modify_implicit_modify(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo', attrs={'a': 'a'})
        conn.modify('cn=foo,dc=localhost', attrs={'a': 'y'})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'a'], [b'y'])

    def test_modify_implicit_delete(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo', attrs={'a': 'a'})
        conn.modify('cn=foo,dc=localhost', attrs={'a': ''})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertFalse(rec.get(b'a'))

        # Trying to modify the record by providing an empty non-existing key
        # should not result in more operations.
        conn.modify('cn=foo,dc=localhost', attrs={'b': ''})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertFalse(rec.get(b'b'))

    def test_modify_readonly(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory,
                             read_only=True)
        self.assertRaises(RuntimeError, conn.modify, 'cn=foo', {})

    def test_modify_binary(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo', attrs={'objectguid': 'a'})
        conn.modify('cn=foo,dc=localhost', attrs={'objectguid;binary': 'y'})
        rec = conn.search('dc=localhost', fltr='(cn=foo)')['results'][0]
        self.assertEqual(rec[b'objectguid'], 'y')

    def test_modify_modrdn(self):
        conn = self._makeSimple()
        conn.insert('dc=localhost', 'cn=foo')
        conn.modify('cn=foo,dc=localhost', attrs={'cn': 'bar'})
        rec = conn.search('dc=localhost', fltr='(cn=bar)')['results'][0]
        self.assertEqual(rec[b'cn'], [b'bar'])
        self.assertEqual(rec['dn'], b'cn=bar,dc=localhost')

    def test_modify_referral(self):
        import ldap
        exc_arg = {'info': 'please go to ldap://otherhost:1389'}
        conn, ldap_connection = self._makeRaising('modify_s', ldap.REFERRAL,
                                                  exc_arg)
        conn.insert('dc=localhost', 'cn=foo')

        conn.modify('cn=foo,dc=localhost', attrs={'a': 'y'})
        self.assertEqual(ldap_connection.conn_string, 'ldap://otherhost:1389')
        dn, modlist = ldap_connection.args
        self.assertEqual(dn, b'cn=foo,dc=localhost')
        self.assertEqual(modlist, [(0, b'a', [b'y'])])

    def test_modify_nonexisting_raises(self):
        import ldap
        conn = self._makeSimple()
        self.assertRaises(ldap.NO_SUCH_OBJECT, conn.modify,
                          'cn=UNKNOWN', attrs={'a': 'y'})
