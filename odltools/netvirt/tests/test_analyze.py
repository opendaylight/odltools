# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import cli as root_cli
from odltools import logg
from odltools.netvirt import analyze
from odltools.netvirt import tests
from odltools.netvirt.tests import capture


class TestAnalyze(unittest.TestCase):
    # TODO: capture stdout and check for list of tables.

    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        self.args = tests.Args(path=tests.get_resources_path())

    def test_analyze_trunks(self):
        with capture.capture(analyze.analyze_trunks, self.args) as output:
            print(output)

    def test_analyze_interface(self):
        self.args.ifname = "98c2e265-b4f2-40a5-8f31-2fb5d2b2baf6"
        with capture.capture(analyze.analyze_interface, self.args) as output:
            self.assertTrue("98c2e265-b4f2-40a5-8f31-2fb5d2b2baf6" in output)

    def test_analyze_inventory(self):
        self.args.store = "config"
        self.args.nodeid = "132319289050514"
        with capture.capture(analyze.analyze_inventory, self.args) as output:
            self.assertTrue("132319289050514" in output)
        self.args.store = "operational"
        self.args.nodeid = "233201308854882"
        # not a great test, but there are no flows in the operational
        with capture.capture(analyze.analyze_inventory, self.args) as output:
            self.assertTrue("Inventory Operational" in output)

    def test_analyze_nodes_cli(self):
        parser = root_cli.create_parser()
        args = parser.parse_args(["netvirt", "analyze", "nodes", "-p",
                                  "--path=" + tests.get_resources_path()])
        with capture.capture(args.func, args) as output:
            self.assertTrue("203251201875890" in output)


if __name__ == '__main__':
    unittest.main()
