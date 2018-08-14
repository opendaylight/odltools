# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging

from odltools.netvirt import capture_node_info
from odltools.netvirt import config

logger = logging.getLogger("netvirt.cluster")

SKIP_LIST = ['org.opendaylight.mdsal.AsyncServiceCloseEntityType']
ovs_nodes = {}
dpn_host_map = {}


def get_entity_name(entity, entity_type):
    ORG_ODL = 'org.opendaylight'
    SERVICE_ENTITY_TYPE = 'org.opendaylight.mdsal.ServiceEntityType'
    name = entity_type
    if entity_type == 'ovsdb':
        id = entity.get('id')
        # Sample: node-id='ovsdb://uuid/58f491df-0645-432a-a828-8f4afa603e05']
        node_id = id.split('node-id=')[1][1:-2]
        if node_id and ovs_nodes and ovs_nodes.get(node_id):
            ovs_node = ovs_nodes.get(node_id)
            hostname = config.gmodels.network_topology_network_topology_operational.get_host_id_from_node(ovs_node)
            hostip = config.gmodels.network_topology_network_topology_operational.get_local_ip_from_node(ovs_node)
            name = '{}:{}/{}'.format(entity_type, hostname if hostname else node_id, hostip if hostip else '')
    elif entity_type.startswith(SERVICE_ENTITY_TYPE):
        id = entity.get('id')
        name = id.split('name=')[1][1:-2]
        if name and name.startswith('openflow'):
            dpnid = name.split(':')[1]
            hostname = dpn_host_map.get(int(dpnid), 'unknown')
            name = '{}:{}/{}'.format('openflow', hostname, dpnid)
    elif entity_type.startswith(ORG_ODL):
        name = entity_type[len(ORG_ODL) + 1:]
    return name


def print_entity_owners(args, owners):
    print("{:55} owner (candidates)".format("entity"))
    print("{} {}".format('-' * 55, '-' * 18))
    for k, v in sorted(owners.items()):
        if v.get('type') not in SKIP_LIST:
            for entity in v.get('entity'):
                owner = entity.get('owner')
                candidate_list = ""
                name = get_entity_name(entity, v.get('type'))
                for candidate in entity.get('candidate', []):
                    candidate_list = '{}{},'.format(candidate_list, candidate.get('name'))
                print("{:55} {} ({})".format(name, owner, candidate_list.rstrip(',')))


def show_eos(args):
    global ovs_nodes
    global dpn_host_map
    config.get_models(args, {"entity_owners_entity_owners", "network_topology_network_topology_operational"})
    owners = config.gmodels.entity_owners_entity_owners.get_clist_by_key()
    ovs_nodes = config.gmodels.network_topology_network_topology_operational.get_nodes_by_tid_and_key()
    dpn_host_map = config.gmodels.network_topology_network_topology_operational.get_dpn_host_mapping()
    print("========================")
    print("Entity Ownership Service")
    print("========================")
    print_entity_owners(args, owners)


def show_cluster_information(args):
    print("===================")
    print("Cluster Information")
    print("===================")
    print(capture_node_info.capture_node_info(args))
