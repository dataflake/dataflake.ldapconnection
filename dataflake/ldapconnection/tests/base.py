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
""" unit tests base classes
"""

import unittest

from dataflake.fakeldap import FakeLDAPConnection
from dataflake.fakeldap import FixedResultFakeLDAPConnection
from dataflake.fakeldap import RaisingFakeLDAPConnection
from dataflake.fakeldap.utils import hash_pwd


class LDAPConnectionTests(unittest.TestCase):

    def setUp(self):
        from dataflake.fakeldap import TREE

        super(LDAPConnectionTests, self).setUp()
        self.db = TREE
        # Put a record into the tree
        self.db.addTreeItems('dc=localhost')

    def tearDown(self):
        from dataflake.ldapconnection.connection import connection_cache

        super(LDAPConnectionTests, self).tearDown()
        self.db.clear()
        connection_cache.invalidate()

    def _getTargetClass(self):
        from dataflake.ldapconnection.connection import LDAPConnection
        return LDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        conn.api_encoding = 'iso-8859-1'
        conn.ldap_encoding = 'UTF-8'
        return conn

    def _makeSimple(self):
        conn = self._makeOne('host', 636, 'ldap', FakeLDAPConnection)
        conn.api_encoding = 'iso-8859-1'
        conn.ldap_encoding = 'UTF-8'
        return conn

    def _makeRaising(self, raise_on, exc_class, exc_arg=None):
        ldap_connection = RaisingFakeLDAPConnection('conn_string')
        ldap_connection.setExceptionAndMethod(raise_on, exc_class, exc_arg)
        def factory(conn_string):
            ldap_connection.conn_string = conn_string
            return ldap_connection
        conn = self._makeOne('host', 389, 'ldaptls', factory)

        return conn, ldap_connection

    def _makeFixedResultConnection(self, results):
        ldap_connection = FixedResultFakeLDAPConnection()
        ldap_connection.search_results = results
        def factory(conn_string):
            ldap_connection.conn_string = conn_string
            return ldap_connection
        conn = self._makeOne('host', 389, 'ldaptls', factory)

        return conn

    def _factory(self, connection_string):
        of = FakeLDAPConnection(connection_string)
        return of

    def _addRecord(self, dn, **kw):
        record = self.db.addTreeItems(dn)
        for key, value in kw.items():
            if key.lower() == 'userpassword':
                value = [hash_pwd(value)]
            elif isinstance(value, basestring):
                value = [value]
            record[key] = value



