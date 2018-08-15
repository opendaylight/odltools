# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "itm"


def transport_zones(store, args):
    return TransportZones(MODULE, store, args)


class TransportZones(Model):
    CONTAINER = "transport-zones"
    CLIST = "transport-zone"
    CLIST_KEY = "zone-name"
    DPN_ID = "dpn-id"
    SUBNETS = "subnets"
    IP_ADDRESS = "ip-address"
    VTEPS = "vteps"

    def get_transport_zone(self, zone_name):
        zones = self.get_clist_by_key()
        return zones.get(zone_name)

    def get_tunnel_endpoints(self, dpn_id):
        dpn_teps_infos = self.get_clist()
        for dpn_teps_info in dpn_teps_infos:
            if dpn_teps_info[self.DPN_ID] == dpn_id:
                return dpn_teps_info[self.TUNNEL_END_POINTS]
