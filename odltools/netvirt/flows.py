# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import collections
import json
import logging

from odltools.flows.odl_flows import OdlFlow
from odltools.mdsal.models import constants
from odltools.mdsal.models.model import Model
from odltools.mdsal.models.neutron import Neutron
from odltools.mdsal.models.opendaylight_inventory import Nodes
from odltools.netvirt import config
from odltools.netvirt import flow_parser
from odltools.netvirt import inv_flow_parser
from odltools.netvirt import services as svcs
from odltools.netvirt import tables as tbls
from odltools.netvirt import utils
from odltools.netvirt.inv_flow_parser import get_matchstr
from odltools.netvirt.utils import to_hex

logger = logging.getLogger("netvirt.flows")

OPTIONALS = ['ifname', 'lport', 'elan-tag', 'mpls', 'vpnid', 'reason', 'serviceid',
             'dst-mac', 'src-mac', 'int-ip4', 'ext-ip4', 'int-mac', 'ext-mac',
             'ofport', 'vlanid']


def filter_flow(flow_dict, filter_list):
    if not filter_list:
        return True
    for flow_filter in filter_list:
        if flow_dict.get(flow_filter):
            return True
    return False


def get_all_flows(args, modules=None, filter_by=None):
    config.get_models(args, {
        "elan_elan_instances",
        "elan_elan_interfaces",
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "l3vpn_vpn_interfaces",
        "odl_fib_fib_entries",
        "odl_interface_meta_if_index_interface_map",
        "odl_l3vpn_vpn_instance_to_vpn_id",
        "odl_inventory_nodes"})

    modules = modules if modules else args.modules if args.modules else "all"
    filter_by = filter_by if filter_by else []
    if not modules:
        return 'No modules specified'
    ifaces = {}
    ifstates = {}
    ifindexes = {}
    # bindings = {}
    einsts = {}
    eifaces = {}
    fibentries = {}
    vpnids = {}
    vpninterfaces = {}
    groups = {}
    if 'all' in modules:
        table_list = list(range(0, 255))
    else:
        table_list = list(set([table for mod in modules for table in tbls.get_table_map(mod)]))
    of_nodes = config.gmodels.odl_inventory_nodes.get_clist_by_key()
    if 'ifm' in modules:
        ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifstates = config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
    if 'l3vpn' in modules:
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
        fibentries = fibentries or config.gmodels.odl_fib_fib_entries.get_vrf_entries_by_key()
        vpnids = vpnids or config.gmodels.odl_l3vpn_vpn_instance_to_vpn_id.get_clist_by_key()
        vpninterfaces = vpninterfaces or config.gmodels.l3vpn_vpn_interfaces.get_clist_by_key()
        groups = groups or config.gmodels.odl_inventory_nodes.get_groups(of_nodes)
    if 'acl' in modules:
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
        einsts = einsts or config.gmodels.elan_elan_instances.get_clist_by_key()
        eifaces = eifaces or config.gmodels.elan_elan_interfaces.get_clist_by_key()
    if 'elan' in modules:
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        einsts = einsts or config.gmodels.elan_elan_instances.get_clist_by_key()
        eifaces = eifaces or config.gmodels.elan_elan_interfaces.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
    if 'all' in modules:
        groups = groups or config.gmodels.odl_inventory_nodes.get_groups(of_nodes)
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifstates = ifstates or config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
        fibentries = fibentries or config.gmodels.odl_fib_fib_entries.get_vrf_entries_by_key()
        vpnids = vpnids or config.gmodels.odl_l3vpn_vpn_instance_to_vpn_id.get_clist_by_key()
        vpninterfaces = vpninterfaces or config.gmodels.l3vpn_vpn_interfaces.get_clist_by_key()
        einsts = einsts or config.gmodels.elan_elan_instances.get_clist_by_key()
        eifaces = eifaces or config.gmodels.elan_elan_interfaces.get_clist_by_key()
    flows = []
    for node in of_nodes.values():
        tables = [x for x in node[Nodes.NODE_TABLE] if x['id'] in table_list]
        for table in tables:
            for odl_flow in table.get('flow', []):
                flow = OdlFlow(odl_flow)
                flow.pdata = {'dpnid': Model.get_dpn_from_ofnodeid(node['id'])}
                get_any_flow(flow, groups,
                             ifaces, ifstates, ifindexes,
                             fibentries, vpnids, vpninterfaces,
                             einsts, eifaces)
                if flow.pdata is not None and filter_flow(flow.pdata, filter_by):
                    flows.append(flow)
    return flows


