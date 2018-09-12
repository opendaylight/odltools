# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model
from odltools.netvirt import inv_flow_parser

MAC_LEN = 17

# Flow table constants

PREFIX_211_GOTO = 'Egress_Fixed_Goto_Classifier_'
PREFIX_211_DHCPSv4 = 'Egress_DHCP_Server_v4'
PREFIX_211_DHCPSv6 = 'Egress_DHCP_Server_v6_'
PREFIX_211_DHCPCv4 = 'Egress_DHCP_Client_v4'
PREFIX_211_DHCPCv6 = 'Egress_DHCP_Client_v6_'
PREFIX_211_ARP = 'Egress_ARP_'
PREFIX_211_L2BCAST = 'Egress_L2Broadcast_'
PREFIX_211_ICMPv6 = 'Egress_ICMPv6_'

PREFIX_213 = 'Egress_Fixed_Conntrk_'
PREFIX_214 = 'Egress_Fixed_Conntrk_Drop'
PREFIX_215 = 'Egress_Fixed_NonConntrk_Drop'
PREFIX_241_DHCPv4 = 'Ingress_DHCP_Server_v4'
PREFIX_241_DHCPv6 = 'Ingress_DHCP_Server_v6_'
PREFIX_241_ICMPv6 = 'Ingress_ICMPv6_'
PREFIX_241_ARP = 'Ingress_ARP_'
PREFIX_241_BCASTv4 = 'Ingress_v4_Broadcast_'
PREFIX_241_GOTO = 'Ingress_Fixed_Goto_Classifier_'
PREFIX_243 = 'Ingress_Fixed_Conntrk_'
PREFIX_244 = 'Ingress_Fixed_Conntrk_Drop'
PREFIX_245 = 'Ingress_Fixed_NonConntrk_Drop'

PREFIX_FOR_LPORT = {211: [PREFIX_211_GOTO, PREFIX_211_DHCPSv4,
                          PREFIX_211_DHCPSv6, PREFIX_211_DHCPCv4,
                          PREFIX_211_DHCPCv6, PREFIX_211_ARP,
                          PREFIX_211_L2BCAST, PREFIX_211_ICMPv6],
                    212: [],
                    213: [PREFIX_213],
                    214: [PREFIX_214],
                    215: [PREFIX_215],
                    241: [PREFIX_241_DHCPv4, PREFIX_241_DHCPv6,
                          PREFIX_241_ICMPv6, PREFIX_241_ARP,
                          PREFIX_241_BCASTv4, PREFIX_241_GOTO],
                    242: [],
                    243: [PREFIX_243],
                    244: [PREFIX_244],
                    245: [PREFIX_245]}

PREFIX_SGR_ETHER = 'ETHERnull_'
PREFIX_SGR_ICMP = 'ICMP_'
PREFIX_SGR_TCP = 'TCP_'
PREFIX_SGR_UDP = 'UDP_'
PREFIX_SGR_OTHER = 'OTHER_PROTO'

PREFIX_LPORT_SGR = {211: [], 212: [], 213: [],
                    214: [PREFIX_SGR_ETHER, PREFIX_SGR_ICMP, PREFIX_SGR_TCP,
                          PREFIX_SGR_UDP, PREFIX_SGR_OTHER],
                    215: [PREFIX_SGR_ETHER, PREFIX_SGR_ICMP, PREFIX_SGR_TCP,
                          PREFIX_SGR_UDP, PREFIX_SGR_OTHER],
                    241: [], 242: [], 243: [],
                    244: [PREFIX_SGR_ETHER, PREFIX_SGR_ICMP, PREFIX_SGR_TCP,
                          PREFIX_SGR_UDP, PREFIX_SGR_OTHER],
                    245: [PREFIX_SGR_ETHER, PREFIX_SGR_ICMP, PREFIX_SGR_TCP,
                          PREFIX_SGR_UDP, PREFIX_SGR_OTHER]
                    }


