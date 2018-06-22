# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.mdsal import tests
from odltools.mdsal.models.id_manager import id_pools
from odltools.mdsal.models.model import Model


class TestIdManager(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        args = tests.Args(path=tests.get_resources_path())
        self.id_pools = id_pools(Model.CONFIG, args)

    def test_get_objects_by_key(self):
        d = self.id_pools.get_clist_by_key()
        self.assertIsNotNone(d.get('interfaces'))


if __name__ == '__main__':
    unittest.main()
