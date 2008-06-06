import unittest

class ConnectionTests(unittest.TestCase):
    def _getTargetClass(self):
        from dataflake.ldapconnection.connection import LDAPConnection
        return LDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _makeSimple(self):
        ob = self._makeLDAPObject()
        conn = self._makeOne('host', 636, 'ldap', ob)
        return conn

    def setUp(self):
        import sys
        self._old = sys.modules.get('ldap')
        from dataflake.ldapconnection.tests import fakeldap
        sys.modules['ldap'] = fakeldap

    def tearDown(self):
        import sys
        if self._old is None:
            del sys.modules['ldap']
        else:
            sys.modules['ldap'] = self._old

    def _makeLDAPObject(self):
        return DummyLDAPObjectFactory

    def test_ctor(self):
        conn = self._makeSimple()
        self.assertEqual(conn.server['host'], 'host')
        self.assertEqual(conn.server['port'], 636)
        self.assertEqual(conn.server['protocol'], 'ldap')
        self.assertEqual(conn.server['conn_timeout'], -1)
        self.assertEqual(conn.server['op_timeout'], -1)

    def test_connect_bind_dn_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect('foo', '')
        self.assertEqual(conn.binduid, 'foo')
        self.assertEqual(conn.bindpwd, '')
        

class DummyLDAPObjectFactory:
    def __init__(self, conn_string, exc=None):
        self.conn_string = conn_string
        self.exc = exc
        self.options = []

    def set_option(self, option, value):
        self.options.append((option, value))

    def simple_bind_s(self, binduid, bindpwd):
        self.binduid = binduid
        self.bindpwd = bindpwd
        if self.exc:
            raise self.exc
        return 1
    

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