def get_flow_info_from_any(flow):
    w_mdata = inv_flow_parser.get_instruction_writemeta(flow.rdata)
    lport = flow.pdata.get('lport') if flow.pdata else None
    serviceid = flow.pdata.get('serviceid') if flow.pdata else None
    if w_mdata:
        metadata = w_mdata['metadata']
        mask = w_mdata['metadata-mask']
        lport = inv_flow_parser.get_lport_from_metadata(metadata, mask) if not lport else lport
        if lport:
            flow.pdata['lport'] = int(lport, 16)
        serviceid = inv_flow_parser.get_service_id_from_metadata(metadata, mask) if not serviceid else serviceid
        if serviceid:
            flow.pdata['serviceid'] = int(serviceid, 16)
    m_metadata = inv_flow_parser.get_match_metadata(flow.rdata)
    if m_metadata:
        elan = flow.pdata.get('elan-tag')
        vpnid = flow.pdata.get('vpnid')
        metadata = m_metadata['metadata']
        mask = m_metadata['metadata-mask']
        if not lport:
            lport = inv_flow_parser.get_lport_from_metadata(metadata, mask)
            if lport:
                flow.pdata['lport'] = int(lport, 16)
        if not serviceid:
            serviceid = inv_flow_parser.get_service_id_from_metadata(metadata, mask)
            if serviceid:
                flow.pdata['serviceid'] = int(serviceid, 16)
        if not elan:
            elan = inv_flow_parser.get_elan_from_metadata(metadata, mask)
            if elan:
                flow.pdata['elan-tag'] = int(elan, 16)
        if not vpnid:
            vpnid = inv_flow_parser.get_vpnid_from_metadata(metadata, mask)
            if vpnid:
                flow.pdata['vpnid'] = vpnid
    if not flow.pdata.get('dst-mac'):
        m_ether_dest = inv_flow_parser.get_match_ether_dest(flow.rdata)
        if m_ether_dest:
            flow.pdata['dst-mac'] = m_ether_dest.lower()
    if not flow.pdata.get('src-mac'):
        m_ether_src = inv_flow_parser.get_match_ether_src(flow.rdata)
        if m_ether_src:
            flow.pdata['src-mac'] = m_ether_src.lower()
    if not flow.pdata.get('dst-ip4'):
        m_ipv4_dest = inv_flow_parser.get_match_ipv4_dest(flow.rdata)
        if m_ipv4_dest:
            flow.pdata['dst-ip4'] = m_ipv4_dest
    if not flow.pdata.get('src-ip4'):
        m_ipv4_src = inv_flow_parser.get_match_ipv4_src(flow.rdata)
        if m_ipv4_src:
            flow.pdata['src-ip4'] = m_ipv4_src
    return flow.pdata

# Table specific parsing


def get_tunnel_ifname_from_flowid(flow_id):
    ifname = None
    tun_index = flow_id.find('tun')
    if tun_index > -1:
        ifname = flow_id[tun_index:]
    return ifname


def get_ifname_from_flowid(flow_id, table):
    ifname = None
    try:
        if table == 0:
            ifname = get_tunnel_ifname_from_flowid(flow_id)
            if not ifname:
                ifname = ':'.join(flow_id.split(':')[2:])
        else:
            ifname = flow_id.split('.')[2]
    except IndexError:
        ifname = get_tunnel_ifname_from_flowid(flow_id)
    return ifname


