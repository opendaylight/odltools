# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
"""Tests for the diagnostic tools"""

import unittest

from odltools.bist.diagnostics import base

try:
    import unittest.mock as mock  # py3
except ImportError:
    import mock  # py2


class DiagnosticTestSuiteTestCase(unittest.TestCase):
    """Tests for the DiagnosticLoader"""

    def setUp(self):
        super(DiagnosticTestSuiteTestCase, self).setUp()
        self.suite = base.DiagnosticTestSuite()

    def test_is_diagnostic_attribute_present(self):
        self.assertTrue(self.suite.is_diagnostic(mock.Mock(spec=['_DIAGNOSTIC'])))

    def test_is_diagnostic_attribute_missing(self):
        self.assertFalse(self.suite.is_diagnostic(mock.Mock(spec=[])))

    def test_only_allows_diagnostic(self):
        # The next 4 lines are to bypass problems that arise in PY2
        TestCase = unittest.TestCase
        TestCase.runTest = mock.Mock()
        Diagnostic = base.Diagnostic
        Diagnostic.runTest = mock.Mock()
        for test in (TestCase(), Diagnostic()):
            self.suite.addTest(test)

        self.assertEqual(self.suite.countTestCases(), 1)

    def test_suiteClass_is_diagnostics(self):
        self.assertTrue(self.suite.is_diagnostic(self.suite))


class DiagnosticLoaderTestCase(unittest.TestCase):
    """Tests for the DiagnosticLoader"""

    def setUp(self):
        super(DiagnosticLoaderTestCase, self).setUp()
        self.loader = base.DiagnosticLoader()

    def test_suiteClass_returns_DiagnosticTestSuite(self):
        # To simplify testing, and not having to write complex test that
        # cover all ways of loading/discovery, we test that suiteClass returns
        # an instance of the tested class that we know only accepts diagnostic
        # tests.
        self.assertIsInstance(self.loader.suiteClass(),
                              base.DiagnosticTestSuite)
