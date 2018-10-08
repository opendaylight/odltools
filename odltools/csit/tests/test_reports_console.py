# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.common import files
from odltools.csit.reports import console
from odltools.csit.reports import reports
from odltools.netvirt import tests
import requests_mock

LOGURL = "https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1"
JOBNAME = "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-fluorine"


class TestReportsConsole(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.DEBUG)
        self.job_list_path = "{}/job_list.html".format(tests.get_resources_path())
        self.log_path = "{}/console.log".format(tests.get_resources_path())
        self.report = console.ConsoleReports(
            "https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1",
            "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-fluorine")

    def test_process_console_log(self):
        console_log = files.read(self.log_path)
        self.report.process_console_log(console_log, 102)
        self.assertEqual(len(self.report.reports), 3)
        suite = self.report.reports.get("01 l2")
        self.assertEqual(len(suite), 2)
        suite = self.report.reports.get("04 security group")
        self.assertEqual(len(suite), 2)

    def test_get_reports(self):
        job_list_html = files.read(self.job_list_path)
        console_log = files.read(self.log_path)
        html_url = "{}/{}".format(LOGURL, JOBNAME)
        console1_url = "{}/{}/1/console.log.gz".format(LOGURL, JOBNAME)
        console2_url = "{}/{}/2/console.log.gz".format(LOGURL, JOBNAME)
        report = console.ConsoleReports(LOGURL, JOBNAME)
        with requests_mock.Mocker() as mrequests:
            mrequests.register_uri('GET', html_url, text=job_list_html)
            mrequests.register_uri('GET', console1_url, text=console_log)
            mrequests.register_uri('GET', console2_url, text=console_log)
            report.get_reports(2)
            report.write_reports("/tmp")

    @unittest.skip("skipping")
    def test_get_console_log_real(self):
        report = console.ConsoleReports(LOGURL, JOBNAME)
        path = "{}/109/console.log.gz".format(JOBNAME)
        console_log = reports.get_log_file(report.restclient, path)
        report.process_console_log(console_log, 109)
        report.write_reports("/tmp")

    @unittest.skip("skipping")
    def test_get_reports_real(self):
        report = console.ConsoleReports(LOGURL, JOBNAME)
        report.get_reports(12)
        report.write_reports("/tmp")


if __name__ == '__main__':
    unittest.main()
