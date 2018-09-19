# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import argparse

from odltools import logg
import odltools.csit.cli
import odltools.flows.cli
import odltools.karaf.cli
import odltools.mdsal.cli
import odltools.monitor.cli
import odltools.netvirt.cli


def create_parser():
    parser = argparse.ArgumentParser(prog="python -m odltools", description="OpenDaylight Troubleshooting Tools")
    parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0,
                        help="verbosity (-v, -vv)")
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s (version {version})".format(version=odltools.__version__))
    subparsers = parser.add_subparsers(dest="command", description="Command Tool")
    odltools.csit.cli.add_parser(subparsers)
    odltools.flows.cli.add_parser(subparsers)
    odltools.karaf.cli.add_parser(subparsers)
    odltools.mdsal.cli.add_parser(subparsers)
    odltools.monitor.cli.add_parser(subparsers)
    odltools.netvirt.cli.add_parser(subparsers)

    return parser


def parse_args():
    parser = create_parser()
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    if args.verbose > 0:
        logg.debug()
    args.func(args)