def get_flow_info_from_ifm_table(flow):
    flow.pdata['ifname'] = get_ifname_from_flowid(flow.rdata['id'], flow.rdata['table_id'])
    w_mdata = inv_flow_parser.get_instruction_writemeta(flow.rdata)
    if w_mdata:
        metadata = w_mdata['metadata']
        mask = w_mdata['metadata-mask']
        lport = inv_flow_parser.get_lport_from_metadata(metadata, mask)
        if lport:
            flow.pdata['lport'] = int(lport, 16)
        service_id = inv_flow_parser.get_service_id_from_metadata(metadata, mask)
        if service_id:
            flow.pdata['serviceid'] = int(service_id, 16)
    m_reg6 = inv_flow_parser.get_match_reg6(flow.rdata)
    if not flow.pdata.get('lport'):
        lport = inv_flow_parser.get_lport_from_mreg6(m_reg6)
        if lport:
            flow.pdata['lport'] = int(lport, 16)
    if flow.rdata['table_id'] == 0:
        m_inport = inv_flow_parser.get_match_inport(flow.rdata)
        if m_inport:
            flow.pdata['ofport'] = Model.get_ofport_from_ncid(m_inport)
        m_vlan = inv_flow_parser.get_match_vlanid(flow.rdata)
        if m_vlan and m_vlan.get('vlan-id'):
            flow.pdata['vlanid'] = m_vlan.get('vlan-id')
    elif flow.rdata['table_id'] == 220:
        a_output = inv_flow_parser.get_act_output(flow.rdata)
        a_vlan = inv_flow_parser.get_act_set_vlanid(flow.rdata)
        if a_output and a_output.get('output-node-connector'):
            flow.pdata['ofport'] = a_output.get('output-node-connector')
        if a_vlan and a_vlan.get('vlan-id'):
            flow.pdata['vlanid'] = a_vlan.get('vlan-id')
    return flow.pdata


def get_flow_info_from_l3vpn_table(flow):
    label = inv_flow_parser.get_match_mpls(flow.rdata)
    if not label and flow.rdata['table_id'] == 36:
        label = inv_flow_parser.get_match_tunnelid(flow.rdata)
    if label:
        flow.pdata['mpls'] = label
    a_group = inv_flow_parser.get_act_group(flow.rdata)
    if a_group and a_group.get('group-id'):
        flow.pdata['group-id'] = a_group.get('group-id')
    m_metadata = inv_flow_parser.get_match_metadata(flow.rdata)
    if m_metadata:
        metadata = m_metadata['metadata']
        mask = m_metadata['metadata-mask']
        lport = inv_flow_parser.get_lport_from_metadata(metadata, mask)
        if lport:
            flow.pdata['lport'] = int(lport, 16)
        vpnid = inv_flow_parser.get_vpnid_from_metadata(metadata, mask)
        if vpnid:
            flow.pdata['vpnid'] = (metadata & inv_flow_parser.VRFID_MASK) / 2
    return flow.pdata


def get_lport_elan_tags_from_flowid(flowid, dpnid):
    res = flowid[:-MAC_LEN].split(dpnid)
    lport = res[1]
    elan = res[0][2:]
    return lport, elan


def get_flow_info_from_elan_table(flow):
    m_metadata = inv_flow_parser.get_match_metadata(flow.rdata)
    if m_metadata:
        metadata = m_metadata['metadata']
        mask = m_metadata['metadata-mask']
        elan = inv_flow_parser.get_elan_from_metadata(metadata, mask)
        if elan:
            flow.pdata['lport'] = int(elan, 16)
            flow.pdata['elan-tag'] = int(elan, 16)
        lport = inv_flow_parser.get_lport_from_metadata(metadata, mask)
        if lport:
            flow.pdata['lport'] = int(lport, 16)
    m_ether_dest = inv_flow_parser.get_match_ether_dest(flow.rdata)
    if m_ether_dest:
        flow.pdata['dst-mac'] = m_ether_dest.lower()
    m_ether_src = inv_flow_parser.get_match_ether_src(flow.rdata)
    if m_ether_src:
        flow.pdata['src-mac'] = m_ether_src.lower()
    if not flow.pdata.get('lport'):
        reg6_load = inv_flow_parser.get_act_reg6load(flow.rdata)
        if reg6_load and reg6_load.get('value'):
            # reg6load value is lport lft-shit by 8 bits.
            lport = ('%x' % reg6_load.get('value'))[:-2]
            flow.pdata['lport'] = int(lport, 16)
    return flow.pdata


def get_flow_info_from_acl_table(flow):
    m_metadata = inv_flow_parser.get_match_metadata(flow.rdata)
    if m_metadata:
        metadata = m_metadata['metadata']
        mask = m_metadata['metadata-mask']
        lport = inv_flow_parser.get_lport_from_metadata(metadata, mask)
        if lport:
            flow.pdata['lport'] = int(lport, 16)
    a_conntrk = inv_flow_parser.get_act_conntrack(flow.rdata)
    if a_conntrk and a_conntrk.get('conntrack-zone'):
        flow.pdata['elan-tag'] = a_conntrk.get('conntrack-zone')
    return flow.pdata


