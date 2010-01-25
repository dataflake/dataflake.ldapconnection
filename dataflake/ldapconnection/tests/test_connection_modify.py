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
""" test_connection_modify: Tests for the LDAPConnection modify method

$Id$
"""

import unittest

from dataflake.ldapconnection.tests.base import LDAPConnectionTests
from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_ENCODED
from dataflake.ldapconnection.tests.dummy import ISO_8859_1_UNICODE

class ConnectionModifyTests(LDAPConnectionTests):

    def test_modify_noauthentication(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify('cn=foo', mod_type=ldap.MOD_ADD, attrs={'b':'b'})
        self.assertEqual(of.binduid, u'')
        self.assertEqual(of.bindpwd, '')

    def test_modify_authentication(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        bind_dn_apiencoded = 'cn=%s,dc=localhost' % ISO_8859_1_ENCODED
        bind_dn_unicode = u'cn=%s,dc=localhost' % ISO_8859_1_UNICODE
        bind_dn_serverencoded = bind_dn_unicode.encode(conn.ldap_encoding)
        import ldap
        conn.modify( 'cn=foo'
                   , mod_type=ldap.MOD_ADD
                   , attrs={'b':'b'}
                   , bind_dn=bind_dn_apiencoded
                   , bind_pwd='foo'
                   )
        self.assertEqual(of.binduid, bind_dn_serverencoded)
        self.assertEqual(of.bindpwd, 'foo')

    def test_modify_explicit_add(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify('cn=foo', mod_type=ldap.MOD_ADD, attrs={'b':'b'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_ADD)
        self.assertEqual(key, 'b')
        self.assertEqual(values, ['b'])

        # Trying to add an empty new value should not cause more operations
        conn.modify('cn=foo', mod_type=ldap.MOD_ADD, attrs={'c':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_explicit_modify(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a', 'b': ['x','y','z']},) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify( 'cn=foo'
                   , mod_type=ldap.MOD_REPLACE
                   , attrs={'a':'y', 'b': ['f','g','h']}
                   )
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        mods = of.modifications
        self.assertEqual(len(mods), 2)
        self.failUnless((ldap.MOD_REPLACE, 'a', ['y']) in mods)
        self.failUnless((ldap.MOD_REPLACE, 'b', ['f', 'g', 'h']) in mods)

        # Trying to modify a non-existing key with an empty value should
        # not result in more operations
        conn.modify('cn=foo', mod_type=ldap.MOD_REPLACE, attrs={'x':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_explicit_delete(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        conn.modify('cn=foo', mod_type=ldap.MOD_DELETE, attrs={'a':'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_DELETE)
        self.assertEqual(key, 'a')

        # Tryng to modify the record by providing an empty non-existing key
        # should not result in more operations.
        conn.modify('cn=foo', mod_type=ldap.MOD_DELETE, attrs={'b':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_implicit_add(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('cn=foo', attrs={'b':'b'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        import ldap
        self.assertEqual(mode, ldap.MOD_ADD)
        self.assertEqual(key, 'b')
        self.assertEqual(values, ['b'])

        # Trying to add an empty new value should not cause more operations
        conn.modify('cn=foo', attrs={'c':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_implicit_modify(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('cn=foo', attrs={'a':'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        import ldap
        self.assertEqual(mode, ldap.MOD_REPLACE)
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['y'])

        # Trying to modify a non-existing key should
        # not result in more operations
        conn.modify('cn=foo', attrs={'b':'z'})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_implicit_delete(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('cn=foo', attrs={'a':''})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        import ldap
        self.assertEqual(mode, ldap.MOD_DELETE)
        self.assertEqual(key, 'a')

        # Trying to modify the record by providing an empty non-existing key
        # should not result in more operations.
        conn.modify('cn=foo', attrs={'b':''})
        self.assertEqual(len(of.modifications), 1)

    def test_modify_readonly(self):
        conn = self._makeOne('host', 636, 'ldap', self._factory, read_only=True)
        self.assertRaises(RuntimeError, conn.modify, 'cn=foo', {})

    def test_modify_binary(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('cn=foo', attrs={'a;binary':u'y'})
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(key, 'a')
        self.assertEqual(values, u'y')

    def test_modify_modrdn(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('a=oldvalue,dc=localhost', {'a':'oldvalue'}) ]
        def factory(conn_string, who='', cred=''):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('a=oldvalue,dc=localhost', attrs={'a':'newvalue'})
        self.failUnless(of.modified_rdn)
        self.assertEqual(of.old_dn, 'a=oldvalue,dc=localhost')
        self.assertEqual(of.new_rdn, 'a=newvalue')
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'a=newvalue,dc=localhost')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['newvalue'])

    def test_modify_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        import ldap
        of.mod_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string, who='', cred=''):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.modify('cn=foo', attrs={'a':'y'})
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')
        self.failUnless(of.modified)
        self.assertEqual(of.modified_dn, 'cn=foo')
        self.assertEqual(len(of.modifications), 1)
        mode, key, values = of.modifications[0]
        self.assertEqual(mode, ldap.MOD_REPLACE)
        self.assertEqual(key, 'a')
        self.assertEqual(values, ['y'])

    def test_modify_nonexisting_raises(self):
        conn = self._makeSimple()
        self.assertRaises( RuntimeError
                         , conn.modify
                         , 'cn=UNKNOWN'
                         , attrs={'a':'y'}
                         )


def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

