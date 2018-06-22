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
from odltools.mdsal.models.odl_fib import fib_entries


class TestOdlFib(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        args = tests.Args(path=tests.get_resources_path())
        self.fib_entries = fib_entries(Model.CONFIG, args)

    def test_get_clist_by_key(self):
        d = self.fib_entries.get_clist_by_key()
        self.assertIsNotNone(d.get('c7922261-90ab-4757-bc03-93ef3bbbaa19'))

    def test_get_vrf_entries_by_key(self):
        d = self.fib_entries.get_vrf_entries_by_key()
        self.assertIsNotNone(d.get(100011))


if __name__ == '__main__':
    unittest.main()
