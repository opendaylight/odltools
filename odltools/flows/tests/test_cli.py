# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.flows import cli
from odltools.netvirt import tests


class TestOvsFlows(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)

    def test_flows_ovs(self):
        infile = "{}/flow_dumps.1.txt".format(tests.get_resources_path())
        args = ["ovs", infile, "/tmp"]
        cli.main("ovs", args)


if __name__ == '__main__':
    unittest.main()
