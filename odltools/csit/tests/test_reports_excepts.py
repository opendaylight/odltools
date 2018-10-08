# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.common import files
from odltools.csit.reports import excepts
from odltools.csit.reports import reports
from odltools.netvirt import tests
import requests_mock

logger = logging.getLogger("test.csit.excepts")
LOGURL = "https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1"
JOBNAME = "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-fluorine"


class TestReportsExcepts(unittest.TestCase):
    def setUp(self):
        logg.Logger(logging.INFO, logging.DEBUG)
        logger.info("Test: {}".format(self.id()))
        self.job_list_path = "{}/job_list.html".format(tests.get_resources_path())
        self.log_path = "{}/odl1_exceptions.txt".format(tests.get_resources_path())
        self.report = excepts.ExceptsReports(
            "https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1",
            "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-fluorine")

    def test_process_txt(self):
        console_log = files.read(self.log_path)
        self.report.process_log(console_log, 102)
        self.assertEqual(len(self.report.reports), 3)
        suite = self.report.reports.get("09 vpn basic ipv6")
        self.assertEqual(len(suite), 4)
        suite = self.report.reports.get("11 arp learning")
        self.assertEqual(len(suite), 5)

    def test_get_reports(self):
        job_list_html = files.read(self.job_list_path)
        console_log = files.read(self.log_path)
        html_url = "{}/{}".format(LOGURL, JOBNAME)
        console1_url = "{}/{}/1/odl_1/odl1_exceptions.txt.gz".format(LOGURL, JOBNAME)
        console2_url = "{}/{}/2/odl_1/odl1_exceptions.txt.gz".format(LOGURL, JOBNAME)
        report = excepts.ExceptsReports(LOGURL, JOBNAME)
        with requests_mock.Mocker() as mrequests:
            mrequests.register_uri('GET', html_url, text=job_list_html)
            mrequests.register_uri('GET', console1_url, text=console_log)
            mrequests.register_uri('GET', console2_url, text=console_log)
            report.get_reports(2)
            report.write_reports("/tmp")

    @unittest.skip("skipping")
    def test_get_console_log_real(self):
        report = excepts.ExceptsReports(LOGURL, JOBNAME)
        path = "{}/109/console.log.gz".format(JOBNAME)
        console_log = reports.get_log_file(report.restclient, path)
        report.process_log(console_log, 109)
        report.write_reports("/tmp")

    @unittest.skip("skipping")
    def test_get_reports_real(self):
        report = excepts.ExceptsReports(LOGURL, JOBNAME)
        report.get_reports(12)
        report.write_reports("/tmp")


if __name__ == '__main__':
    unittest.main()
