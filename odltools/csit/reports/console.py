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

logger = logging.getLogger("csit.report")

LOG_GZ = "console.log.gz"


class ConsoleReports:

    def __init__(self, url, jobname):
        self.url = url
        self.jobname = jobname
        self.jobs = {}
        self.first_job = 0
        self.last_job = 0
        self.failed_jobs = []
        self.failed_devstack = 0
        self.failed_stack = 0
        self.restclient = rest_client.RestClient(url, timeout=(5, 15))
        self.reports = collections.OrderedDict()
        self.reports["jobname"] = jobname
        # ^([0-9]{2}.*) :: .*$ - captures suite name in the group 1
        # (^.*) \| (PASS|FAIL) \|$') - group 2 captures test name, group 3 captures PASS or FAIL
        self.re_tests = re.compile(r'^([0-9]{2}.*) :: .*$|(^.*) \| (PASS|FAIL) \|$')
        time_re = '^Total elapsed time: ([0-9]:[0-9]{2}:[0-9]{2}), stacking time: ([0-9]:[0-9]{2}:[0-9]{2})$'
        stack_re = '^node ([0-2]) [0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}: stacking has failed$'
        self.re_time_stack = re.compile(r'(' + time_re + '|' + stack_re + ')')

    def process_console_log(self, console_log, jobno):
        """
        Extract suite and test data from a console log.

        :param str console_log: A job console log
        :param int jobno:
        :return dict: dictionary of suites with dictionaries of tests
        """
        suite = {}
        for line in console_log.splitlines():
            match = self.re_tests.search(line)
            # match on a suite name and start a new suite or append data to an existing suite
            if match and match.group(1):
                suitename = match.group(1).rstrip()
                suite = self.reports.get(suitename)
                # new suite
                if suite is None:
                    suite = collections.OrderedDict()
                    self.reports[suitename] = suite
            # match a test name and start a new test or append data to an existing test
            elif match and match.group(2):
                testname = match.group(2).partition('::')[0].rstrip()
                status = match.group(3)
                test = suite.get(testname)
                # new test
                if test is None:
                    test = {"pass": [], "fail": []}
                    suite[testname] = test
                if status == "PASS":
                    test.get("pass").append(jobno)
                else:
                    test.get("fail").append(jobno)
            else:
                match = self.re_time_stack.search(line)
                if match and match.group(2):
                    self.jobs[jobno] = {"total": match.group(2), "stack": match.group(3)}
                elif match and match.group(4):
                    self.jobs[jobno] = {"stack failed": match.group(4)}
                    self.failed_devstack += 1
        if len(suite) == 0:
            self.failed_jobs.append(jobno)
            if self.jobs.get(jobno) == {}:
                self.jobs[jobno] = {"stack failed": "*"}
                self.failed_stack += 1
        return self.reports

    def get_reports(self, numjobs=1):
        """
        Create a dictionary of all suites test results.

        Scrape the log server for the requested jobs. Then for each job get the console log and
        extract the suite and test data from the log. Aggregate all results per suite and test.

        :param int numjobs: the number of jobs to scrape
        :return dict: dictionary of suites with dictionaries of tests
        """
        self.jobs, self.first_job, self.last_job = reports.get_job_list(numjobs, self.jobname, self.restclient)
        for jobno in self.jobs:
            urlpath = "{}/{}/{}".format(self.jobname, jobno, LOG_GZ)
            console_log = reports.get_log_file(self.restclient, urlpath)
            self.process_console_log(console_log, jobno)
        return self.reports

    def write_reports(self, path):
        jobline = "{} {:4}  {:7}  {:7}\n"
        lines = [
            "{}\n".format(self.jobname),
            "{}/{}\n".format(self.url, self.jobname),
            "{}\n".format("="*90),
            "failed jobs: {}\n".format(self.failed_jobs),
            "number failed to stack:    {}\n".format(self.failed_stack),
            "number failed to devstack: {}\n".format(self.failed_devstack),
            jobline.format("f", "job", "total", "stack"),
            jobline.format("-", "-"*4, "-"*7, "-"*7, "-"*7),
        ]

        for jobno, job in self.jobs.items():
            lines.append(jobline.format(job.get("stack failed", " "), jobno,
                                        job.get("total", "0:00:00"), job.get("stack", "0:00:00")))
        for suitename, suite in self.reports.items():
            if suitename == "jobname":
                continue
            lines.append("{} {}\n".format("-"*70, "-"*20))
            lines.append("{:70} Failed in Job\n".format(suitename))
            lines.append("{} {}\n".format("-" * 70, "-" * 20))
            for testname, test in suite.items():
                lines.append("{:70} {}\n".format(testname, test.get("fail")))
        report_path = "{}/{}.console.txt".format(path, self.jobname)
        logger.info("writing {}".format(report_path))
        files.writelines(report_path, lines)


def run(args):
    jobnames = args.jobnames or reports.JOBNAMES
    numjobs = args.numjobs or reports.NUMJOBS
    path = args.path or reports.PATH
    for jobname in jobnames:
        url = args.url or reports.LOGURL
        logger.info("Processing {} jobs at {}/{}".format(numjobs, url, jobname))
        reports_ = ConsoleReports(url, jobname)
        reports_.get_reports(numjobs)
        reports_.write_reports(path)