def get_any_flow(flow, groups, ifaces, ifstates, ifindexes,
                 fibentries, vpnids, vpninterfaces, einsts, eifaces):
    table = flow.rdata['table_id']
    if table in tbls.get_table_map('ifm'):
        return stale_ifm_flow(flow, ifaces, ifstates)
    elif table in tbls.get_table_map('acl'):
        return stale_acl_flow(flow, ifaces, ifindexes, einsts, eifaces)
    elif table in tbls.get_table_map('elan'):
        return stale_elan_flow(flow, ifaces, ifindexes, einsts, eifaces)
    elif table in tbls.get_table_map('l3vpn'):
        return stale_l3vpn_flow(flow, groups, ifaces, ifindexes, vpnids, vpninterfaces, fibentries)
    elif table in tbls.get_table_map('nat'):
        return stale_nat_flow(flow, ifaces, ifindexes)
    else:
        flow_parser.get_flow_info_from_any(flow)
        iface = (get_iface_for_lport(ifaces, ifindexes, flow.pdata.get('lport'))
                 if flow.pdata.get('lport') else None)
        if iface and iface.get('name'):
            flow.pdata['ifname'] = iface['name']
    # Get generic fields in here if not already captured
    # flow_parser.get_flow_info_from_any(flow)


def stale_l3vpn_flow(flow, groups, ifaces, ifindexes,
                     vpnids, vpninterfaces, fibentries):
    flow_parser.get_flow_info_from_l3vpn_table(flow)
    flow.pdata['reason'] = None
    lport = flow.pdata.get('lport')
    iface = get_iface_for_lport(ifaces, ifindexes, lport)
    if lport and not iface:
        flow.pdata['reason'] = 'Interface for lport not found'
        return
    if iface:
        flow.pdata['ifname'] = iface['name']
    vpninterface = vpninterfaces.get(iface.get('name')) if iface else None
    if not vpninterfaces:
        flow.pdata['reason'] = 'VpnInterface for lport not found'
        return
    vpnid = flow.pdata.get('vpnid')
    if vpnid and not vpnids.get(vpnid):
        flow.pdata['reason'] = 'VpnInstance for VpnId not found'
        return
    if vpnid and vpninterface and vpnids.get(vpnid):
        if (vpninterface.get('vpn-instance-name') !=
                vpnids[vpnid]['vpn-instance-name']):
            flow.pdata['reason'] = 'Lport VpnId mismatch'
            return
    label = flow.pdata.get('label')
    fibentry = fibentries.get(label) if label else None
    if label and not fibentry:
        flow.pdata['reason'] = 'Fibentry for MplsLabel not found'
        return
    # Label check for group
    prefix = fibentry.get('destPrefix') if fibentry else None
    if prefix and flow.pdata.get('group-id'):
        gid = flow.pdata.get('group-id')
        if groups.get(gid) and (
                    groups.get(gid).get('group-name', '') != prefix):
            flow.pdata['reason'] = 'DestPrefix mismatch for label and group'
            return


def stale_elan_flow(flow, ifaces, ifindexes, einsts, eifaces):
    # hex(int(mask, 16) & int(hexa, 16))
    flow_parser.get_flow_info_from_elan_table(flow)
    flow.pdata['reason'] = None
    lport = flow.pdata.get('lport')
    eltag = flow.pdata.get('elan-tag')
    iface = get_iface_for_lport(ifaces, ifindexes, lport)
    if lport and not iface:
        flow.pdata['reason'] = 'Interface for lport not found'
        return
    if iface:
        flow.pdata['ifname'] = iface['name']
    if not is_tunnel_iface(iface) and not is_elantag_valid(eltag, eifaces, einsts, iface):
        flow.pdata['reason'] = 'Lport Elantag mismatch'
        return


def stale_acl_flow(flow, ifaces, ifindexes, einsts, eifaces):
    flow_parser.get_flow_info_from_acl_table(flow)
    flow.pdata['reason'] = None
    lport = flow.pdata.get('lport')
    eltag = flow.pdata.get('elan-tag')
    iface = get_iface_for_lport(ifaces, ifindexes, lport)
    if lport and not iface:
        flow.pdata['reason'] = 'Interface for lport not found'
        return
    if iface:
        flow.pdata['ifname'] = iface['name']
    if not is_elantag_valid(eltag, eifaces, einsts, iface):
        flow.pdata['reason'] = 'Lport Elantag mismatch'
        return


