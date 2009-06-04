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
""" dataflake.ldapconnnection interfaces

$Id$
"""

from zope.interface import Interface

class ILDAPConnection(Interface):
    """ ILDAPConnection interface

    ILDAPConnection instances provide a simplified way to talk to 
    a LDAP server. It allows defining one or more server connections 
    that allow for automatic failover in case the current connection
    fails.
    """

    def addServer(host, port, protocol, conn_timeout=-1, op_timeout=-1):
        """ Add a server definition

        The `conn_timeout` argument defines the number of seconds to wait
        until a new connection attempt is considered failed, which means 
        the next server is tried if it has been defined. -1 means 
        "wait indefinitely",

        The `op_timeout` argument defines the number of seconds to wait 
        until a LDAP server operation is considered failed, which means 
        the next server is tried if it has been defined. -1 means
        "wait indefinitely".

        If a server definition with a host, port and protocol that matches
        an existing server definition is added, the new values will replace
        the existing definition.
        """

    def removeServer(host, port, protocol):
        """ Remove a server definition

        Please note: I you remove the server definition of a server that 
        is currently being used, that connection will continue to be 
        used until it fails or until the process is restarted.
        """

    def connect(bind_dn=None, bind_pwd=None):
        """ Return a working LDAP server connection

        If no DN or password for binding to the LDAP server are passed in, 
        the DN and password configured into the LDAP connection instance 
        are used.

        The connection is cached and will be re-used. Since a bind operation
        is forced every time the method can be used to re-bind the cached
        connection with new credentials.

        Raises RuntimeError if no server definitions are available.
        """

    def bind(connection, bind_dn, bind_pwd):
        """ Attempt a bind operation on the provided connection object

        If the last bind credentials are the same as the currently 
        required credentials the LDAP server will not be contacted.
        """

    def search( base
              , scope
              , filter='(objectClass=*)'
              , attrs=None
              , convert_filter=True
              , bind_dn=None
              , bind_pwd=None
              ):
        """ Perform a LDAP search

        The search `base` is the point in the tree to searc from. `scope`
        defines how to search and must be one of the scopes defined by the
        `python-ldap` module (`ldap.SCOPE_BASE`, `ldap.SCOPE_ONELEVEL` or
        `ldap.SCOPE_SUBTREE`). What to search for is described by the 
        `filter` argument, which must be a valid LDAP search filter string.
        If only certain record attributes should be returned, they can be
        specified in the `attrs` sequence.

        If the search raised no errors, a mapping with the following keys
        is returned:

        - results: A sequence of mappings representing a matching record

        - size: The number of matching records

        The results sequence itself contains mappings that have a `dn` key
        containing the full distinguished name of the record, and key/values
        representing the records' data as returned by the LDAP server.

        In order to perform the operation using credentials other than the
        credentials configured on the instance a DN and password may be
        passed in.
        """

    def insert(base, rdn, attrs=None, bind_dn=None, bind_pwd=None):
        """ Insert a new record 

        The record will be inserted at `base` with the new RDN `rdn`.
        `attrs` is expected to be a key:value mapping where the value may 
        be a string or a sequence of strings. 
        Multiple values may be expressed as a single string if the values 
        are semicolon-delimited.
        Values can be marked as binary values, meaning they are not encoded
        as UTF-8 before sending the to the LDAP server, by appending 
        ';binary' to the key.

        In order to perform the operation using credentials other than the
        credentials configured on the instance a DN and password may be
        passed in.
        """

    def delete(dn, bind_dn=None, bind_pwd=None):
        """ Delete the record specified by the given DN

        In order to perform the operation using credentials other than the
        credentials configured on the instance a DN and password may be
        passed in.
        """

    def modify(dn, mod_type=None, attrs=None, bind_dn=None, bind_pwd=None):
        """ Modify the record specified by the given DN

        `mod_type` is one of the LDAP modification types as declared by
        the `python-ldap`-module, such as `ldap.MOD_ADD`, 
        PUrl(urlscheme=protocol, hostport=hostport)
        provided, the modification type is guessed by comparing the 
        current record with the `attrs` mapping passed in.

        `attrs` is expected to be a key:value mapping where the value may 
        be a string or a sequence of strings. 
        Multiple values may be expressed as a single string if the values 
        are semicolon-delimited.
        Values can be marked as binary values, meaning they are not encoded
        as UTF-8 before sending the to the LDAP server, by appending 
        ';binary' to the key.

        In order to perform the operation using credentials other than the
        credentials configured on the instance a DN and password may be
        passed in.
        """

