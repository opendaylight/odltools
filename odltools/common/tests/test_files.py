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
from odltools.netvirt import tests


class TestRequest(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        self.filename = "{}/flow_dumps.1.txt".format(tests.get_resources_path())
        self.outpath = "/tmp/flow_dumps.1.out.txt"

    def test_readlines(self):
        data = files.readlines(self.filename)
        self.assertEqual(len(data), 76)

    def test_writelines(self):
        data = files.readlines(self.filename)
        self.assertEqual(len(data), 76)
        files.writelines(self.outpath, data, True)
        self.assertTrue(os.path.exists(self.outpath))


if __name__ == '__main__':
    unittest.main()
