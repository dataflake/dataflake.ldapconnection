##############################################################################
#
# Copyright (c) 2000-2012 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" A fake LDAP module for unit tests
"""

# BBB
from dataflake.fakeldap import FakeLDAPConnection
from dataflake.fakeldap import FixedResultFakeLDAPConnection
from dataflake.fakeldap import ldapobject
from dataflake.fakeldap import RaisingFakeLDAPConnection

