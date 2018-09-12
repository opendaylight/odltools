# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.netvirt import utils


def get_instruction_writemeta(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'write-metadata' in instruction:
            return instruction['write-metadata']


def get_act_reg6load(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'openflowplugin-extension-nicira-action:nx-reg-load' in action:
                    return action['openflowplugin-extension-nicira-action:nx-reg-load']


def get_act_conntrack(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'openflowplugin-extension-nicira-action:nx-conntrack' in action:
                    return action['openflowplugin-extension-nicira-action:nx-conntrack']


def get_act_group(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'group-action' in action:
                    return action['group-action']


def get_act_set_tunnel(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'set-field' in action and 'tunnel' in action.get('set-field'):
                    return action.get('set-field').get('tunnel')


def get_act_resubmit(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'openflowplugin-extension-nicira-action:nx-resubmit' in action:
                    return action[
                        'openflowplugin-extension-nicira-action:nx-resubmit']


def get_act_set_vlanid(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'set-field' in action and 'vlan-match' in action.get('set-field'):
                    return action.get('set-field').get('vlan-match').get('vlan-id')


def get_act_output(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'output-action' in action and 'output-node-connector' in action.get('output-action'):
                    return action.get('output-action')


def get_act_set_ipv4_dest(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'set-field' in action and 'ipv4-destination' in action.get('set-field'):
                    return action.get('set-field').get('ipv4-destination')


def get_act_set_ipv4_src(flow):
    for instruction in flow['instructions'].get('instruction', []):
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'set-field' in action and 'ipv4-source' in action.get('set-field'):
                    return action.get('set-field').get('ipv4-source')


def get_match_metadata(flow):
    return flow['match'].get('metadata')


def get_match_reg6(flow):
    for ofex in (
            flow['match'].get(
                'openflowplugin-extension-general:extension-list', [])):
        if (ofex['extension-key']
                == 'openflowplugin-extension-nicira-match:nxm-nx-reg6-key'):
            return (
                ofex['extension']
                ['openflowplugin-extension-nicira-match:nxm-nx-reg'])


def get_match_mpls(flow):
    if flow['match'].get('protocol-match-fields'):
        return flow['match'].get('protocol-match-fields').get('mpls-label')


def get_match_tunnelid(flow):
    if flow['match'].get('tunnel'):
        return flow['match'].get('tunnel').get('tunnel-id')


def get_match_ether_dest(flow):
    if flow.get('match').get('ethernet-match') and flow['match'].get('ethernet-match').get('ethernet-destination'):
        return flow['match'].get('ethernet-match').get('ethernet-destination').get('address')


def get_match_ether_src(flow):
    if flow.get('match').get('ethernet-match') and flow['match'].get('ethernet-match').get('ethernet-source'):
        return flow['match'].get('ethernet-match').get('ethernet-source').get('address')


def get_match_ipv4_dest(flow):
    return utils.parse_ipv4(flow['match'].get('ipv4-destination'))


def get_match_ipv4_src(flow):
    return utils.parse_ipv4(flow['match'].get('ipv4-source'))


def get_match_vlanid(flow):
    if flow.get('match').get('vlan-match') and flow['match'].get('vlan-match').get('vlan-id'):
        return flow['match'].get('vlan-match').get('vlan-id')


def get_match_inport(flow):
    if flow.get('match').get('in-port'):
        return flow['match'].get('in-port')


def parse_flow(flow):
    # parse flow fields
    # hex(int(mask, 16) & int(data, 16))
    if flow['cookie']:
        utils.to_hex(flow, 'cookie')
    # parse instructions
    for instruction in flow['instructions'].get('instruction', []):
        if 'write-metadata' in instruction:
            utils.to_hex(instruction['write-metadata'], 'metadata')
            utils.to_hex(instruction['write-metadata'], 'metadata-mask')
        if 'apply-actions' in instruction:
            for action in instruction['apply-actions'].get('action', []):
                if 'openflowplugin-extension-nicira-action:nx-reg-load' in action:
                    utils.to_hex(action['openflowplugin-extension-nicira-action:nx-reg-load'], 'value')
    # parse matches
    if 'metadata' in flow['match']:
        metadata = flow['match']['metadata']
        utils.to_hex(metadata, 'metadata')
        utils.to_hex(metadata, 'metadata-mask')

    for ofex in flow['match'].get('openflowplugin-extension-general:extension-list', []):
        if ofex['extension-key'] == 'openflowplugin-extension-nicira-match:nxm-nx-reg6-key':
            utils.to_hex(ofex['extension']['openflowplugin-extension-nicira-match:nxm-nx-reg'], 'value')

    return flow


LPORT_MASK = 0xfffff0000000000
LPORT_MASK_ZLEN = 10  # no. of trailing 0s in lport mask
ELAN_TAG_MASK = 0x000000ffff000000
ELAN_HEX_LEN = 4
LPORT_REG6_MASK = 0xfffff00
LPORT_REG6_MASK_ZLEN = 2
VRFID_MASK = 0x0000000000fffffe
SERVICE_ID_MASK = 0xf000000000000000
SERVICE_ID_MASK_ZLEN = 15


def get_lport_from_mreg6(m_reg6):
    if m_reg6 and m_reg6.get('value'):
        return ('%x' % (m_reg6.get('value') & LPORT_REG6_MASK))[:-LPORT_REG6_MASK_ZLEN]


def get_lport_from_metadata(metadata, mask):
    if mask & LPORT_MASK:
        return ('%x' % (metadata & LPORT_MASK))[:-LPORT_MASK_ZLEN]


def get_elan_from_metadata(metadata, mask):
    if mask & ELAN_TAG_MASK:
        return ('%x' % (metadata & ELAN_TAG_MASK))[:ELAN_HEX_LEN]


def get_service_id_from_metadata(metadata, mask):
    if mask & SERVICE_ID_MASK:
        return ('%x' % (metadata & SERVICE_ID_MASK))[:-SERVICE_ID_MASK_ZLEN]


def get_vpnid_from_metadata(metadata, mask):
    if mask & VRFID_MASK:
        return (metadata & VRFID_MASK) / 2


def get_matchstr(args, flow):
    if flow and flow.get('match'):
        return utils.format_json(args, flow.get('match', None))
