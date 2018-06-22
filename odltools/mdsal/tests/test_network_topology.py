# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.mdsal import tests
from odltools.mdsal.models.model import Model
from odltools.mdsal.models.network_topology import network_topology
from odltools.mdsal.models.network_topology import NetworkTopology


class TestNetworkTopology(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        args = tests.Args(path=tests.get_resources_path())
        self.network_topology = network_topology(Model.CONFIG, args, NetworkTopology.TOPOLOGY_OVSDB1)

    def test_get_topologies(self):
        self.assertIsNotNone(self.network_topology.get_clist())

    def test_get_nodes_by_key(self):
        d = self.network_topology.get_nodes_by_tid_and_key()
        self.assertIsNotNone(d.get('ovsdb://uuid/8eabb815-5570-42fc-9635-89c880ebc4ac/bridge/br-int'))


if __name__ == '__main__':
    unittest.main()
