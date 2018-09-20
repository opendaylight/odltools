# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import cli as root_cli
from odltools import logg
from odltools.netvirt import show
from odltools.netvirt import tests
from odltools.netvirt.tests import capture


class TestShow(unittest.TestCase):
    # TODO: capture stdout and check for list of tables.

    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        self.args = tests.Args(path=tests.get_resources_path())
        # self.args = tests.Args(path="/tmp/testmodels")

    def test_show_elan_instances(self):
        with capture.capture(show.show_elan_instances, self.args) as output:
            self.assertTrue("ElanInstance: a5fe7476-9aa1-4bfb-aec4-05d7a1376f45" in output)

    def test_show_groups(self):
        with capture.capture(show.show_groups, self.args) as output:
            self.assertTrue("Dpn: 74851789353527," in output)

    def test_show_flows_all(self):
        self.args.flowtype = "all"
        self.args.pretty_print = True
        self.args.modules = None
        self.args.metaonly = None
        with capture.capture(show.show_flows, self.args) as output:
            self.assertTrue("FlowId:748517893535270tunf68aef23130" in output)

    def test_show_stale_bindings(self):
        show.show_stale_bindings(self.args)

    def test_show_tables(self):
        table_0 = "0:INGRESS"
        table_220 = "220:EG_LPORT_DISP"
        with capture.capture(show.show_tables, self.args) as output:
            self.assertTrue(table_0 in output)
            self.assertTrue(table_220 in output)

    def test_show_idpools_cli(self):
        parser = root_cli.create_parser()
        args = parser.parse_args(["netvirt", "show", "id-pools", "-p",
                                  "--path=" + tests.get_resources_path(),
                                  "all"])
        with capture.capture(args.func, args) as output:
            self.assertTrue("interfaces" in output)

    def test_show_neutron_cli(self):
        parser = root_cli.create_parser()
        args = parser.parse_args(["netvirt", "show", "neutron", "ports", "-p",
                                  "--path=" + tests.get_resources_path()])
        with capture.capture(args.func, args) as output:
            self.assertTrue("8e3c262e-7b45-4222-ac4e-528db75e5516" in output)

    def test_show_neutron(self):
        self.args.object = "ports"
        self.args.pretty_print = True
        self.args.short = True
        with capture.capture(show.show_neutron, self.args) as output:
            self.assertTrue("8e3c262e-7b45-4222-ac4e-528db75e5516" in output)


if __name__ == '__main__':
    unittest.main()
