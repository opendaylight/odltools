.. image:: https://travis-ci.org/shague/odltools.png?branch=master
   :target: https://travis-ci.org/shague/odltools

.. image:: https://img.shields.io/pypi/v/odltools.svg
   :target: https://pypi.python.org/pypi/odltools

.. image:: https://img.shields.io/pypi/wheel/odltools.svg
   :target: https://pypi.python.org/pypi/odltools

.. image:: https://img.shields.io/pypi/l/odltools.svg
   :target: https://pypi.python.org/pypi/odltools

.. image:: https://img.shields.io/pypi/pyversions/odltools.svg
   :target: https://pypi.python.org/pypi/odltools

odltools
========

A tool to troubleshoot the NetVirt OpenDaylight OpenStack integration.

The tool can fetch mdsal model dumps, openvswitch flow dumps
and extract dumps from CSIT output.xml files.

odltool's documentation can be found at `Read The Docs <http://odltools.readthedocs.org>`_.

Requirements
------------

* python 2.7, 3.3, 3.4, 3.5, 3.6
* requests

Installation
------------
::

  pip install odltools

Usage
-----
::

  usage: python -m odltools [-h] [-v] [-V] {csit,model,analyze} ...

  OpenDaylight Troubleshooting Tools

  optional arguments:
    -h, --help            show this help message and exit
    -v, --verbose         verbosity (-v, -vv)
    -V, --version         show program's version number and exit

  subcommands:
    Command Tool

    {csit,model,analyze}

Contribute
----------
``odltools`` is an open source project that welcomes any and all contributions
from the community. odltools is hosted on `GitHub <http://github.com/shague/odltools>`_
.

Feel free to contribute to:

- `code <https://git.opendaylight.org/gerrit/gitweb?p=odltools.git>`_,
- `documentation <http://odltools.readthedocs.org>`_,
- `bug reports <https://jira.opendaylight.org/projects/ODLTOOLS>`_,
- `contribution reviews <https://git.opendaylight.org/gerrit/#/q/project:odltools>`_.

Please see the `Contributor Guidelines <https://git.opendaylight.org/gerrit/gitweb?p=odltools.git;a=blob;f=CONTRIBUTING.rst>`_
for information about contributing.

Licensing
---------
See the `LICENSE <http://github.com/shague/odltools/LICENSE.txt>`_ file
