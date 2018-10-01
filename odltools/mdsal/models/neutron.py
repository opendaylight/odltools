# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "neutron"


def neutron(store, args):
    return Neutron(MODULE, store, args)


class Neutron(Model):
    CONTAINER = "neutron"
    MODULE = "name"
    UUID = "uuid"

    FLOATINGIPS = "floatingips"
    FLOATINGIP = "floatingip"
    NETWORKS = "networks"
    NETWORK = "network"
    PORTS = "ports"
    PORT = "port"
    ROUTERS = "routers"
    ROUTER = "router"
    SECURITY_GROUPS = "security-groups"
    SECURITY_GROUP = "security-group"
    SECURITY_RULES = "security-rules"
    SECURITY_RULE = "security-rule"
    SUBNETS = "subnets"
    SUBNET = "subnet"
    TRUNKS = "trunks"
    TRUNK = "trunk"
    BGPVPNS = "bgpvpns"
    BGPVPN = "bgpvpn"
    ALL_OBJECTS = [FLOATINGIPS, NETWORKS, PORTS, SECURITY_GROUPS, SECURITY_RULES, SUBNETS, TRUNKS, BGPVPNS]
    OBJECT_MAP = {FLOATINGIPS: FLOATINGIP, NETWORKS: NETWORK, PORTS: PORT, ROUTERS: ROUTER,
                  SECURITY_GROUPS: SECURITY_GROUP, SECURITY_RULES: SECURITY_RULE,
                  SUBNETS: SUBNET, TRUNKS: TRUNK, BGPVPNS: BGPVPN}

    def get_clist(self):
        return self.data[self.CONTAINER]

    def get_ccl(self, parent, child, item):
        c = self.data and self.data.get(parent, {})
        lst = self.get_list(c, child, item)
        return lst

    def get_ccl_by_key(self, parent, child, item, key="uuid"):
        d = {}
        lst = self.get_ccl(parent, child, item)
        for l in lst:
            d[l[key]] = l
        return d

    def get_objects_by_key(self, key="uuid", obj=NETWORKS):
        item = self.OBJECT_MAP.get(obj, self.NETWORKS)
        return self.get_ccl_by_key(self.CONTAINER, obj, item, key)

    def get_ip_address_from_port(self, port):
        fixed_ips = port.get("fixed-ips")
        if fixed_ips is None:
            return None
        fixed_ip = fixed_ips[0]
        return fixed_ip.get("ip-address")
