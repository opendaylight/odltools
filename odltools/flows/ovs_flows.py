# Copyright (c) 2018 Red Hat, Inc. and others.  All rights reserved.
#
# This program and the accompanying materials are made available under the
# terms of the Eclipse Public License v1.0 which accompanies this distribution,
# and is available at http://www.eclipse.org/legal/epl-v10.html

import logging
from pprint import pformat
import re

from odltools.common import files
from odltools.common import ssh
from odltools.flows.flow import Flow
from odltools.flows.flow import FlowTable
from odltools.netvirt import tables

logger = logging.getLogger("ovs.flows")


# TODO:
# metadata decoder
# mac to port
# REG6 decoder
# group decoder
# curl -s -u admin:admin -X GET 127.0.0.1:8080/restconf/operational/odl-l3vpn:learnt-vpn-vip-to-port-data
# - check if external ip is resolved, devstack uses port 8087


class OvsFlow(Flow):
    def __init__(self, data):
        super(OvsFlow, self).__init__(data)

    def parse(self):
        """Parse the flow into a map."""
        # cookie=0x805138a, duration=193.107s, table=50, n_packets=119, n_bytes=11504, idle_timeout=300,
        #  send_flow_rem priority=20,metadata=0x2138a000000/0xfffffffff000000,dl_src=fa:16:3e:15:a8:66
        #  actions=goto_table:51

        if len(self.rdata) == 0:
            logger.warn("There is no data to process")
            return

        # Create a dictionary of all tokens in the flow.
        self.pdata[Flow.IDLE_TIMEOUT] = "---"
        self.pdata[Flow.SEND_FLOW_REMOVED] = "-"
        tokens = self.rdata.split(" ")
        for token in tokens:
            # most lines are key=value so look for that pattern
            splits = token.split("=", 1)
            if len(splits) == 2:
                if Flow.PRIORITY in splits[0]:
                    splitp = splits[1].split(",", 1)
                    if len(splitp) == 2:
                        self.pdata[Flow.PRIORITY] = splitp[0]
                        self.pdata[Flow.MATCH] = splitp[1]
                    else:
                        self.pdata[Flow.PRIORITY] = splitp[0]
                        self.pdata[Flow.MATCH] = ""
                else:
                    self.pdata[splits[0]] = splits[1].rstrip(",")
            elif token == Flow.SEND_FLOW_REMOVED:
                # send_flow_rem is a single token without a value
                self.pdata[token] = token
        logger.debug("parse:\nProcessed line %s into:\n%s",
                     self.rdata, pformat(self.pdata))
        return self.pdata

    def re_table(self, match):
        """
        regex function to add the table name to table lines

        :param match: The regex match
        :return: The new line with table name
        :rtype: str
        """
        if match.group(Flow.GOTO) is not None:
            table_id = int(match.group(Flow.GOTO))
        elif match.group(Flow.RESUBMIT) is not None:
            table_id = int(match.group(Flow.RESUBMIT))
        else:
            table_id = 256

        rep = "{}({})".format(match.group(), tables.get_table_name(table_id))
        return rep

    def format(self):
        # Match goto_table: nnn or resubmit(,nnn) and return as goto or resubmit match group
        re_gt = re.compile(r"goto_table:(?P<goto>\d{1,3})|"
                           r"resubmit\(,(?P<resubmit>\d{1,3})\)")

        line = self.pdata
        if Flow.ACTIONS in line:
            nactions = re_gt.sub(self.re_table, line[Flow.ACTIONS])
        else:
            logger.warn("Missing actions in %s", line)
            nactions = ""

        self.fdata = "{:15}  {:10}  {:3} {:20} {:6} {:12}  {:1} {:3}  {:5}  matches={}  actions={}\n" \
            .format(line[Flow.COOKIE], line[Flow.DURATION],
                    line[Flow.TABLE], tables.get_table_name(int(line[Flow.TABLE])),
                    line[Flow.N_PACKETS], line[Flow.N_BYTES],
                    line[Flow.SEND_FLOW_REMOVED][0], line[Flow.IDLE_TIMEOUT],
                    line[Flow.PRIORITY],
                    line[Flow.MATCH],
                    nactions)

        logger.debug("format: formatted line:\l%s", self.fdata)


class OvsFlowTable(FlowTable):
    def __init__(self, data, flow_type, dpnid, name):
        if type(data) is str:
            data = data.splitlines()
        elif type(data) is list:
            data = data
        else:
            logger.error("init: data is not a supported type")
            raise ValueError("init: data is not a supported type")
        super(OvsFlowTable, self).__init__(data, flow_type, dpnid, name)
        self.parse()
        self.format()

    def parse(self):
        """Parse the flow-dump into a table map of flows."""
        # skip the header if present
        if "OFPST_FLOW" in self.rdata[0]:
            start = 1
            logger.debug("parse: will skip first line: OFPST_FLOW line")
        else:
            start = 0
        if "jenkins" in self.rdata[-1]:
            end = len(self.rdata) - 1
            logger.debug("parse: will skip last line: jenkins line")
        else:
            end = len(self.rdata)

        # Parse each line of the data. Each line is a single flow.
        # Create a dictionary of all tokens in that flow.
        # Append this flow dictionary to a list of flows.
        for line in self.rdata[start:end]:
            flow = OvsFlow(line)
            flow.parse()
            flow.format()
            self.add_flow(flow)
        logger.debug("process_data: Processed %d lines, skipped %d", self.num_flows(),
                     start + len(self.rdata) - end)

    def format(self):
        if len(self.tables) == 0:
            logger.warn("There is no data to format")
            return
        header = "{:3}  {:15}  {:10} {:20}     {:6} {:12}  {:1} {:3}  {:5}  {}  {}\n" \
            .format("nnn", Flow.COOKIE, Flow.DURATION, Flow.TABLE, "n_pack", Flow.N_BYTES,
                    "S", "ito", "prio", Flow.MATCH, Flow.ACTIONS)
        header_under = "{:3}  {:15}  {:10} {:20}     {:6} {:12} {:1} {:3}  {:5}  {:14}\n" \
            .format("-"*3, "-"*9, "-"*8, "-"*20, "-"*6, "-"*12, "-"*1, "-"*3, "-"*5, "-"*10)
        # Add the header as the first two lines of formatted data
        self.fdata = [header, header_under]
        i = 0
        for tableid, flows in sorted(self.tables.items()):
            for flow in flows:
                i += 1
                fline = "{:3} {}".format(i, flow.fdata)
                self.fdata.append(fline)


def run(args):
    if args.infile:
        logger.info("Parsing {} into {}".format(args.infile, args.outfile))
        data = files.readlines(args.infile)
    else:
        logger.info("Executing ssh {}@{}:{} -c sudo ovs-ofctl dump-flows br-int and parsing into {}"
                    .format(args.ip, args.user, args.port, args.outfile))
        data = ssh.execute(args.ip, args.port, args.user, args.pw, "sudo ovs-ofctl dump-flows br-int")

    if data:
        flow_table = OvsFlowTable(data, "ovs", "dpid", "name")

        if flow_table and flow_table.fdata:
            files.writelines(args.outfile, flow_table.fdata)
