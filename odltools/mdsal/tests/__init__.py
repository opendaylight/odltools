# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import os


class Args:
    def __init__(self, transport="http", ip="localhost", port=8181, user="admin", pw="admin", path="/tmp",
                 pretty_print=False):
        self.transport = transport
        self.ip = ip
        self.port = port
        self.user = user
        self.pw = pw
        self.path = path
        self.modules = []
        self.pretty_print = pretty_print


def get_resources_path():
    return os.path.join(os.path.dirname(__file__), '../../tests/resources')
