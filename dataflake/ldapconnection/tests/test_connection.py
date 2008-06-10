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
""" test_connection: Tests for the LDAPConnection class

$Id: test_connection.py 1485 2008-06-04 16:08:38Z jens $
"""

import unittest

class ConnectionTests(unittest.TestCase):
    def _getTargetClass(self):
        from dataflake.ldapconnection.connection import LDAPConnection
        return LDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _makeSimple(self):
        conn = self._makeOne('host', 636, 'ldap', DummyLDAPObjectFactory)
        return conn

    def test_ctor(self):
        conn = self._makeSimple()
        self.assertEqual(conn.server['host'], 'host')
        self.assertEqual(conn.server['port'], 636)
        self.assertEqual(conn.server['protocol'], 'ldap')
        self.assertEqual(conn.server['conn_timeout'], -1)
        self.assertEqual(conn.server['op_timeout'], -1)

    def test_connect_initial_noargs(self):
        conn = self._makeSimple()
        conn = conn.connect()
        self.assertEqual(conn.binduid, '')
        self.assertEqual(conn.bindpwd, '')
        self.assertEqual(conn.searched, True)

    def test_connect_initial_bind_dn_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect('foo', '')
        self.assertEqual(conn.binduid, 'foo')
        self.assertEqual(conn.bindpwd, '')
        self.assertEqual(conn.searched, True)

    def test_connect_initial_bindpwd_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect(None, 'pass')
        self.assertEqual(conn.binduid, '')
        self.assertEqual(conn.bindpwd, 'pass')
        self.assertEqual(conn.searched, True)

    def test_connect_non_initial(self):
        conn = self._makeSimple()
        conn.conn = DummyLDAPObjectFactory('conn_string')
        conn = conn.connect(None, 'pass')
        self.assertEqual(conn.conn_string, 'conn_string')

    def test_search_simple(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_bad_results(self):
        # Make sure the resultset omits "useless" entries that may be
        # emitted by some servers, notable Microsoft ActiveDirectory.
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'})
                 , ('dn2',['thisvalueisuseless']) 
                 , ('dn3','anotheruselessvalue')
                 , ('dn4', ('morebadstuff',))
                 ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    def test_search_partial_results(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.partial = (None, [('dn', {'a':'a'})])
        import ldap
        of.search_exc = (ldap.PARTIAL_RESULTS, '')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
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
        def factory(conn_string):
            of.conn_string = conn_string
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(of.conn_string, 'ldap://otherhost:1389')

    def test_search_binaryattribute(self):
        # A binary value will remain untouched, no transformation 
        # to and from UTF-8 will happen.
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'objectGUID':u'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'objectGUID': u'a', 'dn': 'dn'})

    def test_insert(self):
        attributes = { 'cn' : 'jens'
                     , 'multivaluestring' : 'val1;val2;val3'
                     , 'multivaluelist' : ['val1', 'val2']
                     }
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.insert('dc=localhost', 'cn=jens', attrs=attributes)
        self.failUnless(of.added)
        self.assertEqual(len(of.added_values.keys()), 1)
        dn, values = of.added_values.items()[0]
        self.assertEqual(dn, 'cn=jens' + ',' + 'dc=localhost')
        self.assertEqual(values['cn'], ['jens'])
        self.assertEqual(values['multivaluestring'], ['val1','val2','val3'])
        self.assertEqual(values['multivaluelist'], ['val1','val2'])

    def test_insert_readonly(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory, read_only=True)
        self.assertRaises(RuntimeError, conn.insert, 'dc=localhost', 'cn=jens')

    def test_insert_referral(self):
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        import ldap
        of.add_exc = ( ldap.REFERRAL
                     , {'info':'please go to ldap://otherhost:1389'}
                     )
        def factory(conn_string):
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
        of = DummyLDAPObjectFactory('conn_string')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        conn.insert('dc=localhost', 'cn=jens', {'myvalue;binary' : u'a'})
        self.failUnless(of.added)
        self.assertEqual(len(of.added_values.keys()), 1)
        dn, values = of.added_values.items()[0]
        self.assertEqual(values['myvalue'], u'a')

    # XXX search: test search nonstring values
    # XXX need tests for delete, and modify

class DummyLDAPObjectFactory:
    searched = False
    res = ()
    search_exc = None
    partial = None
    added = None
    add_exc = None
    def __init__(self, conn_string):
        self.conn_string = conn_string
        self.options = []

    def set_option(self, option, value):
        self.options.append((option, value))

    def simple_bind_s(self, binduid, bindpwd):
        self.binduid = binduid
        self.bindpwd = bindpwd
        return 1

    def search_s(self, dn, scope, klass, attrs=None):
        self.searched = True
        if attrs is not None:
            if self.search_exc:
                exception = self.search_exc[0](self.search_exc[1])
                # clear out the exception to prevent looping
                self.search_exc = None
                raise exception
        return self.res

    def result(self, all):
        return self.partial

    def add_s(self, dn, attributes):
        self.added = True
        if self.add_exc:
            exception = self.add_exc[0](self.add_exc[1])
            # clear out the exception to prevent looping
            self.add_exc = None
            raise exception
        added = getattr(self, 'added_values', {})
        added.update({dn:dict(attributes)})
        self.added_values = added

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

