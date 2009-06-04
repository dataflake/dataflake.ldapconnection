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
""" Utility functions and constants

$Id: utils.py 1485 2008-06-04 16:08:38Z jens $
"""

import codecs
import ldap

BINARY_ATTRIBUTES = ('objectguid', 'jpegphoto')

encoding = 'latin1'

try:
    encodeLocal, decodeLocal, reader = codecs.lookup(encoding)[:3]
    encodeUTF8, decodeUTF8 = codecs.lookup('UTF-8')[:2]

    if getattr(reader, '__module__', '')  == 'encodings.utf_8':
        # Everything stays UTF-8, so we can make this cheaper
        to_utf8 = from_utf8 = str

    else:

        def from_utf8(s):
            return encodeLocal(decodeUTF8(s)[0])[0]

        def to_utf8(s):
            if isinstance(s, str):
                s = decodeLocal(s)[0]
            return encodeUTF8(s)[0]

except LookupError:
    raise LookupError, 'Unknown encoding "%s"' % encoding

def escape_dn(dn):
    """ Escape all characters that need escaping for a DN, see RFC 2253 
    """
    return ldap.dn.dn2str(ldap.dn.str2dn(dn))