def stale_nat_flow(flow, ifaces, ifindexes):
    # WiP - Vishal Thapar
    flow_parser.get_flow_info_from_nat_table(flow)
    flow.pdata['reason'] = None


def is_elantag_valid(eltag, eifaces, einsts, iface):
    if iface and eltag and eltag != get_eltag_for_iface(eifaces, einsts, iface):
        return False
    return True


def is_tunnel_iface(iface):
    if iface and iface.get('type', '') == constants.IFTYPE_TUNNEL:
        return True
    return False


def is_correct_elan_flow(flow, mmac, einsts, flow_host):
    flow_etag = flow.pdata.get('elan-tag')
    for k, v in mmac.iteritems():
        mac_host = v.get('compute')
        if einsts.get(k):
            einst_tag = einsts.get(k).get('elan-tag')
            # print einst_tag, flow_etag, mac_host
            if flow_etag and einst_tag and flow_etag == einst_tag:
                if mac_host.startswith(flow_host):
                    act_resubmit = inv_flow_parser.get_act_resubmit(flow.rdata)
                    if act_resubmit and act_resubmit.get('table') == 220:
                        return 'Correct'
                else:
                    act_tunnel = inv_flow_parser.get_act_set_tunnel(flow.rdata)
                    if act_tunnel:
                        return 'Correct'
                return 'Wrong'
    return 'Wrong'


def get_iface_for_lport(ifaces, ifindexes, lport):
    if lport:
        if ifindexes.get(lport):
            ifname = ifindexes.get(lport).get('interface-name')
            if ifname and ifaces.get(ifname):
                return ifaces.get(ifname)
    return None


def get_eltag_for_iface(eifaces, einsts, iface):
    ifname = iface.get('name') if iface else None
    eiface = eifaces.get(ifname) if ifname else None
    einst_name = eiface.get('elan-instance-name') if eiface else None
    einst = einsts.get(einst_name) if einst_name else None
    return einst.get('elan-tag') if einst else None


def get_stale_flows(modules=['ifm']):
    if not modules:
        return 'No modules specified'
    ifaces = {}
    ifstates = {}
    ifindexes = {}
    # bindings = {}
    einsts = {}
    eifaces = {}
    fibentries = {}
    vpnids = {}
    vpninterfaces = {}
    groups = {}
    table_list = list(set([table for module in modules for table in tbls.get_table_map(module)]))
    # table_list = [214, 244]

    of_nodes = config.gmodels.odl_inventory_nodes.get_clist_by_key()
    if 'ifm' in modules:
        ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifstates = config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
    if 'l3vpn' in modules:
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
        fibentries = fibentries or config.gmodels.odl_fib_fib_entries.get_vrf_entries_by_key()
        vpnids = vpnids or config.gmodels.odl_l3vpn_vpn_instance_to_vpn_id.get_clist_by_key()
        vpninterfaces = vpninterfaces or config.gmodels.l3vpn_vpn_interfaces.get_clist_by_key()
        groups = groups or config.gmodels.odl_inventory_nodes.get_groups(of_nodes)
    if 'acl' in modules:
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
        einsts = einsts or config.gmodels.elan_elan_instances.get_clist_by_key()
        eifaces = eifaces or config.gmodels.elan_elan_interfaces.get_clist_by_key()
    if 'elan' in modules:
        ifaces = ifaces or config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
        einsts = einsts or config.gmodels.elan_elan_instances.get_clist_by_key()
        eifaces = eifaces or config.gmodels.elan_elan_interfaces.get_clist_by_key()
        ifindexes = ifindexes or config.gmodels.odl_interface_meta_if_index_interface_map.get_clist_by_key()
    stale_flows = []
    for node in of_nodes.values():
        tables = [x for x in node[Nodes.NODE_TABLE] if x['id'] in table_list]
        for table in tables:
            for odl_flow in table.get('flow', []):
                flow = OdlFlow(odl_flow)
                flow.pdata = {'dpnid': Model.get_dpn_from_ofnodeid(node['id'])}
                if 'ifm' in modules and table['id'] in tbls.get_table_map('ifm'):
                    stale_ifm_flow(flow, ifaces, ifstates)
                if 'l3vpn' in modules and table['id'] in tbls.get_table_map('l3vpn'):
                    stale_l3vpn_flow(flow, groups, ifaces, ifindexes, vpnids,
                                     vpninterfaces, fibentries)
                if 'elan' in modules and table['id'] in tbls.get_table_map('elan'):
                    stale_elan_flow(flow, ifaces, ifindexes, einsts, eifaces)
                if 'acl' in modules and table['id'] in tbls.get_table_map('acl'):
                    stale_acl_flow(flow, ifaces, ifindexes, einsts, eifaces)
                if 'nat' in modules and table['id'] in tbls.get_table_map('nat'):
                    stale_nat_flow(flow, ifaces, ifstates)
                if flow.pdata.get('reason'):
                    stale_flows.append(flow)
    return stale_flows


