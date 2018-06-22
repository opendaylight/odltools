# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import argparse
import logging
import os

logger = logging.getLogger("cli_utils")


def type_input_file(path):
    if path == '-':
        return path

    if not os.path.isfile(path):
        logger.error('File "%s" not found' % path)
        raise argparse.ArgumentError

    return path


def add_common_args(parser):
    parser.add_argument("--path",
                        help="the directory that the parsed data is written into")
    parser.add_argument("--transport", default="http",
                        choices=["http", "https"],
                        help="transport for connections")
    parser.add_argument("-i", "--ip", default="localhost",
                        help="OpenDaylight ip address")
    parser.add_argument("-t", "--port", default="8181",
                        help="OpenDaylight restconf port, default: 8181")
    parser.add_argument("-u", "--user", default="admin",
                        help="OpenDaylight restconf username, default: admin")
    parser.add_argument("-w", "--pw", default="admin",
                        help="OpenDaylight restconf password, default: admin")
    parser.add_argument("-p", "--pretty_print", action="store_true",
                        help="json dump with pretty_print")
