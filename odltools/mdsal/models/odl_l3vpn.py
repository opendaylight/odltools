# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.mdsal.models.model import Model

MODULE = "odl-l3vpn"


def vpn_id_to_vpn_instance(store, args):
    return VpnIdToVpnInstance(MODULE, store, args)


def vpn_instance_to_vpn_id(store, args):
    return VpnInstanceToVpnId(MODULE, store, args)


class VpnIdToVpnInstance(Model):
    CONTAINER = "vpn-id-to-vpn-instance"
    CLIST = "vpn-ids"
    CLIST_KEY = "vpn-id"


class VpnInstanceToVpnId(Model):
    CONTAINER = "vpn-instance-to-vpn-id"
    CLIST = "vpn-instance"
    CLIST_KEY = "vpn-id"
