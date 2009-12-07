Using dataflake.ldapconnection
==============================

:mod:`dataflake.ldapconnection` provides an abstraction layer on 
top of :term:`python-ldap`. It offers a connection object with 
simplified methods for inserting, modifying, searching and deleting 
records in the LDAP directory tree. Failover/redundancy can be 
achieved by supplying connection data for more than one LDAP server.

Instantiating a connection object:

.. code-block:: python
   :linenos:

    >>> from dataflake.ldapconnection.connection import LDAPConnection
    >>> conn = LDAPConnection()
    >>> conn.addServer('localhost', '1389', 'ldap')

To work with the connection object you need to make sure that a LDAP 
server is available on the provided host and port.

Now we will search for a record that does not yet exist, then add 
the missing record and find it when searching again:

.. code-block:: python
   :linenos:

    >>> conn.search('ou=users,dc=localhost', fltr='(cn=testing)')
    {'exception': '', 'results': [], 'size': 0}
    >>> data = { 'objectClass': ['top', 'inetOrgPerson']
    ...        , 'cn': 'testing'
    ...        , 'sn': 'Lastname'
    ...        , 'givenName': 'Fistname'
    ...        , 'mail': 'test@test.com'
    ...        , 'userPassword': '5ecret'
    ...        }
    >>> conn.insert('ou=users,dc=localhost', 'cn=testing', attrs=data, bind_dn='cn=Manager,dc=localhost', bind_pwd='secret')
    >>> conn.search('ou=users,dc=localhost', fltr='(cn=testing)')
    {'exception': '', 'results': [{'dn': 'cn=testing,ou=users,dc=localhost', 'cn': ['testing'], 'objectClass': ['top', 'inetOrgPerson'], 'userPassword': ['5ecret'], 'sn': ['Lastname'], 'mail': ['test@test.com'], 'givenName': ['Fistname']}], 'size': 1}

We can edit an existing record:

.. code-block:: python
   :linenos:

   >>> changes = {'givenName': 'John', 'sn': 'Doe'}
   >>> conn.modify('cn=testing,ou=users,dc=localhost', attrs=changes, bind_dn='cn=Manager,dc=localhost', bind_pwd='secret')
   >>> conn.search('ou=users,dc=localhost', fltr='(cn=testing)')
   {'exception': '', 'results': [{'dn': 'cn=testing,ou=users,dc=localhost', 'cn': ['testing'], 'objectClass': ['top', 'inetOrgPerson'], 'userPassword': ['5ecret'], 'sn': ['Doe'], 'mail': ['test@test.com'], 'givenName': ['John']}], 'size': 1}

As the last step, we will delete our testing record:

.. code-block:: python
   :linenos:

   >>> conn.delete('cn=testing,ou=users,dc=localhost', bind_dn='cn=Manager,dc=localhost', bind_pwd='secret')
   >>> conn.search('ou=users,dc=localhost', fltr='(cn=testing)')
   {'exception': '', 'results': [], 'size': 0}

The :ref:`api_interfaces_section` page contains more
information about the connection APIs.
