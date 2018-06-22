.. _new-release:

Building a new release of odltools
==================================

#. Update the Version ::

    vi odltools/__init__.py
    git add odltools/__init__.py
    git commit -s -m "release x.y.z"
    git tags -m "release x.y.z" -a x.y.z

#. Run the Tests ::

    tox (or detox)

#. Release on PyPi ::

    python setup.py check
    python setup.py clean
    python setup.py sdist bdist_wheel upload

   .. note::

      The above commands assume a .pypirc like below will be used

   ::

    [distutils]
    index-servers =
        pypi
        testpypi

    [pypi]
    username = cooldude
    password = coolpw

    [testpypi]
    repository: https://test.pypi.org/legacy/
    username = cooldude
    password = coolpw

#. Test the PyPi Install ::

    mkvirtualenv tmptest
    pip install odltools
    python -m odltools -V
    deactivate
    rmvirtualenv tmptest

#. Push the Code ::

    git push origin HEAD:refs/for/master
    git push origin x.y.z

#. Verify All is Good in the World

   Check the `PyPi odltools page <https://pypi.org/project/odltools/>`_, README, release notes, etc.
