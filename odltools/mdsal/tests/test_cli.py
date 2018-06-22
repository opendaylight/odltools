# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import shutil
import unittest

from odltools import logg
from odltools.mdsal.models import model
from odltools.mdsal.models import models
from odltools.mdsal.models.Modules import netvirt_data_models
from odltools.mdsal.tests import Args


@unittest.skip("skipping")
class TestCli(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.DEBUG)
        self.args = Args(path="/tmp/testmodels2", pretty_print=True)

    def test_get_models(self):
        # Ensure odl is running at localhost:8181
        # Remove an existing directory
        if os.path.exists(self.args.path):
            if os.path.islink(self.args.path):
                os.unlink(self.args.path)
            else:
                shutil.rmtree(self.args.path)

        # self.args.modules = ["config/network-topology:network-topology/topology/ovsdb:1"]
        models.get_models(self.args)

        # assert each model has been saved to a file
        for res in self.args.modules:
            res_split = res.split("/")
            store = res_split[0]
            model_path = res_split[1]
            path_split = model_path.split(":")
            module = path_split[0]
            name = path_split[1]
            filename = model.make_filename(self.args.path, store, module, name)
            self.assertTrue(os.path.isfile(filename))

    def test_get_all_models(self):
        # Ensure odl is running at localhost:8181
        # Remove an existing directory
        if os.path.exists(self.args.path):
            if os.path.islink(self.args.path):
                os.unlink(self.args.path)
            else:
                shutil.rmtree(self.args.path)

        models.get_models(self.args)

        # assert each model has been saved to a file
        for res in netvirt_data_models:
            res_split = res.split("/")
            store = res_split[0]
            model_path = res_split[1]
            path_split = model_path.split(":")
            module = path_split[0]
            name = path_split[1]
            filename = model.make_filename(self.args.path, store, module, name)
            self.assertTrue(os.path.isfile(filename))


if __name__ == '__main__':
    unittest.main()
