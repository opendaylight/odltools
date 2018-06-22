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
from odltools.mdsal.models.neutron import Neutron
from odltools.mdsal.models.neutron import neutron


class TestNeutron(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        args = tests.Args(path=tests.get_resources_path())
        self.neutron = neutron(Model.CONFIG, args)

    def test_get_objects_by_key(self):
        d = self.neutron.get_objects_by_key(obj=Neutron.NETWORKS)
        self.assertIsNotNone(d.get('bd8db3a8-2b30-4083-a8b3-b3fd46401142'))
        d = self.neutron.get_objects_by_key(obj=Neutron.PORTS)
        self.assertIsNotNone(d.get('8e3c262e-7b45-4222-ac4e-528db75e5516'))


if __name__ == '__main__':
    unittest.main()
