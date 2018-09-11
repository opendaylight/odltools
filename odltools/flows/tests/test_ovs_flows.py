# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import unittest

from odltools import logg
from odltools.common import files
from odltools.flows.ovs_flows import OvsFlowTable
from odltools.netvirt import tests


class TestOvsFlows(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        self.filename = "{}/flow_dumps.1.txt".format(tests.get_resources_path())
        self.data = files.readlines(self.filename)
        self.flow_table = OvsFlowTable(self.data, "ovs", "dpid", "name")

    def test_parse(self):
        self.assertIsNotNone(self.flow_table.num_flows(), 68)

    def test_format(self):
        files.writelines("/tmp/flow_dumps.1.out.txt", self.flow_table.fdata)
        self.assertTrue(os.path.exists(self.filename))
        self.assertEqual(76, len(files.readlines(self.filename)))


if __name__ == '__main__':
    unittest.main()