def show_link_flow_binding(args):
    stale_ids, bindings = get_stale_bindings(args)
    flows = get_stale_flows()
    print(len(stale_ids), len(flows))
    for flow in flows:
        if flow.pdata['ifname'] in stale_ids and 'bound-services' in bindings[flow.pdata['ifname']]:
            print("Flow with binding: {}".format(flow.pdata['ifname']))
        else:
            print("Flow without binding: {}".format(flow.pdata['ifname']))


def show_stale_flows(args, sort_by='table_id'):
    config.get_models(args, {
        "elan_elan_instances",
        "elan_elan_interfaces",
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "interface_service_bindings_service_bindings",
        "l3vpn_vpn_interfaces",
        # "mip_mac",
        "neutron_neutron",
        "odl_fib_fib_entries",
        "odl_interface_meta_if_index_interface_map",
        "odl_l3vpn_vpn_instance_to_vpn_id",
        "odl_inventory_nodes",
        "odl_inventory_nodes_operational"})
    compute_map = config.gmodels.odl_inventory_nodes_operational.get_dpn_host_mapping()
    nports = config.gmodels.neutron_neutron.get_objects_by_key(obj=Neutron.PORTS)
    modules = [args.modules] if args.modules else tbls.get_all_modules()
    for flow in sort(get_stale_flows(modules), sort_by):
        host = compute_map.get(flow.pdata.get('dpnid'), flow.pdata.get('dpnid'))
        ip_list = get_ips_for_iface(nports, flow.pdata.get('ifname'))
        if ip_list:
            flow.pdata['iface-ips'] = ip_list
        flow.pdata['host'] = host
        result = show_all(flow)
        print(result)
        # path = get_data_path('flows', flow)
        # print("http://192.168.2.32:8383/restconf/config/{}".format(path))
        if not args.metaonly:
            print("Flow: ", utils.format_json(args, inv_flow_parser.parse_flow(flow.rdata)))


def show_elan_flows(args):
    config.get_models(args, {
        "elan_elan_instances",
        "elan_elan_interfaces",
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "odl_interface_meta_if_index_interface_map",
        "odl_inventory_nodes",
        "odl_inventory_nodes_operational"})
    compute_map = config.gmodels.odl_inventory_nodes_operational.get_dpn_host_mapping()
    for flow in sort(get_all_flows(args, modules=['elan']), 'id'):
        host = compute_map.get(flow.pdata.get('dpnid'), flow.pdata.get('dpnid'))
        flow.pdata['host'] = host
        result = "{}, Flow:{}".format(show_all(flow),
                                      utils.format_json(args, inv_flow_parser.parse_flow(flow.rdata)))
        print(result)


def get_key_for_dup_detect(args, flow):
    result = '{}:{}:{}'.format(flow.pdata.get('dpnid'), flow.rdata.get('table_id'), get_matchstr(args, flow.rdata))
    return result


def show_dup_flows(args):
    config.get_models(args, {
        "elan_elan_instances",
        "elan_elan_interfaces",
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "interface_service_bindings_service_bindings",
        "l3vpn_vpn_interfaces",
        # "mip_mac",
        "odl_fib_fib_entries",
        "odl_interface_meta_if_index_interface_map",
        "odl_l3vpn_vpn_instance_to_vpn_id",
        "odl_inventory_nodes",
        "odl_inventory_nodes_operational"})
    mmac = {}  # config.gmodels.mip_mac.get_entries_by_key()
    einsts = config.gmodels.elan_elan_instances.get_clist_by_key()
    compute_map = config.gmodels.odl_inventory_nodes_operational.get_dpn_host_mapping()

    flows = sort(get_all_flows(args), 'table_id')
    matches = collections.defaultdict(list)
    for flow in flows:
        dup_key = get_key_for_dup_detect(args, flow)
        if dup_key:
            if matches and matches.get(dup_key):
                matches[dup_key].append(flow)
            else:
                matches[dup_key].append(flow)
    for k, v in matches.iteritems():
        if len(v) > 1:
            dpnid = k.split(':')[0]
            host = compute_map.get(dpnid, dpnid)
            result = "Host:{}, FlowCount:{}, MatchKey:{}, ElanTag:{}".format(host, len(v), k, v[0].get('elan-tag'))
            print(result)
            for idx, flow in enumerate(v):
                result = "Duplicate"
                mac_addr = flow.pdata('dst-mac')
                if mac_addr and mmac.get(mac_addr):
                    result = is_correct_elan_flow(flow, mmac.get(mac_addr), einsts, host)
                print("    {} Flow-{}:{}"
                      .format(result, idx,
                              utils.format_json(args, inv_flow_parser.parse_flow(flow.pdata('flow')))))


