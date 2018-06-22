# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.mdsal import tests
from odltools.mdsal.models.itm_state import dpn_endpoints
from odltools.mdsal.models.itm_state import DpnEndpoints
from odltools.mdsal.models.itm_state import tunnels_state
from odltools.mdsal.models.model import Model

logger = logging.getLogger("test.itmstate")


class TestItmState(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.INFO)
        args = tests.Args(path=tests.get_resources_path())
        self.itm_state_dpn_endpoints = dpn_endpoints(Model.CONFIG, args)
        self.itm_state_tunnels_state = tunnels_state(Model.OPERATIONAL, args)

    def test_read_file(self):
        logger.debug("dpn-endpoints: %s", self.itm_state_dpn_endpoints.data)
        logger.debug("dpn-endpoints: \n%s",
                     self.itm_state_dpn_endpoints.pretty_format(self.itm_state_dpn_endpoints.data))

    def test_get_ip_address(self):
        dpn_ids = self.itm_state_dpn_endpoints.get_dpn_ids()
        dpn_id = dpn_ids[0]
        ip_address = self.itm_state_dpn_endpoints.get_ip_address(dpn_id)
        logger.debug("dpn_id: %s, ip_address: %s", dpn_id, ip_address)
        self.assertEqual(dpn_id, 132319289050514)
        self.assertEqual(ip_address, "10.30.170.17")

    def test_get_all(self):
        logger.debug("dpn-endpoints: %s", self.itm_state_dpn_endpoints.data)
        logger.debug("dpn-endpoints: \n%s",
                     self.itm_state_dpn_endpoints.pretty_format(self.itm_state_dpn_endpoints.data))

        dpn_ids = self.itm_state_dpn_endpoints.get_dpn_ids()
        dpn_id = dpn_ids[0]
        dpn_teps_info = self.itm_state_dpn_endpoints.get_dpn_teps_info(dpn_id)
        logger.debug("dpn_teps_info for %s: %s", dpn_id, dpn_teps_info)

        ip_address = self.itm_state_dpn_endpoints.get_ip_address(dpn_id)
        logger.debug("ip_address: %s", ip_address)
        self.assertEqual(ip_address, "10.30.170.17")

        self.get_info(DpnEndpoints.CONTAINER)
        self.get_info(DpnEndpoints.CLIST)
        self.get_info(DpnEndpoints.TUNNEL_END_POINTS)
        self.get_info(DpnEndpoints.DPN_ID)

    def get_info(self, key):
        info = self.itm_state_dpn_endpoints.get_kv(key, self.itm_state_dpn_endpoints.data, values=[])
        logger.debug("dpn info for %s: %s", key, info)
        return info

    def test_get_ip_address_from_dpn_info(self):
        nodes = self.itm_state_dpn_endpoints.get_clist_by_key()
        node = nodes.get(132319289050514)
        self.assertIsNotNone(node)
        ip = self.itm_state_dpn_endpoints.get_ip_address_from_dpn_info(node)
        self.assertEqual("10.30.170.17", ip)

    def test_get_tunnels_state(self):
        d = self.itm_state_tunnels_state.get_clist_by_key()
        self.assertIsNotNone(d and d['tun428ee8c4fe7'])


if __name__ == '__main__':
    unittest.main()
