# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import argparse
import unittest

import six

from odltools import cli
from odltools.bist import cli as bist_cli
from odltools.csit import robotfiles

try:
    import unittest.mock as mock  # py3
except ImportError:
    import mock  # py2


class TestOdltools(unittest.TestCase):
    DATAPATH = "/tmp/output_01_l2.xml.gz"
    OUTPATH = "/tmp/robotjob"

    def test_parser_empty(self):
        parser = cli.create_parser()
        with self.assertRaises(SystemExit) as cm:
            parser.parse_args([])
        self.assertEqual(cm.exception.code, 2)

    def test_parser_help(self):
        parser = cli.create_parser()
        with self.assertRaises(SystemExit) as cm:
            parser.parse_args(['-h'])
        self.assertEqual(cm.exception.code, 0)

    @unittest.skip("skipping")
    def test_robotfiles_run(self):
        parser = cli.create_parser()
        args = parser.parse_args(['csit', self.DATAPATH, self.OUTPATH, '-g'])
        robotfiles.run(args)

    @unittest.skip("skipping")
    def test_csit(self):
        parser = cli.create_parser()
        args = parser.parse_args(['csit', self.DATAPATH, self.OUTPATH, '-g', '-d'])
        robotfiles.run(args)

    @mock.patch('sys.exit')
    @mock.patch.object(cli, 'parse_args')
    def test_cli_exits_with_error_code(self, parse_args_mock, exit_mock):
        def exit_with_exit_code(args):
            return args.exit_code

        parse_args_mock.return_value = mock.Mock(
            verbose=0,
            func=exit_with_exit_code,
            exit_code=42,
        )

        cli.main()
        exit_mock.assert_called_with(42)

    @mock.patch('sys.exit', new=mock.Mock())
    @mock.patch.object(bist_cli, 'run_bist')
    def test_bist_command_calls_run_bist_with_args(self, mock_run_bist):
        cli.main(args=['bist'])
        args, kwargs = mock_run_bist.call_args
        self.assertIsInstance(args[0], argparse.Namespace)

    @mock.patch('sys.exit', new=mock.Mock())
    @mock.patch.object(bist_cli, 'run_bist', new=mock.Mock())
    def test_bist_command_help_prints_help(self):
        for arg in ('-h', '--help'):
            stream = six.StringIO()
            with mock.patch('sys.stdout', new=stream):
                args = ('bist', arg)
                cli.main(args=args)
            self.assertTrue(stream.getvalue().startswith('usage: '))


if __name__ == '__main__':
    unittest.main()
