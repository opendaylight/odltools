# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import unittest

from odltools import cli
from odltools.csit import robotfiles


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


if __name__ == '__main__':
    unittest.main()