def show_learned_mac_flows(args):
    config.get_models(args, {
        "elan_elan_instances",
        "elan_elan_interfaces",
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "interface_service_bindings_service_bindings",
        "l3vpn_vpn_interfaces",
        # "mip_mac",
        "neutron_neutron",
        "odl_fib_fib_entries",
        "odl_interface_meta_if_index_interface_map",
        "odl_l3vpn_vpn_instance_to_vpn_id",
        "odl_inventory_nodes",
        "odl_inventory_nodes_operational"})
    # nports = config.gmodels.neutron_neutron.get_ports_by_key(key='mac-address')
    nports = config.gmodels.neutron_neutron.get_objects_by_key(obj=Neutron.PORTS, key='mac-address')
    compute_map = config.gmodels.odl_inventory_nodes_operational.get_dpn_host_mapping()

    flows = sort(get_all_flows(args, ['elan']), 'table_id')
    for flow in flows:
        odl_flow = flow.rdata.get('flow')
        dpnid = flow.pdata.get('dpnid')
        host = compute_map.get(dpnid, dpnid)
        if ((flow.pdata.get('table') == 50 and odl_flow.get('idle-timeout') == 300
             and not nports.get(flow.pdata.get('src-mac')))
            or (flow.pdata.get('table') == 51 and not nports.get(flow.pdata.get('dst-mac')))):  # NOQA

            flow.pdata['host'] = host
            result = show_all(flow.pdata)
            print(result)
            print("Flow: {}".format(utils.format_json(args, inv_flow_parser.parse_flow(flow))))


def get_stale_bindings(args):
    # ietf_interfaces_interfaces = ietf_interfaces.interfaces(Model.CONFIG, args)
    # interface_service_bindings_service_bindings = interface_service_bindings.service_bindings(Model.CONFIG, args)
    ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
    bindings, orphans = config.gmodels.interface_service_bindings_service_bindings.get_service_bindings()
    return set(bindings.keys()) - set(ifaces.keys()), bindings


def dump_flows(args, modules=None, sort_by='table_id', filter_by=None):
    config.get_models(args, {
        "neutron_neutron",
        "odl_inventory_nodes_operational",
        "network_topology_network_topology_operational"})
    filter_by = filter_by if filter_by else []
    compute_map = config.gmodels.odl_inventory_nodes_operational.get_dpn_host_mapping()
    node_map = config.gmodels.network_topology_network_topology_operational.get_dpn_host_mapping()
    nports = config.gmodels.neutron_neutron.get_objects_by_key(obj=Neutron.PORTS)
    for flow in sort(get_all_flows(args, modules, filter_by), sort_by):
        dpnid = flow.pdata.get('dpnid')
        host = compute_map.get(dpnid)
        if not host:
            host = node_map.get(int(dpnid))
        ip_list = get_ips_for_iface(nports, flow.pdata.get('ifname'))
        if ip_list:
            flow.pdata['iface-ips'] = ip_list
        flow.pdata['host'] = host
        result = show_all(flow)
        print(result)
        if not args.metaonly:
            print("Flow: {}".format(utils.format_json(args, inv_flow_parser.parse_flow(flow.rdata))))


def show_all_flows(args):
    config.get_models(args, {
        "elan_elan_instances",
        "elan_elan_interfaces",
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "interface_service_bindings_service_bindings",
        "l3vpn_vpn_interfaces",
        "neutron_neutron",
        "odl_fib_fib_entries",
        "odl_interface_meta_if_index_interface_map",
        "odl_l3vpn_vpn_instance_to_vpn_id",
        "odl_inventory_nodes",
        "odl_inventory_nodes_operational"})
    modules = [args.modules] if args.modules else None
    dump_flows(args, modules)


