# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
"""Provides the base classes necesary to run diagnostic tests."""

import unittest


class Diagnostic(unittest.TestCase):
    """Base class for diagnostic test cases."""

    _DIAGNOSTIC = True


class DiagnosticTestSuite(unittest.TestSuite):
    """Base class that only allows diagnostic tests."""

    _DIAGNOSTIC = True

    def addTest(self, test):
        """
        Add tests to the TestSuite.

        Only allows tests of type Diagnostic to be added.

        If the test to be added is not of type Diagnostic it ignores it.
        """
        if self.is_diagnostic(test):
            super(DiagnosticTestSuite, self).addTest(test)

    @staticmethod
    def is_diagnostic(obj):
        """Determine if the object is a diagnostic test."""
        return hasattr(obj, '_DIAGNOSTIC')


class DiagnosticLoader(unittest.TestLoader):
    """
    Load Diagnostic tests only.

    This will allow to filter out tests that are not intended to diagnose the
    application.
    """

    suiteClass = DiagnosticTestSuite
