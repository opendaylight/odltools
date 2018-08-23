# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
"""Tests for the CLI."""

import functools
import os
import unittest

import six

from odltools.bist import cli

try:
    import unittest.mock as mock  # py3
except ImportError:
    import mock  # py2


def force_empty_suite(f):
    def wrapper(*args, **kwargs):
        with mock.patch.object(cli, 'load_diagnostic_tests',
                               return_value=unittest.TestSuite()) as m:
            args += (m,)
            f(*args, **kwargs)
    return wrapper


def disable_run_tests_mock(f):
    def wrapper(self, *args, **kwargs):
        self.run_tests_patcher.stop()
        f(self, *args, **kwargs)
    return wrapper


class CLITestCase(unittest.TestCase):
    """Tests for the diagnostic CLI."""

    def setUp(self):
        super(CLITestCase, self).setUp()
        # We want to make sure that no patcher was left unstopped
        self.addCleanup(mock.patch.stopall)

        self.run_tests_patcher = mock.patch.object(cli, 'run_tests')
        self.run_tests_mock = self.run_tests_patcher.start()

        self.stream = six.StringIO()
        self.main = functools.partial(cli.main, args=[os.path.dirname(__file__)], stream=self.stream)

    @force_empty_suite
    def test_main_no_args_defaults_diagnostics_to_tests_diagnostic(self, mock_load_diag):
        cli.main(args=[], stream=self.stream)
        mock_load_diag.assert_called_with(['odltools.bist.tests.diagnostic'])

    @force_empty_suite
    def test_main_allows_diagnostic_arguments(self, mock_load_diag):
        cli.main(args=['.'], stream=self.stream)
        mock_load_diag.assert_called_with(['.'])

    @disable_run_tests_mock
    def test_main_allows_different_stream(self):
        self.assertEqual(self.stream.getvalue(), '')
        self.main()
        self.assertIn('Ran 0 tests', self.stream.getvalue())

    def _assert_main_result_based_on_test(self, test_success, expected_result):
        test_result = unittest.TestResult()
        test_result.wasSuccessful = mock.Mock(return_value=test_success)
        self.run_tests_mock.return_value = test_result
        result = self.main()
        self.assertEqual(result, expected_result)

    def test_main_returns_zero_when_tests_succeed(self):
        self._assert_main_result_based_on_test(True, 0)

    def test_main_returns_one_when_tests_fail(self):
        self._assert_main_result_based_on_test(False, 1)

    @mock.patch('sys.exit', new=mock.Mock())
    @force_empty_suite
    def _assert_help_starts_with(self, prefix, prog, _):
        for arg in ('-h', '--help'):
            with mock.patch('sys.stdout', new=self.stream):
                cli.main(args=[arg], program=prog, stream=self.stream)
            self.assertTrue(self.stream.getvalue().startswith(prefix))

    def test_main_allows_help_argument(self):
        self._assert_help_starts_with('usage:', None)

    def test_main_allows_different_program_name(self):
        self._assert_help_starts_with('usage: XXXXXX', 'XXXXXX')

    @mock.patch.object(cli.diag_base.DiagnosticLoader, 'discover')
    def test_load_diagnostics_tests_only_in_py_files(self, load_mock):
        args = ['dir1', 'dir2']
        cli.load_diagnostic_tests(args)
        for arg in args:
            load_mock.assert_any_call(arg, pattern='diag_*.py')

    @mock.patch.object(cli.diag_base.DiagnosticLoader, 'discover')
    def test_load_diagnostics_tests_combines_into_test_suite(self, load_mock):
        def return_start_dir_string(start_dir, pattern=None):
            mock_test = mock.Mock(start_dir=start_dir)
            return mock_test
        load_mock.side_effect = return_start_dir_string
        expected = ['dir1', 'dir2']
        suite = cli.load_diagnostic_tests(expected)
        actual = [mock_test.start_dir for mock_test in suite]
        self.assertEqual(actual, expected)

    def test_load_diagnostics_tests_returns_TestSuite(self):
        suite = cli.load_diagnostic_tests([])
        self.assertIsInstance(suite, unittest.TestSuite)

    @disable_run_tests_mock
    def test_run_tests_returns_TestResult(self):
        result = cli.run_tests(unittest.TestSuite(), stream=self.stream)
        self.assertIsInstance(result, unittest.TestResult)

    @disable_run_tests_mock
    def test_run_tests_outputs_to_stream(self):
        cli.run_tests(unittest.TestSuite(), stream=self.stream)
        self.assertIn('Ran 0 tests', self.stream.getvalue())

    @disable_run_tests_mock
    def test_run_tests_results_dependant_on_test_sucess(self):
        class FakeTest(unittest.TestCase):
            def __init__(self, method_name, success, *args, **kwargs):
                super(FakeTest, self).__init__(method_name, *args, **kwargs)
                self.success = success

            def test_trigger(self):
                if not self.success:
                    self.fail()

        for expected in (True, False):
            result = cli.run_tests(
                FakeTest('test_trigger', expected),
                stream=self.stream,
            )
            self.assertEqual(result.wasSuccessful(), expected)
