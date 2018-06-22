# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.cli_utils import add_common_args
from odltools.mdsal.models import models


def add_get_parser(parsers):
    parser = parsers.add_parser("get", help="Get and write all mdsal models")
    add_common_args(parser)
    parser.add_argument("path",
                        help="the directory that the parsed data is written into")
    # Get a list of modules that was csv. The lambda parses the input into a list
    parser.add_argument("--modules", default="all",
                        type=lambda s: [item for item in s.split(',')],
                        help="all or a list of modules")
    parser.set_defaults(func=models.get_models)


def add_parser(parsers):
    parser = parsers.add_parser("model", description="Tools for MDSAL models")
    subparsers = parser.add_subparsers(dest="subcommand", description="Model tools")
    add_get_parser(subparsers)
