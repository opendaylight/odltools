# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import collections

from odltools.mdsal.models.model import Model

MODULE = "opendaylight-inventory"


def nodes(store, args):
    return Nodes(MODULE, store, args)


class Nodes(Model):
    CONTAINER = "nodes"
    CLIST = "node"
    CLIST_KEY = "id"
    NODE_GROUP = 'flow-node-inventory:group'
    NODE_TABLE = 'flow-node-inventory:table'

    def get_groups(self, of_nodes=None):
        key = "group-id"
        group_dict = collections.defaultdict(dict)
        nodez = of_nodes or self.get_clist_by_key()
        for node in nodez.values():
            dpnid = self.get_dpn_from_ofnodeid(node['id'])
            for group in node.get(Nodes.NODE_GROUP, []):
                if group_dict.get(dpnid) and group_dict.get(dpnid).get(group[key]):
                    print("Duplicate: dpn_id: {}, group: {}".format(dpnid, group[key]))
                group_dict[dpnid][group[key]] = group
        return dict(group_dict)

    def get_dpn_host_mapping(self, oper_nodes=None):
        nodes_dict = {}
        nodez = oper_nodes or self.get_clist_by_key()
        for node in nodez.values():
            dpnid = self.get_dpn_from_ofnodeid(node['id'])
            desc = node.get('flow-node-inventory:description', '')
            if desc and desc != 'None':
                nodes_dict[dpnid] = desc.encode('utf8')
        return nodes_dict
