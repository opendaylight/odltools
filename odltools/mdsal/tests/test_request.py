# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import unittest

from odltools import logg
from odltools.mdsal import request
from odltools.mdsal import tests


class TestRequest(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        self.filename = os.path.join(tests.get_resources_path(), 'config___itm-state__dpn-endpoints.json')

    def test_read_file(self):
        data = request.read_file(self.filename)
        self.assertEqual(len(data), 1)


if __name__ == '__main__':
    unittest.main()