def get_ips_for_iface(nports, ifname):
    ips = []
    port = nports.get(ifname) if ifname else None
    fixed_ips = port.get('fixed-ips', []) if port else []
    for fixed_ip in fixed_ips:
        ips.append(fixed_ip['ip-address'])
    return ips


def stale_ifm_flow(flow, ifaces, ifstates):
    flow_parser.get_flow_info_from_ifm_table(flow)
    flow_ifname = flow.pdata['ifname']
    iface = ifaces.get(flow_ifname)
    flow.pdata['reason'] = None
    if flow_ifname is not None and not iface:
        flow.pdata['reason'] = 'Interface doesnt exist'
        return
    elif flow_ifname and ifstates.get(flow_ifname):
        ifstate = ifstates.get(flow_ifname)
        ncid_list = ifstate.get('lower-layer-if')
        ncid = ncid_list[0] if ncid_list else None
        dpn = Model.get_dpn_from_ofnodeid(ncid)
        if dpn and dpn != flow.pdata['dpnid']:
            flow.pdata['reason'] = 'DpnId mismatch for flow and Interface'
            return
        if flow.pdata.get('lport') and ifstate.get('if-index') and flow.pdata['lport'] != ifstate['if-index']:
            flow.pdata['reason'] = 'Lport and IfIndex mismatch'
            return
        if (flow.pdata.get('ofport') and ifstate.get('lower-layer-if')
            and flow.pdata['ofport'] != Model.get_ofport_from_ncid(ifstate.get('lower-layer-if')[0])):  # NOQA
            flow.pdata['reason'] = 'OfPort mismatch'
            return
        if (flow.pdata.get('vlanid') and iface.get('odl-interface:vlan-id')
            and flow.pdata['vlanid'] != iface.get('odl-interface:vlan-id')):  # NOQA
            flow.pdata['reason'] = 'VlanId mismatch'
            return


def sort(data, field):
    return sorted(data, key=lambda x: x.rdata[field])


def show_all(flow):
    dpnid = flow.pdata.get('dpnid')
    host = flow.pdata.get('host')
    result = 'Table:{}'.format(flow.rdata['table_id'])
    if host:
        result = '{}, Host:{}'.format(result, host)
    if dpnid:
        result = '{}, DpnId:{}/{}'.format(result, dpnid, to_hex(dpnid))
    result = '{}, FlowId:{}'.format(result, flow.rdata.get('id'))
    lport = flow.pdata.get('lport')
    elantag = flow.pdata.get('elan-tag')
    serviceid = flow.pdata.get('serviceid')
    label = flow.pdata.get('mpls')
    vpnid = flow.pdata.get('vpnid')
    ip = flow.pdata.get('iface-ips')
    smac = flow.pdata.get('src-mac')
    dmac = flow.pdata.get('dst-mac')
    intip4 = flow.pdata.get('int-ip4')
    extip4 = flow.pdata.get('ext-ip4')
    intmac = flow.pdata.get('int-mac')
    extmac = flow.pdata.get('ext-mac')
    vlanid = flow.pdata.get('vlanid')
    ofport = flow.pdata.get('ofport')
    if lport:
        result = '{}, LportTag: {}/{}'.format(result, lport, to_hex(lport))
    if serviceid:
        result = '{}, Service: {}'.format(result, svcs.get_service_name(serviceid))
    if ofport:
        result = '{}, OfPort: {}'.format(result, ofport)
    if vlanid:
        result = '{}, VlanId: {}'.format(result, vlanid)
    if vpnid:
        result = '{}, VpnId: {}/{}'.format(result, vpnid, to_hex(vpnid*2))
    if label:
        result = '{}, MplsLabel: {}'.format(result, label)
    if elantag:
        result = '{}, ElanTag: {}/{}'.format(result, elantag, to_hex(elantag))
    if smac:
        result = '{}, SrcMac: {}'.format(result, smac)
    if dmac:
        result = '{}, DstMac: {}'.format(result, dmac)
    if intip4:
        result = '{}, InternalIPv4: {}'.format(result, intip4)
    if extip4:
        result = '{}, ExternalIPv4: {}'.format(result, extip4)
    if intmac:
        result = '{}, InternalMAC: {}'.format(result, intmac)
    if extmac:
        result = '{}, ExternalMAC: {}'.format(result, extmac)
    if ip:
        result = '{}, LportIp: {}'.format(result, json.dumps(ip))
    result = '{}, Reason: {}'.format(result, flow.pdata.get('reason'))
    return result
