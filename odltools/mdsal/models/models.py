# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging

from odltools.mdsal.models import elan
from odltools.mdsal.models import entity_owners
from odltools.mdsal.models import id_manager
from odltools.mdsal.models import ietf_interfaces
from odltools.mdsal.models import interface_service_bindings
from odltools.mdsal.models import itm
from odltools.mdsal.models import itm_state
from odltools.mdsal.models import l3vpn
from odltools.mdsal.models import mip
from odltools.mdsal.models import model
from odltools.mdsal.models import network_topology
from odltools.mdsal.models import neutron
from odltools.mdsal.models import odl_fib
from odltools.mdsal.models import odl_interface_meta
from odltools.mdsal.models import odl_l3vpn
from odltools.mdsal.models import opendaylight_inventory
from odltools.mdsal.models.model import Model
from odltools.mdsal.models.Modules import netvirt_data_models

logger = logging.getLogger("mdsal.models")


class Singleton(object):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def init(self, *args, **kwds):
        pass


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class Models:

    def __init__(self):
        # List all the required models in alphabetical order.
        # config is implied for all, add _operational for operational.
        self.args = None
        self.elan_elan_instances = None
        self.elan_elan_interfaces = None
        self.entity_owners_entity_owners = None
        self.id_manager_id_pools = None
        self.ietf_interfaces_interfaces = None
        self.ietf_interfaces_interfaces_state = None
        self.interface_service_bindings_service_bindings = None
        self.itm_state_dpn_endpoints = None
        self.itm_state_tunnel_list = None
        self.itm_state_tunnels_state = None
        self.itm_transport_zones = None
        self.l3vpn_vpn_interfaces = None
        self.mip_mac = None
        self.network_topology_network_topology = None
        self.network_topology_network_topology_operational = None
        self.neutron_neutron = None
        self.odl_fib_fib_entries = None
        self.odl_interface_meta_if_index_interface_map = None
        self.odl_inventory_nodes = None
        self.odl_inventory_nodes_operational = None
        self.odl_l3vpn_vpn_instance_to_vpn_id = None

    def get_models(self, args, models):
        self.args = args

        if "elan_elan_instances" in models:
            self.elan_elan_instances = elan.elan_instances(Model.CONFIG, args)
        if "elan_elan_interfaces" in models:
            self.elan_elan_interfaces = elan.elan_interfaces(Model.CONFIG, args)
        if "entity_owners_entity_owners" in models:
            self.entity_owners_entity_owners = entity_owners.entity_owners(Model.OPERATIONAL, args)
        if "id_manager_id_pools" in models:
            self.id_manager_id_pools = id_manager.id_pools(Model.CONFIG, args)
        if "ietf_interfaces_interfaces" in models:
            self.ietf_interfaces_interfaces = ietf_interfaces.interfaces(Model.CONFIG, args)
        if "ietf_interfaces_interfaces_state" in models:
            self.ietf_interfaces_interfaces_state = ietf_interfaces.interfaces_state(Model.OPERATIONAL, args)
        if "interface_service_bindings_service_bindings" in models:
            self.interface_service_bindings_service_bindings = \
                interface_service_bindings.service_bindings(Model.CONFIG, args)
        if "itm_state_dpn_endpoints" in models:
            self.itm_state_dpn_endpoints = itm_state.dpn_endpoints(Model.CONFIG, args)
        if "itm_state_tunnel_list" in models:
            self.itm_state_tunnel_list = itm_state.tunnel_list(Model.CONFIG, args)
        if "itm_state_tunnels_state" in models:
            self.itm_state_tunnels_state = itm_state.tunnels_state(Model.OPERATIONAL, args)
        if "itm_transport_zones" in models:
            self.itm_transport_zones = itm.transport_zones(Model.CONFIG, args)
        if "l3vpn_vpn_interfaces" in models:
            self.l3vpn_vpn_interfaces = l3vpn.vpn_interfaces(Model.CONFIG, args)
        if "mip_mac" in models:
            self.mip_mac = mip.mac(Model.CONFIG, args)
        if "network_topology_network_topology" in models:
            self.network_topology_network_topology = network_topology.network_topology(Model.CONFIG, args)
        if "network_topology_network_topology_operational" in models:
            self.network_topology_network_topology_operational = \
                network_topology.network_topology(Model.OPERATIONAL, args)
        if "neutron_neutron" in models:
            self.neutron_neutron = neutron.neutron(Model.CONFIG, args)
        if "odl_fib_fib_entries" in models:
            self.odl_fib_fib_entries = odl_fib.fib_entries(Model.CONFIG, args)
        if "odl_interface_meta_if_index_interface_map" in models:
            self.odl_interface_meta_if_index_interface_map = \
                odl_interface_meta.if_indexes_interface_map(Model.OPERATIONAL, args)
        if "odl_inventory_nodes" in models:
            self.odl_inventory_nodes = opendaylight_inventory.nodes(Model.CONFIG, args)
        if "odl_inventory_nodes_operational" in models:
            self.odl_inventory_nodes_operational = opendaylight_inventory.nodes(Model.OPERATIONAL, args)
        if "odl_l3vpn_vpn_instance_to_vpn_id" in models:
            self.odl_l3vpn_vpn_instance_to_vpn_id = odl_l3vpn.vpn_instance_to_vpn_id(Model.CONFIG, args)


def get_models(args):
    if args.modules == ["all"]:
        data_models = netvirt_data_models
    else:
        data_models = args.modules

    logger.debug("get_models: modules: %s, data_models: %s", args.modules, data_models)

    if data_models == [""]:
        print("please enter a list of modules")
        return

    model.init_rest_client(args)
    for resource in data_models:
        filename = model.make_filename_from_resource(args, resource)
        url_root, url_path = model.make_url_parts(args, resource)
        model.get_model_data(None, filename, url_path, args)
