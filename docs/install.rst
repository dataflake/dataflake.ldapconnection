Installation
============

You will need `Python <http://python.org>`_ version 2.7 or better to
run :mod:`dataflake.ldapconnection`.

It is advisable to install :mod:`dataflake.ldapconnection` into a
:term:`virtualenv` in order to obtain isolation from any "system"
packages you've got installed in your Python version (and likewise, 
to prevent :mod:`dataflake.ldapconnection` from globally installing 
versions of packages that are not compatible with your system Python).

After you've got the requisite dependencies installed, you may install
:mod:`dataflake.ldapconnection` into your Python environment using the 
following command::

  $ easy_install dataflake.ldapconnection

or::

  $ pip install dataflake.fakeldap

If you use :mod:`zc.buildout` you can add :mod:`dataflake.fakeldap`
to the necessary ``eggs`` section to have it pulled in automatically.

When you ``easy_install``  or ``pip`` :mod:`dataflake.fakeldap`, the
:term:`python-ldap` libraries are installed if they are not present.
