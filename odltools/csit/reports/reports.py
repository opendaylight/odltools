# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

from collections import OrderedDict
import logging
import re

import requests

logger = logging.getLogger("csit.report")

NUMJOBS = 1
PATH = "/tmp"
LOGURL = "https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1"
JOBNAMES = [
    "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-fluorine",
    "netvirt-csit-1node-0cmb-1ctl-2cmp-openstack-queens-upstream-stateful-snat-conntrack-fluorine"
]


def extract_job_list_from_html(html):
    """
    Parse an HTML file to find a list of job numbers.

    :param str html: An HTML file
    :return list: A list of job numbers
    """
    # find all the href links which are links to the jobs as a number
    joblist_strings = re.findall(r'<a href="[0-9]+/">([0-9]+)/</a>', html)
    joblist = [int(x) for x in joblist_strings]
    return sorted(joblist)


def get_log_file(restclient, urlpath):
    response = restclient.get(urlpath)
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        logger.error("{}".format(str(e)))
        return ""
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, ValueError):
        logger.error("timeout or ValueError")
        return ""
    return response.content.decode(response.encoding)


def get_job_list(numjobs, jobname, restclient):
    """
    Scrape the log server for jobs and extract the job list.

    :param obj restclient: A restclient to the logs server
    :param str jobname: The job name
    :param int numjobs: the number of jobs to scrape
    :return dict: A dictionary of job numbers
    """
    try:
        response = restclient.get(jobname)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Whoops it wasn't a 200
        logger.error("{}".format(str(e)))
        return {}, -1, -1
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, ValueError):
        logger.error("timeout or ValueError")
        return {}, -1, -1
    job_list_html = response.content.decode(response.encoding)
    job_list = extract_job_list_from_html(job_list_html)[-numjobs:]
    return OrderedDict.fromkeys(job_list, {}), job_list[0], job_list[-1]
