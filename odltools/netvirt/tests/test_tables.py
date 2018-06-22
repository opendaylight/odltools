# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.netvirt import tables


class TestTables(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)

    def test_get_table_name(self):
        self.assertEqual(tables.get_table_name(17), "DISPATCHER")


if __name__ == '__main__':
    unittest.main()
