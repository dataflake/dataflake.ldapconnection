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
""" Utility functions and constants
"""

import ldap
import six


BINARY_ATTRIBUTES = (b'objectguid', b'jpegphoto')


def escape_dn(dn, encoding='UTF-8'):
    """ Escape all characters that need escaping for a DN, see RFC 2253
    """
    if not dn:
        return dn

    escaped = ldap.dn.dn2str(ldap.dn.str2dn(dn))

    if isinstance(escaped, six.text_type):
        escaped = escaped.encode(encoding)

    return escaped

def dn2str(dn_parts, encoding='UTF-8'):
    """ Build a DN string from a parts structure
    """
    dn_list = []

    for dn_part in dn_parts:
        key = dn_part[0][0]
        value = dn_part[0][1]

        if not isinstance(key, six.binary_type):
            key = key.encode(encoding)

        if not isinstance(value, six.binary_type):
            value = value.encode(encoding)

        dn_list.append(b'%s=%s' % (key, value))

    return b','.join(dn_list)
