# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import unittest

from odltools.flows import cli
from odltools.netvirt import tests


class TestOvsFlowsCli(unittest.TestCase):
    def test_flows_ovs_file(self):
        infile = "{}/flow_dumps.1.txt".format(tests.get_resources_path())
        args = ["ovs", "--infile", infile, "/tmp/flow_dumps.1.out.txt"]
        cli.main("ovs", args)

    @unittest.skip("skipping")
    def test_flows_ovs_ssh(self):
        args = ["ovs", "--ip", "localhost", "--user", "shague", "--pw", "Bos46760!", "/tmp/flow_dumps.1.out.txt"]
        cli.main("ovs", args)


if __name__ == '__main__':
    unittest.main()
