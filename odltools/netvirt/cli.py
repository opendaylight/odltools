# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.cli_utils import add_common_args
from odltools.netvirt import analyze
from odltools.netvirt import show


def add_analyze_parser(parser):
    parsers = parser.add_subparsers(dest="subcommand")

    parser = parsers.add_parser("interface", description="analyze interface data", help="analyze interface data")
    add_common_args(parser)
    parser.add_argument("--ifname",
                        help="interfaces-state:interface:name")
    parser.set_defaults(func=analyze.analyze_interface)

    parser = parsers.add_parser("inventory", description="analyze inventory data", help="analyze inventory data")
    add_common_args(parser)
    parser.add_argument("store", choices=["config", "operational"],
                        help="config or operational inventory")
    parser.add_argument("nodeid",
                        help="an openflow node id, not including the prefix such as openflow:")
    parser.add_argument("--ifname",
                        help="interfaces-state:interface:name")
    parser.set_defaults(func=analyze.analyze_inventory)

    parser = parsers.add_parser("nodes", description="analyze nodes data", help="analyze nodes data")
    add_common_args(parser)
    parser.set_defaults(func=analyze.analyze_nodes)

    parser = parsers.add_parser("trunks", description="analyze trunks data", help="analyze trunks data")
    add_common_args(parser)
    parser.set_defaults(func=analyze.analyze_trunks)

    parser = parsers.add_parser("tunnels", description="analyze tunnels data", help="analyze tunnels data")
    add_common_args(parser)
    parser.set_defaults(func=analyze.analyze_tunnels)


def call_func(args):
    args.func2(args)


def add_show_parser(parser):
    parsers = parser.add_subparsers(dest="subcommand")

    parser = parsers.add_parser("cluster-info", description="show cluster-info data", help="show cluster-info data")
    add_common_args(parser)
    parser.set_defaults(func=show.show_cluster_information)

    parser = parsers.add_parser("elan-instances", description="show elan-instances data",
                                help="show elan-instances data")
    add_common_args(parser)
    parser.set_defaults(func=show.show_elan_instances)

    parser = parsers.add_parser("eos", description="show eos data", help="show eos data")
    add_common_args(parser)
    parser.set_defaults(func=show.show_eos)

    parser = parsers.add_parser("flows", description="show flows data", help="show flows data")
    add_common_args(parser)
    parser.add_argument("--modules",
                        help="service module owning the flow",
                        choices=["ifm", "acl", "elan", "l3vpn", "nat"])
    parser.add_argument("flowtype", choices=["all", "duplicate", "elan", "learned", "stale"])
    parser.add_argument("--metaonly", action="store_true",
                        help="display flow meta info only")
    parser.add_argument("--urls", action="store_true",
                        help="show flow urls")
    parser.set_defaults(func=show.show_flows)

    parser = parsers.add_parser("id-pools", description="show id-pools data", help="show id-pools data")
    add_common_args(parser)
    parser.add_argument("type", choices=["all", "duplicate"])
    parser.add_argument("--short", action="store_true", default=False,
                        help="display less information")
    parser.set_defaults(func=show.show_idpools)

    parser = parsers.add_parser("groups", description="show groups data", help="show groups data")
    add_common_args(parser)
    parser.set_defaults(func=show.show_groups)

    parser = parsers.add_parser("neutron", description="show neutron data", help="show neutron data")
    add_common_args(parser)
    parser.add_argument("object", choices=["all", "floatingips", "networks", "ports", "routers",
                                           "security-groups", "security-rules", "subnets", "trunks", "bgpvpns"])
    parser.add_argument("--short", action="store_true", default=False,
                        help="display less information")
    parser.set_defaults(func=show.show_neutron)

    parser = parsers.add_parser("stale-bindings", description="show stale-bindings data",
                                help="show stale-bindings data")
    add_common_args(parser)
    parser.set_defaults(func=show.show_stale_bindings)
    # This was a test to see if we could call a func - which allows us more than func(args)
    # parser.add_argument("--func2", default=show.show_stale_bindings, help=argparse.SUPPRESS)
    parser.set_defaults(func=call_func)

    parser = parsers.add_parser("tables", description="show tables data", help="show tables data")
    add_common_args(parser)
    parser.set_defaults(func=show.show_tables)


def add_parser(parsers):
    parser = parsers.add_parser("netvirt", description="Tools for processing NetVirt data",
                                help="Tools for processing NetVirt data")
    subparsers = parser.add_subparsers(dest="subcommand")

    parser = subparsers.add_parser("analyze", description="analyze data", help="analyze data")
    add_analyze_parser(parser)

    parser = subparsers.add_parser("show", description="show data", help="show data")
    add_show_parser(parser)
