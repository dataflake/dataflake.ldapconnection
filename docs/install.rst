Installation
============

You will need `Python <http://python.org>`_ version 2.4 or better to
run :mod:`dataflake.ldapconnection`.  Development of 
:mod:`dataflake.ldapconnection` is done primarily under Python 2.6, so 
that version is recommended.

.. warning:: To succesfully install :mod:`dataflake.ldapconnection`, 
   you will need an environment capable of compiling Python C code.  
   See the documentation about installing, e.g. ``gcc`` and 
   ``python-devel`` for your system.  You will also need 
   :term:`setuptools` installed on within your Python system in order 
   to run the ``easy_install`` command.

It is advisable to install :mod:`dataflake.ldapconnection` into a
:term:`virtualenv` in order to obtain isolation from any "system"
packages you've got installed in your Python version (and likewise, 
to prevent :mod:`dataflake.ldapconnection` from globally installing 
versions of packages that are not compatible with your system Python).

After you've got the requisite dependencies installed, you may install
:mod:`dataflake.ldapconnection` into your Python environment using the 
following command::

  $ easy_install dataflake.ldapconnection

When you ``easy_install`` :mod:`dataflake.ldapconnection`, the
:term:`python-ldap` libraries are installed if they are not present.
