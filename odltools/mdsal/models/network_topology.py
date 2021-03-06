# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "network-topology"


def network_topology(store, args, mid="topology/ovsdb:1"):
    return NetworkTopology(MODULE, store, args, mid)


class NetworkTopology(Model):
    # TODO: class currently assumes the ovsdb:1 has been used so need to fix that to take a topology-id
    CONTAINER = "network-topology"
    TOPOLOGY = "topology"
    NODE = "node"
    OVSDB1 = "ovsdb:1"
    TOPOLOGY_OVSDB1 = TOPOLOGY + "/" + OVSDB1

    def get_clist(self):
        return self.data.get(self.TOPOLOGY, [])

    def get_topology_by_tid(self, tid="ovsdb:1"):
        topologies = self.get_clist()
        for topology in topologies:
            if topology['topology-id'] == tid:
                return topology
        return {}

    def get_nodes_by_tid(self, tid="ovsdb:1"):
        topology = self.get_topology_by_tid(tid)
        return topology.get(self.NODE, [])

    def get_nodes_by_tid_and_key(self, tid="ovsdb:1", key='node-id'):
        d = {}
        nodes = self.get_nodes_by_tid(tid)
        for node in nodes:
            d[node[key]] = node
        return d

    def get_nodes_by_dpid(self, tid="ovsdb:1"):
        d = {}
        nodes = self.get_nodes_by_tid(tid)
        for node in nodes:
            dpid = self.get_datapathid_from_node(node)
            if dpid:
                d[dpid] = node
        return d

    def get_dpn_host_mapping(self):
        d = {}
        nodes = self.get_nodes_by_tid_and_key()
        for nodeid in nodes:
            node = nodes.get(nodeid)
            dpid = self.get_datapathid_from_node(node)
            if dpid:
                parentid = self.get_parent_nodeid(nodeid)
                host = self.get_host_id_from_node(nodes.get(parentid))
                d[dpid] = host
        return d

    def get_host_id_from_node(self, node):
        extids = node.get("ovsdb:openvswitch-external-ids", {})
        for extid in extids:
            if extid.get("external-id-key") == "hostname":
                return extid.get("external-id-value")

    def get_local_ip_from_node(self, node):
        extids = node.get("ovsdb:openvswitch-other-configs", {})
        for extid in extids:
            if extid.get("other-config-key") == "local_ip":
                return extid.get("other-config-value")

    def get_datapathid_from_node(self, node):
        datapathid = node.get("ovsdb:datapath-id")
        if datapathid:
            return int(datapathid.replace(':', ''), 16)

    def get_parent_nodeid(self, nodeid):
        parentid = nodeid.split('/bridge/')[0]
        return parentid if parentid else ''
