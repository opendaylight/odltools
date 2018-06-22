# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.netvirt import config
from odltools.netvirt import tests


class TestConfig(unittest.TestCase):
    # TODO: capture stdout and check for list of tables.

    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        self.args = tests.Args(path=tests.get_resources_path())

    def test_get_gnodes(self):
        config.update_gnodes(self.args)
        gnodes = config.get_gnodes()
        self.assertIsNotNone(gnodes.get("203251201875890"))


if __name__ == '__main__':
    unittest.main()
