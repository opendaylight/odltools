# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import argparse
import sys

import odltools
from odltools import logg
from odltools.flows import ovs_flows


def add_ovs_parser(parser):
    parser = parser.add_parser("ovs", description="Parse ovs dump-flows", help="Parse ovs dump-flows")
    parser.add_argument("outfile",
                        help="the file the parsed data is written into")
    parser.add_argument("--infile",
                        help="path to a file with output from ovs-ofctl dump-flows")
    parser.add_argument("-i", "--ip", default="localhost",
                        help="switch ip address")
    parser.add_argument("-t", "--port", default="22",
                        help="switch restconf port, default: 22")
    parser.add_argument("-u", "--user", default="admin",
                        help="switch ssh username, default: admin")
    parser.add_argument("-w", "--pw", default="admin",
                        help="switch ssh password, default: admin")
    parser.set_defaults(func=ovs_flows.run)


def add_parser(parsers):
    parser = parsers.add_parser("flows", description="Tools for processing flow dumps",
                                help="Tools for processing flow dumps")
    subparsers = parser.add_subparsers(dest="subcommand")
    add_ovs_parser(subparsers)


def create_parser(program):
    parser = argparse.ArgumentParser(prog=program, description="Tools for processing flow dumps")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                        help="verbosity (-v, -vv)")
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s (version {version})".format(version=odltools.__version__))
    subparsers = parser.add_subparsers(dest="subcommand")
    add_ovs_parser(subparsers)
    return parser


def main(program=None, args=None, stream=sys.stderr):
    parser = create_parser(program)
    cli_args = parser.parse_args(args)
    logg.Logger()
    if cli_args.verbose > 0:
        logg.debug()
    cli_args.func(cli_args)
    return


if __name__ == '__main__':
    sys.exit(main())
