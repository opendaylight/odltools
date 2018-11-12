# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.netvirt import config


def get_all_models(args):
    config.get_models(args, {
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "itm_transport_zones",
        "itm_state_tunnel_list",
        "itm_state_tunnels_state",
        "itm_state_dpn_endpoints",
        "itm_state_dpn_teps_state",
        "network_topology_network_topology",
        "network_topology_network_topology_operational"})


def get_vteps(args, tz_name="default-transport-zone"):
    config.get_models(args, {
        "itm_transport_zones"})
    t_zones = config.gmodels.itm_transport_zones.get_clist_by_key()
    t_zone = t_zones.get(tz_name)
    if not t_zone or not t_zone.get('subnets'):
        return None
    for subnet in t_zone.get('subnets'):
        # Currently assume just one subnet configured.
        # Revisit when multiple supported
        if subnet.get('vteps'):
            return subnet.get('vteps')
    return None


def check_vteps(args, vteps, bridge_name='br-int'):
    bridge_nodes = config.gmodels.network_topology_network_topology_operational.get_nodes_by_dpid()
    all_vteps = {}
    missing_vteps = {}
    present_vteps = {}
    for dpnid, node in bridge_nodes.items():
        if node.get('node-id').endswith(bridge_name):
            missing_vteps[dpnid] = node
    for vtep in vteps:
        src_dpn = vtep.get('dpn-id')
        missing_vteps.pop(src_dpn, 0)
        present_vteps[src_dpn] = vtep
    all_vteps['missing'] = missing_vteps
    all_vteps['present'] = present_vteps
    return all_vteps


def get_ovsdb_tunnels(args, type='config'):
    if type == 'config':
        bridge_nodes = config.gmodels.network_topology_network_topology.get_nodes_by_tid_and_key()
    else:
        bridge_nodes = config.gmodels.network_topology_network_topology_operational.get_nodes_by_dpid()
    ovsdb_tunnels = {}
    for node in bridge_nodes.values():
        for port in node.get('termination-point', []):
            if port.get('tp-id', '').startswith('tun'):
                ovsdb_tunnels[port.get('tp-id')] = port
    return ovsdb_tunnels


def get_tunnel_endpoints(args, vteps):
    tunnel_endpoints = {}
    missing_endpoints = []
    present_endpoints = []
    for src_dpn in vteps:
        vtep = vteps.get(src_dpn)
        tunnel_endpoint = config.gmodels.itm_state_dpn_endpoints.get_tunnel_endpoints(src_dpn)
        if not tunnel_endpoint:
            missing_endpoints.append(vtep)
        present_endpoints.append(vtep)
    tunnel_endpoints['missing'] = missing_endpoints
    tunnel_endpoints['present'] = present_endpoints
    return tunnel_endpoints


def get_tunnels(args, vteps):
    tunnel_list = config.gmodels.itm_state_tunnel_list.get_tunnels_by_src_dst_dpn()
    direct_tunnels = config.gmodels.itm_state_dpn_teps_state.get_tunnels_by_src_dst_dpn()
    all_tunnels = {}
    missing_tunnels = []
    present_tunnels = {}
    if not tunnel_list and not direct_tunnels:
        return None
    for src_dpn in vteps:
        vtep = vteps.get(src_dpn)
        src_tun_list = tunnel_list.get(src_dpn) if tunnel_list else None
        src_direct_tun = direct_tunnels.get(src_dpn) if direct_tunnels else None
        for dst_dpn in vteps:
            remote_vtep = vteps.get(dst_dpn)
            if src_dpn == dst_dpn:
                continue
            dst_present = (src_tun_list.get(dst_dpn) if src_tun_list else
                           src_direct_tun.get(dst_dpn) if src_direct_tun else None)
            if not dst_present:
                missing_tunnel = {}
                missing_tunnel['src-vtep'] = vtep
                missing_tunnel['dst-vtep'] = remote_vtep
                missing_tunnels.append(missing_tunnel)
            else:
                present_tunnel = {}
                present_tunnel['src-vtep'] = vtep
                present_tunnel['dst-vtep'] = remote_vtep
                if src_tun_list:
                    tunnel_names = dst_present.get('tunnel-interface-names')
                    for tunnel_name in tunnel_names:
                        present_tunnels[tunnel_name] = present_tunnel
                elif src_direct_tun:
                    tunnel_name = dst_present.get('tunnel-name')
                    present_tunnels[tunnel_name] = present_tunnel
    all_tunnels['missing'] = missing_tunnels
    all_tunnels['present'] = present_tunnels
    return all_tunnels


def is_direct_tunnels(args):
    direct_tunnels = config.gmodels.itm_state_dpn_teps_state.get_clist()
    return True if direct_tunnels else False