def get_flow_info_from_nat_table(flow):
    m_metadata = inv_flow_parser.get_match_metadata(flow.rdata)
    vpnid = None
    if m_metadata:
        metadata = m_metadata['metadata']
        mask = m_metadata['metadata-mask']
        lport = inv_flow_parser.get_lport_from_metadata(metadata, mask)
        if lport:
            flow.pdata['lport'] = int(lport, 16)
        vpnid = inv_flow_parser.get_vpnid_from_metadata(metadata, mask)
        if vpnid:
            flow.pdata['vpnid'] = vpnid
    if not vpnid:
        w_metadata = inv_flow_parser.get_instruction_writemeta(flow.rdata)
        metadata = w_metadata['metadata']
        mask = w_metadata['metadata-mask']
        vpnid = inv_flow_parser.get_vpnid_from_metadata(metadata, mask)
        if vpnid:
            flow.pdata['vpnid'] = vpnid
    m_ipv4_dest = inv_flow_parser.get_match_ipv4_dest(flow.rdata)
    m_ipv4_src = inv_flow_parser.get_match_ipv4_src(flow.rdata)
    a_set_ipv4_dest = inv_flow_parser.get_act_set_ipv4_dest(flow.rdata)
    a_set_ipv4_src = inv_flow_parser.get_act_set_ipv4_src(flow.rdata)
    m_ether_src = inv_flow_parser.get_match_ether_src(flow.rdata)
    if flow.rdata['table_id'] in [25, 27]:
        if a_set_ipv4_dest:
            flow.pdata['int-ip4'] = a_set_ipv4_dest
        if m_ipv4_dest:
            flow.pdata['ext-ip4'] = m_ipv4_dest
        m_ether_dest = inv_flow_parser.get_match_ether_dest(flow.rdata)
        if m_ether_dest:
            flow.pdata['ext-mac'] = m_ether_dest
    if flow.rdata['table_id'] in [26, 28]:
        if a_set_ipv4_src:
            flow.pdata['ext-ip4'] = a_set_ipv4_src
        if m_ipv4_src:
            flow.pdata['int-ip4'] = m_ipv4_src
        m_ether_src = inv_flow_parser.get_match_ether_src(flow.rdata)
        if m_ether_src:
            flow.pdata['ext-mac'] = m_ether_src
    return flow.pdata


