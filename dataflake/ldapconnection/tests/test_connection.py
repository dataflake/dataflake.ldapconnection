import unittest

class ConnectionTests(unittest.TestCase):
    def _getTargetClass(self):
        from dataflake.ldapconnection.connection import LDAPConnection
        return LDAPConnection

    def _makeOne(self, *args, **kw):
        conn = self._getTargetClass()(*args, **kw)
        return conn

    def _makeSimple(self):
        conn = self._makeOne('host', 636, 'ldap', DummyLDAPObjectFactory)
        return conn

    def test_ctor(self):
        conn = self._makeSimple()
        self.assertEqual(conn.server['host'], 'host')
        self.assertEqual(conn.server['port'], 636)
        self.assertEqual(conn.server['protocol'], 'ldap')
        self.assertEqual(conn.server['conn_timeout'], -1)
        self.assertEqual(conn.server['op_timeout'], -1)

    def test_connect_initial_noargs(self):
        conn = self._makeSimple()
        conn = conn.connect()
        self.assertEqual(conn.binduid, '')
        self.assertEqual(conn.bindpwd, '')
        self.assertEqual(conn.searched, True)

    def test_connect_initial_bind_dn_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect('foo', '')
        self.assertEqual(conn.binduid, 'foo')
        self.assertEqual(conn.bindpwd, '')
        self.assertEqual(conn.searched, True)

    def test_connect_initial_bindpwd_not_None(self):
        conn = self._makeSimple()
        conn = conn.connect(None, 'pass')
        self.assertEqual(conn.binduid, '')
        self.assertEqual(conn.bindpwd, 'pass')
        self.assertEqual(conn.searched, True)

    def test_connect_non_initial(self):
        conn = self._makeSimple()
        conn.conn = DummyLDAPObjectFactory('conn_string')
        conn = conn.connect(None, 'pass')
        self.assertEqual(conn.conn_string, 'conn_string')

    def test_search_simple(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.res = [ ('dn', {'a':'a'}) ]
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})
        
    def test_search_partial_results(self):
        of = DummyLDAPObjectFactory('conn_string')
        of.partial = (None, [('dn', {'a':'a'})])
        import ldap
        of.search_exc = (ldap.PARTIAL_RESULTS, '')
        def factory(conn_string):
            return of
        conn = self._makeOne('host', 636, 'ldap', factory)
        response = conn.search('base', 'scope')
        self.assertEqual(response['size'], 1)
        results = response['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], {'a': 'a', 'dn': 'dn'})

    # XXX search: test search referrals, binary attrs, nonstring values

class DummyLDAPObjectFactory:
    searched = False
    res = ()
    search_exc = None
    partial = None
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
                raise self.search_exc[0](self.search_exc[1])
        return self.res

    def result(self, all):
        return self.partial

def test_suite():
    import sys
    return unittest.findTestCases(sys.modules[__name__])

