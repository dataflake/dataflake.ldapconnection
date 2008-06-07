##############################################################################
#
# Copyright (c) 2000-2008 Jens Vagelpohl and Contributors. All Rights Reserved.
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

$Id: LDAPConnection.py 1485 2008-06-04 16:08:38Z jens $
"""

import ldap
from ldapurl import LDAPUrl
from ldapurl import isLDAPUrl
from ldap.dn import escape_dn_chars

from dataflake.ldapconnection.utils import BINARY_ATTRIBUTES
from dataflake.ldapconnection.utils import from_utf8
from dataflake.ldapconnection.utils import to_utf8

class LDAPConnection(object):
    """ LDAPConnection

    This object handles all LDAP operations. All search operations will
    return a dictionary, where the keys are as follows:

    size        - An integer containing the length of the result set
                  generated by the operation.

    results     - Sequence of results
    """

    def __init__( self, host, port, protocol, c_factory,
                  login_attr='', rdn_attr='', bind_dn='', bind_pwd='',
                  read_only=0, conn_timeout=-1, op_timeout=-1,
                  logger = None,
                ):
        """ LDAPConnection initialization
        """
        self.login_attr = login_attr
        self.rdn_attr = rdn_attr
        self.bind_dn = bind_dn
        self.bind_pwd = bind_pwd
        self.read_only = not not read_only
        self.c_factory = c_factory
        self.conn = None

        self.logger = logger

        self.server = { 'host' : host,
                        'port' : port,
                        'protocol' : protocol,
                        'conn_timeout' : conn_timeout,
                        'op_timeout' : op_timeout,
                        }

    def connect(self, bind_dn=None, bind_pwd=''):
        """ initialize an ldap server connection 
        """

        user_dn = bind_dn or self.bind_dn
        user_pwd = bind_pwd or self.bind_pwd

        if self.conn is None:
            conn_string = self._createConnectionString(self.server)
            self.conn = self._connect(
                conn_string,
                user_dn,
                user_pwd,
                conn_timeout=self.server['conn_timeout'],
                op_timeout=self.server['op_timeout'],
                )

        self.conn.simple_bind_s(user_dn, user_pwd)
        self.conn.search_s('', ldap.SCOPE_BASE, '(objectClass=*)')
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
        connection = self.c_factory(connection_string)

        # Set the protocol version - version 3 is preferred
        try:
            connection.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION3)
        except ldap.LDAPError: # Invalid protocol version, fall back safely
            connection.set_option(ldap.OPT_PROTOCOL_VERSION, ldap.VERSION2)

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

        # Now bind with the credentials given. Let exceptions propagate out.
        connection.simple_bind_s(user_dn, user_pwd)

        return connection

    def handle_referral(self, exception):
        """ Handle a referral specified in the passed-in exception 
        """
        payload = exception.args[0]
        info = payload.get('info')
        ldap_url = info[info.find('ldap'):]

        if isLDAPUrl(ldap_url):
            conn_str = LDAPUrl(ldap_url).initializeUrl()

            return self._connect(conn_str, self.bind_dn, self.bind_pwd)

        else:
            raise ldap.CONNECT_ERROR, 'Bad referral "%s"' % str(exception)

    def search( self
              , base
              , scope
              , filter='(objectClass=*)'
              , attrs=[]
              , bind_dn=''
              , bind_pwd=''
              , convert_filter=True
              ):
        """ Search for entries in the database
        """
        result = { 'size' : 0
                 , 'results' : []
                 }
        if convert_filter:
            filter = to_utf8(filter)
        base = self._clean_dn(base)

        connection = self.connect(bind_dn=bind_dn, bind_pwd=bind_pwd)
        if connection is None:
            raise RuntimeError('Cannot connect to LDAP server')

        try:
            res = connection.search_s(base, scope, filter, attrs)
        except ldap.PARTIAL_RESULTS:
            res_type, res = connection.result(all=0)
        except ldap.REFERRAL, e:
            connection = self.handle_referral(e)

            try:
                res = connection.search_s(base, scope, filter, attrs)
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
                if ( not isinstance(value, str) and 
                     key.lower() not in BINARY_ATTRIBUTES ):
                    try:
                        for i in range(len(value)):
                            value[i] = from_utf8(value[i])
                    except:
                        pass

            rec_dict['dn'] = from_utf8(rec_dn)

            result['results'].append(rec_dict)
            result['size'] += 1

        return result

    def insert(self, base, rdn, attrs=None):
        """ Insert a new record 
        """
        if self.read_only:
            raise RuntimeError(
                'Running in read-only mode, insertion is disabled')

        dn = self._clean_dn(to_utf8('%s,%s' % (rdn, base)))
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
            connection = self.connect()
            connection.add_s(dn, attribute_list)
        except ldap.REFERRAL, e:
            connection = self.handle_referral(e)
            connection.add_s(dn, attribute_list)

    def delete(self, dn):
        """ Delete a record 
        """
        if self.read_only:
            raise RuntimeError(
                'Running in read-only mode, deletion is disabled')

        utf8_dn = self._clean_dn(to_utf8(dn))

        try:
            connection = self.connect()
            connection.delete_s(utf8_dn)
        except ldap.REFERRAL, e:
            connection = self.handle_referral(e)
            connection.delete_s(utf8_dn)

    def modify(self, dn, mod_type=None, attrs=None):
        """ Modify a record 
        """
        if self.read_only:
            raise RuntimeError(
                'Running in read-only mode, modification is disabled')

        utf8_dn = self._clean_dn(to_utf8(dn))
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
            else:
                values = map(to_utf8, values)

            if mod_type is None:
                if cur_rec.get(key, ['']) != values and values != ['']:
                    mod_list.append((ldap.MOD_REPLACE, key, values))
                elif cur_rec.has_key(key) and values == ['']:
                    mod_list.append((ldap.MOD_DELETE, key, None))
            else:
                mod_list.append((mod_type, key, values))

        try:
            connection = self.connect()

            new_rdn = attrs.get(self.rdn_attr, [''])[0]
            if new_rdn and new_rdn != cur_rec.get(self.rdn_attr)[0]:
                raw_utf8_rdn = to_utf8('%s=%s' % (self.rdn_attr, new_rdn))
                new_utf8_rdn = self._clean_rdn(raw_utf8_rdn)
                connection.modrdn_s(utf8_dn, new_utf8_rdn)
                old_dn_exploded = ldap.explode_dn(utf8_dn, 0)
                old_dn_exploded[0] = new_utf8_rdn
                utf8_dn = ','.join(old_dn_exploded)

            if mod_list:
                connection.modify_s(utf8_dn, mod_list)
            else:
                debug_msg = 'Nothing to modify: %s' % utf8_dn
                if self.logger is not None:
                    self.logger.debug('LDAPDelegate.modify: %s' % debug_msg)

        except ldap.REFERRAL, e:
            connection = self.handle_referral(e)
            connection.modify_s(dn, mod_list)

    def _clean_rdn(self, rdn):
        """ Escape all characters that need escaping for a DN, see RFC 2253 
        """
        if rdn.find('\\') != -1:
            # already escaped, disregard
            return rdn

        try:
            key, val = rdn.split('=')
            val = val.lstrip()
            return '%s=%s' % (key, escape_dn_chars(val))
        except ValueError:
            return rdn

    def _clean_dn(self, dn):
        """ Escape all characters that need escaping for a DN, see RFC 2253 
        """
        elems = [self._clean_rdn(x) for x in dn.split(',')]

        return ','.join(elems)

    def _createConnectionString(self, server_info):
        """ Convert a server info mapping into a connection string
        """
        protocol = server_info['protocol']

        if protocol == 'ldapi':
            hostport = server_info['host']
        else:
            hostport = '%s:%s' % (server_info['host'], server_info['port'])

        ldap_url = LDAPUrl(urlscheme=protocol, hostport=hostport)

        return ldap_url.initializeUrl()


