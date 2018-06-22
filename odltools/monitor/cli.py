# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import odltools.monitor.monitor_odl_cluster as monitor

JSON_FORMAT = """
    {
        "cluster": {
            "controllers": [
                {"ip": "172.17.10.93", "port": "8181"},
                {"ip": "172.17.10.93", "port": "8181"},
                {"ip": "172.17.10.93", "port": "8181"}
            ],
            "user": "username",
            "pass": "password",
            "shards_to_exclude": ["prefix-configuration-shard"]
        }
    }
"""


def add_parser(parsers):
    parser = parsers.add_parser("monitor",
                                description="Graphical tool for monitoring "
                                            "an OpenDaylight cluster")
    parser.set_defaults(func=monitor.run_monitor)
    parser.add_argument('-d', '--datastore', default='Config', type=str,
                        choices=["Config", "Operational"],
                        help=('polling can be done on "Config" or '
                              '"Operational" data stores'))
    parser.add_argument('config_file',
                        metavar='cluster.json',
                        help='JSON Cluster configuration file in the '
                             'following format:\n{}'.format(JSON_FORMAT))
