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
""" dummy: dummy test fixtures

$Id$
"""

class DummyLDAPObjectFactory:
    searched = False
    res = ()
    search_exc = None
    partial = None
    added = False
    add_exc = None
    modified = False
    mod_exc = None
    modified_rdn = False
    deleted = False
    del_exc = None
    deleted_dn = None
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

    def modify_s(self, dn, mod_list):
        self.modified = True
        if self.mod_exc:
            exception = self.mod_exc[0](self.mod_exc[1])
            # clear out the exception to prevent looping
            self.mod_exc = None
            raise exception
        self.modified_dn = dn
        self.modifications = mod_list

    def modrdn_s(self, old_dn, new_rdn):
        self.modified_rdn = True
        self.old_dn = old_dn
        self.new_rdn = new_rdn

    def delete_s(self, dn):
        self.deleted = True
        if self.del_exc:
            exception = self.del_exc[0](self.del_exc[1])
            # clear out the exception to prevent looping
            self.del_exc = None
            raise exception
        self.deleted_dn = dn

