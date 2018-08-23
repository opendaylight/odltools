# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html
"""CLI to run diagnostics for ODL."""

import argparse
import sys
import unittest

from odltools.bist.diagnostics import base as diag_base

DEFAULT_DIAGNOSTICS = ['odltools.bist.tests.diagnostic']


def add_parser(main_parser):
    """Add subparser to the main parser."""
    parser = main_parser.add_parser(
        "bist",
        description="Runs a set of BIST (built-in self-tests) that provide a"
                    "starting point for debugging an ODL deployment."
    )
    parser.set_defaults(func=run_bist)
    return add_arguments(parser)


def create_parser(program):
    """Return the argument parser for the program."""
    parser = argparse.ArgumentParser(prog=program)
    return add_arguments(parser)


def add_arguments(parser):
    """Add the arguments allowed by the parser."""
    parser.add_argument(
        'diagnostics',
        default=DEFAULT_DIAGNOSTICS,
        nargs='*',
        help='Space separated list of diagnostics to check. '
             'Can be any of: module, package or a folder.'
    )
    return parser


def load_diagnostic_tests(diagnostics):
    """
    Return a test suite with all diagnostic tests.

    Given a list of module, packages or folders, load all diagnostic tests
    that are found.
    """
    loader = diag_base.DiagnosticLoader()
    suite = loader.suiteClass()
    for dir_ in diagnostics:
        suite.addTest(loader.discover(dir_, pattern='diag_*.py'))
    return suite


def run_tests(suite, stream):
    """Run the tests defined in the test suite"""
    runner = unittest.TextTestRunner(stream=stream)
    return runner.run(suite)


def run_bist(cli_args, stream=sys.stderr):
    suite = load_diagnostic_tests(cli_args.diagnostics)
    result = run_tests(suite, stream)

    return 0 if result.wasSuccessful() else 1


def main(program=None, args=None, stream=sys.stderr):
    """Point of entry for the CLI tool"""
    parser = create_parser(program)
    cli_args = parser.parse_args(args)

    return run_bist(cli_args, stream)


if __name__ == '__main__':
    sys.exit(main())
