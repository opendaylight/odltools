# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import os
import unittest

import mock
from odltools.common import files
from odltools.flows import cli
from odltools.netvirt import tests
import paramiko


class TestOvsFlowsCli(unittest.TestCase):

    def setUp(self):
        self.outfile = "/tmp/flow_dumps.1.out.txt"

    def test_flows_ovs_file(self):
        infile = "{}/flow_dumps.1.txt".format(tests.get_resources_path())
        args = ["ovs", "--infile", infile, "/tmp/flow_dumps.1.out.txt"]
        cli.main("ovs", args)

    @unittest.skip("skipping")
    def test_flows_ovs_ssh_real(self):
        args = ["ovs", "--ip", "localhost", "--user", "shague", "--pw", "Bos46760!",
                "/tmp/flow_dumps.1.out.txt"]
        cli.main("ovs", args)

    def test_flows_ovs_ssh(self):
        with mock.patch.object(paramiko, "SSHClient", mock.Mock(return_value=FakeSSHClient())):
            args = ["ovs", "--ip", "localhost", "--user", "shague", "--pw", "Bos46760!", self.outfile]
            cli.main("ovs", args)
            self.assertTrue(os.path.exists(self.outfile))
            self.assertEqual(76, len(files.readlines(self.outfile)))


class FakeSSHClient(object):

    def __init__(self):
        self.filename = "{}/flow_dumps.1.txt".format(tests.get_resources_path())
        self.data = files.readlines(self.filename)

    def load_system_host_keys(self):
        pass

    def set_missing_host_key_policy(self, policy):
        pass

    def connect(self, ip, port=22, username=None, password=None):
        pass

    def exec_command(self, cmd):
        stdout = mock.MagicMock()
        stdout.read.return_value = self.data
        return None, stdout, None

    def close(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


if __name__ == '__main__':
    unittest.main()
