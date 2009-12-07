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
""" LDAPConnection: A class modeling a LDAP server connection

Instances of this class offer a simplified API to do searches, insertions, 
deletions or modifications.

$Id$
"""

import ldap
from ldap.dn import explode_dn
from ldap.filter import filter_format
from ldap.ldapobject import SmartLDAPObject
import ldapurl
import logging

from zope.interface import implements

from dataflake.ldapconnection.interfaces import ILDAPConnection
from dataflake.ldapconnection.utils import BINARY_ATTRIBUTES
from dataflake.ldapconnection.utils import escape_dn
from dataflake.ldapconnection.utils import from_utf8
from dataflake.ldapconnection.utils import to_utf8

default_logger = logging.getLogger('dataflake.ldapconnection')


class LDAPConnection(object):
    """ LDAPConnection object

    See `interfaces.py` for interface documentation.
    """

    implements(ILDAPConnection)

    def __init__( self, host='', port=389, protocol='ldap'
                , c_factory=SmartLDAPObject, rdn_attr='', bind_dn=''
                , bind_pwd='', read_only=False
                , conn_timeout=-1, op_timeout=-1, logger=None
                ):
        """ LDAPConnection initialization
        """
        self.rdn_attr = rdn_attr
        self.bind_dn = bind_dn
        self.bind_pwd = bind_pwd
        self.read_only = read_only
        self.c_factory = c_factory
        self.conn = None
        self.logger = logger or default_logger

        self.servers = {}

        if host:
            self.addServer(host, port, protocol, conn_timeout, op_timeout)

    def addServer(self, host, port, protocol, conn_timeout=-1, op_timeout=-1):
        """ Add a server definition to the list of servers used
        """
        l = ldapurl.LDAPUrl(urlscheme=protocol, hostport='%s:%s' % (host, port))
        server_url = l.initializeUrl()
        self.servers[server_url] = { 'url' : server_url
                                   , 'conn_timeout' : conn_timeout
                                   , 'op_timeout' : op_timeout
                                   }

    def removeServer(self, host, port, protocol):
        """ Remove a server definition from the list of servers used
        """
        l = ldapurl.LDAPUrl(urlscheme=protocol, hostport='%s:%s' % (host, port))
        server_url = l.initializeUrl()
        if server_url in self.servers.keys():
            del self.servers[server_url]

    def connect(self, bind_dn=None, bind_pwd=None):
        """ initialize an ldap server connection 
        """
        if len(self.servers.keys()) == 0:
            raise RuntimeError('No servers defined')

        if bind_dn is None:
            bind_dn = self.bind_dn
            bind_pwd = self.bind_pwd

        if self.conn is None:
            for server in self.servers.values():
                try:
                    self.conn = self._connect( server['url']
                                             , bind_dn
                                             , bind_pwd
                                             , conn_timeout=server['conn_timeout']
                                             , op_timeout=server['op_timeout']
                                             )
                    break
                except (ldap.SERVER_DOWN, ldap.TIMEOUT), e:
                    continue

            if self.conn is None:
                exception_string = str(e or 'no exception')
                msg = 'Failure connecting, last attempt: %s (%s)' % (
                            server['url'], str(e or 'no exception'))
                self.logger.critical(msg, exc_info=1)

                if e:
                    raise e

        last_bind = getattr(self.conn, '_last_bind', (None, ((),()), {}))
        if last_bind[1][0] != bind_dn and last_bind[1][1] != bind_pwd:
            self.conn.simple_bind_s(bind_dn, bind_pwd)

        return self.conn

    def _connect( self
                , connection_string
                , user_dn
                , user_pwd
                , conn_timeout=5
                , op_timeout=-1
                ):
        """ Factored out to allow usage by other pieces 
        """
        connection = self.c_factory(connection_string,who=user_dn,cred=user_pwd)

        # Deny auto-chasing of referrals to be safe, we handle them instead
        try:
            connection.set_option(ldap.OPT_REFERRALS, 0)
        except ldap.LDAPError: # Cannot set referrals, so do nothing
            pass

        # Set the connection timeout
        if conn_timeout > 0:
            connection.set_option(ldap.OPT_NETWORK_TIMEOUT, conn_timeout)

        # Set the operations timeout
        if op_timeout > 0:
            connection.timeout = op_timeout

        return connection

    def search( self
              , base
              , scope=ldap.SCOPE_SUBTREE
              , fltr='(objectClass=*)'
              , attrs=None
              , convert_filter=True
              , bind_dn=None
              , bind_pwd=None
              ):
        """ Search for entries in the database
        """
        result = {'size': 0, 'results': [], 'exception': ''}
        if convert_filter:
            fltr = to_utf8(fltr)
        base = escape_dn(base)

        connection = self.connect(bind_dn=bind_dn, bind_pwd=bind_pwd)

        try:
            res = connection.search_s(base, scope, fltr, attrs)
        except ldap.PARTIAL_RESULTS:
            res_type, res = connection.result(all=0)
        except ldap.REFERRAL, e:
            connection = self._handle_referral(e)

            try:
                res = connection.search_s(base, scope, fltr, attrs)
            except ldap.PARTIAL_RESULTS:
                res_type, res = connection.result(all=0)

        for rec_dn, rec_dict in res:
            # When used against Active Directory, "rec_dict" may not be
            # be a dictionary in some cases (instead, it can be a list)
            # An example of a useless "res" entry that can be ignored
            # from AD is
            # (None, ['ldap://ForestDnsZones.PORTAL.LOCAL/DC=ForestDnsZones,DC=PORTAL,DC=LOCAL'])
            # This appears to be some sort of internal referral, but
            # we can't handle it, so we need to skip over it.
            try:
                items =  rec_dict.items()
            except AttributeError:
                # 'items' not found on rec_dict
                continue

            for key, value in items:
                if key.lower() not in BINARY_ATTRIBUTES:
                    if not isinstance(value, str):
                        for i in range(len(value)):
                            value[i] = from_utf8(value[i])

            rec_dict['dn'] = from_utf8(rec_dn)

            result['results'].append(rec_dict)
            result['size'] += 1

        return result

    def insert(self, base, rdn, attrs=None, bind_dn=None, bind_pwd=None):
        """ Insert a new record 

        attrs is expected to be a mapping where the value may be a string
        or a sequence of strings. 
        Multiple values may be expressed as a single string if the values 
        are semicolon-delimited.
        Values can be marked as binary values, meaning they are not encoded
        as UTF-8, by appending ';binary' to the key.
        """
        self._complainIfReadOnly()

        dn = escape_dn(to_utf8('%s,%s' % (rdn, base)))
        attribute_list = []
        attrs = attrs and attrs or {}

        for attr_key, attr_val in attrs.items():
            if attr_key.endswith(';binary'):
                is_binary = True
                attr_key = attr_key[:-7]
            else:
                is_binary = False

            if isinstance(attr_val, (str, unicode)) and not is_binary:
                attr_val = [x.strip() for x in attr_val.split(';')]

            if attr_val != ['']:
                if not is_binary:
                    attr_val = map(to_utf8, attr_val)
                attribute_list.append((attr_key, attr_val))

        try:
            connection = self.connect(bind_dn=bind_dn, bind_pwd=bind_pwd)
            connection.add_s(dn, attribute_list)
        except ldap.REFERRAL, e:
            connection = self._handle_referral(e)
            connection.add_s(dn, attribute_list)

    def delete(self, dn, bind_dn=None, bind_pwd=None):
        """ Delete a record 
        """
        self._complainIfReadOnly()

        utf8_dn = escape_dn(to_utf8(dn))

        try:
            connection = self.connect(bind_dn=bind_dn, bind_pwd=bind_pwd)
            connection.delete_s(utf8_dn)
        except ldap.REFERRAL, e:
            connection = self._handle_referral(e)
            connection.delete_s(utf8_dn)

    def modify(self, dn, mod_type=None, attrs=None, bind_dn=None, bind_pwd=None):
        """ Modify a record 
        """
        self._complainIfReadOnly()

        utf8_dn = escape_dn(to_utf8(dn))
        res = self.search(base=utf8_dn, scope=ldap.SCOPE_BASE)
        attrs = attrs and attrs or {}

        if res['size'] == 0:
            raise RuntimeError(
                'LDAPDelegate.modify: Cannot find dn "%s"' % dn)

        cur_rec = res['results'][0]
        mod_list = []

        for key, values in attrs.items():

            if key.endswith(';binary'):
                key = key[:-7]
            elif isinstance(values, (str, unicode)):
                values = map(to_utf8, [x.strip() for x in values.split(';')])
            else:
                values = map(to_utf8, values)

            if mod_type is None:
                if not cur_rec.has_key(key) and values != ['']:
                    mod_list.append((ldap.MOD_ADD, key, values))
                elif cur_rec.get(key,['']) != values and values not in ([''],[]):
                    mod_list.append((ldap.MOD_REPLACE, key, values))
                elif cur_rec.has_key(key) and values in ([''], []):
                    mod_list.append((ldap.MOD_DELETE, key, None))
            else:
                mod_list.append((mod_type, key, values))

        try:
            connection = self.connect(bind_dn=bind_dn, bind_pwd=bind_pwd)

            raw_rdn = attrs.get(self.rdn_attr, '')
            if isinstance(raw_rdn, (str, unicode)):
                raw_rdn = [raw_rdn]
            new_rdn = raw_rdn[0]

            if new_rdn and new_rdn != cur_rec.get(self.rdn_attr)[0]:
                raw_utf8_rdn = to_utf8('%s=%s' % (self.rdn_attr, new_rdn))
                new_utf8_rdn = escape_dn(raw_utf8_rdn)
                connection.modrdn_s(utf8_dn, new_utf8_rdn)
                old_dn_exploded = explode_dn(utf8_dn, 0)
                old_dn_exploded[0] = new_utf8_rdn
                utf8_dn = ','.join(old_dn_exploded)

            if mod_list:
                connection.modify_s(utf8_dn, mod_list)
            else:
                debug_msg = 'Nothing to modify: %s' % utf8_dn
                self.logger.debug('LDAPDelegate.modify: %s' % debug_msg)

        except ldap.REFERRAL, e:
            connection = self._handle_referral(e)
            connection.modify_s(dn, mod_list)

    def _handle_referral(self, exception):
        """ Handle a referral specified in the passed-in exception 
        """
        payload = exception.args[0]
        info = payload.get('info')
        ldap_url = info[info.find('ldap'):]

        if ldapurl.isLDAPUrl(ldap_url):
            conn_str = ldapurl.LDAPUrl(ldap_url).initializeUrl()
            return self._connect(conn_str, self.bind_dn, self.bind_pwd)
        else:
            raise ldap.CONNECT_ERROR, 'Bad referral "%s"' % str(exception)

    def _complainIfReadOnly(self):
        """ Raise RuntimeError if the connection is set to `read-only`

        This method should be called before any directory tree modfication
        """
        if self.read_only:
            raise RuntimeError(
                'Running in read-only mode, directory modifications disabled')

