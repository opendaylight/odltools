# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
import unittest

from odltools import logg
from odltools.common import files
from odltools.common import rest_client
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
        self.job_list_html_path = "{}/job_list.html".format(tests.get_resources_path())
        self.console_log_path = "{}/console.log".format(tests.get_resources_path())
        self.excepts_log_path = "{}/odl1_exceptions.txt".format(tests.get_resources_path())

    def test_get_job_list(self):
        job_list_html = files.read(self.job_list_html_path)
        joblist = reports.extract_job_list_from_html(job_list_html)
        self.assertEqual(len(joblist), 2)

    def test_get_console_log_file(self):
        log_text = files.read(self.console_log_path)
        path = "{}/1/console.log.gz".format(JOBNAME)
        url = "{}/{}".format(LOGURL, path)
        restclient = rest_client.RestClient(LOGURL)
        with requests_mock.Mocker() as mrequests:
            mrequests.register_uri('GET', url, text=log_text)
            log = reports.get_log_file(restclient, path)
            self.assertEqual(log[0:5], "pybot")

    def test_get_exceptions_txt_file(self):
        log_text = files.read(self.excepts_log_path)
        path = "{}/1/odl_1_exceptions.txt.gz".format(JOBNAME)
        url = "{}/{}".format(LOGURL, path)
        restclient = rest_client.RestClient(LOGURL)
        with requests_mock.Mocker() as mrequests:
            mrequests.register_uri('GET', url, text=log_text)
            log = reports.get_log_file(restclient, path)
            self.assertEqual(log[0:5], "=====")
