# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.csit import robotfiles


def add_parser(subparsers):
    parser = subparsers.add_parser("csit")
    parser.add_argument("infile",
                        help="XML output from a Robot test, e.g. output_01_l2.xml.gz")
    parser.add_argument("path",
                        help="the directory that the parsed data is written into")
    parser.add_argument("-g", "--gunzip", action="store_true",
                        help="unzip the infile")
    parser.add_argument("-d", "--dump", action="store_true",
                        help="dump extra debugging, e.g. ovs metadata")
    parser.set_defaults(func=robotfiles.run)
