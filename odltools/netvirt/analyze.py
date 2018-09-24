# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models import constants
from odltools.mdsal.models.model import Model
from odltools.mdsal.models.neutron import Neutron
from odltools.mdsal.models.opendaylight_inventory import Nodes
from odltools.netvirt import config
from odltools.netvirt import flows
from odltools.netvirt import inv_flow_parser
from odltools.netvirt import utils


def print_keys(args, ifaces, ifstates):
    print("InterfaceNames: {}\n".format(utils.format_json(args, ifaces.keys())))
    print("IfStateNames: {}".format(utils.format_json(args, ifstates.keys())))


def by_ifname(args, ifname, ifstates, ifaces):
    config.get_models(args, {
        "itm_state_tunnels_state",
        "neutron_neutron"})
    ifstate = ifstates.get(ifname)
    iface = ifaces.get(ifname)
    port = None
    tunnel = None
    tun_state = None
    if is_vlan_port(iface):
        ports = config.gmodels.neutron_neutron.get_objects_by_key(obj=Neutron.PORTS)
        port = ports.get(ifname)
    elif is_tunnel_port(iface):
        tun_states = config.gmodels.itm_state_tunnels_state.get_clist_by_key()
        tun_state = tun_states.get(ifname)
    else:
        print("UNSUPPORTED IfType")
    return iface, ifstate, port, tunnel, tun_state


def is_vlan_port(iface):
    if iface and iface.get('type') == constants.IFTYPE_VLAN:
        return True
    return False


def is_tunnel_port(iface):
    if iface and iface.get('type') == constants.IFTYPE_TUNNEL:
        return True
    return False


def is_patch_port(iface):
    if iface and 'patch' in iface.get('name'):
        return True
    return False


