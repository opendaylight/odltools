# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import odltools.cli_utils
from odltools.karaf import dump


def add_parser(parsers):
    parser = parsers.add_parser("karaf", description="Karaf log tools")
    subparsers = parser.add_subparsers(dest="subcommand",
                                       description="Karaf tools")
    format_parser = subparsers.add_parser("format", help="Dump a karaf log "
                                          "with pretty printing of MDSAL "
                                          "objects")
    format_parser.add_argument("path", type=odltools.cli_utils.type_input_file,
                               help="Path to karaf log file")
    format_parser.set_defaults(func=dump.dump_karaf_log)
