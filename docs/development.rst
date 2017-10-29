=============
 Development
=============

Getting the source code
=======================
The source code is maintained in the Dataflake Git 
repository. To check out the trunk:

.. code-block:: sh

  $ git clone https://github.com/dataflake/dataflake.ldapconnection.git

You can also browse the code online at 
https://github.com/dataflake/dataflake.ldapconnection


Bug tracker
===========
For bug reports, suggestions or questions please use the 
GitHub issue tracker at 
https://github.com/dataflake/dataflake.ldapconnection/issues.


Running the tests in a ``virtualenv``
=====================================
If you use the ``virtualenv`` package to create lightweight Python
development environments, you can run the tests using nothing more
than the ``python`` binary in a virtualenv.  First, create a scratch
environment:

.. code-block:: sh

   $ /path/to/virtualenv --no-site-packages /tmp/virtualpy

Next, get this package registered as a "development egg" in the
environment:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py develop

Finally, run the tests using the build-in ``setuptools`` testrunner:

.. code-block:: sh

   $ /tmp/virtualpy/bin/python setup.py test
   running test
   ...
   test_escape_dn (dataflake.ldapconnection.tests.test_utils.UtilsTest) ... ok
   
   ----------------------------------------------------------------------
   Ran 88 tests in 0.058s
   
   OK

If you have the :mod:`nose` package installed in the virtualenv, you can
use its testrunner too:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install nose
   ...
   $ /tmp/virtualpy/bin/python setup.py nosetests
   running nosetests
   ......................................................................
   ...............................
   ----------------------------------------------------------------------
   Ran 101 tests in 0.162s

   OK

or:

.. code-block:: sh

   $ /tmp/virtualpy/bin/nosetests
   ......................................................................
   ...............................
   ----------------------------------------------------------------------
   Ran 101 tests in 0.160s

   OK

If you have the :mod:`coverage` package installed in the virtualenv,
you can see how well the tests cover the code:

.. code-block:: sh

   $ /tmp/virtualpy/bin/easy_install nose coverage
   ...
   $ /tmp/virtualpy/bin/python setup.py nosetests \
       --with-coverage --cover-package=dataflake.ldapconnection
   running nosetests
   ...

   Name                                  Stmts   Exec  Cover   Missing
   -------------------------------------------------------------------
   dataflake.ldapconnection                  1      1   100%   
   dataflake.ldapconnection.connection     246    244    99%   214-215
   dataflake.ldapconnection.interfaces      10     10   100%   
   dataflake.ldapconnection.utils            7      7   100%   
   -------------------------------------------------------------------
   TOTAL                                   264    262    99%   
   ----------------------------------------------------------------------
   Ran 101 tests in 0.226s

   OK


Running the tests using  :mod:`zc.buildout`
===========================================
:mod:`dataflake.ldapconnection` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

  $ python bootstrap.py
  ...
  Generated script '.../bin/buildout'
  $ bin/buildout
  ...

Once you have a buildout, the tests can be run as follows:

.. code-block:: sh

   $ bin/test --all
   Running tests at all levels
   Running zope.testing.testrunner.layer.UnitTests tests:
     Set up zope.testing.testrunner.layer.UnitTests in 0.000 seconds.
     Running:
   .....................................................................
   .........................
     Ran 94 tests with 0 failures and 0 errors in 0.042 seconds.
   Tearing down left over layers:
     Tear down zope.testing.testrunner.layer.UnitTests in 0.000 seconds.


Building the documentation using :mod:`zc.buildout`
===================================================
The :mod:`dataflake.ldapconnection` buildout installs the Sphinx 
scripts required to build the documentation, including testing 
its code snippets:

.. code-block:: sh

    $ cd docs
    $ make doctest
    Running Sphinx v1.6.5
    ...
    running tests...

    Doctest summary
    ===============
        0 tests
        0 failures in tests
        0 failures in setup code
    build succeeded.
    Testing of doctests sn the sources finished, look at the  results in \
         .../docs/_build/doctest/output.txt.


Making a release
================
These instructions assume that you have a development sandbox set 
up using :mod:`zc.buildout` as the scripts used here are generated 
by the buildout.

.. code-block:: sh

  $ bin/buildout -o
  $ python setup.py sdist bdist_wheel upload --sign

The ``bin/buildout`` step will make sure the correct package information 
is used.

