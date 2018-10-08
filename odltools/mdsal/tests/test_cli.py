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
from odltools.mdsal.models import model
from odltools.mdsal.models import models
from odltools.mdsal.tests import Args
from odltools.netvirt import tests
import requests_mock


class TestCli(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.DEBUG)
        self.args = Args(path="/tmp/testmodels2", pretty_print=True)
        self.args.modules = [
            "config/elan:elan-instances",
            "config/network-topology:network-topology/topology/ovsdb:1"
        ]

    def test_get_models(self):
        files.rmdir(self.args.path)

        with requests_mock.Mocker() as mrequests:
            for res in self.args.modules:
                args2 = Args(path=tests.get_resources_path(), pretty_print=True)
                filename = model.make_filename_from_resource(args2, res)
                data = files.read(filename)
                url_path = model.make_url_path_from_resource(res)
                url_root, _ = model.make_url_parts(self.args, None)
                mrequests.register_uri('GET', '/'.join((url_root, url_path)), text=data)

            models.get_models(self.args)
            # assert each model has been saved to a file
            for res in self.args.modules:
                filename = model.make_filename_from_resource(self.args, res)
                self.assertTrue(os.path.isfile(filename))


if __name__ == '__main__':
    unittest.main()