def analyze_interface(args):
    config.get_models(args, {
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state"})
    if not args.ifname or args.ifname == 'all':
        analyze_all_interfaces(args)
        return
    ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
    ifstates = config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
    ifname = args.ifname
    iface, ifstate, port, tunnel, tunState = by_ifname(args, ifname, ifstates, ifaces)
    print("InterfaceConfig: \n{}".format(utils.format_json(args, iface)))
    print("InterfaceState: \n{}".format(utils.format_json(args, ifstate)))
    if port:
        print("NeutronPort: \n{}".format(utils.format_json(args, port)))
        # analyze_neutron_port(port, iface, ifstate)
        return
    if tunnel:
        print("Tunnel: \n{}".format(utils.format_json(args, tunnel)))
    if tunState:
        print("TunState: \n{}".format(utils.format_json(args, tunState)))
    # if ifstate:
        # ncid = ifstate.get('lower-layer-if')[0]
        # nodeid = ncid[:ncid.rindex(':')]
        # analyze_inventory(nodeid, True, ncid, ifname)
        # analyze_inventory(nodeid, False, ncid, ifname)


def analyze_all_interfaces(args):
    ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
    ifstates = config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
    print("\nAnalyzing all interfaces")
    all_up = True
    for ifname in ifaces:
        iface, ifstate, nport, tunnel, tunState = by_ifname(args, ifname, ifstates, ifaces)
        if not ifstate:
            if not nport or (nport and 'network:' not in nport.get('device-owner')):
                print("..ifState not found for {}".format(ifname))
                all_up = False
        elif ifstate.get('oper-status') != 'up':
            print('..ifState for {} is {}'.format(ifname, ifstate.get('oper-status')))
            all_up = False
        if is_tunnel_port(iface) and not tunState:
            print("..tunnelState not found for {}".format(ifname))
            all_up = False
        elif is_vlan_port(iface) and not is_patch_port(iface) and not nport:
            print("..NeutronPort not found for {}".format(ifname))
            all_up = False
    if all_up:
        print("..all interfaces are up")


def analyze_trunks(args):
    config.get_models(args, {
        "ietf_interfaces_interfaces",
        # "ietf_interfaces_interfaces_state",
        "l3vpn_vpn_interfaces",
        "neutron_neutron"})

    vpninterfaces = config.gmodels.l3vpn_vpn_interfaces.get_clist_by_key()
    ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
    # ifstates = config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
    nports = config.gmodels.neutron_neutron.get_objects_by_key(obj=Neutron.PORTS)
    ntrunks = config.gmodels.neutron_neutron.get_objects_by_key(obj=Neutron.TRUNKS)
    subport_dict = {}
    for v in ntrunks.values():
        nport = nports.get(v.get('port-id'))
        s_subports = []
        for subport in v.get('sub-ports'):
            sport_id = subport.get('port-id')
            snport = nports.get(sport_id)
            svpniface = vpninterfaces.get(sport_id)
            siface = ifaces.get(sport_id)
            # sifstate = ifstates.get(sport_id)
            subport['SubNeutronPort'] = 'Correct' if snport else 'Wrong'
            subport['SubVpnInterface'] = 'Correct' if svpniface else 'Wrong'
            subport['ofport'] = Model.get_ofport_from_ncid()
            if siface:
                vlan_mode = siface.get('odl-interface:l2vlan-mode')
                parent_iface_id = siface.get('odl-interface:parent-interface')
                if vlan_mode != 'trunk-member':
                    subport['SubIface'] = 'WrongMode'
                elif parent_iface_id != v.get('port-id'):
                    subport['SubIface'] = 'WrongParent'
                elif siface.get('odl-interface:vlan-id') != subport.get('segmentation-id'):
                    subport['SubIface'] = 'WrongVlanId'
                else:
                    subport['SubIface'] = 'Correct'
            else:
                subport['SubIface'] = 'Wrong'
                # s_subport = 'SegId:{}, PortId:{}, SubNeutronPort:{}, SubIface:{}, SubVpnIface:{}'.format(
                #     subport.get('segmentation-id'), subport.get('port-id'),
                #     subport.get('SubNeutronPort'),
                #     subport.get('SubIface'),
                #     subport.get('SubVpnInterface'))
            s_subports.append(subport)
            subport_dict[subport['port-id']] = subport
            s_trunk = 'TrunkName:{}, TrunkId:{}, PortId:{}, NeutronPort:{}, SubPorts:{}'.format(
                v.get('name'), v.get('uuid'), v.get('port-id'),
                'Correct' if nport else 'Wrong', utils.format_json(args, s_subports))
            print(s_trunk)
            print("\n------------------------------------")
            print("Analyzing Flow status for SubPorts")
            print("------------------------------------")
            for flow in flows.sort(flows.get_all_flows(args, ['ifm'], ['vlanid']), 'ifname'):
                subport = subport_dict.get(flow.get('ifname')) or None
                vlanid = subport.get('segmentation-id') if subport else None
                ofport = subport.get('ofport') if subport else None
                flow_status = 'Okay'
                if flow.get('ofport') and flow.get('ofport') != ofport:
                    flow_status = 'OfPort mismatch for SubPort:{} and Flow:{}'.format(subport, flow.get('flow'))
                if flow.get('vlanid') and flow.get('vlanid') != vlanid:
                    flow_status = 'VlanId mismatch for SubPort:{} and Flow:{}'.format(subport, flow.get('flow'))
                if subport:
                    print("SubPort:{},Table:{},FlowStatus:{}".format(
                        subport.get('port-id'), flow.get('table'), flow_status))


def analyze_neutron_port(args, port, iface, ifstate):
    for flow in flows.sort(flows.get_all_flows(args, ['all']), 'table'):
        if ((flow.pdata.get('ifname') == port['uuid']) or
                (flow.pdata.get('lport') and ifstate and flow.pdata['lport'] == ifstate.get('if-index')) or
                (iface['name'] == flow.pdata.get('ifname'))):
            result = flows.show_all(flow)
            print(result)
            print("Flow: {}".format(utils.format_json(None, inv_flow_parser.parse_flow(flow.rdata))))


def analyze_inventory(args):
    config.get_models(args, {
        "odl_inventory_nodes",
        "odl_inventory_nodes_operational"})

    if args.store == "config":
        nodes = config.gmodels.odl_inventory_nodes.get_clist_by_key()
        print("Inventory Config:")
    else:
        print("Inventory Operational:")
        nodes = config.gmodels.odl_inventory_nodes_operational.get_clist_by_key()
    node = nodes.get("openflow:" + args.nodeid)
    if node is None:
        print("node: {} was not found".format("openflow:" + args.nodeid))
        return
    tables = node.get(Nodes.NODE_TABLE)
    # groups = node.get(Nodes.NODE_GROUP)
    flow_list = []
    print("Flows: ")
    for table in tables:
        for flow in table.get('flow', []):
            if not args.ifname or args.ifname in utils.nstr(flow.get('flow-name')):
                flow_dict = {'table': table['id'], 'id': flow['id'], 'name': flow.get('flow-name'), 'flow': flow}
                flow_list.append(flow_dict)
    flowlist = sorted(flow_list, key=lambda x: x['table'])
    for flow in flowlist:
        print("Table: {}".format(flow['table']))
        print("FlowId: {}, FlowName: {} ".format(flow['id'], flow.get('name')))


def analyze_nodes(args):
    config.update_gnodes(args)
    gnodes = config.get_gnodes()

    print("\nnodes\n")
    for nodeid, node in sorted(gnodes.items()):
        dpn_id = node.get("dpn_id")
        ip = node.get("ip")
        print("dpnid: {}, ip: {}".format(dpn_id, ip))

    for nodeid, node in sorted(gnodes.items()):
        dpn_id = nodeid
        ip = node.get("ip")
        ovs_version = node.get("ovs_version")
        hostname = node.get("hostname")
        print("\ndpnid: {}, dpid: {:016x}, ip: {}, version: {}\n"
              "hostname: {}"
              .format(dpn_id, int(dpn_id), ip, ovs_version, hostname))
        pline = "{:3} {:17} {:14} {:15} {:36} {:17}"
        print(pline.format("of#", "mac", "name", "ip", "uuid", "nmac"))
        print(pline.format("-"*3, "-"*17, "-"*14, "-"*15, "-"*36, "-"*17))
        ports = node.get("ports", {})
        for portno, port in sorted(ports.items()):
            print(pline.format(
                port.get("portno"), port.get("mac"), port.get("name"),
                port.get("ip", ""), port.get("uuid"), port.get("nmac")))


def analyze_tunnels(args):
    config.get_models(args, {
        "ietf_interfaces_interfaces",
        "ietf_interfaces_interfaces_state",
        "itm_transport_zones",
        "itm_state_tunnel_list",
        "itm_state_tunnels_state",
        "itm_state_dpn_endpoints",
        "network_topology_network_topology",
        "network_topology_network_topology_operational"})
    t_zones = config.gmodels.itm_transport_zones.get_clist_by_key()
    for k in t_zones:
        t_zone = t_zones.get(k)
        print("Analysing transport-zone:{}".format(k))
        if not t_zone.get('subnets'):
            print("..No subnets configured for TransportZone {}".format(k))
            continue
        for subnet in t_zone.get('subnets'):
            analyze_vteps(args, k, subnet, subnet.get('vteps', []))


def analyze_vteps(args, tz_name, subnet, vteps):
    # TODO: Support for direct tunnels
    missing_endpoints = []
    vtep_count = 0
    endpoint_count = 0
    tunnel_list = config.gmodels.itm_state_tunnel_list.get_tunnels_by_src_dst_dpn()
    tunnel_names_list = []
    bridge_nodes = config.gmodels.network_topology_network_topology_operational.get_nodes_by_dpid()
    missing_br_int_vteps = {}
    for dpnid, node in bridge_nodes.iteritems():
        if node.get('node-id').endswith('br-int'):
            missing_br_int_vteps[dpnid] = node
    for vtep in vteps:
        vtep_count += 1
        src_dpn = vtep.get('dpn-id')
        missing_br_int_vteps.pop(src_dpn)
        tunnel_endpoint = config.gmodels.itm_state_dpn_endpoints.get_tunnel_endpoints(src_dpn)
        src_tun_list = tunnel_list.get(src_dpn)
        if not src_tun_list:
            print("..direct tunnels not supported yet")
            return
        if not tunnel_endpoint:
            missing_endpoints.append(vtep)
        else:
            endpoint_count += 1
            for remote_vtep in vteps:
                dst_dpn = remote_vtep.get('dpn-id')
                if src_dpn == dst_dpn:
                    continue
                if not src_tun_list.get(dst_dpn):
                    print("..Tunnel Missing between {} and {}".format(src_dpn, dst_dpn))
                else:
                    tunnel_names_list.extend(src_tun_list.get(dst_dpn).get('tunnel-interface-names'))
    for dpnid, node in missing_br_int_vteps.iteritems():
        node_name = node.get('node-id')[len('ovsdb://uuid/'):]
        print("..{}:{} not present in vteps configured".format(dpnid, node_name))
    ifaces = config.gmodels.ietf_interfaces_interfaces.get_clist_by_key()
    ifstates = config.gmodels.ietf_interfaces_interfaces_state.get_clist_by_key()
    tunnel_states = config.gmodels.itm_state_tunnels_state.get_clist_by_key()
    all_tunnels_up = True
    for tunnel_name in tunnel_names_list:
        if not ifaces.get(tunnel_name):
            print("..TunnelInterface {} missing from config".format(tunnel_name))
            all_tunnels_up = False
        elif not ifstates.get(tunnel_name):
            all_tunnels_up = False
            print("..InterfaceState missing for tunnel {}".format(tunnel_name))
        elif ifstates.get(tunnel_name).get('oper-status') != 'up':
            all_tunnels_up = False
            print("..Interface {} is down".format(tunnel_name))
        elif not tunnel_states.get(tunnel_name):
            all_tunnels_up = False
            print("..TunnelState missing for {}".format(tunnel_name))
        elif not tunnel_states.get(tunnel_name).get('tunnel-state'):
            all_tunnels_up = False
            print("..TunnelState for {} is False".format(tunnel_name))
    if all_tunnels_up:
        print("..All tunnels are up")
    for vtep in missing_endpoints:
        print("..TunnelEndpoint configuration missing for dpn:{},ip:{}", vtep.get('dpn-id'), vtep.get('ip-address'))
