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
from odltools.mdsal.models.opendaylight_inventory import nodes


class TestOpendaylightInventory(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        args = tests.Args(path=tests.get_resources_path())
        self.nodes = nodes(Model.CONFIG, args)

    def test_get_clist_by_key(self):
        d = self.nodes.get_clist_by_key()
        self.assertIsNotNone(d.get('openflow:132319289050514'))

    def test_get_groups(self):
        d = self.nodes.get_groups()
        self.assertIsNotNone(d.get('132319289050514'))

    def test_get_dpn_host_mapping(self):
        d = self.nodes.get_dpn_host_mapping()
        self.assertIsNone(d.get('132319289050514'))


if __name__ == '__main__':
    unittest.main()
