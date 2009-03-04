##############################################################################
#
# Copyright (c) 2008-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
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

$Id$
"""

import unittest

from dataflake.ldapconnection.tests.dummy import DummyLDAPObjectFactory

class LDAPConnectionTests(unittest.TestCase):

    def _getTargetClass(self):
        from dataflake.ldapconnection.connection import LDAPConnection
        return LDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _makeSimple(self):
        conn = self._makeOne('host', 636, 'ldap', DummyLDAPObjectFactory)
        return conn

    def _factory(self, connection_string):
        of = DummyLDAPObjectFactory(connection_string)
        return of
