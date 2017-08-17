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
    dn_str = ldap.dn.dn2str(dn_parts)
    
    if isinstance(dn_str, six.text_type):
        dn_str = dn_str.encode(encoding)

    return dn_str
