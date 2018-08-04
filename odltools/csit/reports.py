# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import collections
import logging
import re

import requests

from odltools.common import files
from odltools.common import rest_client

logger = logging.getLogger("csit.report")

CONSOLE_LOG_GZ = "console.log.gz"
NUMJOBS = 1
PATH = "/tmp"
LOGURL = "https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1"
JOBNAMES = [
    "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-fluorine",
    "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-snat-conntrack-fluorine"
]


class Reports:

    def __init__(self, url, jobname):
        self.url = url
        self.jobname = jobname
        self.jobs = {}
        self.failed_jobs = []
        self.failed_devstack = 0
        self.failed_stack = 0
        self.restclient = rest_client.RestClient(url)
        self.reports = collections.OrderedDict()
        self.reports["jobname"] = jobname
        # ^([0-9]{2}.*) :: .*$ - captures suite name in the group 1
        # (^.*) \| (PASS|FAIL) \|$') - group 2 captures test name, group 3 captures PASS or FAIL
        self.re_tests = re.compile(r'^([0-9]{2}.*) :: .*$|(^.*) \| (PASS|FAIL) \|$')
        time_re = '^Total elapsed time: ([0-9]:[0-9]{2}:[0-9]{2}), stacking time: ([0-9]:[0-9]{2}:[0-9]{2})$'
        stack_re = '^node ([0-2]) [0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}: stacking has failed$'
        self.re_time_stack = re.compile(r'(' + time_re + '|' + stack_re + ')')

    def get_job_list(self, html):
        """
        Parse an HTML file to find a list of job numbers.

        :param str html: An HTML file
        :return list: A list of job numbers
        """
        # find all the href links which are links to the jobs as a number
        joblist_strings = re.findall(r'<a href="[0-9]+/">([0-9]+)/</a>', html)
        joblist = [int(x) for x in joblist_strings]
        return joblist

    def get_console_log(self, urlpath):
        response = self.restclient.get(urlpath)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            logger.error("{}".format(str(e)))
            return ""
        return response.content.decode(response.encoding)

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
        Scrape the log server for jobs, get their console logs and extract the
        suite and test data.

        :param int numjobs: the number of jobs to scrape
        :return dict: dictionary of suites with dictionaries of tests
        """
        response = self.restclient.get(self.jobname)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            logger.error("{}".format(str(e)))
            return {}
        job_list_html = response.content.decode(response.encoding)
        job_list = self.get_job_list(job_list_html)[-numjobs:]
        self.jobs = dict.fromkeys(job_list, {})
        for jobno in self.jobs:
            urlpath = "{}/{}/{}".format(self.jobname, jobno, CONSOLE_LOG_GZ)
            console_log = self.get_console_log(urlpath)
            self.process_console_log(console_log, jobno)
        return self.reports

    def print_reports(self, path):
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
        files.writelines("{}/{}.txt".format(path, self.jobname), lines)


def run(args):
    jobnames = args.jobnames or JOBNAMES
    numjobs = args.numjobs or NUMJOBS
    path = args.path or PATH
    for jobname in jobnames:
        url = args.url or LOGURL
        logger.info("Processing {} jobs at {}/{}".format(numjobs, url, jobname))
        reports_ = Reports(url, jobname)
        reports_.get_reports(numjobs)
        reports_.print_reports(path)
