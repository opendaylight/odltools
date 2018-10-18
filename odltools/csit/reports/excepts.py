# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import collections
import logging
import re

from odltools.common import files
from odltools.common import rest_client
from odltools.csit.reports import reports

logger = logging.getLogger("csit.excepts")

LOG_GZ = "odl1_exceptions.txt.gz"


class ExceptsReports:

    def __init__(self, url, jobname):
        self.url = url
        self.jobname = jobname
        self.jobs = {}
        self.first_job = 0
        self.last_job = 0
        self.restclient = rest_client.RestClient(url, timeout=(5, 15))
        self.reports = collections.OrderedDict()
        # (.*?) - group(1): capture suite name
        # ((.*?)\.(.*)|.*)') - group(2): capture from second suite name to end of line
        # (.*?) - group(3): capture second suite name when followed by test name
        # (.*)|.*) - group(4): capture test name
        tests_re = r'^Starting test: (.*?)\.((.*?)\.(.*)|.*)'
        # (^Exception was matched to:.*) - group(5): matched exceptions
        # (exception is new:.*) - group(6): new exceptions
        exs_re = r'^Exception was matched to: (.*)|(Exception is new)'
        self.re_tests = re.compile(tests_re + '|' + exs_re)

    def process_log(self, log, jobno):
        """
        Extract suite and test data from a log.

        :param str log: A job log
        :param int jobno:
        :return dict: dictionary of suites with dictionaries of tests
        """
        # Starting test: 03 external network.03 external network
        # Starting test: 03 external network.03 external network
        #     .Initial Ping To External Network PNF from Vm Instance 1
        # group(1): suite name
        # group(4): test name
        suite = {}
        test = {}
        current_suitename = None
        for line in log.splitlines():
            match = self.re_tests.search(line)

            # match a test name and start a new test or append data to an existing test
            if match and match.group(4):
                testname = match.group(4)
                test = suite.get(testname)
                # new test
                if test is None:
                    test = collections.OrderedDict()
                    suite[testname] = test

            # match on a suite name and start a new suite or append data to an existing suite
            elif match and match.group(1):
                suitename = match.group(1)
                suite = self.reports.get(suitename)
                # new suite
                if suite is None:
                    suite = collections.OrderedDict()
                    self.reports[suitename] = suite
                # suite teardown
                if suitename == current_suitename:
                    test = suite.get("teardown", collections.OrderedDict())
                    suite["teardown"] = test
                # suite setup
                else:
                    test = suite.get("setup", collections.OrderedDict())
                    suite["setup"] = test
                current_suitename = suitename

            # match a matched exception
            elif match and match.group(5):
                exmatch = match.group(5)
                job = test.get(jobno)
                if job is None:
                    job = {"matches": [], "new": 0}
                    test[jobno] = job
                job.get("matches").append(exmatch)

            # match a new exception
            elif match and match.group(6):
                job = test.get(jobno)
                if job is None:
                    job = {"matches": [], "new": 0}
                    test[jobno] = job
                new = job.get("new")
                new += 1
                job["new"] = new
        return self.reports

    def get_reports(self, numjobs=1):
        """
        Scrape the log server for jobs, get their console logs and extract the
        suite and test data.

        :param int numjobs: the number of jobs to scrape
        :return dict: dictionary of suites with dictionaries of tests
        """
        self.jobs, self.first_job, self.last_job = reports.get_job_list(numjobs, self.jobname, self.restclient)
        for jobno in self.jobs:
            urlpath = "{}/{}/odl_1/{}".format(self.jobname, jobno, LOG_GZ)
            log = reports.get_log_file(self.restclient, urlpath)
            self.process_log(log, jobno)
        return self.reports

    def write_reports(self, path):
        lines = [
            "{}\n".format(self.jobname),
            "{}/{}\n".format(self.url, self.jobname),
            "jobs {} to {}\n".format(self.first_job, self.last_job),
            "{}\n".format("=" * 90)
        ]

        for suitename, suite in self.reports.items():
            lines.append("{}\n".format("-" * 70))
            lines.append("{:70}\n".format(suitename))
            lines.append("{}\n".format("-" * 70))
            for testname, test in suite.items():
                lines.append("{:70}\n".format(testname))
                for jobno, job in test.items():
                    matches = job.get("matches")
                    new = job.get("new")
                    if matches or new:
                        new = new or 0
                        lines.append("  *** job {}: new exceptions: {}\n".format(jobno, new))
                    if matches:
                        for match in matches:
                            lines.append("    - {}\n".format(match))
        report_path = "{}/{}.excepts.txt".format(path, self.jobname)
        logger.info("writing {}".format(report_path))
        files.writelines("{}".format(report_path, self.jobname), lines)


def run(args):
    jobnames = args.jobnames or reports.JOBNAMES
    numjobs = args.numjobs or reports.NUMJOBS
    path = args.path or reports.PATH
    for jobname in jobnames:
        url = args.url or reports.LOGURL
        logger.info("Processing {} jobs at {}/{}".format(numjobs, url, jobname))
        reports_ = ExceptsReports(url, jobname)
        reports_.get_reports(numjobs)
        reports_.write_reports(path)
