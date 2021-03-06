# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import os
import unittest

from odltools import logg
from odltools.csit.robotfiles import RobotFiles

# Requirements
# - output.xml.gz in /tmp
# - running tests will create job dir, unzip, parse and format output


class TestRobotFiles(unittest.TestCase):
    DATAPATH = "/tmp/output_02_l3.xml.gz"
    OUTPATH = "/tmp/robotjob"

    def setUp(self):
        logg.Logger(logging.INFO, logging.DEBUG)

    def test_mk_outdir(self):
        self.robotfile = RobotFiles(self.DATAPATH, self.OUTPATH)
        self.robotfile.mk_outdir()
        self.assertTrue(os.path.isdir(self.robotfile.outdir))

    def test_gunzip_xml_data_file(self):
        self.robotfile = RobotFiles(self.DATAPATH, self.OUTPATH)
        self.robotfile.mk_outdir()
        self.robotfile.gunzip()
        self.assertTrue(os.path.isfile(self.robotfile.datafilepath))

    @unittest.skip("skipping")
    def test_parse_xml_data_file(self):
        self.robotfile = RobotFiles(self.DATAPATH, self.OUTPATH)
        self.robotfile.print_config()
        self.robotfile.mk_outdir()
        self.robotfile.gunzip()
        self.robotfile.parse_xml_data_file()

        print("tests: {}".format(len(self.robotfile.pdata)))
        # test_id = "s1-s1-s4-t28"
        test_id = "s1-t1"
        if test_id not in self.robotfile.pdata:
            self.fail("wrong test_id")
        pdata = self.robotfile.pdata[test_id]
        print("\n{} test id = {} - {}".format(1, test_id, pdata['name']))
        if 0:
            for nindex, (node, ndata) in enumerate(pdata['nodes'].items()):
                print("{}: node = {}".format(nindex, node))
                for cindex, (command, cdata) in enumerate(ndata.items()):
                    print("{}: command = {}\n{}".format(cindex, command, cdata))
        if 0:
            for mindex, (model, mdata) in enumerate(sorted(pdata['models'].items())):
                print("{}: model = {} - {}".format(mindex, model, mdata))

        self.robotfile.write_pdata()
        self.robotfile.write_debug_pdata()


if __name__ == '__main__':
    unittest.main()