def get_flow_info_from_acl_table_flowid(flow):
    """
        Format for ACL flow ids is as follows:
        211:Egress_Fixed_Goto_Classifier_<dpId>_<lportTag>_<attachMac>_<attachIp>,
            Egress_DHCP_Server_v4<dpId>_<lportTag>__Drop_,
            Egress_DHCP_Server_v6_<dpId>_<lportTag>__Drop_,
            Egress_DHCP_Client_v4<dpId>_<lportTag>_<macAddress>_Permit_,
            Egress_DHCP_Client_v6_<dpId>_<lportTag>_<macAddress>_Permit_,
            Egress_ARP_<dpId>_<lportTag>_<allowedAddressMac><allowedAddressIp>,
            Egress_L2Broadcast_<dpId>_<lportTag>_<attachMac>,
            Egress_ICMPv6_<dpId>_<lportTag>_134_Drop_,
            Egress_ICMPv6_<dpId>_<lportTag>_<icmpv6Type>_<allowedAddressMac>_Permit_,
            Egress_Fixed_Goto_Classifier_<dpId>_<lportTag>_<attachMac>_<attachIp>

        212:Fixed_Conntrk_Classifier_<dpId>_212_<etherType>_<protocol>
        213:Egress_Fixed_Conntrk_<dpId>_<lportTag>_<etherType>_Recirc
        214:Fixed_Conntrk_Trk_<dpId>_Tracked_Established17,
            Fixed_Conntrk_Trk_<dpId>_Tracked_Related17,
            Egress_Fixed_Conntrk_Drop<dpId>_<lportTag>_Tracked_New,
            Egress_Fixed_Conntrk_Drop<dpId>_<lportTag>_Tracked_Invalid,
            ETHERnull_Egress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP__Egress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__Egress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__Egress_<lportTag>_<sgRuleId>,
            ICMP__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_Egress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,

        215:Egress_Fixed_NonConntrk_Drop<dpId>_<lportTag>_ACL_Rule_Miss,
            ETHERnull_Egress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP__Egress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__Egress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__Egress_<lportTag>_<sgRuleId>,
            ICMP__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_Egress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv4_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv6_remoteACL_interface_aap_<remoteIp>_Egress_<lportTag>_<sgRuleId>

        241:Ingress_v4_Broadcast_<dpId>_Permit,
            Ingress_L2_Broadcast_<dpId>_Permit,
            Ingress_DHCP_Server_v4<dpId>_<lportTag>__Permit_,
            Ingress_DHCP_Server_v6_<dpId>_<lportTag>___Permit_,
            Ingress_ICMPv6_<dpId>_<lportTag>_130_Permit_,
            Ingress_ICMPv6_<dpId>_<lportTag>_134_LinkLocal_Permit_,
            Ingress_ICMPv6_<dpId>_<lportTag>_135_Permit_,
            Ingress_ICMPv6_<dpId>_<lportTag>_136_Permit_,
            Ingress_ARP_<dpId>_<lportTag>,
            Ingress_v4_Broadcast_<dpId>_<lportTag>_<broadcastAddress>_Permit,
            Ingress_Fixed_Goto_Classifier_<dpId>_<lportTag>_<attachMac>_<attachIp>

        242:Fixed_Conntrk_Classifier_<dpId>_242_<etherType>_<protocol>

        243:Ingress_Fixed_Conntrk_<dpId>_<lportTag>_<etherType>_Recirc

        244:Fixed_Conntrk_Trk_<dpId>_Tracked_Established220
            Fixed_Conntrk_Trk_<dpId>_Tracked_Related220,
            Ingress_Fixed_Conntrk_Drop<dpId>_<lportTag>_Tracked_New,
            Ingress_Fixed_Conntrk_Drop<dpId>_<lportTag>_Tracked_Invalid,
            ETHERnull_Ingress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP__Ingress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__Ingress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__Ingress_<lportTag>_<sgRuleId>,
            ICMP__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_Ingress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>

        245:Ingress_Fixed_NonConntrk_Drop<dpId>_<lportTag>_ACL_Rule_Miss,
            ETHERnull_Ingress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ETHERnull_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP__Ingress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__Ingress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__Ingress_<lportTag>_<sgRuleId>,
            ICMP__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP_V4_DESTINATION_<type><code>__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            ICMP_V6_DESTINATION_<type><code>__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            TCP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_DESTINATION_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_<port>_<portMask>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            UDP_SOURCE_ALL__ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_Ingress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv4_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>,
            OTHER_PROTO<protocolNumber>_ipv6_remoteACL_interface_aap_<remoteIp>_Ingress_<lportTag>_<sgRuleId>

    """
    flowid = flow.rdata['id']
    """
        This captures flows with following format:
            *_<dpnid>_<lport>_*
    """
    for prefix in PREFIX_FOR_LPORT[flow.rdata['table_id']]:
        if flowid.startswith(prefix):
            res = flowid[len(prefix):].split('_')
            try:
                flow.pdata['lport'] = int(res[1])
                return flow.pdata
            except ValueError:
                """ Possible cases, ignore:
                    241:Ingress_v4_Broadcast_<dpId>_Permit
                """
                pass
    """
        This captures flows with following format:
            *_<lport>_<sgRuleId>
    """
    for prefix in PREFIX_LPORT_SGR[flow.rdata['table_id']]:
        if flowid.startswith(prefix):
            res = flowid[len(prefix):].split('_')
            try:
                flow.pdata['lport'] = int(res[-2])
                return flow.pdata
            except ValueError:
                """ Possible cases, ignore:
                    Unexpected, log?
                """
                pass
            except IndexError:
                # Unknown flow type. Log???
                pass
    return flow.pdata
