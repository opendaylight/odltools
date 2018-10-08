# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from odltools.csit import robotfiles
from odltools.csit.reports import console
from odltools.csit.reports import excepts


def add_exceptions_parser(parsers):
    parser = parsers.add_parser("exceptions", description="Write reports for test exceptions",
                                help="Write reports for test exceptions")
    parser.add_argument("-j", "--jobnames", nargs="+",
                        help="space separated list of job names")
    parser.add_argument("-n", "--numjobs", type=int,
                        help="number of jobs to analyze default: 1")
    parser.add_argument("-p", "--path",
                        help="the output directory for the reports, default: /tmp")
    parser.add_argument("-u", "--url",
                        help="root url for logs, default: https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1")
    parser.set_defaults(func=excepts.run)


def add_reports_parser(parsers):
    parser = parsers.add_parser("reports", description="Write reports for test failures",
                                help="Write reports for test failures")
    parser.add_argument("-j", "--jobnames", nargs="+",
                        help="space separated list of job names")
    parser.add_argument("-n", "--numjobs", type=int,
                        help="number of jobs to analyze default: 1")
    parser.add_argument("-p", "--path",
                        help="the output directory for the reports, default: /tmp")
    parser.add_argument("-u", "--url",
                        help="root url for logs, default: https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1")
    parser.set_defaults(func=console.run)


def add_robot_parser(parsers):
    parser = parsers.add_parser("robot", description="Process and analyze CSIT robot output",
                                help="Process and analyze CSIT robot output")
    parser.add_argument("infile",
                        help="XML output from a Robot test, e.g. output_01_l2.xml.gz")
    parser.add_argument("path",
                        help="the directory that the parsed data is written into")
    parser.add_argument("-g", "--gunzip", action="store_true",
                        help="unzip the infile")
    parser.add_argument("-d", "--dump", action="store_true",
                        help="dump extra debugging, e.g. ovs metadata")
    parser.set_defaults(func=robotfiles.run)


def add_parser(parsers):
    parser = parsers.add_parser("csit", description="Tools for processing CSIT data")
    subparsers = parser.add_subparsers(dest="subcommand")
    add_exceptions_parser(subparsers)
    add_reports_parser(subparsers)
    add_robot_parser(subparsers)
